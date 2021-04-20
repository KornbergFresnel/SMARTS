# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: action.proto

from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database

# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


DESCRIPTOR = _descriptor.FileDescriptor(
    name="action.proto",
    package="action",
    syntax="proto3",
    serialized_options=None,
    create_key=_descriptor._internal_create_key,
    serialized_pb=b'\n\x0c\x61\x63tion.proto\x12\x06\x61\x63tion"{\n\x0b\x41\x63tionsBoid\x12-\n\x05\x62oids\x18\x01 \x03(\x0b\x32\x1e.action.ActionsBoid.BoidsEntry\x1a=\n\nBoidsEntry\x12\x0b\n\x03key\x18\x01 \x01(\t\x12\x1e\n\x05value\x18\x02 \x01(\x0b\x32\x0f.action.Actions:\x02\x38\x01"{\n\x07\x41\x63tions\x12/\n\x08vehicles\x18\x01 \x03(\x0b\x32\x1d.action.Actions.VehiclesEntry\x1a?\n\rVehiclesEntry\x12\x0b\n\x03key\x18\x01 \x01(\t\x12\x1d\n\x05value\x18\x02 \x01(\x0b\x32\x0e.action.Action:\x02\x38\x01"\xfd\x02\n\x06\x41\x63tion\x12(\n\ncontinuous\x18\x01 \x01(\x0b\x32\x12.action.ContinuousH\x00\x12\x1c\n\x04lane\x18\x02 \x01(\x0b\x32\x0c.action.LaneH\x00\x12\x33\n\x10\x61\x63tuator_dynamic\x18\x03 \x01(\x0b\x32\x17.action.ActuatorDynamicH\x00\x12\x45\n\x1alane_with_continuous_speed\x18\x04 \x01(\x0b\x32\x1f.action.LaneWithContinuousSpeedH\x00\x12)\n\x0btarget_pose\x18\x05 \x01(\x0b\x32\x12.action.TargetPoseH\x00\x12(\n\ntrajectory\x18\x06 \x01(\x0b\x32\x12.action.TrajectoryH\x00\x12\x34\n\x11multi_target_pose\x18\x07 \x01(\x0b\x32\x17.action.MultiTargetPoseH\x00\x12\x1a\n\x03mpc\x18\x08 \x01(\x0b\x32\x0b.action.MPCH\x00\x42\x08\n\x06\x61\x63tion"\x1c\n\nContinuous\x12\x0e\n\x06\x61\x63tion\x18\x01 \x03(\x02"\x16\n\x04Lane\x12\x0e\n\x06\x61\x63tion\x18\x01 \x01(\t"!\n\x0f\x41\x63tuatorDynamic\x12\x0e\n\x06\x61\x63tion\x18\x01 \x03(\x02")\n\x17LaneWithContinuousSpeed\x12\x0e\n\x06\x61\x63tion\x18\x01 \x03(\x02"\x1c\n\nTargetPose\x12\x0e\n\x06\x61\x63tion\x18\x01 \x03(\x02"T\n\nTrajectory\x12\x10\n\x08\x61\x63tion_1\x18\x01 \x03(\x02\x12\x10\n\x08\x61\x63tion_2\x18\x02 \x03(\x02\x12\x10\n\x08\x61\x63tion_3\x18\x03 \x03(\x02\x12\x10\n\x08\x61\x63tion_4\x18\x04 \x03(\x02"\x11\n\x0fMultiTargetPose"M\n\x03MPC\x12\x10\n\x08\x61\x63tion_1\x18\x01 \x03(\x02\x12\x10\n\x08\x61\x63tion_2\x18\x02 \x03(\x02\x12\x10\n\x08\x61\x63tion_3\x18\x03 \x03(\x02\x12\x10\n\x08\x61\x63tion_4\x18\x04 \x03(\x02\x62\x06proto3',
)


