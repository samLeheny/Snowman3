import os
from Snowman3.rigger.rig_factory.objects.base_objects.properties import ObjectListProperty, DataProperty, ObjectProperty
from Snowman3.rigger.rig_factory.objects.biped_objects.biped_arm import BipedArmGuide, BipedArm
from Snowman3.rigger.rig_factory.objects.rig_objects.limb_segment import LimbSegment
from Snowman3.rigger.rig_factory.objects.rig_objects.plugin_limb_segment import PluginLimbSegment
from Snowman3.rigger.rig_factory.objects.node_objects.transform import Transform
from Snowman3.rigger.rig_factory.objects.node_objects.joint import Joint
from Snowman3.rigger.rig_factory.objects.node_objects.depend_node import DependNode
from Snowman3.rigger.rig_factory.objects.rig_objects.grouped_handle import GroupedHandle
from Snowman3.rigger.rig_factory.objects.part_objects.part import Part
import Snowman3.rigger.rig_factory.environment as env
from Snowman3.rigger.rig_math.vector import Vector
from Snowman3.rigger.rig_math.matrix import Matrix
import Snowman3.rigger.rig_factory as rig_factory


class BipedArmBendyGuide(BipedArmGuide):
    default_settings = {
        'root_name': 'Arm',
        'size': 4.0,
        'side': 'left',
        'squash': 0,
        'pole_distance_multiplier': 1.0,
        'make_hand_roll': False,
        'create_bendy_hand': False,
        'use_plugins': os.getenv('USE_RIG_PLUGINS', False),
        'new_twist_system': True,
        'create_plane':True

    }
    squash = DataProperty(
        name='squash'
    )
    segment_names = DataProperty(
        name='segment_names',
        default_value=['Clavicle', 'Shoulder', 'Elbow', 'Hand', 'HandEnd']
    )
    create_bendy_hand = DataProperty(
        name='create_bendy_hand'
    )
    new_twist_system = DataProperty(
        name='new_twist_system',
        default_value=True,
    )
    base_joints = ObjectListProperty(
        name='base_joints'
    )
    pole_distance_multiplier = DataProperty(
        name='pole_distance_multiplier',
        default_value=1.0
    )

    make_hand_roll = DataProperty(
        name='make_hand_roll',
        default_value=False
    )

    def __init__(self, **kwargs):
        super(BipedArmBendyGuide, self).__init__(**kwargs)
        self.toggle_class = BipedArmBendy.__name__

    @classmethod
    def create(cls, **kwargs):
        this = super(BipedArmBendyGuide, cls).create(**kwargs)
        segment_joint_count = 6
        this.create_plug(
            'squash',
            defaultValue=this.squash,
            keyable=True,
        )
        ordered_joints = [this.joints[0], this.joints[1]]

        shoulder_joints = create_segment_joints(
            this.joints[1],
            this.joints[2],
            this.segment_names[1],
            segment_joint_count
        )
        ordered_joints.extend(shoulder_joints)
        ordered_joints.append(this.joints[2])

        elbow_joints = create_segment_joints(
            this.joints[2],
            this.joints[3],
            this.segment_names[2],
            segment_joint_count
        )
        ordered_joints.extend(elbow_joints)
        ordered_joints.append(this.joints[3])
        if this.create_bendy_hand:
            hand_joints = create_segment_joints(
                this.joints[3],
                this.joints[4],
                this.segment_names[3],
                segment_joint_count
            )
            ordered_joints.extend(hand_joints)
        ordered_joints.append(this.joints[4])
        this.base_joints = this.joints
        this.joints = ordered_joints

        return this

    def get_blueprint(self):
        blueprint = super(BipedArmBendyGuide, self).get_blueprint()
        blueprint['squash'] = self.plugs['squash'].get_value()
        return blueprint

    def get_toggle_blueprint(self):
        blueprint = super(BipedArmBendyGuide, self).get_toggle_blueprint()
        blueprint['squash'] = self.plugs['squash'].get_value()
        matrices = [list(x.get_matrix()) for x in self.base_joints]
        matrices.extend([list(x.get_matrix()) for x in self.pivot_joints])
        blueprint['matrices'] = matrices
        return blueprint


