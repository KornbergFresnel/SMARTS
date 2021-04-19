# MIT License
#
# Copyright (C) 2021. Huawei Technologies Co., Ltd. All rights reserved.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
import os
import pickle
from typing import Sequence, Tuple

# Set environment to better support Ray
os.environ["MKL_NUM_THREADS"] = "1"
import argparse
import glob
import time
from pydoc import locate

import gym
import numpy as np
import ray
import torch

from smarts.zoo.registry import make
from ultra.utils.common import str_to_bool
from ultra.utils.episode import LogInfo, episodes
from ultra.utils.ray import default_ray_kwargs
from ultra.utils.curriculum.curriculum_info import CurriculumInfo
from ultra.utils.curriculum.scenario_data_handler import ScenarioDataHandler
from ultra.utils.curriculum.dynamic_scenarios import DynamicScenarios

num_gpus = 1 if torch.cuda.is_available() else 0


def evaluation_check(
    agents,
    episode,
    agent_ids,
    policy_classes,
    eval_rate,
    eval_episodes,
    max_episode_steps,
    scenario_info,
    timestep_sec,
    headless,
    log_dir,
    evaluation_task_ids,
    curriculum_metadata=None,
    curriculum_mode=False,
    static_coordinator=None,
):
    # Evaluate agents that have reached the eval_rate.
    if curriculum_mode is True:
        if (
            CurriculumInfo.static_curriculum_toggle is True
            and static_coordinator.eval_per_grade is True
        ):
            agent_ids_to_evaluate = [
                agent_id
                for agent_id in agent_ids
                if static_coordinator.get_eval_check_condition() == True
            ]
        else:
            agent_ids_to_evaluate = [
                agent_id
                for agent_id in agent_ids
                if (episode.index + 1) % eval_rate == 0
                and episode.last_eval_iterations[agent_id] != episode.index
            ]

    else:
        agent_ids_to_evaluate = [
            agent_id
            for agent_id in agent_ids
            if (episode.index + 1) % eval_rate == 0
            and episode.last_eval_iterations[agent_id] != episode.index
        ]

    # Skip evaluation if there are no agents needing an evaluation.
    if len(agent_ids_to_evaluate) < 1:
        return

    if eval_episodes < 1:
        return

    if curriculum_mode is True:
        if CurriculumInfo.static_curriculum_toggle is True:
            static_coordinator.next_eval_grade()

    for agent_id in agent_ids_to_evaluate:
        # Get the checkpoint directory for the current agent and save its model.
        checkpoint_directory = episode.checkpoint_dir(
            agent_id, episode.get_itr(agent_id)
        )
        agents[agent_id].save(checkpoint_directory)

        evaluation_task_id = evaluate.remote(
            seed=episode.eval_count,
            experiment_dir=episode.experiment_dir,
            agent_ids=[agent_id],
            policy_classes={agent_id: policy_classes[agent_id]},
            checkpoint_dirs={agent_id: checkpoint_directory},
            scenario_info=scenario_info,
            num_episodes=eval_episodes,
            max_episode_steps=max_episode_steps,
            headless=headless,
            timestep_sec=timestep_sec,
            log_dir=log_dir,
            curriculum_metadata=curriculum_metadata,
            curriculum_mode=curriculum_mode,
            static_coordinator=static_coordinator,
            eval_mode=True,
        )
        evaluation_task_ids[evaluation_task_id] = (
            episode.get_itr(agent_id),
            episode,
            "eval",
        )

    """ For ultra-gb, evaluating on train episode is not necessary"""
    # for agent_id in agent_ids_to_evaluate:
    #     # Get the checkpoint directory for the current agent and save its model.
    #     checkpoint_directory = episode.checkpoint_dir(
    #         agent_id, episode.get_itr(agent_id)
    #     )
    #     agents[agent_id].save(checkpoint_directory)

    #     evaluation_train_task_id = evaluate.remote(
    #         seed=episode.eval_count,
    #         experiment_dir=episode.experiment_dir,
    #         agent_ids=[agent_id],
    #         policy_classes={agent_id: policy_classes[agent_id]},
    #         checkpoint_dirs={agent_id: checkpoint_directory},
    #         scenario_info=scenario_info,
    #         num_episodes=eval_episodes,
    #         max_episode_steps=max_episode_steps,
    #         headless=headless,
    #         timestep_sec=timestep_sec,
    #         log_dir=log_dir,
    #         curriculum_metadata=curriculum_metadata
    #         curriculum_mode=curriculum_mode,
    #         static_coordinator=static_coordinator,
    #         eval_mode=False,
    #     )
    #     evaluation_task_ids[evaluation_train_task_id] = (
    #         episode.get_itr(agent_id),
    #         episode,
    #         "eval_train",
    #     )

    #     episode.eval_count += 1
    #     episode.last_eval_iterations[agent_id] = episode.get_itr(agent_id)


