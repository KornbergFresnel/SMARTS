# MIT License

# Copyright (C) 2021. Huawei Technologies Co., Ltd. All rights reserved.

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

import logging
import time

from collections import deque, namedtuple
from dataclasses import dataclass
from functools import lru_cache
from typing import Dict, Iterable, List, NamedTuple, Set, Tuple

import numpy as np
from direct.showbase.ShowBase import ShowBase
from panda3d.core import (
    FrameBufferProperties,
    GraphicsOutput,
    GraphicsPipe,
    NodePath,
    OrthographicLens,
    Texture,
    WindowProperties,
)

from smarts.core import coordinates
from smarts.core import scenario
from smarts.core import waypoints
from smarts.core.coordinates import BoundingBox, Heading, HeadingMethods
from smarts.core.events import Events, Collision
from smarts.core.lidar import Lidar
from smarts.core.lidar_sensor_params import SensorParams
from smarts.core.mission_planner import MissionPlanner
from smarts.core.masks import RenderMasks
from smarts.core.scenario import MissionData, Via
from smarts.core.utils import sequence
from smarts.core.utils.math import squared_dist, vec_2d
from smarts.core.waypoints import Waypoint
from smarts.sstudio.types import CutIn, UTurn, ZoneData
from smarts.zoo import worker_pb2

logger = logging.getLogger(__name__)


class VehicleObservation(NamedTuple):
    id: str = None
    position: Tuple[float, float, float] = (None, None, None)
    bounding_box: BoundingBox = BoundingBox()
    heading: float = None
    speed: float = None
    edge_id: str = None
    lane_id: str = None
    lane_index: int = None


def vehicle_observation_to_proto(
    vehicle_observation: VehicleObservation,
) -> worker_pb2.VehicleObservation:
    return worker_pb2.VehicleObservation(
        id=vehicle_observation.id,
        position=vehicle_observation.position,
        bounding_box=coordinates.bounding_box_to_proto(
            vehicle_observation.bounding_box
        ),
        heading=vehicle_observation.heading,
        speed=vehicle_observation.speed,
        edge_id=vehicle_observation.edge_id,
        lane_id=vehicle_observation.lane_id,
        lane_index=vehicle_observation.lane_index,
    )


def proto_to_vehicle_observation(
    proto: worker_pb2.VehicleObservation,
) -> VehicleObservation:
    return VehicleObservation(
        id=proto.id,
        position=tuple(proto.position),
        bounding_box=coordinates.proto_to_bounding_box(proto.bounding_box),
        heading=proto.heading,
        speed=proto.speed,
        edge_id=proto.edge_id,
        lane_id=proto.lane_id,
        lane_index=proto.lane_index,
    )


class EgoVehicleObservation(NamedTuple):
    id: str
    position: np.ndarray  # np.ndarray((3,), dtype=float)
    bounding_box: BoundingBox
    heading: Heading
    speed: float
    steering: float
    yaw_rate: np.ndarray
    edge_id: str
    lane_id: str
    lane_index: int
    mission: MissionData
    linear_velocity: np.ndarray
    angular_velocity: np.ndarray
    linear_acceleration: np.ndarray
    angular_acceleration: np.ndarray
    linear_jerk: np.ndarray
    angular_jerk: np.ndarray


def ego_vehicle_observation_to_proto(
    ego: EgoVehicleObservation,
) -> worker_pb2.EgoVehicleObservation:
    return worker_pb2.EgoVehicleObservation(
        id=ego.id,
        position=ego.position,
        bounding_box=coordinates.bounding_box_to_proto(ego.bounding_box),
        heading=ego.heading,
        speed=ego.speed,
        steering=ego.steering,
        yaw_rate=ego.yaw_rate,
        edge_id=ego.edge_id,
        lane_id=ego.lane_id,
        lane_index=ego.lane_index,
        mission=scenario.mission_to_proto(ego.mission),
        linear_velocity=ego.linear_velocity,
        angular_velocity=ego.angular_velocity,
        linear_acceleration=ego.linear_acceleration,
        angular_acceleration=ego.angular_acceleration,
        linear_jerk=ego.linear_jerk,
        angular_jerk=ego.angular_jerk,
    )


def proto_to_ego_vehicle_observation(
    proto: worker_pb2.EgoVehicleObservation,
) -> EgoVehicleObservation:
    return EgoVehicleObservation(
        id=proto.id,
        position=np.array(proto.position),
        bounding_box=coordinates.proto_to_bounding_box(proto.bounding_box),
        heading=proto.heading,
        speed=proto.speed,
        steering=proto.steering,
        yaw_rate=np.array(proto.yaw_rate),
        edge_id=proto.edge_id,
        lane_id=proto.lane_id,
        lane_index=proto.lane_index,
        mission=scenario.proto_to_mission(proto.mission),
        linear_velocity=np.array(proto.linear_velocity),
        angular_velocity=np.array(proto.angular_velocity),
        linear_acceleration=np.array(proto.linear_acceleration),
        angular_acceleration=np.array(proto.angular_acceleration),
        linear_jerk=np.array(proto.linear_jerk),
        angular_jerk=np.array(proto.angular_jerk),
    )


class RoadWaypoints(NamedTuple):
    lanes: Dict[str, List[Waypoint]] = {}
    route_waypoints: List[Waypoint] = []


def road_waypoints_to_proto(road_waypoints: RoadWaypoints) -> worker_pb2.RoadWaypoints:
    return worker_pb2.RoadWaypoints(
        lanes={
            k: worker_pb2.ListWaypoint(
                waypoints=[waypoints.waypoint_to_proto(elem) for elem in list_elem]
            )
            for k, list_elem in road_waypoints.lanes
        },
        route_waypoints=[
            waypoints.waypoint_to_proto(elem) for elem in road_waypoints.route_waypoints
        ],
    )


def proto_to_road_waypoints(proto: worker_pb2.RoadWaypoints) -> RoadWaypoints:
    return RoadWaypoints(
        lanes={
            k: [waypoints.proto_to_waypoint(elem) for elem in list_elem]
            for k, list_elem in proto.lanes
        },
        route_waypoints=[
            waypoints.proto_to_waypoint(elem) for elem in proto.route_waypoints
        ],
    )