_ACTIONSBOID_BOIDSENTRY = _descriptor.Descriptor(
    name="BoidsEntry",
    full_name="action.ActionsBoid.BoidsEntry",
    filename=None,
    file=DESCRIPTOR,
    containing_type=None,
    create_key=_descriptor._internal_create_key,
    fields=[
        _descriptor.FieldDescriptor(
            name="key",
            full_name="action.ActionsBoid.BoidsEntry.key",
            index=0,
            number=1,
            type=9,
            cpp_type=9,
            label=1,
            has_default_value=False,
            default_value=b"".decode("utf-8"),
            message_type=None,
            enum_type=None,
            containing_type=None,
            is_extension=False,
            extension_scope=None,
            serialized_options=None,
            file=DESCRIPTOR,
            create_key=_descriptor._internal_create_key,
        ),
        _descriptor.FieldDescriptor(
            name="value",
            full_name="action.ActionsBoid.BoidsEntry.value",
            index=1,
            number=2,
            type=11,
            cpp_type=10,
            label=1,
            has_default_value=False,
            default_value=None,
            message_type=None,
            enum_type=None,
            containing_type=None,
            is_extension=False,
            extension_scope=None,
            serialized_options=None,
            file=DESCRIPTOR,
            create_key=_descriptor._internal_create_key,
        ),
    ],
    extensions=[],
    nested_types=[],
    enum_types=[],
    serialized_options=b"8\001",
    is_extendable=False,
    syntax="proto3",
    extension_ranges=[],
    oneofs=[],
    serialized_start=86,
    serialized_end=147,
)

_ACTIONSBOID = _descriptor.Descriptor(
    name="ActionsBoid",
    full_name="action.ActionsBoid",
    filename=None,
    file=DESCRIPTOR,
    containing_type=None,
    create_key=_descriptor._internal_create_key,
    fields=[
        _descriptor.FieldDescriptor(
            name="boids",
            full_name="action.ActionsBoid.boids",
            index=0,
            number=1,
            type=11,
            cpp_type=10,
            label=3,
            has_default_value=False,
            default_value=[],
            message_type=None,
            enum_type=None,
            containing_type=None,
            is_extension=False,
            extension_scope=None,
            serialized_options=None,
            file=DESCRIPTOR,
            create_key=_descriptor._internal_create_key,
        ),
    ],
    extensions=[],
    nested_types=[
        _ACTIONSBOID_BOIDSENTRY,
    ],
    enum_types=[],
    serialized_options=None,
    is_extendable=False,
    syntax="proto3",
    extension_ranges=[],
    oneofs=[],
    serialized_start=24,
    serialized_end=147,
)


_ACTIONS_VEHICLESENTRY = _descriptor.Descriptor(
    name="VehiclesEntry",
    full_name="action.Actions.VehiclesEntry",
    filename=None,
    file=DESCRIPTOR,
    containing_type=None,
    create_key=_descriptor._internal_create_key,
    fields=[
        _descriptor.FieldDescriptor(
            name="key",
            full_name="action.Actions.VehiclesEntry.key",
            index=0,
            number=1,
            type=9,
            cpp_type=9,
            label=1,
            has_default_value=False,
            default_value=b"".decode("utf-8"),
            message_type=None,
            enum_type=None,
            containing_type=None,
            is_extension=False,
            extension_scope=None,
            serialized_options=None,
            file=DESCRIPTOR,
            create_key=_descriptor._internal_create_key,
        ),
        _descriptor.FieldDescriptor(
            name="value",
            full_name="action.Actions.VehiclesEntry.value",
            index=1,
            number=2,
            type=11,
            cpp_type=10,
            label=1,
            has_default_value=False,
            default_value=None,
            message_type=None,
            enum_type=None,
            containing_type=None,
            is_extension=False,
            extension_scope=None,
            serialized_options=None,
            file=DESCRIPTOR,
            create_key=_descriptor._internal_create_key,
        ),
    ],
    extensions=[],
    nested_types=[],
    enum_types=[],
    serialized_options=b"8\001",
    is_extendable=False,
    syntax="proto3",
    extension_ranges=[],
    oneofs=[],
    serialized_start=209,
    serialized_end=272,
)

