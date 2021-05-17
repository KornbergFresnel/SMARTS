import logging
from pathlib import Path

from smarts.sstudio import gen_scenario
from smarts.sstudio import types as t

from sys import path

path.append(str(Path(__file__).parent.parent))
from copy_scenario import copy_to_dir

scenario_map_file = "scenarios/4lane_cross_turn_in"

logger = logging.getLogger(str(Path(__file__)))
s_dir = str(Path(__file__).parent)

try:
    copy_to_dir(scenario_map_file, s_dir)
except Exception as e:
    logger.error(f"Scenario {scenario_map_file} failed to copy")
    raise e

ego_missions = [
    t.Mission(
        t.Route(begin=("east_ew", 0, 20), end=("south_ns", 1, "max")),
        via=[
            t.Via("east_ew", 0, 50, 30),
            # t.Via(t.JunctionEdgeIDResolver("east_ew", 0, "south_ns", 0), 1, 5, 15),
            t.Via(
                t.JunctionEdgeIDResolver("east_ew", 1, "south_ns", 1),
                lane_index=0,
                lane_offset=1,
                required_speed=10,
            ),
            t.Via("south_ns", 1, 20, 7.5),
        ],
    )
]

traffic = t.Traffic(
    flows=[
        t.Flow(
            route=t.Route(
                begin=("east_ew", 1, 20),
                end=("south_ns", 1, "max"),
            ),
            rate=1,
            actors={
                t.TrafficActor("target", speed=t.Distribution(mean=0.9, sigma=0)): 1
            },
        )
    ]
)

scenario = t.Scenario(
    traffic={"all": traffic},
    ego_missions=ego_missions,
)

gen_scenario(scenario, output_dir=s_dir)