class GridMapMetadata(NamedTuple):
    # time at which the map was loaded
    created_at: int = None
    # map resolution in world-space-distance/cell
    resolution: float = None
    # map width in # of cells
    width: int = None
    # map height in # of cells
    height: int = None
    # camera position when project onto the map
    camera_pos: Tuple[float, float, float] = None
    # camera rotation angle along z-axis when project onto the map
    camera_heading_in_degrees: float = None


def grid_map_metadata_to_proto(
    grid_map_metadata: GridMapMetadata,
) -> worker_pb2.GridMapMetadata:
    return worker_pb2.GridMapMetadata(
        created_at=grid_map_metadata.created_at,
        resolution=grid_map_metadata.resolution,
        width=grid_map_metadata.width,
        height=grid_map_metadata.height,
        camera_pos=grid_map_metadata.camera_pos,
        camera_heading_in_degrees=grid_map_metadata.camera_heading_in_degrees,
    )


def proto_to_grid_map_metadata(proto: worker_pb2.GridMapMetadata) -> GridMapMetadata:
    return GridMapMetadata(
        created_at=proto.created_at,
        resolution=proto.resolution,
        width=proto.width,
        height=proto.height,
        camera_pos=tuple(proto.camera_pos),
        camera_heading_in_degrees=proto.camera_heading_in_degrees,
    )


class TopDownRGB(NamedTuple):
    metadata: GridMapMetadata = GridMapMetadata()
    data: np.ndarray = np.zeros((1, 1), dtype=float)


class OccupancyGridMap(NamedTuple):
    metadata: GridMapMetadata = GridMapMetadata()
    data: np.ndarray = np.zeros((1, 1), dtype=float)


class DrivableAreaGridMap(NamedTuple):
    metadata: GridMapMetadata = GridMapMetadata()
    data: np.ndarray = np.zeros((1, 1), dtype=float)


def grid_map_to_proto(grid_map) -> worker_pb2.GridMap:
    return worker_pb2.GridMap(
        metadata=grid_map_metadata_to_proto(grid_map.metadata),
        data=worker_pb2.Matrix(
            data=np.ravel(grid_map.data),
            rows=(grid_map.data).shape[0],
            cols=(grid_map.data).shape[1],
        ),
    )


def proto_to_grid_map(proto: worker_pb2.GridMap, class_type):
    return class_type(
        metadata=proto_to_grid_map_metadata(proto.metadata),
        data=proto_matrix_to_obs(proto.data),
    )


def proto_matrix_to_obs(proto: worker_pb2.Matrix) -> np.ndarray:
    return np.array(proto.data).reshape((proto.rows, proto.cols))


class ViaPoint(NamedTuple):
    position: Tuple[float, float] = (None, None)
    lane_index: float = None
    edge_id: str = None
    required_speed: float = None


def via_point_to_proto(via_point: ViaPoint) -> worker_pb2.ViaPoint:
    return worker_pb2.ViaPoint(
        position=via_point.position,
        lane_index=via_point.lane_index,
        edge_id=via_point.edge_id,
        required_speed=via_point.required_speed,
    )


def proto_to_via_point(proto: worker_pb2.ViaPoint) -> ViaPoint:
    return ViaPoint(
        position=tuple(proto.position),
        lane_index=proto.lane_index,
        edge_id=proto.edge_id,
        required_speed=proto.required_speed,
    )


class Vias(NamedTuple):
    near_via_points: List[ViaPoint] = []
    """Ordered list of nearby points that have not been hit"""
    hit_via_points: List[ViaPoint] = []
    """List of points that were hit in the previous step"""


def vias_to_proto(vias: Vias) -> worker_pb2.Vias:
    return worker_pb2.Vias(
        near_via_points=[via_point_to_proto(elem) for elem in vias.near_via_points],
        hit_via_points=[via_point_to_proto(elem) for elem in vias.hit_via_points],
    )


def proto_to_vias(proto: worker_pb2.Vias) -> Vias:
    return Vias(
        near_via_points=[proto_to_via_point(elem) for elem in proto.near_via_points],
        hit_via_points=[proto_to_via_point(elem) for elem in proto.hit_via_points],
    )


class Observation(NamedTuple):
    events: Events
    ego_vehicle_state: EgoVehicleObservation
    neighborhood_vehicle_states: List[VehicleObservation]
    waypoint_paths: List[List[Waypoint]]
    distance_travelled: float
    # TODO: Convert to `namedtuple` or only return point cloud
    # [points], [hits], [(ray_origin, ray_direction)]
    # TODO: Convert type to Tuple[
    #     List[np.ndarray((3,), dtype=float)],
    #     List[np.ndarray((3,), dtype=float)],
    #     List[np.ndarray((2,3), dtype=float)]
    # ]
    lidar_point_cloud: Tuple[
        List[np.ndarray], List[np.ndarray], List[Tuple[np.ndarray, np.ndarray]]
    ]
    drivable_area_grid_map: DrivableAreaGridMap
    occupancy_grid_map: OccupancyGridMap
    top_down_rgb: TopDownRGB
    road_waypoints: RoadWaypoints = RoadWaypoints()
    via_data: Vias = Vias()