_ACTIONS = _descriptor.Descriptor(
    name="Actions",
    full_name="action.Actions",
    filename=None,
    file=DESCRIPTOR,
    containing_type=None,
    create_key=_descriptor._internal_create_key,
    fields=[
        _descriptor.FieldDescriptor(
            name="vehicles",
            full_name="action.Actions.vehicles",
            index=0,
            number=1,
            type=11,
            cpp_type=10,
            label=3,
            has_default_value=False,
            default_value=[],
            message_type=None,
            enum_type=None,
            containing_type=None,
            is_extension=False,
            extension_scope=None,
            serialized_options=None,
            file=DESCRIPTOR,
            create_key=_descriptor._internal_create_key,
        ),
    ],
    extensions=[],
    nested_types=[
        _ACTIONS_VEHICLESENTRY,
    ],
    enum_types=[],
    serialized_options=None,
    is_extendable=False,
    syntax="proto3",
    extension_ranges=[],
    oneofs=[],
    serialized_start=149,
    serialized_end=272,
)


_ACTION = _descriptor.Descriptor(
    name="Action",
    full_name="action.Action",
    filename=None,
    file=DESCRIPTOR,
    containing_type=None,
    create_key=_descriptor._internal_create_key,
    fields=[
        _descriptor.FieldDescriptor(
            name="continuous",
            full_name="action.Action.continuous",
            index=0,
            number=1,
            type=11,
            cpp_type=10,
            label=1,
            has_default_value=False,
            default_value=None,
            message_type=None,
            enum_type=None,
            containing_type=None,
            is_extension=False,
            extension_scope=None,
            serialized_options=None,
            file=DESCRIPTOR,
            create_key=_descriptor._internal_create_key,
        ),
        _descriptor.FieldDescriptor(
            name="lane",
            full_name="action.Action.lane",
            index=1,
            number=2,
            type=11,
            cpp_type=10,
            label=1,
            has_default_value=False,
            default_value=None,
            message_type=None,
            enum_type=None,
            containing_type=None,
            is_extension=False,
            extension_scope=None,
            serialized_options=None,
            file=DESCRIPTOR,
            create_key=_descriptor._internal_create_key,
        ),
        _descriptor.FieldDescriptor(
            name="actuator_dynamic",
            full_name="action.Action.actuator_dynamic",
            index=2,
            number=3,
            type=11,
            cpp_type=10,
            label=1,
            has_default_value=False,
            default_value=None,
            message_type=None,
            enum_type=None,
            containing_type=None,
            is_extension=False,
            extension_scope=None,
            serialized_options=None,
            file=DESCRIPTOR,
            create_key=_descriptor._internal_create_key,
        ),
        _descriptor.FieldDescriptor(
            name="lane_with_continuous_speed",
            full_name="action.Action.lane_with_continuous_speed",
            index=3,
            number=4,
            type=11,
            cpp_type=10,
            label=1,
            has_default_value=False,
            default_value=None,
            message_type=None,
            enum_type=None,
            containing_type=None,
            is_extension=False,
            extension_scope=None,
            serialized_options=None,
            file=DESCRIPTOR,
            create_key=_descriptor._internal_create_key,
        ),
        _descriptor.FieldDescriptor(
            name="target_pose",
            full_name="action.Action.target_pose",
            index=4,
            number=5,
            type=11,
            cpp_type=10,
            label=1,
            has_default_value=False,
            default_value=None,
            message_type=None,
            enum_type=None,
            containing_type=None,
            is_extension=False,
            extension_scope=None,
            serialized_options=None,
            file=DESCRIPTOR,
            create_key=_descriptor._internal_create_key,
        ),
        _descriptor.FieldDescriptor(
            name="trajectory",
            full_name="action.Action.trajectory",
            index=5,
            number=6,
            type=11,
            cpp_type=10,
            label=1,
            has_default_value=False,
            default_value=None,
            message_type=None,
            enum_type=None,
            containing_type=None,
            is_extension=False,
            extension_scope=None,
            serialized_options=None,
            file=DESCRIPTOR,
            create_key=_descriptor._internal_create_key,
        ),
        _descriptor.FieldDescriptor(
            name="multi_target_pose",
            full_name="action.Action.multi_target_pose",
            index=6,
            number=7,
            type=11,
            cpp_type=10,
            label=1,
            has_default_value=False,
            default_value=None,
            message_type=None,
            enum_type=None,
            containing_type=None,
            is_extension=False,
            extension_scope=None,
            serialized_options=None,
            file=DESCRIPTOR,
            create_key=_descriptor._internal_create_key,
        ),
        _descriptor.FieldDescriptor(
            name="mpc",
            full_name="action.Action.mpc",
            index=7,
            number=8,
            type=11,
            cpp_type=10,
            label=1,
            has_default_value=False,
            default_value=None,
            message_type=None,
            enum_type=None,
            containing_type=None,
            is_extension=False,
            extension_scope=None,
            serialized_options=None,
            file=DESCRIPTOR,
            create_key=_descriptor._internal_create_key,
        ),
    ],
    extensions=[],
    nested_types=[],
    enum_types=[],
    serialized_options=None,
    is_extendable=False,
    syntax="proto3",
    extension_ranges=[],
    oneofs=[
        _descriptor.OneofDescriptor(
            name="action",
            full_name="action.Action.action",
            index=0,
            containing_type=None,
            create_key=_descriptor._internal_create_key,
            fields=[],
        ),
    ],
    serialized_start=275,
    serialized_end=656,
)


