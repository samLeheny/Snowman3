import os
from Snowman3.rigger.rig_factory.objects.quadruped_objects.quadruped_back_leg import QuadrupedBackLeg,\
    QuadrupedBackLegGuide
from Snowman3.rigger.rig_factory.objects.node_objects.joint import Joint
from Snowman3.rigger.rig_factory.objects.base_objects.properties import DataProperty, ObjectProperty, ObjectListProperty
from Snowman3.rigger.rig_factory.objects.rig_objects.grouped_handle import GroupedHandle
from Snowman3.rigger.rig_factory.objects.rig_objects.limb_segment import LimbSegment
from Snowman3.rigger.rig_factory.objects.rig_objects.plugin_limb_segment import PluginLimbSegment
from Snowman3.rigger.rig_factory.objects.node_objects.transform import Transform
from Snowman3.rigger.rig_factory.objects.node_objects.depend_node import DependNode
import Snowman3.rigger.rig_factory.environment as env
from Snowman3.rigger.rig_math.vector import Vector
from Snowman3.rigger.rig_math.matrix import Matrix
import Snowman3.rigger.rig_math.utilities as rmu
import Snowman3.rigger.rig_factory as rig_factory


class QuadrupedBendyBackLegGuide(QuadrupedBackLegGuide):
    segment_joint_count = DataProperty( name='segment_joint_count', default_value=8 )
    pole_distance_multiplier = DataProperty( name='pole_distance_multiplier', default_value=0.5 )
    world_space_foot = DataProperty( name='world_space_foot', default_value=True )
    base_joints = ObjectListProperty( name='base_joints' )
    new_twist_system = DataProperty( name='new_twist_system', default_value=True )

    default_settings = dict(
        root_name='BackLeg',
        size=3.0,
        side='left',
        pole_distance_multiplier=0.5,
        world_space_foot=True,
        use_plugins=os.getenv('USE_RIG_PLUGINS', False),
        new_twist_system=True,
        create_plane=True
    )
    create_plane = DataProperty(
        name='create_plane',
        default_value=True
    )

    def __init__(self, **kwargs):
        super(QuadrupedBendyBackLegGuide, self).__init__(**kwargs)
        self.toggle_class = QuadrupedBendyBackLeg.__name__

    @classmethod
    def create(cls, **kwargs):
        this = super(QuadrupedBendyBackLegGuide, cls).create(**kwargs)
        ordered_joints = [this.joints[0], this.joints[1]]
        segment_joint_count = this.segment_joint_count
        thigh_joints = create_segment_joints(
            this.joints[1],
            this.joints[2],
            this.segment_names[1],
            segment_joint_count
        )
        ordered_joints.extend(thigh_joints)
        ordered_joints.append(this.joints[2])
        knee_joints = create_segment_joints(
            this.joints[2],
            this.joints[3],
            this.segment_names[2],
            segment_joint_count
        )
        ordered_joints.extend(knee_joints)
        ordered_joints.append(this.joints[3])
        ankle_joints = create_segment_joints(
            this.joints[3],
            this.joints[4],
            this.segment_names[3],
            segment_joint_count
        )
        ordered_joints.extend(ankle_joints)
        ordered_joints.append(this.joints[4])
        ordered_joints.append(this.joints[5])
        this.base_joints = this.joints
        this.joints = ordered_joints
        return this

    def get_toggle_blueprint(self):
        blueprint = super(QuadrupedBendyBackLegGuide, self).get_toggle_blueprint()
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