class Sensors:
    _log = logging.getLogger("Sensors")

    @staticmethod
    def observe_batch(sim, agent_id, sensor_states, vehicles):
        """Operates on a batch of vehicles for a single agent."""
        # TODO: Replace this with a more efficient implementation that _actually_
        #       does batching
        assert sensor_states.keys() == vehicles.keys()

        observations, dones = {}, {}
        for vehicle_id, vehicle in vehicles.items():
            sensor_state = sensor_states[vehicle_id]
            observations[vehicle_id], dones[vehicle_id] = Sensors.observe(
                sim, agent_id, sensor_state, vehicle
            )

        return observations, dones

    @staticmethod
    def observe(sim, agent_id, sensor_state, vehicle):
        neighborhood_vehicles = []
        if vehicle.subscribed_to_neighborhood_vehicles_sensor:
            neighborhood_vehicles = vehicle.neighborhood_vehicles_sensor()

            if len(neighborhood_vehicles) > 0:
                neighborhood_vehicle_wps = sim.waypoints.closest_waypoint_batched(
                    [v.pose for v in neighborhood_vehicles],
                    within_radius=vehicle.length,
                    filter_from_count=10,
                )
                neighborhood_vehicles = [
                    VehicleObservation(
                        id=v.vehicle_id,
                        position=v.pose.position,
                        bounding_box=v.dimensions,
                        heading=v.pose.heading,
                        speed=v.speed,
                        edge_id=sim.road_network.edge_by_lane_id(wp.lane_id).getID(),
                        lane_id=wp.lane_id,
                        lane_index=wp.lane_index,
                    )
                    for v, wp in zip(neighborhood_vehicles, neighborhood_vehicle_wps)
                ]

        if vehicle.subscribed_to_waypoints_sensor:
            waypoint_paths = vehicle.waypoints_sensor()
        else:
            waypoint_paths = sim.waypoints.waypoint_paths_at(
                vehicle.pose,
                lookahead=1,
                within_radius=vehicle.length,
                filter_from_count=3,  # For calculating distance travelled
            )

        closest_waypoint = sim.waypoints.closest_waypoint(vehicle.pose)
        ego_lane_id = closest_waypoint.lane_id
        ego_lane_index = closest_waypoint.lane_index
        ego_edge_id = sim.road_network.edge_by_lane_id(ego_lane_id).getID()
        ego_vehicle_state = vehicle.state

        acceleration_params = {
            "linear_acceleration": np.array([0, 0, 0]),
            "angular_acceleration": np.array([0, 0, 0]),
            "linear_jerk": np.array([0, 0, 0]),
            "angular_jerk": np.array([0, 0, 0]),
        }
        if vehicle.subscribed_to_accelerometer_sensor:
            acceleration_values = vehicle.accelerometer_sensor(
                ego_vehicle_state.linear_velocity, ego_vehicle_state.angular_velocity
            )
            acceleration_params.update(
                dict(
                    zip(
                        [
                            "linear_acceleration",
                            "angular_acceleration",
                            "linear_jerk",
                            "angular_jerk",
                        ],
                        acceleration_values,
                    )
                )
            )

        # Retrieve mission data
        mission_data = sensor_state.mission_planner.mission.data
        # Change (i)  goal type from EndlessGoal or PositionalGoal to GoalData type
        #        (ii) zone type from "MapZone" to ZoneData type
        if (mission_data.entry_tactic is not None) and (
            mission_data.entry_tactic.zone is not None
        ):
            entry_tactic_data = mission_data.entry_tactic._replace(
                zone=mission_data.entry_tactic.zone.data
            )
            mission_data = mission_data._replace(
                goal=mission_data.goal.data, entry_tactic=entry_tactic_data
            )
        else:
            mission_data = mission_data._replace(goal=mission_data.goal.data)

        ego_vehicle_observation = EgoVehicleObservation(
            id=ego_vehicle_state.vehicle_id,
            position=ego_vehicle_state.pose.position,
            bounding_box=ego_vehicle_state.dimensions,
            heading=ego_vehicle_state.pose.heading,
            speed=ego_vehicle_state.speed,
            steering=ego_vehicle_state.steering,
            yaw_rate=ego_vehicle_state.yaw_rate,
            edge_id=ego_edge_id,
            lane_id=ego_lane_id,
            lane_index=ego_lane_index,
            mission=mission_data,
            linear_velocity=ego_vehicle_state.linear_velocity,
            angular_velocity=ego_vehicle_state.angular_velocity,
            **acceleration_params,
        )

        road_waypoints = (
            vehicle.road_waypoints_sensor()
            if vehicle.subscribed_to_road_waypoints_sensor
            else RoadWaypoints()
        )

        near_via_points = []
        hit_via_points = []
        if vehicle.subscribed_to_via_sensor:
            (
                near_via_points,
                hit_via_points,
            ) = vehicle.via_sensor()
        via_data = Vias(
            near_via_points=near_via_points,
            hit_via_points=hit_via_points,
        )

        vehicle.trip_meter_sensor.append_waypoint_if_new(waypoint_paths[0][0])
        distance_travelled = vehicle.trip_meter_sensor(sim)

        vehicle.driven_path_sensor.track_latest_driven_path(sim)

        if not vehicle.subscribed_to_waypoints_sensor:
            waypoint_paths = None

        drivable_area_grid_map = (
            vehicle.drivable_area_grid_map_sensor()
            if vehicle.subscribed_to_drivable_area_grid_map_sensor
            else DrivableAreaGridMap()
        )
        ogm = (
            vehicle.ogm_sensor()
            if vehicle.subscribed_to_ogm_sensor
            else OccupancyGridMap()
        )
        rgb = vehicle.rgb_sensor() if vehicle.subscribed_to_rgb_sensor else TopDownRGB()
        lidar = (
            vehicle.lidar_sensor()
            if vehicle.subscribed_to_lidar_sensor
            else ([], [], [])
        )

        done, events = Sensors._is_done_with_events(
            sim, agent_id, vehicle, sensor_state
        )

        if (
            done
            and sensor_state.steps_completed == 1
            and agent_id in sim.agent_manager.ego_agent_ids
        ):
            logger.warning(f"Agent Id: {agent_id} is done on the first step")

        return (
            Observation(
                events=events,
                ego_vehicle_state=ego_vehicle_observation,
                neighborhood_vehicle_states=neighborhood_vehicles,
                waypoint_paths=waypoint_paths,
                distance_travelled=distance_travelled,
                top_down_rgb=rgb,
                occupancy_grid_map=ogm,
                drivable_area_grid_map=drivable_area_grid_map,
                lidar_point_cloud=lidar,
                road_waypoints=road_waypoints,
                via_data=via_data,
            ),
            done,
        )

    @staticmethod
    def step(sim, sensor_state):
        return sensor_state.step()

    @classmethod
    def _is_done_with_events(cls, sim, agent_id, vehicle, sensor_state):
        interface = sim.agent_manager.agent_interface_for_agent_id(agent_id)
        done_criteria = interface.done_criteria

        collided = (
            sim.vehicle_did_collide(vehicle.id) if done_criteria.collision else False
        )
        is_off_road = (
            cls._vehicle_is_off_road(sim, vehicle) if done_criteria.off_road else False
        )
        is_on_shoulder = (
            cls._vehicle_is_on_shoulder(sim, vehicle)
            if done_criteria.on_shoulder
            else False
        )
        is_not_moving = (
            cls._vehicle_is_not_moving(sim, vehicle)
            if done_criteria.not_moving
            else False
        )
        reached_goal = cls._agent_reached_goal(sim, vehicle)
        reached_max_episode_steps = sensor_state.reached_max_episode_steps
        is_off_route, is_wrong_way = cls._vehicle_is_off_route_and_wrong_way(
            sim, vehicle
        )

        done = (
            is_off_road
            or reached_goal
            or reached_max_episode_steps
            or is_on_shoulder
            or collided
            or is_not_moving
            or (is_off_route and done_criteria.off_route)
            or (is_wrong_way and done_criteria.wrong_way)
        )

        events = Events(
            collisions=sim.vehicle_collisions(vehicle.id),
            off_road=is_off_road,
            reached_goal=reached_goal,
            reached_max_episode_steps=reached_max_episode_steps,
            off_route=is_off_route,
            wrong_way=is_wrong_way,
            not_moving=is_not_moving,
        )

        return done, events

    @classmethod
    def _agent_reached_goal(cls, sim, vehicle):
        sensor_state = sim.vehicle_index.sensor_state_for_vehicle_id(vehicle.id)
        distance_travelled = vehicle.trip_meter_sensor()
        mission = sensor_state.mission_planner.mission
        return mission.is_complete(vehicle, distance_travelled)

    @classmethod
    def _vehicle_is_off_road(cls, sim, vehicle):
        if sim.scenario.road_network.point_is_within_road(vehicle.position):
            return False

        return True

    @classmethod
    def _vehicle_is_on_shoulder(cls, sim, vehicle):
        return any(
            [
                not sim.scenario.road_network.point_is_within_road(corner_coordinate)
                for corner_coordinate in vehicle.bounding_box
            ]
        )

    @classmethod
    def _vehicle_is_not_moving(cls, sim, vehicle):
        last_n_seconds_considered = 60

        # Flag if the vehicle has been immobile for the past 60 seconds
        if sim.elapsed_sim_time < last_n_seconds_considered:
            return False

        distance = vehicle.driven_path_sensor.distance_travelled(
            sim, last_n_seconds=last_n_seconds_considered
        )

        # Due to controller instabilities there may be some movement even when a
        # vehicle is "stopped". Here we allow 1m of total distance in 60 seconds.
        return distance < 1

    @classmethod
    def _vehicle_is_off_route_and_wrong_way(cls, sim, vehicle):
        """Determines if the agent is on route and on the correct side of the road.

        Args:
            sim: An instance of the simulator.
            agent_id: The id of the agent to check.

        Returns:
            A tuple (is_off_route, is_wrong_way)
            is_off_route:
                Actor's vehicle is not on its route or an oncoming traffic lane.
            is_wrong_way:
                Actor's vehicle is going against the lane travel direction.
        """

        sensor_state = sim.vehicle_index.sensor_state_for_vehicle_id(vehicle.id)
        route_edges = sensor_state.mission_planner.route.edges

        vehicle_pos = vehicle.position[:2]
        vehicle_minimum_radius_bounds = (
            np.linalg.norm(vehicle.chassis.dimensions[:2]) * 0.5
        )
        # Check that center of vehicle is still close to route
        # Most lanes are around 3.2 meters wide
        nearest_lanes = sim.scenario.road_network.nearest_lanes(
            vehicle_pos, radius=vehicle_minimum_radius_bounds + 5
        )

        # No road nearby.
        if not nearest_lanes:
            return (True, False)

        nearest_lane, _ = nearest_lanes[0]

        # Route is endless
        if not route_edges:
            is_wrong_way = cls._vehicle_is_wrong_way(sim, vehicle, nearest_lane.getID())
            return (False, is_wrong_way)

        closest_edges = []
        used_edges = set()
        for lane, _ in nearest_lanes:
            edge = lane.getEdge()
            if edge in used_edges:
                continue
            used_edges.add(edge)
            closest_edges.append(edge)

        # TODO: Narrow down the route edges to check using distance travelled.
        is_off_route, route_edge_or_oncoming = cls._vehicle_off_route_info(
            sim.scenario.root_filepath, tuple(route_edges), tuple(closest_edges)
        )
        is_wrong_way = False
        if route_edge_or_oncoming:
            # Lanes from an edge are parallel so any lane from the edge will do for direction check
            # but the innermost lane will be the last lane in the edge and usually the closest.
            lane_to_check = route_edge_or_oncoming.getLanes()[-1]
            is_wrong_way = cls._vehicle_is_wrong_way(
                sim, vehicle, lane_to_check.getID()
            )

        return (is_off_route, is_wrong_way)

    @staticmethod
    def _vehicle_is_wrong_way(sim, vehicle, lane_id):
        closest_waypoint = sim.scenario.waypoints.closest_waypoint_on_lane(
            vehicle.pose,
            lane_id,
        )

        # Check if the vehicle heading is oriented away from the lane heading.
        return (
            np.fabs(
                HeadingMethods.relative_to(
                    vehicle.pose.heading, closest_waypoint.heading
                )
            )
            > 0.5 * np.pi
        )

    @classmethod
    @lru_cache(maxsize=32)
    def _vehicle_off_route_info(cls, instance_id, route_edges, closest_edges):
        for route_edge in route_edges:
            for index_of_edge in range(len(closest_edges)):
                if route_edge != closest_edges[index_of_edge]:
                    continue
                closest_edge = cls._edge_or_closer_oncoming(
                    instance_id, index_of_edge, closest_edges
                )
                return (False, closest_edge)

        # Check to see if actor is in the oncoming traffic lane.
        for close_edge in closest_edges:
            # Forgive the actor if it is in an intersection
            if close_edge.isSpecial():
                return (False, close_edge)

            oncoming_edge = cls._oncoming_traffic_edge(instance_id, close_edge)

            if not oncoming_edge:
                continue

            for close_edge in route_edges:
                if oncoming_edge != close_edge:
                    continue
                # Actor is in the oncoming traffic lane.
                return (False, oncoming_edge)

        return (True, None)

    @classmethod
    def _edge_or_closer_oncoming(cls, instance_id, on_route_edge_index, closest_edges):
        """Check backward to find if the oncoming edge is closer."""
        oncoming_edge = cls._oncoming_traffic_edge(
            instance_id, closest_edges[on_route_edge_index]
        )
        if (
            oncoming_edge
            and oncoming_edge in closest_edges[: max(0, on_route_edge_index - 1)]
        ):
            # oncoming edge was closer
            return oncoming_edge
        # or the route edge we already found
        return closest_edges[on_route_edge_index]

    @staticmethod
    @lru_cache(maxsize=128)
    def _oncoming_traffic_edge(instance_id, edge):
        from_node = edge.getFromNode()
        to_node = edge.getToNode()

        for candidate in to_node.getOutgoing():
            if candidate.getToNode() == from_node:
                return candidate

        return None

    @classmethod
    def clean_up(cls):
        cls._oncoming_traffic_edge.cache_clear()
        cls._vehicle_off_route_info.cache_clear()