def collect_evaluations(evaluation_task_ids: dict):
    ready_evaluation_task_ids, _ = ray.wait(list(evaluation_task_ids.keys()), timeout=0)

    # For each ready evaluation result, put it in the episode's
    # evaluation info so that it can be recorded to tensorboard.
    for ready_evaluation_task_id in ready_evaluation_task_ids:
        agent_iteration, episode, mode = evaluation_task_ids.pop(
            ready_evaluation_task_id
        )

        if mode == "eval":
            episode.eval_mode()
        elif mode == "eval_train":
            episode.eval_train_mode()

        episode.info[episode.active_tag] = ray.get(ready_evaluation_task_id)
        episode.record_tensorboard(recording_step=agent_iteration)
        episode.train_mode()

    return len(evaluation_task_ids) > 0


# Number of GPUs should be split between remote functions.
@ray.remote(num_gpus=num_gpus / 2, max_calls=1)
def evaluate(
    experiment_dir,
    seed,
    agent_ids,
    policy_classes,
    checkpoint_dirs,
    scenario_info,
    num_episodes,
    max_episode_steps,
    headless,
    timestep_sec,
    log_dir,
    curriculum_metadata=None,
    curriculum_mode=False,
    static_coordinator=None,
    explore=False,
    eval_mode=True,
):
    torch.set_num_threads(1)

    # Create the agent specifications matched with their associated ID.
    agent_specs = {
        agent_id: make(
            locator=policy_classes[agent_id],
            checkpoint_dir=checkpoint_dirs[agent_id],
            experiment_dir=experiment_dir,
            max_episode_steps=max_episode_steps,
            agent_id=agent_id,
        )
        for agent_id in agent_ids
    }

    if curriculum_mode is True:
        CurriculumInfo.initialize(curriculum_metadata["curriculum_dir"])
        if CurriculumInfo.dynamic_curriculum_toggle is True:
            dynamic_coordinator = DynamicScenarios(
                curriculum_metadata["curriculum_scenarios_root_dir"],
                curriculum_metadata["curriculum_scenarios_save_dir"],
                rate=num_episodes,
            )
            dynamic_coordinator.reset_test_scenarios(CurriculumInfo.tasks_levels_used)
            scenario_info = CurriculumInfo.tasks_levels_used

    # Create the environment with the specified agents.
    env = gym.make(
        "ultra.env:ultra-v0",
        agent_specs=agent_specs,
        scenario_info=scenario_info,
        headless=headless,
        timestep_sec=timestep_sec,
        seed=seed,
        curriculum_mode=curriculum_mode,
        eval_mode=eval_mode,
    )

    # Build each agent from its specification.
    agents = {
        agent_id: agent_spec.build_agent()
        for agent_id, agent_spec in agent_specs.items()
    }

    # A dictionary to hold the evaluation data for each agent.
    summary_log = {agent_id: LogInfo() for agent_id in agent_ids}

    # Define an 'etag' for this experiment's data directory based off policy_classes.
    # E.g. From a ["ultra.baselines.dqn:dqn-v0", "ultra.baselines.ppo:ppo-v0"]
    # policy_classes list, transform it to an etag of "dqn-v0:ppo-v0".
    etag = ":".join([policy_class.split(":")[-1] for policy_class in policy_classes])

    initial_grade_switch = False

    scenario_data_handler_eval = ScenarioDataHandler("Evaluation")

    for episode in episodes(num_episodes, etag=etag, log_dir=log_dir):
        # Reset the environment and retrieve the initial observations.
        if curriculum_mode is True:
            if CurriculumInfo.static_curriculum_toggle is True:
                if initial_grade_switch == False:
                    observations, scenario = env.reset(
                        True, static_coordinator.get_eval_grade()
                    )
                    initial_grade_switch = True
                else:
                    observations, scenario = env.reset()
        else:
            observations, scenario = env.reset()

        dones = {"__all__": False}
        infos = None
        episode.reset(mode="Evaluation")

        while not dones["__all__"]:
            # Get and perform the available agents' actions.
            actions = {
                agent_id: agents[agent_id].act(observation, explore=False)
                for agent_id, observation in observations.items()
            }
            observations, rewards, dones, infos = env.step(actions)

            # Record the data from this episode.
            episode.record_step(
                agent_ids_to_record=infos.keys(), infos=infos, rewards=rewards
            )

        density_counter = scenario_data_handler_eval.record_density_data(
            scenario["scenario_density"]
        )
        scenario["density_counter"] = density_counter
        episode.record_scenario_info(agents, scenario)
        episode.record_episode()
        if curriculum_mode is True and eval_mode is True:
            episode.record_tensorboard()

        for agent_id, agent_data in episode.info[episode.active_tag].items():
            for key, value in agent_data.data.items():
                if not isinstance(value, (list, tuple, dict, np.ndarray)):
                    summary_log[agent_id].data[key] += value

    # Normalize by the number of evaluation episodes.
    for agent_id, agent_data in summary_log.items():
        for key, value in agent_data.data.items():
            if not isinstance(value, (list, tuple, dict, np.ndarray)):
                summary_log[agent_id].data[key] /= num_episodes

    env.close()

    if curriculum_mode is True:
        if CurriculumInfo.static_curriculum_toggle is True:
            scenario_data_handler_eval.display_grade_scenario_distribution(
                num_episodes, static_coordinator.get_eval_grade()
            )
            scenario_data_handler_eval.save_grade_density(num_episodes)
        else:
            scenario_data_handler_eval.display_grade_scenario_distribution(num_episodes)
            scenario_data_handler_eval.save_grade_density(num_episodes)

    try:
        if eval_mode:
            filepath = os.path.join(
                checkpoint_dirs["000"], "Evaluate-test-scenarios.csv"
            )
        else:
            filepath = os.path.join(
                checkpoint_dirs["000"], "Evaluate-train-scenarios.csv"
            )
        scenario_data_handler_eval.plot_densities_data(filepath)
    except KeyError as e:
        pass

    return summary_log