class QuadrupedBendyBackLeg(QuadrupedBackLeg):
    segment_joint_count = DataProperty(
        name='segment_joint_count',
        default_value=8
    )
    pole_distance_multiplier = DataProperty(
        name='pole_distance_multiplier',
        default_value=0.5
    )
    knee_line = ObjectProperty(
        name='knee_line'
    )
    limb_segments = ObjectListProperty(
        name='limb_segments'
    )
    world_space_foot = DataProperty(
        name='world_space_foot',
        default_value=True
    )
    base_joints = ObjectListProperty(
        name='base_joints'
    )
    new_twist_system = DataProperty(
        name='new_twist_system',
        default_value=True,
    )

    def __init__(self, **kwargs):
        super(QuadrupedBendyBackLeg, self).__init__(**kwargs)

    @classmethod
    def create(cls, **kwargs):
        this = super(QuadrupedBendyBackLeg, cls).create(**kwargs)
        controller = this.controller
        size = this.size
        side = this.side
        new_twist_system = this.new_twist_system
        aim_vector = env.side_aim_vectors[side]
        matrices = this.matrices
        hip_matrix = matrices[0]
        thigh_matrix = matrices[1]
        knee_matrix = matrices[2]
        ankle_matrix = matrices[3]
        foot_matrix = matrices[4]
        toe_matrix = matrices[5]
        thigh_position = thigh_matrix.get_translation()
        knee_position = knee_matrix.get_translation()
        ankle_position = ankle_matrix.get_translation()
        foot_position = foot_matrix.get_translation()
        toe_position = toe_matrix.get_translation()
        thigh_length = (knee_position - thigh_position).mag()
        shin_length = (ankle_position - knee_position).mag()
        ankle_length = (foot_position - ankle_position).mag()
        leg_length = thigh_length + shin_length + ankle_length
        hock_side_position = ankle_matrix.get_translation() + (Vector(ankle_matrix.data[0]).normalize() * (size*10 if side != 'right' else size*-10.0))
        joints = this.joints

        knee_pole_position = Vector(rmu.calculate_pole_vector_position(
            thigh_position,
            knee_position,
            ankle_position,
            distance=leg_length * this.pole_distance_multiplier
        ))

        ankle_pole_position = Vector(rmu.calculate_pole_vector_position(
            knee_position,
            ankle_position,
            foot_position,
            distance=leg_length * this.pole_distance_multiplier
        ))
        foot_pole_position = Vector(rmu.calculate_pole_vector_position(
            ankle_position,
            foot_position,
            toe_position,
            distance=leg_length * this.pole_distance_multiplier
        ))
        ordered_joints = [joints[0], joints[1]]

        knee_corner_aim_transform = this.create_child(
            Transform,
            segment_name='KneeCornerAim',
            matrix=knee_pole_position,
            parent=joints[1]
        )

        ankle_corner_aim_transform = this.create_child(
            Transform,
            segment_name='AnkleCornerAim',
            matrix=ankle_pole_position,
            parent=joints[2]

        )

        foot_corner_aim_transform = this.create_child(
            Transform,
            segment_name='FootCornerAim',
            matrix=foot_pole_position,
            parent=joints[3]
        )

        hock_side_vector_transform = joints[2].create_child(
            Transform,
            segment_name='HockSideVector',
            matrix=Matrix(hock_side_position)
        )
        knee_side_vector_transform = this.create_child(
            Transform,
            segment_name='KneeSideVector',
            parent=joints[2],
        )
        ankle_side_vector_transform = this.create_child(
            Transform,
            segment_name='AnkleSideVector',
            parent=joints[3],
        )
        foot_side_vector_transform = this.create_child(
            Transform,
            segment_name='FootSideVector',
            parent=joints[4],
        )

        hip_side_vector_transform = this.create_child(
            Transform,
            segment_name='HipUpVector',
            parent=joints[1],
        )

        knee_corner_parent_constraint = controller.create_parent_constraint(
            joints[1],
            joints[2],
            knee_corner_aim_transform,
            mo=True
        )

        ankle_corner_parent_constraint = controller.create_parent_constraint(
            joints[2],
            joints[3],
            ankle_corner_aim_transform,
            mo=True
        )
        foot_corner_parent_constraint = controller.create_parent_constraint(
            joints[3],
            joints[4],
            foot_corner_aim_transform,
            mo=True

        )
        knee_corner_parent_constraint.plugs['interpType'].set_value(2)
        ankle_corner_parent_constraint.plugs['interpType'].set_value(2)
        foot_corner_parent_constraint.plugs['interpType'].set_value(2)
        knee_side_vector_transform.plugs['translate'].set_value([size * 10.0 if side != 'right' else size * -10.0, 0.0, 0.0])
        ankle_side_vector_transform.plugs['translate'].set_value([size * 10.0 if side != 'right' else size * -10.0, 0.0, 0.0])
        foot_side_vector_transform.plugs['translate'].set_value([size * 10.0 if side != 'right' else size * -10.0, 0.0, 0.0])
        hip_side_vector_transform.plugs['translate'].set_value([size * 10.0 if side != 'right' else size * -10.0, 0.0, 0.0])
        hip_side_vector_transform.set_parent(this)
        knee_corner_handle = this.create_handle(
            handle_type=GroupedHandle,
            segment_name='KneeCorner',
            shape='ball',
            size=size,
            group_count=3,
            parent=this.joints[2]
        )

        ankle_corner_handle = this.create_handle(
            handle_type=GroupedHandle,
            segment_name='AnkleCorner',
            shape='ball',
            size=size,
            group_count=3,
            parent=this.joints[3]
        )

        controller.create_aim_constraint(
            joints[4],
            ankle_corner_handle.groups[0],
            aimVector=aim_vector,
            upVector=[1.0, 0.0, 0.0],
            worldUpType='object',
            worldUpObject=hock_side_vector_transform
        )

        foot_corner_transform = this.create_child(
            Transform,
            segment_name='FootCorner',
            parent=joints[4]

        )
        knee_segment_up_transform = this.create_child(
            Transform,
            segment_name='KneeSegmentUp',
            parent=knee_corner_handle,
        )
        ankle_segment_up_transform = this.create_child(
            Transform,
            segment_name='AnkleSegmentUp',
            parent=ankle_corner_handle,
        )
        foot_segment_up_transform = this.create_child(
            Transform,
            segment_name='FootSegmentUp',
            parent=foot_corner_transform,
        )
        knee_segment_up_transform.plugs['translate'].set_value([size * 10.0 if side != 'right' else size * -10.0, 0.0, 0.0])
        ankle_segment_up_transform.plugs['translate'].set_value([size * 10.0, 0.0, 0.0])
        foot_segment_up_transform.plugs['translate'].set_value([size * 10.0 if side != 'right' else size * -10.0, 0.0, 0.0])
        thigh_segment = this.create_child(
            PluginLimbSegment if this.use_plugins else LimbSegment,
            owner=this,
            segment_name=this.segment_names[1],
            matrices=[matrices[1], matrices[2]],
            joint_count=this.segment_joint_count,
            functionality_name='Bendy',
            new_twist_system=new_twist_system,
            start_joint=joints[1],
            end_joint=joints[2],
            ignore_parent_twist=True,
        )
        ordered_joints.extend(thigh_segment.joints)

        for segment in thigh_segment.handles:
            segment.plugs.set_values(
                overrideEnabled=True,
                overrideRGBColors=True,
                overrideColorRGB=env.secondary_colors[side]
            )

        controller.create_aim_constraint(
            thigh_segment.handles[1],
            thigh_segment.handles[0].groups[0],
            aimVector=env.side_aim_vectors[side],
            upVector=[x * -1.0 for x in env.side_cross_vectors[side]],
            worldUpType='object',  # This should use "objectRotation"
            worldUpObject=hip_side_vector_transform
        )
        controller.create_aim_constraint(
            thigh_segment.handles[1],
            thigh_segment.handles[2].groups[0],
            aimVector=[x * -1.0 for x in env.side_aim_vectors[side]],
            upVector=[x * -1.0 for x in env.side_cross_vectors[side]],
            worldUpType='object',  # This should use "objectRotation"
            worldUpObject=knee_side_vector_transform
        )

        controller.create_point_constraint(
            joints[1],
            knee_corner_handle,
            thigh_segment.handles[1].groups[0],
            mo=False
        )

        controller.create_point_constraint(
            joints[1],
            thigh_segment.handles[0].groups[0],
            mo=False
        )

        controller.create_point_constraint(
            knee_corner_handle,
            thigh_segment.handles[2].groups[0],
            mo=False
        )
        controller.create_aim_constraint(
            knee_corner_handle,
            thigh_segment.handles[1].groups[0],
            aimVector=[x * -1.0 for x in env.side_aim_vectors[side]],
            upVector=[x * -1.0 for x in env.side_cross_vectors[side]],
            worldUpType='object',
            worldUpObject=hip_side_vector_transform,
            mo=False
        )

        ordered_joints.append(joints[2])

        calf_segment = this.create_child(
            PluginLimbSegment if this.use_plugins else LimbSegment,
            side=side,
            owner=this,
            segment_name=this.segment_names[2],
            matrices=[matrices[2], matrices[3]],
            joint_count=this.segment_joint_count,
            functionality_name='Bendy',
            new_twist_system=new_twist_system,
            start_joint=joints[2],
            end_joint=joints[3],
            ignore_parent_twist=False,
        )
        ordered_joints.extend(calf_segment.joints)

        for segment in calf_segment.handles:
            segment.plugs.set_values(
                overrideEnabled=True,
                overrideRGBColors=True,
                overrideColorRGB=env.secondary_colors[side]
            )

        controller.create_aim_constraint(
            calf_segment.handles[1],
            calf_segment.handles[0].groups[0],
            aimVector=env.side_aim_vectors[side],
            upVector=[x * -1.0 for x in env.side_cross_vectors[side]],
            worldUpType='object',  # This should use "objectRotation"
            worldUpObject=knee_side_vector_transform
        )

        controller.create_aim_constraint(
            calf_segment.handles[1],
            calf_segment.handles[2].groups[0],
            aimVector=[x * -1.0 for x in env.side_aim_vectors[side]],
            upVector=[x * -1.0 for x in env.side_cross_vectors[side]],
            worldUpType='object',  # This should use "objectRotation"
            worldUpObject=hock_side_vector_transform
        )

        controller.create_point_constraint(
            knee_corner_handle,
            calf_segment.handles[0].groups[0],
            mo=False
        )

        controller.create_point_constraint(
            ankle_corner_handle,
            calf_segment.handles[2].groups[0],
            mo=False
        )

        controller.create_aim_constraint(
            ankle_corner_handle,
            calf_segment.handles[1].groups[0],
            aimVector=aim_vector,
            upVector=[x * -1.0 for x in env.side_cross_vectors[side]],
            worldUpType='object',  # This should use "objectRotation"
            worldUpObject=knee_side_vector_transform,
            mo=False
        )

        controller.create_point_constraint(
            calf_segment.handles[0].groups[0],
            calf_segment.handles[2].groups[0],
            calf_segment.handles[1].groups[0],
            mo=False
        )

        ordered_joints.append(joints[3])

        ankle_segment = this.create_child(
            PluginLimbSegment if this.use_plugins else LimbSegment,
            side=side,
            owner=this,
            segment_name=this.segment_names[3],
            matrices=[matrices[3], matrices[4]],
            joint_count=this.segment_joint_count,
            functionality_name='Bendy',
            new_twist_system=new_twist_system,
            start_joint=joints[3],
            end_joint=joints[4],
            ignore_parent_twist=False,
        )
        ordered_joints.extend(ankle_segment.joints)

        for segment in ankle_segment.handles:
            segment.plugs.set_values(
                overrideEnabled=True,
                overrideRGBColors=True,
                overrideColorRGB=env.secondary_colors[side]
            )

        controller.create_aim_constraint(
            ankle_segment.handles[1],
            ankle_segment.handles[0].groups[0],
            aimVector=env.side_aim_vectors[side],
            upVector=[x * -1.0 for x in env.side_cross_vectors[side]],
            worldUpType='object',  # This should use "objectRotation"
            worldUpObject=hock_side_vector_transform
        )

        controller.create_aim_constraint(
            ankle_segment.handles[1],
            ankle_segment.handles[2].groups[0],
            aimVector=[x * -1.0 for x in env.side_aim_vectors[side]],
            upVector=[x * -1.0 for x in env.side_cross_vectors[side]],
            worldUpType='object',  # This should use "objectRotation"
            worldUpObject=foot_side_vector_transform
        )

        controller.create_point_constraint(
            ankle_corner_handle,
            foot_corner_transform,
            ankle_segment.handles[1].groups[0],
            mo=True
        )

        controller.create_point_constraint(
            ankle_corner_handle,
            ankle_segment.handles[0].groups[0],
            mo=False
        )

        controller.create_point_constraint(
            foot_corner_transform,
            ankle_segment.handles[2].groups[0],
            mo=False
        )

        controller.create_aim_constraint(
            foot_corner_transform,
            ankle_segment.handles[1].groups[0],
            aimVector=aim_vector,
            upVector=[x * -1.0 for x in env.side_cross_vectors[side]],
            worldUpType='object',  # This should use "objectRotation"
            worldUpObject=hock_side_vector_transform,
            mo=False
        )

        if this.use_plugins:
            joints[1].plugs['worldMatrix'].element(0).connect_to(thigh_segment.spline_node.plugs['parentMatrix'])
            joints[2].plugs['worldMatrix'].element(0).connect_to(calf_segment.spline_node.plugs['parentMatrix'])
            joints[3].plugs['worldMatrix'].element(0).connect_to(ankle_segment.spline_node.plugs['parentMatrix'])
        else:
            thigh_segment.setup_scale_joints()
            calf_segment.setup_scale_joints()
            ankle_segment.setup_scale_joints()

            this.hip_handle.plugs['sx'].connect_to(thigh_segment.handles[0].plugs['EndScaleX'])
            this.hip_handle.plugs['sz'].connect_to(thigh_segment.handles[0].plugs['EndScaleZ'])
            knee_corner_handle.plugs['sx'].connect_to(thigh_segment.handles[-1].plugs['EndScaleX'])
            knee_corner_handle.plugs['sz'].connect_to(thigh_segment.handles[-1].plugs['EndScaleZ'])
            knee_corner_handle.plugs['sx'].connect_to(calf_segment.handles[0].plugs['EndScaleX'])
            knee_corner_handle.plugs['sz'].connect_to(calf_segment.handles[0].plugs['EndScaleZ'])
            ankle_corner_handle.plugs['sx'].connect_to(calf_segment.handles[-1].plugs['EndScaleX'])
            ankle_corner_handle.plugs['sz'].connect_to(calf_segment.handles[-1].plugs['EndScaleZ'])
            ankle_corner_handle.plugs['sx'].connect_to(ankle_segment.handles[0].plugs['EndScaleX'])
            ankle_corner_handle.plugs['sz'].connect_to(ankle_segment.handles[0].plugs['EndScaleZ'])
            this.foot_handle.plugs['sx'].connect_to(ankle_segment.handles[-1].plugs['EndScaleX'])
            this.foot_handle.plugs['sz'].connect_to(ankle_segment.handles[-1].plugs['EndScaleZ'])

        root = this.get_root()
        squash_plug = this.settings_handle.create_plug(
            'squash',
            attributeType='float',
            keyable=True,
            defaultValue=0.0
        )
        squash_min_plug = this.settings_handle.create_plug(
            'squashMin',
            attributeType='float',
            keyable=True,
            defaultValue=-0.5,
        )
        squash_max_plug = this.settings_handle.create_plug(
            'squashMax',
            attributeType='float',
            keyable=True,
            defaultValue=0.5,
        )

        squash_plug.connect_to(thigh_segment.plugs['AutoVolume'])
        squash_min_plug.connect_to(thigh_segment.plugs['MinAutoVolume'])
        squash_max_plug.connect_to(thigh_segment.plugs['MaxAutoVolume'])

        squash_plug.connect_to(calf_segment.plugs['AutoVolume'])
        squash_min_plug.connect_to(calf_segment.plugs['MinAutoVolume'])
        squash_max_plug.connect_to(calf_segment.plugs['MaxAutoVolume'])

        squash_plug.connect_to(ankle_segment.plugs['AutoVolume'])
        squash_min_plug.connect_to(ankle_segment.plugs['MinAutoVolume'])
        squash_max_plug.connect_to(ankle_segment.plugs['MaxAutoVolume'])

        root.add_plugs(
            ankle_corner_handle.plugs['tx'],
            ankle_corner_handle.plugs['ty'],
            ankle_corner_handle.plugs['tz'],
            ankle_corner_handle.plugs['sx'],
            ankle_corner_handle.plugs['sy'],
            ankle_corner_handle.plugs['sz'],
            knee_corner_handle.plugs['tx'],
            knee_corner_handle.plugs['ty'],
            knee_corner_handle.plugs['tz'],
            knee_corner_handle.plugs['sx'],
            knee_corner_handle.plugs['sy'],
            knee_corner_handle.plugs['sz'],
            squash_plug
        )

        root.add_plugs(
            squash_min_plug,
            squash_max_plug,
            keyable=False
        )

        ordered_joints.extend([joints[4], joints[5]])
        limb_segments = [thigh_segment, calf_segment, ankle_segment]
        for segment in limb_segments:
            this.secondary_handles.extend(segment.handles)
        this.secondary_handles.append(ankle_corner_handle)
        this.secondary_handles.append(knee_corner_handle)
        this.base_joints = joints
        this.joints = ordered_joints
        this.limb_segments = limb_segments

        return this