class Sensor:
    def step(self):
        pass


class SensorState:
    def __init__(self, max_episode_steps, mission_planner):
        self._max_episode_steps = max_episode_steps
        self._mission_planner = mission_planner
        self._step = 0

    def step(self):
        self._step += 1

    @property
    def reached_max_episode_steps(self):
        if self._max_episode_steps is None:
            return False

        return self._step >= self._max_episode_steps

    @property
    def mission_planner(self):
        return self._mission_planner

    @property
    def steps_completed(self):
        return self._step


class CameraSensor(Sensor):
    def __init__(self, vehicle, scene_np: NodePath, showbase: ShowBase):
        self._log = logging.getLogger(self.__class__.__name__)
        self._vehicle = vehicle
        self._scene_np = scene_np
        self._showbase = showbase

    def _build_offscreen_camera(
        self,
        name: str,
        mask: int,
        width: int,
        height: int,
        resolution: float,
    ):
        # setup buffer
        win_props = WindowProperties.size(width, height)
        fb_props = FrameBufferProperties()
        fb_props.setRgbColor(True)
        fb_props.setRgbaBits(8, 8, 8, 1)
        # XXX: Though we don't need the depth buffer returned, setting this to 0
        #      causes undefined behaviour where the ordering of meshes is random.
        fb_props.setDepthBits(8)

        buffer = self._showbase.win.engine.makeOutput(
            self._showbase.pipe,
            "{}-buffer".format(name),
            -100,
            fb_props,
            win_props,
            GraphicsPipe.BFRefuseWindow,
            self._showbase.win.getGsg(),
            self._showbase.win,
        )
        buffer.setClearColor((0, 0, 0, 0))  # Set background color to black

        # setup texture
        tex = Texture()
        region = buffer.getDisplayRegion(0)
        region.window.addRenderTexture(
            tex, GraphicsOutput.RTM_copy_ram, GraphicsOutput.RTP_color
        )

        # setup camera
        lens = OrthographicLens()
        lens.setFilmSize(width * resolution, height * resolution)

        camera_np = self._showbase.makeCamera(
            buffer, camName=name, scene=self._scene_np, lens=lens
        )
        camera_np.reparentTo(self._scene_np)

        # mask is set to make undesireable objects invisible to this camera
        camera_np.node().setCameraMask(camera_np.node().getCameraMask() & mask)

        return OffscreenCamera(camera_np, buffer, tex)

    def _follow_vehicle(self, camera_np):
        center = self._vehicle.position
        largest_dim = max(self._vehicle._chassis.dimensions)
        camera_np.setPos(center[0], center[1], 20 * largest_dim)
        camera_np.lookAt(*center)
        camera_np.setH(self._vehicle._np.getH())

    def _wait_for_ram_image(self, format, retries=100):
        # Rarely, we see dropped frames where an image is not available
        # for our observation calculations.
        #
        # We've seen this happen fairly reliable when we are initializing
        # a multi-agent + multi-instance simulation.
        #
        # To deal with this, we can try to force a render and block until
        # we are fairly certain we have an image in ram to return to the user
        for i in range(retries):
            if self._camera.tex.mightHaveRamImage():
                break
            self._log.debug(
                f"No image available (attempt {i}/{retries}), forcing a render"
            )
            region = self._camera.buffer.getDisplayRegion(0)
            region.window.engine.renderFrame()

        assert self._camera.tex.mightHaveRamImage()
        ram_image = self._camera.tex.getRamImageAs(format)
        assert ram_image is not None
        return ram_image