def evaluate_saved_models(
    experiment_dir: str,
    log_dir: str,
    headless: bool,
    max_episode_steps: int,
    model_paths: Sequence[str],
    num_episodes: int,
    scenario_info: Tuple[str, str],
    timestep: float,
):
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    if not all([os.path.exists(model_path) for model_path in model_paths]):
        raise "At least one path to a model is invalid"
    if not all([os.listdir(model_path) for model_path in model_paths]):
        raise "There are no models to evaluate in at least one model path"

    # Get agent IDs from the models to be evaluated.
    agent_ids_from_models = [
        os.path.basename(os.path.normpath(model_path)) for model_path in model_paths
    ]

    # Load relevant agent metadata.
    with open(
        os.path.join(experiment_dir, "agent_metadata.pkl"), "rb"
    ) as metadata_file:
        agent_metadata = pickle.load(metadata_file)

    # Extract the agent IDs and policy classes from the metadata and given models.
    agent_ids = [
        agent_id
        for agent_id in agent_metadata["agent_ids"]
        if agent_id in agent_ids_from_models
    ]
    policy_classes = {
        agent_id: agent_metadata["agent_classes"][agent_id] for agent_id in agent_ids
    }

    # From a base model directory such as logs/<experiment_name>/models/*, assign each agent ID with its
    # checkpoint directories in sorted order based on the checkpoint iteration. The agent IDs are
    # obtained from the direct child folders of the model directory given. As an example result:
    # {
    #     '000': ['logs/<experiment_name>/models/000/1042', 'logs/<experiment_name>/models/000/2062'],
    #     '001': ['logs/<experiment_name>/models/001/999', 'logs/<experiment_name>/models/001/1999'],
    #     '003': ['logs/<experiment_name>/models/003/1009', 'logs/<experiment_name>/models/003/2120'],
    #     '002': ['logs/<experiment_name>/models/002/1053', 'logs/<experiment_name>/models/002/2041'],
    # }
    agent_checkpoint_directories = {
        agent_id: sorted(
            glob.glob(os.path.join(experiment_dir, "models", agent_id, "*")),
            key=lambda x: int(x.split("/")[-1]),
        )
        for agent_id in agent_ids
    }

    # Assert each agent ID has the same number of checkpoints saved.
    directories_iterator = iter(agent_checkpoint_directories.values())
    number_of_checkpoints = len(next(directories_iterator))
    assert all(
        len(checkpoint_directory) == number_of_checkpoints
        for checkpoint_directory in directories_iterator
    ), "Not all agents have the same number of checkpoints saved"

    # Define an 'etag' for this experiment's data directory based off policy_classes.
    # E.g. From a {"000": "ultra.baselines.dqn:dqn-v0", "001": "ultra.baselines.ppo:ppo-v0"]
    # policy_classes dict, transform it to an etag of "dqn-v0:ppo-v0-evaluation".
    etag = (
        ":".join([policy_classes[agent_id].split(":")[-1] for agent_id in agent_ids])
        + "-evaluation"
    )

    ray.init()
    try:
        for episode in episodes(
            number_of_checkpoints,
            etag=etag,
            log_dir=log_dir,
        ):
            # Obtain a checkpoint directory for each agent.
            current_checkpoint_directories = {
                agent_id: agent_directories[episode.index]
                for agent_id, agent_directories in agent_checkpoint_directories.items()
            }
            episode.eval_mode()
            episode.info[episode.active_tag] = ray.get(
                [
                    evaluate.remote(
                        experiment_dir=experiment_dir,
                        agent_ids=agent_ids,
                        policy_classes=policy_classes,
                        seed=episode.eval_count,
                        checkpoint_dirs=current_checkpoint_directories,
                        scenario_info=scenario_info,
                        num_episodes=num_episodes,
                        max_episode_steps=max_episode_steps,
                        timestep_sec=timestep,
                        headless=headless,
                        log_dir=log_dir,
                    )
                ]
            )[0]
            episode.record_tensorboard()
            episode.eval_count += 1
    finally:
        time.sleep(1)
        ray.shutdown()


