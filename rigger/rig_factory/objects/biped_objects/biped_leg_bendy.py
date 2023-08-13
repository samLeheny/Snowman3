import os
import Snowman3.rigger.rig_factory.environment as env
from Snowman3.rigger.rig_factory.objects.base_objects.properties import ObjectListProperty, DataProperty, ObjectProperty
from Snowman3.rigger.rig_factory.objects.node_objects.transform import Transform
from Snowman3.rigger.rig_factory.objects.rig_objects.grouped_handle import GroupedHandle
from Snowman3.rigger.rig_factory.objects.biped_objects.biped_leg import BipedLeg, BipedLegGuide
from Snowman3.rigger.rig_factory.objects.rig_objects.limb_segment import LimbSegment
from Snowman3.rigger.rig_factory.objects.rig_objects.plugin_limb_segment import PluginLimbSegment
from Snowman3.rigger.rig_factory.objects.node_objects.joint import Joint
from Snowman3.rigger.rig_factory.objects.node_objects.depend_node import DependNode
from Snowman3.rigger.rig_factory.objects.part_objects.part import Part
import Snowman3.rigger.rig_factory.positions as pos
import Snowman3.rigger.rig_factory as rig_factory


class BipedLegBendyGuide(BipedLegGuide):
    default_settings = dict(
        root_name='Leg',
        size=4.0,
        side='left',
        foot_placement_depth=1.0,
        master_foot=False,
        world_space_foot=True,
        pole_distance_multiplier=1.0,
        use_plugins=os.getenv('USE_RIG_PLUGINS', False),
        new_twist_system=True,
        create_plane=True
    )

    segment_names = DataProperty(
        name='segment_names',
        default_value=['Base', 'Hip', 'Knee', 'Foot', 'Toe', 'ToeTip']
    )

    master_foot = DataProperty(
        name='master_foot'
    )

    world_space_foot = DataProperty(
        name='world_space_foot',
        default_value=True
    )

    pole_distance_multiplier = DataProperty(
        name='pole_distance_multiplier',
        default_value=1.0
    )

    base_joints = ObjectListProperty(
        name='base_joints'
    )

    new_twist_system = DataProperty(
        name='new_twist_system',
        default_value=True,
    )

    def __init__(self, **kwargs):
        super(BipedLegBendyGuide, self).__init__(**kwargs)
        self.toggle_class = BipedLegBendy.__name__

    @classmethod
    def create(cls, **kwargs):
        this = super(BipedLegBendyGuide, cls).create(**kwargs)
        this.create_plug(
            'squash',
            defaultValue=0.0,
            keyable=True,
        )
        this.set_handle_positions(pos.BIPED_POSITIONS)
        segment_joint_count = 6
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
        ordered_joints.append(this.joints[4])
        ordered_joints.append(this.joints[5])

        this.base_joints = this.joints
        this.joints = ordered_joints

        return this

    def get_blueprint(self):
        blueprint = super(BipedLegBendyGuide, self).get_blueprint()
        return blueprint

    def get_toggle_blueprint(self):
        blueprint = super(BipedLegBendyGuide, self).get_toggle_blueprint()
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