class OffscreenCamera(NamedTuple):
    camera_np: NodePath
    buffer: GraphicsOutput
    tex: Texture

    def teardown(self, showbase: ShowBase):
        self.camera_np.removeNode()
        region = self.buffer.getDisplayRegion(0)
        region.window.clearRenderTextures()
        self.buffer.removeAllDisplayRegions()
        showbase.graphicsEngine.removeWindow(self.buffer)


class DrivableAreaGridMapSensor(CameraSensor):
    def __init__(
        self,
        vehicle,
        width: int,
        height: int,
        resolution: float,
        scene_np: NodePath,
        showbase: ShowBase,
    ):
        super().__init__(vehicle, scene_np, showbase)
        self._camera = self._build_offscreen_camera(
            "drivable_area_grid_map",
            RenderMasks.DRIVABLE_AREA_HIDE,
            width,
            height,
            resolution,
        )

        self._resolution = resolution

    def step(self):
        self._follow_vehicle(camera_np=self._camera.camera_np)

    def __call__(self) -> DrivableAreaGridMap:
        assert (
            self._camera is not None
        ), "Drivable area grid map has not been initialized"

        ram_image = self._wait_for_ram_image(format="A")
        mem_view = memoryview(ram_image)
        image = np.frombuffer(mem_view, np.uint8)
        image.shape = (self._camera.tex.getYSize(), self._camera.tex.getXSize(), 1)
        image = np.flipud(image)

        metadata = GridMapMetadata(
            created_at=int(time.time()),
            resolution=self._resolution,
            height=image.shape[0],
            width=image.shape[1],
            camera_pos=self._camera.camera_np.getPos(),
            camera_heading_in_degrees=self._camera.camera_np.getH(),
        )
        return DrivableAreaGridMap(data=image, metadata=metadata)

    def teardown(self):
        self._camera.teardown(self._showbase)


