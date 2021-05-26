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
import enum
from typing import Any, Callable, Dict

import gym

import ultra.adapters.default_action_continuous_adapter as default_action_continuous_adapter
import ultra.adapters.default_action_discrete_adapter as default_action_discrete_adapter
import ultra.adapters.default_observation_image_adapter as default_observation_image_adapter
import ultra.adapters.default_observation_vector_adapter as default_observation_vector_adapter
import ultra.adapters.default_reward_adapter as default_reward_adapter


class AdapterType(enum.Enum):
    # Action adapters.
    DefaultActionContinuous = enum.auto()
    DefaultActionDiscrete = enum.auto()

    # Observation adapters.
    DefaultObservationVector = enum.auto()
    DefaultObservationImage = enum.auto()

    # Reward adapters.
    DefaultReward = enum.auto()


_STRING_TO_TYPE = {
    "default_action_continuous": AdapterType.DefaultActionContinuous,
    "default_action_discrete": AdapterType.DefaultActionDiscrete,
    "default_observation_image": AdapterType.DefaultObservationImage,
    "default_observation_vector": AdapterType.DefaultObservationVector,
    "default_reward": AdapterType.DefaultReward,
}
_TYPE_TO_SPACE = {
    AdapterType.DefaultActionContinuous: default_action_continuous_adapter.gym_space,
    AdapterType.DefaultActionDiscrete: default_action_discrete_adapter.gym_space,
    AdapterType.DefaultObservationImage: default_observation_image_adapter.gym_space,
    AdapterType.DefaultObservationVector: default_observation_vector_adapter.gym_space,
}
_TYPE_TO_ADAPTER = {
    AdapterType.DefaultActionContinuous: default_action_continuous_adapter.adapt,
    AdapterType.DefaultActionDiscrete: default_action_discrete_adapter.adapt,
    AdapterType.DefaultObservationImage: default_observation_image_adapter.adapt,
    AdapterType.DefaultObservationVector: default_observation_vector_adapter.adapt,
    AdapterType.DefaultReward: default_reward_adapter.adapt,
}
_TYPE_TO_REQUIRED_INTERFACE = {
    AdapterType.DefaultActionContinuous: default_action_continuous_adapter.required_interface,
    AdapterType.DefaultActionDiscrete: default_action_discrete_adapter.required_interface,
    AdapterType.DefaultObservationImage: default_observation_image_adapter.required_interface,
    AdapterType.DefaultObservationVector: default_observation_vector_adapter.required_interface,
    AdapterType.DefaultReward: default_reward_adapter.required_interface,
}


def type_from_string(string_type: str) -> AdapterType:
    if string_type in _STRING_TO_TYPE:
        return _STRING_TO_TYPE[string_type]
    raise Exception(f"An adapter type is not set for string '{string_type}'.")


def space_from_type(adapter_type: AdapterType) -> gym.Space:
    if adapter_type in _TYPE_TO_SPACE:
        return _TYPE_TO_SPACE[adapter_type]
    raise Exception(f"A Gym Space is not set for adapter type {adapter_type}.")


def adapter_from_type(adapter_type: AdapterType) -> Callable:
    if adapter_type in _TYPE_TO_ADAPTER:
        return _TYPE_TO_ADAPTER[adapter_type]
    raise Exception(f"An adapter function is not set for adapter type {adapter_type}.")


def required_interface_from_types(
    action_type: AdapterType, observation_type: AdapterType, reward_type: AdapterType
) -> Dict[str, Any]:
    required_interface = {}

    if action_type not in _TYPE_TO_REQUIRED_INTERFACE:
        raise Exception(
            f"A required interface is not set for adapter type {action_type}."
        )
    if observation_type not in _TYPE_TO_REQUIRED_INTERFACE:
        raise Exception(
            f"A required interface is not set for adapter type {observation_type}."
        )
    if reward_type not in _TYPE_TO_REQUIRED_INTERFACE:
        raise Exception(
            f"A required interface is not set for adapter type {reward_type}."
        )

    action_interface = _TYPE_TO_REQUIRED_INTERFACE[action_type]
    observation_interface = _TYPE_TO_REQUIRED_INTERFACE[observation_type]
    reward_interface = _TYPE_TO_REQUIRED_INTERFACE[reward_type]

    # TODO: Make this nicer.

    for interface_name, interface in action_interface.items():
        if interface_name in required_interface:
            # TODO: Does this actually compare the interfaces correctly?
            assert required_interface[interface_name] == interface
        else:
            required_interface[interface_name] = interface
    for interface_name, interface in observation_interface.items():
        if interface_name in required_interface:
            # TODO: Does this actually compare the interfaces correctly?
            assert required_interface[interface_name] == interface
        else:
            required_interface[interface_name] = interface
    for interface_name, interface in reward_interface.items():
        if interface_name in required_interface:
            # TODO: Does this actually compare the interfaces correctly?
            assert required_interface[interface_name] == interface
        else:
            required_interface[interface_name] = interface

    return required_interface