class BipedLegBendy(Part):
    spline_joints = ObjectListProperty(
        name='spline_joints'
    )
    foot_placement_depth = DataProperty(
        name='foot_placement_depth',
        default_value=1.0
    )
    ik_match_joint = ObjectProperty(
        name='ik_match_joint'
    )
    settings_handle = ObjectProperty(
        name='settings_handle'
    )
    heel_placement_node = ObjectProperty(
        name='heel_placement_node'
    )
    ball_placement_node = ObjectProperty(
        name='ball_placement_node'
    )
    ankle_handle = ObjectProperty(
        name='ankle_handle'
    )
    knee_handle = ObjectProperty(
        name='knee_handle'
    )
    toe_handle = ObjectProperty(
        name='toe_handle'
    )
    ik_joints = ObjectListProperty(
        name='ik_joints'
    )
    ik_handles = ObjectListProperty(
        name='ik_handles'
    )
    fk_handles = ObjectListProperty(
        name='fk_handles'
    )
    fk_joints = ObjectListProperty(
        name='fk_joints'
    )
    fk_handle_gimbals = ObjectListProperty(
        name='fk_handle_gimbals'
    )
    knee_line = ObjectProperty(
        name='knee_line'
    )
    segment_names = DataProperty(
        name='segment_names',
        default_value=['Base', 'Hip', 'Knee', 'Foot', 'Toe', 'ToeTip']
    )
    master_foot = DataProperty(
        name='master_foot'
    )
    world_space_foot = DataProperty(
        name='world_space_foot',
        default_value=True
    )
    pole_distance_multiplier = DataProperty(
        name='pole_distance_multiplier',
        default_value=1.0
    )
    limb_segments = ObjectListProperty(
        name='limb_segments'
    )
    base_joints = ObjectListProperty(
        name='base_joints'
    )
    new_twist_system = DataProperty(
        name='new_twist_system',
        default_value=True,
    )

    def __init__(self, **kwargs):
        super(BipedLegBendy, self).__init__(**kwargs)

    @classmethod
    def create(cls, **kwargs):
        this = super(BipedLegBendy, cls).create(**kwargs)
        BipedLeg.build_rig(this)
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
        squash_plug = settings_handle.create_plug(
            'squash',
            attributeType='float',
            keyable=True,
            defaultValue=0.0
        )
        squash_min_plug = settings_handle.create_plug(
            'squashMin',
            attributeType='float',
            keyable=True,
            defaultValue=-0.5
        )
        squash_max_plug = settings_handle.create_plug(
            'squashMax',
            attributeType='float',
            keyable=True,
            defaultValue=0.5,
        )

        root.add_plugs(
            squash_plug
        )
        root.add_plugs(
            squash_min_plug,
            squash_max_plug,
            keyable=False
        )

        for deform_joint in joints[1:3]:
            deform_joint.plugs.set_values(
                radius=0
            )
        bendy_knee_handle = this.create_handle(
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
            bendy_knee_handle.plugs['tx'],
            bendy_knee_handle.plugs['ty'],
            bendy_knee_handle.plugs['tz'],
            bendy_knee_handle.plugs['rx'],
            bendy_knee_handle.plugs['ry'],
            bendy_knee_handle.plugs['rz'],
            bendy_knee_handle.plugs['sx'],
            bendy_knee_handle.plugs['sy'],
            bendy_knee_handle.plugs['sz'],
        )
        bendy_knee_handle.plugs.set_values(
            overrideEnabled=True,
            overrideRGBColors=True,
            overrideColorRGB=env.secondary_colors[side]
        )
        hip_orient_group_1 = joints[0].create_child(
            Transform,
            segment_name='HipOrientBase',
            matrix=matrices[1]
        )
        hip_orient_group_2 = joints[1].create_child(
            Transform,
            segment_name='HipOrientTip',
            matrix=matrices[1],
        )
        hip_orient_group = joints[0].create_child(
            Transform,
            segment_name='HipOrient',
            matrix=matrices[1],
        )
        knee_orient_group = joints[1].create_child(
            Transform,
            segment_name='KneeOrient',
            matrix=matrices[2],

        )
        ankle_orient_group = joints[3].create_child(
            Transform,
            segment_name='AnkleOrient',
            matrix=matrices[3],
        )
        hip_up_group = hip_orient_group.create_child(
            Transform,
            segment_name='HipUp',
        )
        up_group_distance = [x * size * -5.0 * this.pole_distance_multiplier for x in env.side_cross_vectors[side]]
        hip_up_group.plugs['translate'].set_value(up_group_distance)  # Use "matrix" kwarg please.(not set_value)
        knee_up_group = knee_orient_group.create_child(
            Transform,
            segment_name='KneeUp',
        )
        knee_up_group.plugs['translate'].set_value(up_group_distance)
        ankle_up_group = ankle_orient_group.create_child(
            Transform,
            segment_name='AnkleUp',
        )
        ankle_up_group.plugs['translate'].set_value(up_group_distance)  # Use "matrix" kwarg please.(not set_value)
        constraint = controller.create_orient_constraint(
            hip_orient_group_1,
            hip_orient_group_2,
            hip_orient_group,
            skip='y',
        )
        constraint.plugs['interpType'].set_value(2)
        constraint = controller.create_orient_constraint(
            joints[1],
            joints[2],
            knee_orient_group,
            skip='y'
        )
        constraint.plugs['interpType'].set_value(2)
        constraint = controller.create_orient_constraint(
            joints[2],
            joints[3],
            ankle_orient_group,
            skip='y'

        )
        constraint.plugs['interpType'].set_value(2)
        controller.create_point_constraint(
            joints[1],
            hip_orient_group
        )
        controller.create_point_constraint(
            joints[2],
            knee_orient_group
        )
        controller.create_point_constraint(
            joints[3],
            ankle_orient_group
        )

        ordered_joints = [this.joints[0], this.joints[1]]

        #  Thigh Bendy's
        thigh_segment = this.create_child(
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
        ordered_joints.extend(thigh_segment.joints)

        joints[1].plugs['scale'].connect_to(
            thigh_segment.joints[0].plugs['inverseScale'],
        )
        for segment in thigh_segment.handles:
            segment.plugs.set_values(
                overrideEnabled=True,
                overrideRGBColors=True,
                overrideColorRGB=env.secondary_colors[side]
            )
            this.secondary_handles.append(segment)
        this.controller.create_aim_constraint(
            thigh_segment.handles[1],
            thigh_segment.handles[0].groups[0],
            aimVector=env.side_aim_vectors[side],
            upVector=[x * -1.0 for x in env.side_cross_vectors[side]],
            worldUpType='object',
            worldUpObject=hip_up_group
        )
        this.controller.create_aim_constraint(
            thigh_segment.handles[1],
            thigh_segment.handles[2].groups[0],
            aimVector=[x * -1.0 for x in env.side_aim_vectors[side]],
            upVector=[x * -1.0 for x in env.side_cross_vectors[side]],
            worldUpType='object',
            worldUpObject=knee_up_group
        )
        this.controller.create_point_constraint(
            joints[1],
            bendy_knee_handle,
            thigh_segment.handles[1].groups[0],
            mo=False
        )
        this.controller.create_point_constraint(
            joints[1],
            thigh_segment.handles[0].groups[0],
            mo=False
        )
        this.controller.create_point_constraint(
            bendy_knee_handle,
            thigh_segment.handles[2].groups[0],
            mo=False
        )
        this.controller.create_aim_constraint(
            bendy_knee_handle,
            thigh_segment.handles[1].groups[0],
            aimVector=[x * -1.0 for x in env.side_aim_vectors[side]],
            upVector=[x * -1.0 for x in env.side_cross_vectors[side]],
            worldUpType='object',
            worldUpObject=hip_up_group,
            mo=False
        )

        #  Calf Bendy's

        calf_segment = this.create_child(
            PluginLimbSegment if this.use_plugins else LimbSegment,
            owner=this,
            segment_name=this.segment_names[2],
            matrices=[matrices[2], matrices[3]],
            joint_count=segment_joint_count,
            functionality_name='Bendy',
            new_twist_system=new_twist_system,
            start_joint=joints[2],
            end_joint=joints[3],
            ignore_parent_twist=False,
        )
        ordered_joints.append(joints[2])
        ordered_joints.extend(calf_segment.joints)

        joints[2].plugs['scale'].connect_to(
            calf_segment.joints[0].plugs['inverseScale'],
        )

        for segment in calf_segment.handles:
            segment.plugs.set_values(
                overrideEnabled=True,
                overrideRGBColors=True,
                overrideColorRGB=env.secondary_colors[side]
            )
            this.secondary_handles.append(segment)
        this.controller.create_aim_constraint(
            calf_segment.handles[1],
            calf_segment.handles[0].groups[0],
            aimVector=env.side_aim_vectors[side],
            upVector=[x * -1.0 for x in env.side_cross_vectors[side]],
            worldUpType='object',
            worldUpObject=knee_up_group
        )
        this.controller.create_aim_constraint(
            calf_segment.handles[1],
            calf_segment.handles[2].groups[0],
            aimVector=[x * -1.0 for x in env.side_aim_vectors[side]],
            upVector=[x * -1.0 for x in env.side_cross_vectors[side]],
            worldUpType='object',
            worldUpObject=ankle_up_group
        )

        this.controller.create_point_constraint(
            bendy_knee_handle,
            joints[3],
            calf_segment.handles[1].groups[0],
            mo=False
        )

        this.controller.create_point_constraint(
            bendy_knee_handle,
            calf_segment.handles[0].groups[0],
            mo=False
        )

        this.controller.create_point_constraint(
            joints[3],
            calf_segment.handles[2].groups[0],
            mo=False
        )
        this.controller.create_aim_constraint(
            joints[3],
            calf_segment.handles[1].groups[0],
            aimVector=[x * -1.0 for x in env.side_aim_vectors[side]],
            upVector=[x * -1.0 for x in env.side_cross_vectors[side]],
            worldUpType='object',
            worldUpObject=knee_up_group,
            mo=False
        )

        if this.use_plugins:
            joints[1].plugs['worldMatrix'].element(0).connect_to(thigh_segment.spline_node.plugs['parentMatrix'])
            joints[2].plugs['worldMatrix'].element(0).connect_to(calf_segment.spline_node.plugs['parentMatrix'])
            settings_handle.plugs['squash'].connect_to(thigh_segment.plugs['AutoVolume'])
            settings_handle.plugs['squashMin'].connect_to(thigh_segment.plugs['MinAutoVolume'])
            settings_handle.plugs['squashMax'].connect_to(thigh_segment.plugs['MaxAutoVolume'])
            settings_handle.plugs['squash'].connect_to(calf_segment.plugs['AutoVolume'])
            settings_handle.plugs['squashMin'].connect_to(calf_segment.plugs['MinAutoVolume'])
            settings_handle.plugs['squashMax'].connect_to(calf_segment.plugs['MaxAutoVolume'])
        else:
            calf_segment.setup_scale_joints()
            thigh_segment.setup_scale_joints()

            bendy_knee_handle.plugs['sx'].connect_to(thigh_segment.handles[-1].plugs['EndScaleX'])
            bendy_knee_handle.plugs['sz'].connect_to(thigh_segment.handles[-1].plugs['EndScaleZ'])
            bendy_knee_handle.plugs['sx'].connect_to(calf_segment.handles[0].plugs['EndScaleX'])
            bendy_knee_handle.plugs['sz'].connect_to(calf_segment.handles[0].plugs['EndScaleZ'])

            settings_handle.plugs['squash'].connect_to(thigh_segment.plugs['AutoVolume'])
            settings_handle.plugs['squashMin'].connect_to(thigh_segment.plugs['MinAutoVolume'])
            settings_handle.plugs['squashMax'].connect_to(thigh_segment.plugs['MaxAutoVolume'])

            settings_handle.plugs['squash'].connect_to(calf_segment.plugs['AutoVolume'])
            settings_handle.plugs['squashMin'].connect_to(calf_segment.plugs['MinAutoVolume'])
            settings_handle.plugs['squashMax'].connect_to(calf_segment.plugs['MaxAutoVolume'])

        ordered_joints.append(joints[3])
        ordered_joints.append(joints[4])
        ordered_joints.append(joints[5])

        this.secondary_handles.append(bendy_knee_handle)
        this.limb_segments = [thigh_segment, calf_segment]
        this.base_joints = this.joints
        this.joints = ordered_joints

        return this
    #
    # def create_deformation_rig(self, **kwargs):
    #     root = self.get_root()
    #     hip_joint = create_deform_joint(
    #         self.base_joints[0],
    #         root.deform_group
    #     )
    #     thigh_joint = create_deform_joint(
    #         self.base_joints[1],
    #         hip_joint
    #     )
    #     deform_joints = [hip_joint, thigh_joint]
    #     joint_parent = thigh_joint
    #     for bendy_joint in self.limb_segments[0].joints:
    #         joint_parent = create_deform_joint(bendy_joint, joint_parent)
    #         deform_joints.append(joint_parent)
    #
    #     knee_joint = create_deform_joint(
    #         self.base_joints[2],
    #         thigh_joint
    #     )
    #     deform_joints.append(knee_joint)
    #     joint_parent = knee_joint
    #     for bendy_joint in self.limb_segments[1].joints:
    #         joint_parent = create_deform_joint(bendy_joint, joint_parent)
    #         deform_joints.append(joint_parent)
    #     foot_joint = create_deform_joint(
    #         self.base_joints[3],
    #         knee_joint
    #     )
    #     deform_joints.append(foot_joint)
    #
    #     toe_joint = create_deform_joint(
    #         self.base_joints[4],
    #         foot_joint
    #     )
    #     toe_tip_joint = create_deform_joint(
    #         self.base_joints[5],
    #         toe_joint
    #     )
    #     deform_joints.extend([toe_joint, toe_tip_joint])
    #     self.deform_joints = deform_joints
    #     self.base_deform_joints = deform_joints


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
        drawStyle=bendy_joint.plugs['drawStyle'].get_value(2)
    )
    bendy_joint.plugs['rotateOrder'].connect_to(deform_joint.plugs['rotateOrder'])
    bendy_joint.plugs['inverseScale'].connect_to(deform_joint.plugs['inverseScale'])
    bendy_joint.plugs['jointOrient'].connect_to(deform_joint.plugs['jointOrient'])
    bendy_joint.plugs['translate'].connect_to(deform_joint.plugs['translate'])
    bendy_joint.plugs['rotate'].connect_to(deform_joint.plugs['rotate'])
    bendy_joint.plugs['scale'].connect_to(deform_joint.plugs['scale'])
    bendy_joint.plugs['drawStyle'].set_value(2)
    return deform_joint