class OGMSensor(CameraSensor):
    def __init__(
        self,
        vehicle,
        width: int,
        height: int,
        resolution: float,
        scene_np: NodePath,
        showbase: ShowBase,
    ):
        super().__init__(vehicle, scene_np, showbase)
        self._camera = self._build_offscreen_camera(
            "ogm", RenderMasks.OCCUPANCY_HIDE, width, height, resolution
        )

        self._resolution = resolution

    def step(self):
        self._follow_vehicle(camera_np=self._camera.camera_np)

    def __call__(self) -> OccupancyGridMap:
        assert self._camera is not None, "OGM has not been initialized"

        ram_image = self._wait_for_ram_image(format="A")
        mem_view = memoryview(ram_image)
        grid = np.frombuffer(mem_view, np.uint8)
        grid.shape = (self._camera.tex.getYSize(), self._camera.tex.getXSize(), 1)
        grid = np.flipud(grid)
        grid = grid.clip(min=0, max=1).astype(np.int8)
        grid *= 100  # full confidence on known cells

        metadata = GridMapMetadata(
            created_at=int(time.time()),
            resolution=self._resolution,
            height=grid.shape[0],
            width=grid.shape[1],
            camera_pos=self._camera.camera_np.getPos(),
            camera_heading_in_degrees=self._camera.camera_np.getH(),
        )
        return OccupancyGridMap(data=grid, metadata=metadata)

    def teardown(self):
        self._camera.teardown(self._showbase)


class RGBSensor(CameraSensor):
    def __init__(
        self,
        vehicle,
        width: int,
        height: int,
        resolution: float,
        scene_np: NodePath,
        showbase: ShowBase,
    ):
        super().__init__(vehicle, scene_np, showbase)
        self._camera = self._build_offscreen_camera(
            "rgb", RenderMasks.RGB_HIDE, width, height, resolution
        )

        self._resolution = resolution

    def step(self):
        self._follow_vehicle(camera_np=self._camera.camera_np)

    def __call__(self) -> TopDownRGB:
        assert self._camera is not None, "RGB has not been initialized"

        ram_image = self._wait_for_ram_image(format="RGB")
        mem_view = memoryview(ram_image)
        image = np.frombuffer(mem_view, np.uint8)
        image.shape = (self._camera.tex.getYSize(), self._camera.tex.getXSize(), 3)
        image = np.flipud(image)

        metadata = GridMapMetadata(
            created_at=int(time.time()),
            resolution=self._resolution,
            height=image.shape[0],
            width=image.shape[1],
            camera_pos=self._camera.camera_np.getPos(),
            camera_heading_in_degrees=self._camera.camera_np.getH(),
        )
        return TopDownRGB(data=image, metadata=metadata)

    def teardown(self):
        self._camera.teardown(self._showbase)


class LidarSensor(Sensor):
    def __init__(
        self,
        vehicle,
        bullet_client,
        showbase: ShowBase,
        sensor_params: SensorParams = None,
        lidar_offset=(0, 0, 1),
    ):
        self._vehicle = vehicle
        self._bullet_client = bullet_client
        self._lidar_offset = np.array(lidar_offset)
        self._showbase = showbase

        self._lidar = Lidar(
            self._vehicle.position + self._lidar_offset,
            sensor_params,
            self._bullet_client,
        )

    def step(self):
        self._follow_vehicle()

    def _follow_vehicle(self):
        self._lidar.origin = self._vehicle.position + self._lidar_offset

    def __call__(self):
        return self._lidar.compute_point_cloud()

    def teardown(self):
        pass


class DrivenPathSensor(Sensor):
    """Tracks the driven path as a series of positions (regardless if the vehicle is
    following the route or not). For performance reasons it only keeps the last
    N=max_path_length path segments.
    """

    Entry = namedtuple("TimeAndPos", ["timestamp", "position"])

    def __init__(self, vehicle, max_path_length: float = 500):
        self._vehicle = vehicle
        self._driven_path = deque(maxlen=max_path_length)

    def track_latest_driven_path(self, sim):
        pos = self._vehicle.position[:2]
        self._driven_path.append(
            DrivenPathSensor.Entry(timestamp=sim.elapsed_sim_time, position=pos)
        )

    def __call__(self):
        return [x.position for x in self._driven_path]  # only return the positions

    def teardown(self):
        pass

    def distance_travelled(
        self, sim, last_n_seconds: float = None, last_n_steps: int = None
    ):
        if last_n_seconds is None and last_n_steps is None:
            raise ValueError("Either last N seconds or last N steps must be provided")

        if last_n_steps is not None:
            n = last_n_steps + 1  # to factor in the current step we're on
            filtered_pos = [x.position for x in self._driven_path][-n:]
        else:  # last_n_seconds
            threshold = sim.elapsed_sim_time - last_n_seconds
            filtered_pos = [
                x.position for x in self._driven_path if x.timestamp >= threshold
            ]

        xs = np.array([p[0] for p in filtered_pos])
        ys = np.array([p[1] for p in filtered_pos])
        dist_array = (xs[:-1] - xs[1:]) ** 2 + (ys[:-1] - ys[1:]) ** 2
        return np.sum(np.sqrt(dist_array))


class TripMeterSensor(Sensor):
    """Tracks distance travelled along the route (in KM). Kilometeres driven while
    off-route are not counted as part of the total.
    """

    def __init__(self, vehicle, sim, mission_planner):
        self._vehicle = vehicle
        self._sim = sim
        self._mission_planner = mission_planner

        waypoint_paths = sim.waypoints.waypoint_paths_at(
            vehicle.pose, lookahead=1, within_radius=vehicle.length
        )
        starting_wp = waypoint_paths[0][0]
        self._wps_for_distance = [starting_wp]

        self._dist_travelled = 0.0
        self._last_dist_travelled = 0.0

    def append_waypoint_if_new(self, new_wp):
        # Distance calculation. Intention is the shortest trip travelled at the lane
        # level the agent has travelled. This is to prevent lateral movement from
        # increasing the total distance travelled.
        most_recent_wp = self._wps_for_distance[-1]
        self._last_dist_travelled = self._dist_travelled

        wp_edge = self._sim.road_network.edge_by_lane_id(new_wp.lane_id)

        should_count_wp = (
            # if we do not have a fixed route, we count all waypoints we accumulate
            not self._mission_planner.mission.has_fixed_route
            # if we have a route to follow, only count wps on route
            or wp_edge in self._mission_planner.route.edges
        )

        threshold_for_counting_wp = 0.5  # meters from last tracked waypoint
        if (
            np.linalg.norm(new_wp.pos - most_recent_wp.pos) > threshold_for_counting_wp
            and should_count_wp
        ):
            self._dist_travelled += TripMeterSensor._compute_additional_dist_travelled(
                most_recent_wp, new_wp
            )
            self._wps_for_distance.append(new_wp)

    @staticmethod
    def _compute_additional_dist_travelled(recent_wp, waypoint):
        heading_vec = HeadingMethods.direction_vector(recent_wp.heading)
        disp_vec = waypoint.pos - recent_wp.pos
        direction = np.sign(np.dot(heading_vec, disp_vec))
        distance = np.linalg.norm(disp_vec)
        return direction * distance

    def __call__(self, increment=False):
        if increment:
            return self._dist_travelled - self._last_dist_travelled

        return self._dist_travelled

    def teardown(self):
        pass