_CONTINUOUS = _descriptor.Descriptor(
    name="Continuous",
    full_name="action.Continuous",
    filename=None,
    file=DESCRIPTOR,
    containing_type=None,
    create_key=_descriptor._internal_create_key,
    fields=[
        _descriptor.FieldDescriptor(
            name="action",
            full_name="action.Continuous.action",
            index=0,
            number=1,
            type=2,
            cpp_type=6,
            label=3,
            has_default_value=False,
            default_value=[],
            message_type=None,
            enum_type=None,
            containing_type=None,
            is_extension=False,
            extension_scope=None,
            serialized_options=None,
            file=DESCRIPTOR,
            create_key=_descriptor._internal_create_key,
        ),
    ],
    extensions=[],
    nested_types=[],
    enum_types=[],
    serialized_options=None,
    is_extendable=False,
    syntax="proto3",
    extension_ranges=[],
    oneofs=[],
    serialized_start=658,
    serialized_end=686,
)


_LANE = _descriptor.Descriptor(
    name="Lane",
    full_name="action.Lane",
    filename=None,
    file=DESCRIPTOR,
    containing_type=None,
    create_key=_descriptor._internal_create_key,
    fields=[
        _descriptor.FieldDescriptor(
            name="action",
            full_name="action.Lane.action",
            index=0,
            number=1,
            type=9,
            cpp_type=9,
            label=1,
            has_default_value=False,
            default_value=b"".decode("utf-8"),
            message_type=None,
            enum_type=None,
            containing_type=None,
            is_extension=False,
            extension_scope=None,
            serialized_options=None,
            file=DESCRIPTOR,
            create_key=_descriptor._internal_create_key,
        ),
    ],
    extensions=[],
    nested_types=[],
    enum_types=[],
    serialized_options=None,
    is_extendable=False,
    syntax="proto3",
    extension_ranges=[],
    oneofs=[],
    serialized_start=688,
    serialized_end=710,
)


_ACTUATORDYNAMIC = _descriptor.Descriptor(
    name="ActuatorDynamic",
    full_name="action.ActuatorDynamic",
    filename=None,
    file=DESCRIPTOR,
    containing_type=None,
    create_key=_descriptor._internal_create_key,
    fields=[
        _descriptor.FieldDescriptor(
            name="action",
            full_name="action.ActuatorDynamic.action",
            index=0,
            number=1,
            type=2,
            cpp_type=6,
            label=3,
            has_default_value=False,
            default_value=[],
            message_type=None,
            enum_type=None,
            containing_type=None,
            is_extension=False,
            extension_scope=None,
            serialized_options=None,
            file=DESCRIPTOR,
            create_key=_descriptor._internal_create_key,
        ),
    ],
    extensions=[],
    nested_types=[],
    enum_types=[],
    serialized_options=None,
    is_extendable=False,
    syntax="proto3",
    extension_ranges=[],
    oneofs=[],
    serialized_start=712,
    serialized_end=745,
)