def create_segment_joints(start_joint, end_joint, segment_name, segment_joint_count):
    segment_joints = []
    for x in range(segment_joint_count):
        index_character = rig_factory.index_dictionary[x].upper()
        segment_joint = start_joint.create_child(
            Joint,
            segment_name="{}{}".format(
                segment_name,
                index_character
            ),
        )
        segment_joint.zero_rotation()
        multiply_node = start_joint.create_child(
            DependNode,
            node_type='multiplyDivide',
            segment_name="{}{}".format(
                segment_name,
                index_character
            )
        )
        end_joint.plugs['translate'].connect_to(multiply_node.plugs['input1'])
        multiply_node.plugs['input2X'].set_value(1.0 / (segment_joint_count - 1) * x)
        multiply_node.plugs['input2Y'].set_value(1.0 / (segment_joint_count - 1) * x)
        multiply_node.plugs['input2Z'].set_value(1.0 / (segment_joint_count - 1) * x)
        multiply_node.plugs['output'].connect_to(segment_joint.plugs['translate'])
        segment_joints.append(segment_joint)
    return segment_joints


class BipedArmBendy(Part):
    spline_joints = ObjectListProperty(
        name='spline_joints'
    )
    squash = DataProperty(
        name='squash',
        default_value=0
    )

    settings_handle = ObjectProperty(
        name='settings_handle'
    )
    clavicle_handle = ObjectProperty(
        name='clavicle_handle'
    )
    base_joints = ObjectListProperty(
        name='base_joints'
    )
    finger_handle = ObjectProperty(
        name='finger_handle'
    )
    wrist_handle = ObjectProperty(
        name='wrist_handle'
    )
    wrist_handle_gimbal = ObjectProperty(
        name='wrist_handle_gimbal'
    )
    elbow_handle = ObjectProperty(
        name='elbow_handle'
    )
    ik_group = ObjectProperty(
        name='ik_group'
    )
    ik_joints = ObjectListProperty(
        name='ik_joints'
    )
    fk_joints = ObjectListProperty(
        name='fk_joints'
    )
    ik_handles = ObjectListProperty(
        name='ik_handles'
    )
    fk_handles = ObjectListProperty(
        name='fk_handles'
    )
    stretchable_plugs = ObjectListProperty(
        name='stretchable_plugs'
    )
    elbow_line = ObjectProperty(
        name='elbow_line'
    )
    segment_names = DataProperty(
        name='segment_names',
        default_value=['Clavicle', 'Shoulder', 'Elbow', 'Hand', 'HandEnd']
    )

    pole_distance_multiplier = DataProperty(
        name='pole_distance_multiplier',
        default_value=1.0
    )
    make_hand_roll = DataProperty(
        name='make_hand_roll',
        default_value=False
    )
    limb_segments = ObjectListProperty(
        name='limb_segments'
    )
    create_bendy_hand = DataProperty(
        name='create_bendy_hand'
    )
    new_twist_system = DataProperty(
        name='new_twist_system',
        default_value=True,
    )

    def __init__(self, **kwargs):
        super(BipedArmBendy, self).__init__(**kwargs)

    @classmethod
    def create(cls, **kwargs):
        this = super(BipedArmBendy, cls).create(**kwargs)
        BipedArm.build_rig(this)

        side = this.side
        size = this.size
        controller = this.controller
        joints = this.joints
        matrices = this.matrices
        root = this.get_root()
        segment_joint_count = 6
        settings_handle = this.settings_handle
        this.secondary_handles = []
        new_twist_system = this.new_twist_system
        ordered_joints = [joints[0], joints[1]]
        for joint in joints[1:-1]:
            joint.plugs.set_values(
                radius=0
            )
        bendy_elbow_handle = this.create_handle(
            handle_type=GroupedHandle,
            segment_name='%s%s' % (
                this.segment_names[1].title(),
                this.segment_names[2].title()
            ),
            functionality_name='Bendy',
            shape='ball',
            matrix=matrices[2],
            parent=joints[2],
            size=size * 0.75
        )
        root.add_plugs(
            bendy_elbow_handle.plugs['tx'],
            bendy_elbow_handle.plugs['ty'],
            bendy_elbow_handle.plugs['tz'],
            bendy_elbow_handle.plugs['rx'],
            bendy_elbow_handle.plugs['ry'],
            bendy_elbow_handle.plugs['rz'],
            bendy_elbow_handle.plugs['sx'],
            bendy_elbow_handle.plugs['sy'],
            bendy_elbow_handle.plugs['sz'],
        )
        bendy_elbow_handle.plugs.set_values(
            overrideEnabled=True,
            overrideRGBColors=True,
            overrideColorRGB=env.secondary_colors[side]
        )
        shoulder_orient_group_1 = joints[0].create_child(
            Transform,
            segment_name='ShoulderOrientBase',
            matrix=matrices[1]
        )
        shoulder_orient_group_2 = joints[1].create_child(
            Transform,
            segment_name='ShoulderOrientTip',
            matrix=matrices[1],
        )
        shoulder_orient_group = joints[0].create_child(
            Transform,
            segment_name='ShoulderOrient',
            matrix=matrices[1],
        )
        elbow_orient_group = joints[1].create_child(
            Transform,
            segment_name='ElbowOrient',
            matrix=matrices[2],
        )
        wrist_orient_group = joints[3].create_child(
            Transform,
            segment_name='WristOrient',
            matrix=matrices[3],
        )
        shoulder_up_group = shoulder_orient_group.create_child(
            Transform,
            segment_name='ShoulderUp',
        )
        up_group_distance = [x * size * -5.0 * this.pole_distance_multiplier for x in env.side_cross_vectors[side]]
        shoulder_up_group.plugs['translate'].set_value(up_group_distance)
        elbow_up_group = elbow_orient_group.create_child(
            Transform,
            segment_name='ElbowUp',
        )
        elbow_up_group.plugs['translate'].set_value(up_group_distance)
        wrist_up_group = wrist_orient_group.create_child(
            Transform,
            segment_name='WristUp',
        )
        wrist_up_group.plugs['translate'].set_value(up_group_distance)
        hand_up_group = joints[4].create_child(
            Transform,
            segment_name='HandUp',
        )
        hand_up_group.plugs['translate'].set_value(up_group_distance)
        constraint = controller.create_orient_constraint(
            shoulder_orient_group_1,
            shoulder_orient_group_2,
            shoulder_orient_group,
            skip='y',
        )
        constraint.plugs['interpType'].set_value(2)
        constraint = controller.create_orient_constraint(
            joints[2],
            joints[3],
            wrist_orient_group,
            skip='y'
        )
        constraint.plugs['interpType'].set_value(2)
        controller.create_point_constraint(
            joints[1],
            shoulder_orient_group
        )
        controller.create_point_constraint(
            joints[2],
            elbow_orient_group
        )
        controller.create_point_constraint(
            joints[3],
            wrist_orient_group
        )

        # creating additional single chain setup to calculate upvector for elbow bendy segments aim constraints
        joint_parent = joints[0]
        clavholderjoint = joints[0].create_child(
            Joint,
            segment_name="{}clavholdtwistfix".format(this.segment_names[0]),
            parent=joint_parent,
            matrix=matrices[0],
        )
        clavholderjoint.zero_rotation()
        root.add_plugs(
            clavholderjoint.plugs['rx'],
            clavholderjoint.plugs['ry'],
            clavholderjoint.plugs['rz']
        )
        shouldtwistnegate_pv_group = joints[1].create_child(
            Transform,
            segment_name='ShouldtwistnegatePV',
            matrix=matrices[1]
        )
        shouldtwistnegate_pv_group.plugs['translate'].set_value(up_group_distance)
        shouldertwistnegatelist = []
        shouldiksinglechain = this.segment_names[1:3]
        joint_parent = clavholderjoint
        i = 1
        for segment_name in shouldiksinglechain:
            joint = clavholderjoint.create_child(
                Joint,
                segment_name="{}shouldiktwistfix".format(segment_name),
                parent=joint_parent,
                matrix=matrices[i],
            )
            joint.zero_rotation()
            root.add_plugs(
                joint.plugs['rx'],
                joint.plugs['ry'],
                joint.plugs['rz']
            )
            shouldertwistnegatelist.append(joint)
            joint_parent = joint
            i = i + 1

        shouldtwistnegate_ik_solver = controller.create_ik_handle(
            shouldertwistnegatelist[0],
            shouldertwistnegatelist[1],
            parent=clavholderjoint,
            solver='ikRPsolver'
        )
        controller.create_point_constraint(joints[1], shouldertwistnegatelist[0])
        controller.create_point_constraint(joints[2], shouldtwistnegate_ik_solver)
        controller.create_pole_vector_constraint(shouldtwistnegate_pv_group, shouldtwistnegate_ik_solver)
        elbowtwistnegate_pv_group = joints[2].create_child(
            Transform,
            segment_name='ElbowtwistwistnegatePV',
            matrix=matrices[1]
        )
        elbowtwistnegate_pv_group.plugs['translate'].set_value(up_group_distance)
        elbowtwistnegatelist = []
        elbowiksinglechain = this.segment_names[2:4]

        joint_parent = clavholderjoint
        i = 1
        for segment_name in elbowiksinglechain:
            joint = clavholderjoint.create_child(
                Joint,
                segment_name="{}elbowiktwistfix".format(segment_name),
                parent=joint_parent,
                matrix=matrices[i],
            )
            joint.zero_rotation()
            root.add_plugs(
                joint.plugs['rx'],
                joint.plugs['ry'],
                joint.plugs['rz']
            )
            elbowtwistnegatelist.append(joint)
            joint_parent = joint
            i = i + 1

        elbowtwistnegate_ik_solver = controller.create_ik_handle(
            elbowtwistnegatelist[0],
            elbowtwistnegatelist[1],
            parent=clavholderjoint,
            solver='ikRPsolver'
        )
        controller.create_point_constraint(joints[2], elbowtwistnegatelist[0])
        controller.create_point_constraint(joints[3], elbowtwistnegate_ik_solver)
        controller.create_pole_vector_constraint(elbowtwistnegate_pv_group, elbowtwistnegate_ik_solver)
        elbow_orientfix_group = joints[1].create_child(
            Transform,
            segment_name='ElbowOrientFix',
            matrix=matrices[2],

        )
        elboworifix_up_group = elbow_orientfix_group.create_child(
            Transform,
            segment_name='ElbowUpOrientFix',
        )
        elboworifix_up_group.plugs['translate'].set_value(up_group_distance)
        constraint = controller.create_orient_constraint(
            shouldertwistnegatelist[0],
            elbowtwistnegatelist[0],
            elbow_orient_group
        )
        # as the control needs less twist from elbow than shoulder
        shoulder_twist = 0.7
        constraint.get_weight_plug(shouldertwistnegatelist[0]).set_value(shoulder_twist)
        constraint.get_weight_plug(elbowtwistnegatelist[0]).set_value(1.0 - shoulder_twist)
        constraint.plugs['interpType'].set_value(2)
        constraint = controller.create_orient_constraint(
            shouldertwistnegatelist[0],
            elbowtwistnegatelist[0],
            elbow_orientfix_group
        )
        constraint.plugs['interpType'].set_value(2)
        controller.create_point_constraint(
            joints[2],
            elbow_orientfix_group
        )
        clavholderjoint.plugs['visibility'].set_value(False)
        elbowtwistnegate_ik_solver.plugs['visibility'].set_value(False)
        shouldtwistnegate_ik_solver.plugs['visibility'].set_value(False)
        settings_handle.create_plug(
            'squash',
            attributeType='float',
            keyable=True,
        )
        settings_handle.create_plug(
            'squashMin',
            attributeType='float',
            keyable=True,
            defaultValue=-0.5,
        )
        settings_handle.create_plug(
            'squashMax',
            attributeType='float',
            keyable=True,
            defaultValue=0.5,
        )
        root.add_plugs(settings_handle.plugs['squash'])
        root.add_plugs(
            settings_handle.plugs['squashMin'],
            settings_handle.plugs['squashMax'],
            keyable=False
        )
        bendy_joints = []

        #  Up Arm Bendy's
        up_arm_segment = this.create_child(
            PluginLimbSegment if this.use_plugins else LimbSegment,
            owner=this,
            segment_name=this.segment_names[1],
            matrices=[matrices[1], matrices[2]],
            joint_count=segment_joint_count,
            functionality_name='Bendy',
            new_twist_system=new_twist_system,
            start_joint=joints[1],
            end_joint=joints[2],
            ignore_parent_twist=True,
        )
        ordered_joints.extend(up_arm_segment.joints)
        joints[1].plugs['scale'].connect_to(
            up_arm_segment.joints[0].plugs['inverseScale'],
        )

        for segment in up_arm_segment.handles:
            segment.plugs.set_values(
                overrideEnabled=True,
                overrideRGBColors=True,
                overrideColorRGB=env.secondary_colors[side]
            )
            this.secondary_handles.append(segment)

        this.controller.create_aim_constraint(
            up_arm_segment.handles[1],
            up_arm_segment.handles[0].groups[0],
            aimVector=env.side_aim_vectors[side],
            upVector=[x * -1.0 for x in env.side_cross_vectors[side]],
            worldUpType='object',
            worldUpObject=shoulder_up_group
        )
        this.controller.create_aim_constraint(
            up_arm_segment.handles[1],
            up_arm_segment.handles[2].groups[0],
            aimVector=[x * -1.0 for x in env.side_aim_vectors[side]],
            upVector=[x * -1.0 for x in env.side_cross_vectors[side]],
            worldUpType='object',
            worldUpObject=elbow_up_group
        )

        this.controller.create_point_constraint(
            joints[1],
            bendy_elbow_handle,
            up_arm_segment.handles[1].groups[0],
            mo=False
        )

        this.controller.create_point_constraint(
            joints[1],
            up_arm_segment.handles[0].groups[0],
            mo=False
        )

        this.controller.create_point_constraint(
            bendy_elbow_handle,
            up_arm_segment.handles[2].groups[0],
            mo=False
        )
        this.controller.create_aim_constraint(
            bendy_elbow_handle,
            up_arm_segment.handles[1].groups[0],
            aimVector=[x * -1.0 for x in env.side_aim_vectors[side]],
            upVector=[x * -1.0 for x in env.side_cross_vectors[side]],
            worldUpType='object',
            worldUpObject=shoulder_up_group
        )

        bendy_joints.extend(up_arm_segment.joints)

        #  Elbow Bendy's
        ordered_joints.append(joints[2])
        elbow_segment = this.create_child(
            PluginLimbSegment if this.use_plugins else LimbSegment,
            owner=this,
            segment_name=this.segment_names[2],
            functionality_name='Bendy',
            matrices=[matrices[2], matrices[3]],
            joint_count=segment_joint_count,
            new_twist_system=new_twist_system,
            start_joint=joints[2],
            end_joint=joints[3],
            ignore_parent_twist=False,
        )
        ordered_joints.extend(elbow_segment.joints)
        joints[2].plugs['scale'].connect_to(
            elbow_segment.joints[0].plugs['inverseScale'],
        )

        for segment in elbow_segment.handles:
            segment.plugs.set_values(
                overrideEnabled=True,
                overrideRGBColors=True,
                overrideColorRGB=env.secondary_colors[side]
            )
            this.secondary_handles.append(segment)

        this.controller.create_aim_constraint(
            elbow_segment.handles[1],
            elbow_segment.handles[0].groups[0],
            aimVector=env.side_aim_vectors[side],
            upVector=[x * -1.0 for x in env.side_cross_vectors[side]],
            worldUpType='object',
            worldUpObject=elboworifix_up_group
        )
        this.controller.create_aim_constraint(
            elbow_segment.handles[1],
            elbow_segment.handles[2].groups[0],
            aimVector=[x * -1.0 for x in env.side_aim_vectors[side]],
            upVector=[x * -1.0 for x in env.side_cross_vectors[side]],
            worldUpType='object',
            worldUpObject=wrist_up_group
        )

        this.controller.create_point_constraint(
            bendy_elbow_handle,
            joints[3],
            elbow_segment.handles[1].groups[0],
            mo=False
        )

        this.controller.create_point_constraint(
            bendy_elbow_handle,
            elbow_segment.handles[0].groups[0],
            mo=False
        )

        this.controller.create_point_constraint(
            joints[3],
            elbow_segment.handles[2].groups[0],
            mo=False
        )
        this.controller.create_aim_constraint(
            joints[3],
            elbow_segment.handles[1].groups[0],
            aimVector=[x * -1.0 for x in env.side_aim_vectors[side]],
            upVector=[x * -1.0 for x in env.side_cross_vectors[side]],
            worldUpType='object',
            worldUpObject=elboworifix_up_group
        )

        bendy_joints.extend(elbow_segment.joints)

        if this.use_plugins:
            joints[1].plugs['worldMatrix'].element(0).connect_to(up_arm_segment.spline_node.plugs['parentMatrix'])
            joints[2].plugs['worldMatrix'].element(0).connect_to(elbow_segment.spline_node.plugs['parentMatrix'])
        else:
            up_arm_segment.setup_scale_joints()
            elbow_segment.setup_scale_joints()

        limb_segments = [up_arm_segment, elbow_segment]

        #  Hand Bendy
        ordered_joints.append(joints[3])

        if this.create_bendy_hand:
            hand_segment = this.create_child(
                PluginLimbSegment if this.use_plugins else LimbSegment,
                owner=this,
                segment_name=this.segment_names[3],
                functionality_name='Bendy',
                matrices=[matrices[3], matrices[4]],
                joint_count=segment_joint_count,
                new_twist_system=new_twist_system,
                start_joint=joints[3],
                end_joint=joints[4],
                ignore_parent_twist=False,
            )
            ordered_joints.extend(hand_segment.joints)
            if this.use_plugins:
                joints[3].plugs['worldMatrix'].element(0).connect_to(hand_segment.spline_node.plugs['parentMatrix'])
            joints[3].plugs['scale'].connect_to(
                hand_segment.joints[0].plugs['inverseScale'],
            )

            for secondary_handle in hand_segment.handles:
                secondary_handle.plugs.set_values(
                    overrideEnabled=True,
                    overrideRGBColors=True,
                    overrideColorRGB=env.secondary_colors[side]
                )
                this.secondary_handles.append(secondary_handle)

            this.controller.create_aim_constraint(
                hand_segment.handles[1],
                hand_segment.handles[0].groups[0],
                aimVector=env.side_aim_vectors[side],
                upVector=[x * -1.0 for x in env.side_cross_vectors[side]],
                worldUpType='object',
                worldUpObject=wrist_up_group
            )
            this.controller.create_aim_constraint(
                hand_segment.handles[1],
                hand_segment.handles[2].groups[0],
                aimVector=[x * -1.0 for x in env.side_aim_vectors[side]],
                upVector=[x * -1.0 for x in env.side_cross_vectors[side]],
                worldUpType='object',
                worldUpObject=hand_up_group
            )
            this.controller.create_point_constraint(
                joints[3],
                joints[4],
                hand_segment.handles[1].groups[0],
                mo=False
            )
            this.controller.create_point_constraint(
                joints[3],
                hand_segment.handles[0].groups[0],
                mo=False
            )
            this.controller.create_point_constraint(
                joints[4],
                hand_segment.handles[2].groups[0],
                mo=False
            )
            this.controller.create_aim_constraint(
                joints[4],
                hand_segment.handles[1].groups[0],
                aimVector=[x * -1.0 for x in env.side_aim_vectors[side]],
                upVector=[x * -1.0 for x in env.side_cross_vectors[side]],
                worldUpType='object',
                worldUpObject=wrist_up_group
            )
            bendy_joints.extend(hand_segment.joints)

            if this.use_plugins:
                settings_handle.plugs['squash'].connect_to(hand_segment.plugs['AutoVolume'])
                settings_handle.plugs['squashMin'].connect_to(hand_segment.plugs['MinAutoVolume'])
                settings_handle.plugs['squashMax'].connect_to(hand_segment.plugs['MaxAutoVolume'])

            else:
                hand_segment.setup_scale_joints()
                settings_handle.plugs['squash'].connect_to(hand_segment.plugs['AutoVolume'])
                settings_handle.plugs['squashMin'].connect_to(hand_segment.plugs['MinAutoVolume'])
                settings_handle.plugs['squashMax'].connect_to(hand_segment.plugs['MaxAutoVolume'])
                joints[4].plugs['sx'].connect_to(hand_segment.handles[0].plugs['EndScaleX'])
                joints[4].plugs['sz'].connect_to(hand_segment.handles[0].plugs['EndScaleZ'])
            limb_segments.append(hand_segment)
        ordered_joints.append(joints[4])

        if this.use_plugins:
            settings_handle.plugs['squash'].connect_to(up_arm_segment.plugs['AutoVolume'])
            settings_handle.plugs['squashMin'].connect_to(up_arm_segment.plugs['MinAutoVolume'])
            settings_handle.plugs['squashMax'].connect_to(up_arm_segment.plugs['MaxAutoVolume'])

            settings_handle.plugs['squash'].connect_to(elbow_segment.plugs['AutoVolume'])
            settings_handle.plugs['squashMin'].connect_to(elbow_segment.plugs['MinAutoVolume'])
            settings_handle.plugs['squashMax'].connect_to(elbow_segment.plugs['MaxAutoVolume'])

        else:
            settings_handle.plugs['squash'].connect_to(up_arm_segment.plugs['AutoVolume'])
            settings_handle.plugs['squashMin'].connect_to(up_arm_segment.plugs['MinAutoVolume'])
            settings_handle.plugs['squashMax'].connect_to(up_arm_segment.plugs['MaxAutoVolume'])
            settings_handle.plugs['squash'].connect_to(elbow_segment.plugs['AutoVolume'])
            settings_handle.plugs['squashMin'].connect_to(elbow_segment.plugs['MinAutoVolume'])
            settings_handle.plugs['squashMax'].connect_to(elbow_segment.plugs['MaxAutoVolume'])
            bendy_elbow_handle.plugs['sx'].connect_to(up_arm_segment.handles[-1].plugs['EndScaleX'])
            bendy_elbow_handle.plugs['sz'].connect_to(up_arm_segment.handles[-1].plugs['EndScaleZ'])
            bendy_elbow_handle.plugs['sx'].connect_to(elbow_segment.handles[0].plugs['EndScaleX'])
            bendy_elbow_handle.plugs['sz'].connect_to(elbow_segment.handles[0].plugs['EndScaleZ'])

        this.limb_segments = limb_segments
        this.secondary_handles.append(bendy_elbow_handle)
        this.base_joints = this.joints
        this.joints = ordered_joints

        return this
    #
    # def create_deformation_rig(self, **kwargs):
    #     root = self.get_root()
    #     clavicle_joint = create_deform_joint(
    #         self.base_joints[0],
    #         root.deform_group
    #     )
    #     shoulder_joint = create_deform_joint(
    #         self.base_joints[1],
    #         clavicle_joint
    #     )
    #     deform_joints = [clavicle_joint, shoulder_joint]
    #     joint_parent = shoulder_joint
    #     for bendy_joint in self.limb_segments[0].joints:
    #         joint_parent = create_deform_joint(bendy_joint, joint_parent)
    #         deform_joints.append(joint_parent)
    #
    #     elbow_joint = create_deform_joint(
    #         self.base_joints[2],
    #         shoulder_joint
    #     )
    #     deform_joints.append(elbow_joint)
    #     joint_parent = elbow_joint
    #     for bendy_joint in self.limb_segments[1].joints:
    #         joint_parent = create_deform_joint(bendy_joint, joint_parent)
    #         deform_joints.append(joint_parent)
    #     hand_joint = create_deform_joint(
    #         self.base_joints[3],
    #         elbow_joint
    #     )
    #     deform_joints.append(hand_joint)
    #     if len(self.limb_segments) > 2:
    #         joint_parent = hand_joint
    #         for bendy_joint in self.limb_segments[2].joints:
    #             joint_parent = create_deform_joint(bendy_joint, joint_parent)
    #             deform_joints.append(joint_parent)
    #     hand_tip_joint = create_deform_joint(
    #         self.base_joints[4],
    #         hand_joint
    #     )
    #     deform_joints.append(hand_tip_joint)
    #     self.deform_joints = deform_joints
    #     self.base_deform_joints = deform_joints

    def toggle_ik(self):
        value = self.settings_handle.plugs['ikSwitch'].get_value()
        if value > 0.5:
            self.match_to_fk()
        else:
            self.match_to_ik()

    def match_to_fk(self):
        self.settings_handle.plugs['ikSwitch'].set_value(0.0)
        positions = [x.get_matrix() for x in self.ik_joints]
        for i in range(len(positions[0:3])):
            self.fk_handles[i].set_matrix(Matrix(positions[i]))

        if self.make_hand_roll:
            self.finger_handle.set_matrix(positions[3])

    def match_to_ik(self):
        self.settings_handle.plugs['ikSwitch'].set_value(1.0)
        positions = [x.get_matrix() for x in self.fk_joints]
        self.wrist_handle.set_matrix(positions[2])
        vector_multiplier = self.size * 10
        if self.side == 'left':
            vector_multiplier = vector_multiplier * -1
        z_vector_1 = Vector(positions[0].data[2][0:3]).normalize()
        z_vector_2 = Vector(positions[1].data[2][0:3]).normalize()
        z_vector = (z_vector_1 + z_vector_2) * 0.5
        pole_position = positions[1].get_translation() + (z_vector * vector_multiplier)
        self.elbow_handle.set_matrix(Matrix(pole_position))

        if self.make_hand_roll:
            self.finger_handle.set_matrix(positions[3])