class NeighborhoodVehiclesSensor(Sensor):
    def __init__(self, vehicle, sim, radius=None):
        self._vehicle = vehicle
        self._sim = sim
        self._radius = radius

    @property
    def radius(self):
        return self._radius

    def __call__(self):
        return self._sim.neighborhood_vehicles_around_vehicle(
            self._vehicle, radius=self._radius
        )

    def teardown(self):
        pass


class WaypointsSensor(Sensor):
    def __init__(self, sim, vehicle, mission_planner: MissionPlanner, lookahead=50):
        self._sim = sim
        self._vehicle = vehicle
        self._mission_planner = mission_planner
        self._lookahead = lookahead

    def __call__(self):
        waypoints_with_task = None

        @lru_cache(1)
        def lazy_calculate_waypoints():
            return self._mission_planner.waypoint_paths_at(
                sim=self._sim,
                pose=self._vehicle.pose,
                lookahead=self._lookahead,
            )

        if self._mission_planner.mission.data.task is not None:
            if isinstance(self._mission_planner.mission.data.task, UTurn):
                waypoints_with_task = self._mission_planner.uturn_waypoints(
                    self._sim, self._vehicle.pose, self._vehicle
                )
            elif isinstance(self._mission_planner.mission.data.task, CutIn):
                waypoints_with_task = self._mission_planner.cut_in_waypoints(
                    self._sim, self._vehicle.pose, self._vehicle
                )

        if waypoints_with_task:
            return waypoints_with_task
        else:
            return lazy_calculate_waypoints()

    def teardown(self):
        pass


class RoadWaypointsSensor(Sensor):
    def __init__(self, vehicle, sim, mission_planner, horizon=50):
        self._vehicle = vehicle
        self._sim = sim
        self._mission_planner = mission_planner
        self._horizon = horizon

    def __call__(self):
        wp = self._sim.waypoints.closest_waypoint(self._vehicle.pose)
        road_edges = self._sim.road_network.road_edge_data_for_lane_id(wp.lane_id)

        lane_paths = {}
        for edge in road_edges.forward_edges + road_edges.oncoming_edges:
            for lane in edge.getLanes():
                lane_paths[lane.getID()] = self.paths_for_lane(lane)

        route_waypoints = self.route_waypoints()

        return RoadWaypoints(lanes=lane_paths, route_waypoints=route_waypoints)

    def route_waypoints(self):
        return self._mission_planner.waypoint_paths_at(
            sim=self._sim,
            pose=self._vehicle.pose,
            lookahead=50,
        )

    def paths_for_lane(self, lane, overflow_offset=None):
        if overflow_offset is None:
            offset = self._sim.road_network.offset_into_lane(
                lane, self._vehicle.position[:2]
            )
            start_offset = offset - self._horizon
        else:
            start_offset = lane.getLength() + overflow_offset

        incoming_lanes = lane.getIncoming(onlyDirect=True)
        if start_offset < 0 and len(incoming_lanes) > 0:
            paths = []
            for lane in incoming_lanes:
                paths += self.paths_for_lane(lane, start_offset)
            return paths
        else:
            start_offset = max(0, start_offset)
            wp_start = self._sim.road_network.world_coord_from_offset(
                lane, start_offset
            )

            wps_to_lookahead = self._horizon * 2
            paths = self._sim.waypoints.waypoint_paths_on_lane_at(
                point=wp_start,
                lane_id=lane.getID(),
                lookahead=wps_to_lookahead,
            )
            return paths

    def teardown(self):
        pass


class AccelerometerSensor(Sensor):
    def __init__(self, vehicle, sim):
        self.linear_accelerations = deque(maxlen=3)
        self.angular_accelerations = deque(maxlen=3)

    def __call__(self, linear_velocity, angular_velocity):
        if linear_velocity is not None:
            self.linear_accelerations.append(linear_velocity)
        if angular_velocity is not None:
            self.angular_accelerations.append(angular_velocity)

        if len(self.linear_accelerations) < 3 or len(self.angular_accelerations) < 3:
            return (
                np.array([0, 0, 0]),
                np.array([0, 0, 0]),
                np.array([0, 0, 0]),
                np.array([0, 0, 0]),
            )

        linear_acc = self.linear_accelerations[0] - self.linear_accelerations[1]
        last_linear_acc = self.linear_accelerations[1] - self.linear_accelerations[2]
        angular_acc = self.angular_accelerations[0] - self.angular_accelerations[1]
        last_angular_acc = self.angular_accelerations[1] - self.angular_accelerations[2]

        linear_jerk = linear_acc - last_linear_acc
        angular_jerk = angular_acc - last_angular_acc

        return (linear_acc, angular_acc, linear_jerk, angular_jerk)

    def teardown(self):
        pass


class ViaSensor(Sensor):
    def __init__(
        self, vehicle, mission_planner, lane_acquisition_range, speed_accuracy
    ):
        self._consumed_via_points = set()
        self._mission_planner: MissionPlanner = mission_planner
        self._acquisition_range = lane_acquisition_range
        self._vehicle = vehicle
        self._speed_accuracy = speed_accuracy

    @property
    def _vias(self) -> Iterable[Via]:
        return self._mission_planner.mission.data.via

    def __call__(self):
        near_points: List[ViaPoint] = list()
        hit_points: List[ViaPoint] = list()
        vehicle_position = self._vehicle.position[:2]

        @lru_cache()
        def closest_point_on_lane(position, lane_id):
            return self._mission_planner.closest_point_on_lane(position, lane_id)

        for via in self._vias:
            closest_position_on_lane = closest_point_on_lane(
                tuple(vehicle_position), via.lane_id
            )
            closest_position_on_lane = closest_position_on_lane[:2]

            dist_from_lane_sq = squared_dist(vehicle_position, closest_position_on_lane)
            if dist_from_lane_sq > self._acquisition_range ** 2:
                continue

            point = ViaPoint(
                position=tuple(via.position),
                lane_index=via.lane_index,
                edge_id=via.edge_id,
                required_speed=via.required_speed,
            )

            near_points.append(point)
            dist_from_point_sq = squared_dist(vehicle_position, via.position)
            if (
                dist_from_point_sq <= via.hit_distance ** 2
                and via not in self._consumed_via_points
                and np.isclose(
                    self._vehicle.speed, via.required_speed, atol=self._speed_accuracy
                )
            ):
                self._consumed_via_points.add(via)
                hit_points.append(point)

        return (
            sorted(
                near_points,
                key=lambda point: squared_dist(point.position, vehicle_position),
            ),
            hit_points,
        )

    def teardown(self):
        pass