_LANEWITHCONTINUOUSSPEED = _descriptor.Descriptor(
    name="LaneWithContinuousSpeed",
    full_name="action.LaneWithContinuousSpeed",
    filename=None,
    file=DESCRIPTOR,
    containing_type=None,
    create_key=_descriptor._internal_create_key,
    fields=[
        _descriptor.FieldDescriptor(
            name="action",
            full_name="action.LaneWithContinuousSpeed.action",
            index=0,
            number=1,
            type=2,
            cpp_type=6,
            label=3,
            has_default_value=False,
            default_value=[],
            message_type=None,
            enum_type=None,
            containing_type=None,
            is_extension=False,
            extension_scope=None,
            serialized_options=None,
            file=DESCRIPTOR,
            create_key=_descriptor._internal_create_key,
        ),
    ],
    extensions=[],
    nested_types=[],
    enum_types=[],
    serialized_options=None,
    is_extendable=False,
    syntax="proto3",
    extension_ranges=[],
    oneofs=[],
    serialized_start=747,
    serialized_end=788,
)


_TARGETPOSE = _descriptor.Descriptor(
    name="TargetPose",
    full_name="action.TargetPose",
    filename=None,
    file=DESCRIPTOR,
    containing_type=None,
    create_key=_descriptor._internal_create_key,
    fields=[
        _descriptor.FieldDescriptor(
            name="action",
            full_name="action.TargetPose.action",
            index=0,
            number=1,
            type=2,
            cpp_type=6,
            label=3,
            has_default_value=False,
            default_value=[],
            message_type=None,
            enum_type=None,
            containing_type=None,
            is_extension=False,
            extension_scope=None,
            serialized_options=None,
            file=DESCRIPTOR,
            create_key=_descriptor._internal_create_key,
        ),
    ],
    extensions=[],
    nested_types=[],
    enum_types=[],
    serialized_options=None,
    is_extendable=False,
    syntax="proto3",
    extension_ranges=[],
    oneofs=[],
    serialized_start=790,
    serialized_end=818,
)


_TRAJECTORY = _descriptor.Descriptor(
    name="Trajectory",
    full_name="action.Trajectory",
    filename=None,
    file=DESCRIPTOR,
    containing_type=None,
    create_key=_descriptor._internal_create_key,
    fields=[
        _descriptor.FieldDescriptor(
            name="action_1",
            full_name="action.Trajectory.action_1",
            index=0,
            number=1,
            type=2,
            cpp_type=6,
            label=3,
            has_default_value=False,
            default_value=[],
            message_type=None,
            enum_type=None,
            containing_type=None,
            is_extension=False,
            extension_scope=None,
            serialized_options=None,
            file=DESCRIPTOR,
            create_key=_descriptor._internal_create_key,
        ),
        _descriptor.FieldDescriptor(
            name="action_2",
            full_name="action.Trajectory.action_2",
            index=1,
            number=2,
            type=2,
            cpp_type=6,
            label=3,
            has_default_value=False,
            default_value=[],
            message_type=None,
            enum_type=None,
            containing_type=None,
            is_extension=False,
            extension_scope=None,
            serialized_options=None,
            file=DESCRIPTOR,
            create_key=_descriptor._internal_create_key,
        ),
        _descriptor.FieldDescriptor(
            name="action_3",
            full_name="action.Trajectory.action_3",
            index=2,
            number=3,
            type=2,
            cpp_type=6,
            label=3,
            has_default_value=False,
            default_value=[],
            message_type=None,
            enum_type=None,
            containing_type=None,
            is_extension=False,
            extension_scope=None,
            serialized_options=None,
            file=DESCRIPTOR,
            create_key=_descriptor._internal_create_key,
        ),
        _descriptor.FieldDescriptor(
            name="action_4",
            full_name="action.Trajectory.action_4",
            index=3,
            number=4,
            type=2,
            cpp_type=6,
            label=3,
            has_default_value=False,
            default_value=[],
            message_type=None,
            enum_type=None,
            containing_type=None,
            is_extension=False,
            extension_scope=None,
            serialized_options=None,
            file=DESCRIPTOR,
            create_key=_descriptor._internal_create_key,
        ),
    ],
    extensions=[],
    nested_types=[],
    enum_types=[],
    serialized_options=None,
    is_extendable=False,
    syntax="proto3",
    extension_ranges=[],
    oneofs=[],
    serialized_start=820,
    serialized_end=904,
)