def create_deform_joint(bendy_joint, joint_parent):
    deform_joint = bendy_joint.create_child(
        Joint,
        parent=joint_parent,
        functionality_name='Bind'
    )
    deform_joint.plugs['radius'].set_value(bendy_joint.plugs['radius'].get_value())
    deform_joint.zero_rotation()
    deform_joint.plugs.set_values(
        overrideEnabled=True,
        overrideRGBColors=True,
        overrideColorRGB=env.colors['bindJoints'],
        radius=bendy_joint.plugs['radius'].get_value(),
        type=bendy_joint.plugs['type'].get_value(),
        side={'center': 0, 'left': 1, 'right': 2, None: 3}[bendy_joint.side],
        drawStyle=bendy_joint.plugs['drawStyle'].get_value(2),
    )
    bendy_joint.plugs['rotateOrder'].connect_to(deform_joint.plugs['rotateOrder'])
    bendy_joint.plugs['inverseScale'].connect_to(deform_joint.plugs['inverseScale'])
    bendy_joint.plugs['jointOrient'].connect_to(deform_joint.plugs['jointOrient'])
    bendy_joint.plugs['translate'].connect_to(deform_joint.plugs['translate'])
    bendy_joint.plugs['rotate'].connect_to(deform_joint.plugs['rotate'])
    bendy_joint.plugs['scale'].connect_to(deform_joint.plugs['scale'])
    bendy_joint.plugs['drawStyle'].set_value(2)
    return deform_joint