def fix_observation_size(obs_config: Dict, obs: Dict) -> Dict:
    # Skip empty observations
    if obs == {}:
        return obs

    fixed_obs = {
        agent_id: fix_agent_observation_size(obs_config, agent_obs)
        for agent_id, agent_obs in obs.items()
    }
    return fixed_obs


def fix_agent_observation_size(obs_config: Dict, obs: NamedTuple) -> Observation:

    # Truncate/pad observation.events
    collisions = sequence.truncate_pad_li(
        obs.events.collisions,
        obs_config["observation"]["events"]["collisions"],
        Collision(),
    )
    events = obs.events._replace(collisions=collisions)

    # Truncate/pad observation.ego_vehicle_state
    yaw_rate = (sequence.truncate_pad_arr(obs.ego_vehicle_state.yaw_rate, 3, 0),)
    route_vias = sequence.truncate_pad_li(
        obs.ego_vehicle_state.mission.route_vias,
        obs_config["observation"]["ego_vehicle_state"]["mission"]["route_vias"],
        None,
    )
    via = (
        sequence.truncate_pad_li(
            obs.ego_vehicle_state.mission.via,
            obs_config["observation"]["ego_vehicle_state"]["mission"]["via"],
            Via(),
        ),
    )
    mission = obs.ego_vehicle_state.mission._replace(
        entry_tactic=None,  # EntryTactic removed from observation output
        task=None,  # Task removed from observation output
        via=via,
        route_vias=route_vias,
    )
    linear_velocity = (
        sequence.truncate_pad_arr(obs.ego_vehicle_state.linear_velocity, 3, 0),
    )
    angular_velocity = (
        sequence.truncate_pad_arr(obs.ego_vehicle_state.angular_velocity, 3, 0),
    )
    linear_acceleration = (
        sequence.truncate_pad_arr(obs.ego_vehicle_state.linear_acceleration, 3, 0),
    )
    angular_acceleration = (
        sequence.truncate_pad_arr(obs.ego_vehicle_state.angular_acceleration, 3, 0),
    )
    linear_jerk = (sequence.truncate_pad_arr(obs.ego_vehicle_state.linear_jerk, 3, 0),)
    angular_jerk = (
        sequence.truncate_pad_arr(obs.ego_vehicle_state.angular_jerk, 3, 0),
    )
    ego_vehicle_state = obs.ego_vehicle_state._replace(
        mission=mission,
        linear_velocity=linear_velocity,
        angular_velocity=angular_velocity,
        linear_acceleration=linear_acceleration,
        angular_acceleration=angular_acceleration,
        linear_jerk=linear_jerk,
        angular_jerk=angular_jerk,
    )

    # Truncate/pad observation.neighborhood_vehicle_states
    neighborhood_vehicle_states = obs.neighborhood_vehicle_states or []
    neighborhood_vehicle_states = (
        sequence.truncate_pad_li(
            neighborhood_vehicle_states,
            obs_config["observation"]["neighborhood_vehicle_states"],
            VehicleObservation(),
        ),
    )

    # Truncate/pad observation.lidar_point_cloud
    lidar_points = sequence.truncate_pad_li(
        obs.lidar_point_cloud[0],
        obs_config["observation"]["lidar_point_cloud"][0],
        np.array([0, 0, 0]),
    )
    lidar_hits = sequence.truncate_pad_li(
        obs.lidar_point_cloud[1],
        obs_config["observation"]["lidar_point_cloud"][1],
        np.array([0, 0, 0]),
    )
    lidar_ray = sequence.truncate_pad_li(
        obs.lidar_point_cloud[2],
        obs_config["observation"]["lidar_point_cloud"][2],
        (np.array([0, 0, 0]), np.array([0, 0, 0])),
    )
    lidar_point_cloud = (lidar_points, lidar_hits, lidar_ray)

    # Truncate/pad observation.road_waypoints
    if obs.road_waypoints:
        lanes = {
            k: sequence.truncate_pad_li(
                v,
                obs_config["observation"]["road_waypoints"]["lanes"],
                Waypoint(),
            )
            for k, v in obs.road_waypoints.lanes.items()
        }
        route_waypoints = sequence.truncate_pad_li(
            obs.road_waypoints.route_waypoints,
            obs_config["observation"]["road_waypoints"]["route_waypoints"],
            Waypoint(),
        )
        road_waypoints = RoadWaypoints(lanes=lanes, route_waypoints=route_waypoints)
    else:
        road_waypoints = obs.road_waypoints

    # Truncate/pad observation.via_data
    near_via_points = sequence.truncate_pad_li(
        obs.via_data.near_via_points,
        obs_config["observation"]["via_data"]["near_via_points"],
        ViaPoint(),
    )
    hit_via_points = sequence.truncate_pad_li(
        obs.via_data.hit_via_points,
        obs_config["observation"]["via_data"]["hit_via_points"],
        ViaPoint(),
    )
    via_data = Vias(near_via_points=near_via_points, hit_via_points=hit_via_points)

    # Fixed-size observation
    fixed_obs = Observation(
        events=events,
        ego_vehicle_state=ego_vehicle_state,
        neighborhood_vehicle_states=neighborhood_vehicle_states,
        waypoint_paths=sequence.truncate_pad_li_2d(
            obs.waypoint_paths,
            obs_config["observation"]["waypoint_paths"],
            ([], Waypoint()),
        ),
        distance_travelled=obs.distance_travelled,
        lidar_point_cloud=lidar_point_cloud,
        drivable_area_grid_map=obs.drivable_area_grid_map,
        occupancy_grid_map=obs.occupancy_grid_map,
        top_down_rgb=obs.top_down_rgb,
        road_waypoints=road_waypoints,
        via_data=via_data,
    )

    return fixed_obs