_MULTITARGETPOSE = _descriptor.Descriptor(
    name="MultiTargetPose",
    full_name="action.MultiTargetPose",
    filename=None,
    file=DESCRIPTOR,
    containing_type=None,
    create_key=_descriptor._internal_create_key,
    fields=[],
    extensions=[],
    nested_types=[],
    enum_types=[],
    serialized_options=None,
    is_extendable=False,
    syntax="proto3",
    extension_ranges=[],
    oneofs=[],
    serialized_start=906,
    serialized_end=923,
)


_MPC = _descriptor.Descriptor(
    name="MPC",
    full_name="action.MPC",
    filename=None,
    file=DESCRIPTOR,
    containing_type=None,
    create_key=_descriptor._internal_create_key,
    fields=[
        _descriptor.FieldDescriptor(
            name="action_1",
            full_name="action.MPC.action_1",
            index=0,
            number=1,
            type=2,
            cpp_type=6,
            label=3,
            has_default_value=False,
            default_value=[],
            message_type=None,
            enum_type=None,
            containing_type=None,
            is_extension=False,
            extension_scope=None,
            serialized_options=None,
            file=DESCRIPTOR,
            create_key=_descriptor._internal_create_key,
        ),
        _descriptor.FieldDescriptor(
            name="action_2",
            full_name="action.MPC.action_2",
            index=1,
            number=2,
            type=2,
            cpp_type=6,
            label=3,
            has_default_value=False,
            default_value=[],
            message_type=None,
            enum_type=None,
            containing_type=None,
            is_extension=False,
            extension_scope=None,
            serialized_options=None,
            file=DESCRIPTOR,
            create_key=_descriptor._internal_create_key,
        ),
        _descriptor.FieldDescriptor(
            name="action_3",
            full_name="action.MPC.action_3",
            index=2,
            number=3,
            type=2,
            cpp_type=6,
            label=3,
            has_default_value=False,
            default_value=[],
            message_type=None,
            enum_type=None,
            containing_type=None,
            is_extension=False,
            extension_scope=None,
            serialized_options=None,
            file=DESCRIPTOR,
            create_key=_descriptor._internal_create_key,
        ),
        _descriptor.FieldDescriptor(
            name="action_4",
            full_name="action.MPC.action_4",
            index=3,
            number=4,
            type=2,
            cpp_type=6,
            label=3,
            has_default_value=False,
            default_value=[],
            message_type=None,
            enum_type=None,
            containing_type=None,
            is_extension=False,
            extension_scope=None,
            serialized_options=None,
            file=DESCRIPTOR,
            create_key=_descriptor._internal_create_key,
        ),
    ],
    extensions=[],
    nested_types=[],
    enum_types=[],
    serialized_options=None,
    is_extendable=False,
    syntax="proto3",
    extension_ranges=[],
    oneofs=[],
    serialized_start=925,
    serialized_end=1002,
)

