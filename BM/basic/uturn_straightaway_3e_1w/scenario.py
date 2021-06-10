from examples.single_agent import UTurnAgent
import logging
from pathlib import Path

from smarts.sstudio import gen_scenario
from smarts.sstudio import types as t

from sys import path

file_path = Path(__file__)
path.append(str(file_path.parent.parent))
from copy_scenario import copy_to_dir

scenario_map_file = "maps/straight/4lane_straight_3e_1w"

logger = logging.getLogger(str(file_path))

scenario_name= str(file_path.parent.name)
s_dir = str(file_path.parent)
output_dir = f"{str(file_path.parent.parent)}/scenarios/uturn/{scenario_name}"

ego_missions = [
    t.Mission(
        t.Route(begin=("-straightaway", 0, 30), end=("-straightaway", 0, "max")),
        task=t.UTurn(initial_speed=20),
    ),
]

traffic = t.Traffic(
    flows=[
        t.Flow(
            route=t.Route(
                begin=("straightaway", 1, 30),
                end=("straightaway", 1, "max"),
            ),
            rate=1,
            actors={t.TrafficActor("ego"): 1},
        )
    ]
)

scenario = t.Scenario(
    traffic={"all": traffic},
    ego_missions=ego_missions,
)

try:
    copy_to_dir(scenario_map_file, output_dir)
except Exception as e:
    logger.error(f"Scenario {scenario_map_file} failed to copy")
    raise e
gen_scenario(scenario, output_dir=output_dir, overwrite=True)
