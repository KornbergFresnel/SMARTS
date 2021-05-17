from examples.single_agent import UTurnAgent
import logging
from pathlib import Path

from smarts.sstudio import gen_scenario
from smarts.sstudio import types as t

from sys import path

path.append(str(Path(__file__).parent.parent))
from copy_scenario import copy_to_dir

scenario_map_file = "scenarios/6lane_straightaway"

logger = logging.getLogger(str(Path(__file__)))

s_dir = str(Path(__file__).parent)

try:
    copy_to_dir(scenario_map_file, s_dir)
except Exception as e:
    logger.error(f"Scenario {scenario_map_file} failed to copy")
    raise e

ego_missions = [
    t.Mission(
        t.Route(begin=("-straightaway", 0, 30), end=("-straightaway", 0, "max")),
        task=t.UTurn(initial_speed=20),
    ),
]

start_offset_target = 60
start_offset_inner = 160
start_offset_mid = 10
interval = 10
traffic = t.Traffic(
    flows=[
        t.Flow(
            route=t.Route(
                begin=("straightaway", 2, o * interval + start_offset_inner),
                end=("straightaway", 2, "max"),
            ),
            rate=1,
            actors={
                t.TrafficActor(
                    "left_lane_car",
                    speed=t.Distribution(mean=0.9, sigma=0),
                    lane_changing_model=t.LaneChangingModel(
                        strategic=0, cooperative=0, keepRight=0
                    ),
                ): 1
            },
        )
        for o in range(4)
    ]
    + [
        t.Flow(
            route=t.Route(
                begin=("straightaway", 1, o * interval + start_offset_mid),
                end=("straightaway", 1, "max"),
            ),
            rate=1,
            actors={
                t.TrafficActor(
                    "mid_lane_car",
                    speed=t.Distribution(mean=0.9, sigma=0),
                    lane_changing_model=t.LaneChangingModel(
                        strategic=0, cooperative=0, keepRight=0
                    ),
                ): 1
            },
        )
        for o in range(4)
    ]
    + [
        t.Flow(
            route=t.Route(
                begin=("straightaway", 2, start_offset_target),
                end=("straightaway", 2, "max"),
            ),
            rate=1,
            actors={
                t.TrafficActor(
                    "target",
                    speed=t.Distribution(mean=0.9, sigma=0),
                    lane_changing_model=t.LaneChangingModel(
                        strategic=0, cooperative=0, keepRight=0
                    ),
                ): 1
            },
        )
    ]
)

scenario = t.Scenario(
    traffic={"all": traffic},
    ego_missions=ego_missions,
)

gen_scenario(scenario, output_dir=s_dir)