_ACTIONSBOID_BOIDSENTRY.fields_by_name["value"].message_type = _ACTIONS
_ACTIONSBOID_BOIDSENTRY.containing_type = _ACTIONSBOID
_ACTIONSBOID.fields_by_name["boids"].message_type = _ACTIONSBOID_BOIDSENTRY
_ACTIONS_VEHICLESENTRY.fields_by_name["value"].message_type = _ACTION
_ACTIONS_VEHICLESENTRY.containing_type = _ACTIONS
_ACTIONS.fields_by_name["vehicles"].message_type = _ACTIONS_VEHICLESENTRY
_ACTION.fields_by_name["continuous"].message_type = _CONTINUOUS
_ACTION.fields_by_name["lane"].message_type = _LANE
_ACTION.fields_by_name["actuator_dynamic"].message_type = _ACTUATORDYNAMIC
_ACTION.fields_by_name[
    "lane_with_continuous_speed"
].message_type = _LANEWITHCONTINUOUSSPEED
_ACTION.fields_by_name["target_pose"].message_type = _TARGETPOSE
_ACTION.fields_by_name["trajectory"].message_type = _TRAJECTORY
_ACTION.fields_by_name["multi_target_pose"].message_type = _MULTITARGETPOSE
_ACTION.fields_by_name["mpc"].message_type = _MPC
_ACTION.oneofs_by_name["action"].fields.append(_ACTION.fields_by_name["continuous"])
_ACTION.fields_by_name["continuous"].containing_oneof = _ACTION.oneofs_by_name["action"]
_ACTION.oneofs_by_name["action"].fields.append(_ACTION.fields_by_name["lane"])
_ACTION.fields_by_name["lane"].containing_oneof = _ACTION.oneofs_by_name["action"]
_ACTION.oneofs_by_name["action"].fields.append(
    _ACTION.fields_by_name["actuator_dynamic"]
)
_ACTION.fields_by_name["actuator_dynamic"].containing_oneof = _ACTION.oneofs_by_name[
    "action"
]
_ACTION.oneofs_by_name["action"].fields.append(
    _ACTION.fields_by_name["lane_with_continuous_speed"]
)
_ACTION.fields_by_name[
    "lane_with_continuous_speed"
].containing_oneof = _ACTION.oneofs_by_name["action"]
_ACTION.oneofs_by_name["action"].fields.append(_ACTION.fields_by_name["target_pose"])
_ACTION.fields_by_name["target_pose"].containing_oneof = _ACTION.oneofs_by_name[
    "action"
]
_ACTION.oneofs_by_name["action"].fields.append(_ACTION.fields_by_name["trajectory"])
_ACTION.fields_by_name["trajectory"].containing_oneof = _ACTION.oneofs_by_name["action"]
_ACTION.oneofs_by_name["action"].fields.append(
    _ACTION.fields_by_name["multi_target_pose"]
)
_ACTION.fields_by_name["multi_target_pose"].containing_oneof = _ACTION.oneofs_by_name[
    "action"
]
_ACTION.oneofs_by_name["action"].fields.append(_ACTION.fields_by_name["mpc"])
_ACTION.fields_by_name["mpc"].containing_oneof = _ACTION.oneofs_by_name["action"]
DESCRIPTOR.message_types_by_name["ActionsBoid"] = _ACTIONSBOID
DESCRIPTOR.message_types_by_name["Actions"] = _ACTIONS
DESCRIPTOR.message_types_by_name["Action"] = _ACTION
DESCRIPTOR.message_types_by_name["Continuous"] = _CONTINUOUS
DESCRIPTOR.message_types_by_name["Lane"] = _LANE
DESCRIPTOR.message_types_by_name["ActuatorDynamic"] = _ACTUATORDYNAMIC
DESCRIPTOR.message_types_by_name["LaneWithContinuousSpeed"] = _LANEWITHCONTINUOUSSPEED
DESCRIPTOR.message_types_by_name["TargetPose"] = _TARGETPOSE
DESCRIPTOR.message_types_by_name["Trajectory"] = _TRAJECTORY
DESCRIPTOR.message_types_by_name["MultiTargetPose"] = _MULTITARGETPOSE
DESCRIPTOR.message_types_by_name["MPC"] = _MPC
_sym_db.RegisterFileDescriptor(DESCRIPTOR)

ActionsBoid = _reflection.GeneratedProtocolMessageType(
    "ActionsBoid",
    (_message.Message,),
    {
        "BoidsEntry": _reflection.GeneratedProtocolMessageType(
            "BoidsEntry",
            (_message.Message,),
            {
                "DESCRIPTOR": _ACTIONSBOID_BOIDSENTRY,
                "__module__": "action_pb2"
                # @@protoc_insertion_point(class_scope:action.ActionsBoid.BoidsEntry)
            },
        ),
        "DESCRIPTOR": _ACTIONSBOID,
        "__module__": "action_pb2"
        # @@protoc_insertion_point(class_scope:action.ActionsBoid)
    },
)
_sym_db.RegisterMessage(ActionsBoid)
_sym_db.RegisterMessage(ActionsBoid.BoidsEntry)