if __name__ == "__main__":
    parser = argparse.ArgumentParser("intersection-evaluation")
    parser.add_argument(
        "--task", help="Tasks available : [0, 1, 2]", type=str, default="1"
    )
    parser.add_argument(
        "--level",
        help="Levels available : [easy, medium, hard, no-traffic]",
        type=str,
        default="easy",
    )
    parser.add_argument(
        "--models",
        nargs="+",
        help="The models in the models/ directory of the experiment to evaluate",
    )
    parser.add_argument(
        "--episodes", help="Number of training episodes", type=int, default=200
    )
    parser.add_argument(
        "--max-episode-steps",
        help="Maximum number of steps per episode",
        type=int,
        default=10000,
    )
    parser.add_argument(
        "--timestep", help="Environment timestep (sec)", type=float, default=0.1
    )
    parser.add_argument(
        "--headless",
        help="Run without envision",
        action="store_true",
    )
    parser.add_argument(
        "--experiment-dir",
        help="Path to the experiment directory",
        type=str,
    )
    parser.add_argument(
        "--log-dir",
        help="Log directory location",
        default="logs",
        type=str,
    )
    args = parser.parse_args()

    evaluate_saved_models(
        experiment_dir=args.experiment_dir,
        log_dir=args.log_dir,
        headless=args.headless,
        max_episode_steps=int(args.max_episode_steps),
        model_paths=args.models,
        num_episodes=int(args.episodes),
        scenario_info=(args.task, args.level),
        timestep=float(args.timestep),
    )