Actions = _reflection.GeneratedProtocolMessageType(
    "Actions",
    (_message.Message,),
    {
        "VehiclesEntry": _reflection.GeneratedProtocolMessageType(
            "VehiclesEntry",
            (_message.Message,),
            {
                "DESCRIPTOR": _ACTIONS_VEHICLESENTRY,
                "__module__": "action_pb2"
                # @@protoc_insertion_point(class_scope:action.Actions.VehiclesEntry)
            },
        ),
        "DESCRIPTOR": _ACTIONS,
        "__module__": "action_pb2"
        # @@protoc_insertion_point(class_scope:action.Actions)
    },
)
_sym_db.RegisterMessage(Actions)
_sym_db.RegisterMessage(Actions.VehiclesEntry)

Action = _reflection.GeneratedProtocolMessageType(
    "Action",
    (_message.Message,),
    {
        "DESCRIPTOR": _ACTION,
        "__module__": "action_pb2"
        # @@protoc_insertion_point(class_scope:action.Action)
    },
)
_sym_db.RegisterMessage(Action)

Continuous = _reflection.GeneratedProtocolMessageType(
    "Continuous",
    (_message.Message,),
    {
        "DESCRIPTOR": _CONTINUOUS,
        "__module__": "action_pb2"
        # @@protoc_insertion_point(class_scope:action.Continuous)
    },
)
_sym_db.RegisterMessage(Continuous)

Lane = _reflection.GeneratedProtocolMessageType(
    "Lane",
    (_message.Message,),
    {
        "DESCRIPTOR": _LANE,
        "__module__": "action_pb2"
        # @@protoc_insertion_point(class_scope:action.Lane)
    },
)
_sym_db.RegisterMessage(Lane)

ActuatorDynamic = _reflection.GeneratedProtocolMessageType(
    "ActuatorDynamic",
    (_message.Message,),
    {
        "DESCRIPTOR": _ACTUATORDYNAMIC,
        "__module__": "action_pb2"
        # @@protoc_insertion_point(class_scope:action.ActuatorDynamic)
    },
)
_sym_db.RegisterMessage(ActuatorDynamic)

LaneWithContinuousSpeed = _reflection.GeneratedProtocolMessageType(
    "LaneWithContinuousSpeed",
    (_message.Message,),
    {
        "DESCRIPTOR": _LANEWITHCONTINUOUSSPEED,
        "__module__": "action_pb2"
        # @@protoc_insertion_point(class_scope:action.LaneWithContinuousSpeed)
    },
)
_sym_db.RegisterMessage(LaneWithContinuousSpeed)

TargetPose = _reflection.GeneratedProtocolMessageType(
    "TargetPose",
    (_message.Message,),
    {
        "DESCRIPTOR": _TARGETPOSE,
        "__module__": "action_pb2"
        # @@protoc_insertion_point(class_scope:action.TargetPose)
    },
)
_sym_db.RegisterMessage(TargetPose)

Trajectory = _reflection.GeneratedProtocolMessageType(
    "Trajectory",
    (_message.Message,),
    {
        "DESCRIPTOR": _TRAJECTORY,
        "__module__": "action_pb2"
        # @@protoc_insertion_point(class_scope:action.Trajectory)
    },
)
_sym_db.RegisterMessage(Trajectory)

MultiTargetPose = _reflection.GeneratedProtocolMessageType(
    "MultiTargetPose",
    (_message.Message,),
    {
        "DESCRIPTOR": _MULTITARGETPOSE,
        "__module__": "action_pb2"
        # @@protoc_insertion_point(class_scope:action.MultiTargetPose)
    },
)
_sym_db.RegisterMessage(MultiTargetPose)

MPC = _reflection.GeneratedProtocolMessageType(
    "MPC",
    (_message.Message,),
    {
        "DESCRIPTOR": _MPC,
        "__module__": "action_pb2"
        # @@protoc_insertion_point(class_scope:action.MPC)
    },
)
_sym_db.RegisterMessage(MPC)


_ACTIONSBOID_BOIDSENTRY._options = None
_ACTIONS_VEHICLESENTRY._options = None
# @@protoc_insertion_point(module_scope)
