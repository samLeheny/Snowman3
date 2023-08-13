import copy
from Snowman3.rigger.rig_factory.objects.base_objects.properties import DataProperty
from Snowman3.rigger.rig_factory.objects.part_objects.chain_guide import ChainGuide
from Snowman3.rigger.rig_factory.objects.part_objects.part import Part
from Snowman3.rigger.rig_factory.objects.rig_objects.cone import Cone
from Snowman3.rigger.rig_factory.objects.node_objects.transform import Transform
from Snowman3.rigger.rig_factory.objects.node_objects.joint import Joint
from Snowman3.rigger.rig_factory.objects.node_objects.depend_node import DependNode
from Snowman3.rigger.rig_factory.objects.rig_objects.grouped_handle import WorldHandle, LocalHandle
from Snowman3.rigger.rig_factory.objects.rig_objects.line import Line
from Snowman3.rigger.rig_factory.objects.node_objects.locator import Locator
import Snowman3.rigger.rig_factory.environment as env
from Snowman3.rigger.rig_factory.objects.base_objects.properties import ObjectProperty, ObjectListProperty
from Snowman3.rigger.rig_math.matrix import Matrix, compose_matrix
from Snowman3.rigger.rig_math.vector import Vector
import Snowman3.rigger.rig_math.utilities as rmu
import Snowman3.rigger.rig_factory.positions as pos
import Snowman3.rigger.rig_factory.utilities.limb_utilities as limb_utilities


class QuadrupedBackLegIkGuide(ChainGuide):

    segment_names = DataProperty(
        name='segment_names',
        default_value=['Hip', 'Knee', 'Ankle', 'Foot', 'Toe']
    )

    pole_distance_multiplier = DataProperty(
        name='pole_distance_multiplier',
        default_value=0.5
    )

    pivot_joints = ObjectListProperty(
        name='pivot_joints'
    )
    world_space_foot = DataProperty(
        name='world_space_foot',
        default_value=True
    )
    default_settings = dict(
        root_name='BackLeg',
        size=3.0,
        side='left',
        pole_distance_multiplier=0.5,
        world_space_foot=True
    )

    limb_plane = ObjectProperty(
        name='limb_plane'
    )

    def __init__(self, **kwargs):
        super(QuadrupedBackLegIkGuide, self).__init__(**kwargs)
        self.toggle_class = QuadrupedBackLegIk.__name__

    @classmethod
    def create(cls, **kwargs):
        kwargs['count'] = 5
        kwargs['up_vector_indices'] = [0, 3]
        this = super(QuadrupedBackLegIkGuide, cls).create(**kwargs)
        controller = this.controller
        body = this.get_root()
        size = this.size
        side = this.side
        size_plug = this.plugs['size']
        size_multiply_node = this.create_child(
            DependNode,
            node_type='multiplyDivide'
        )
        size_plug.connect_to(size_multiply_node.plugs['input1X'])
        size_multiply_node.plugs['input2X'].set_value(0.5)
        size_multiply_plug = size_multiply_node.plugs['outputX']
        pivot_handles = []
        pivot_joints = []
        for pivot_segment_name in ['Toe', 'Heel', 'InFoot', 'OutFoot']:
            handle = this.create_handle(
                segment_name=pivot_segment_name,
                functionality_name='Pivot'
            )
            joint = handle.create_child(
                Joint,
                segment_name=pivot_segment_name,
                functionality_name='Pivot',
            )
            cone_x = joint.create_child(
                Cone,
                segment_name='%sConeX' % pivot_segment_name,
                size=size * 0.1,
                axis=[1.0, 0.0, 0.0]
            )
            cone_y = joint.create_child(
                Cone,
                segment_name='%sConeY' % pivot_segment_name,
                size=size * 0.099,
                axis=[0.0, 1.0, 0.0]
            )
            cone_z = joint.create_child(
                Cone,
                segment_name='%sConeZ' % pivot_segment_name,
                size=size * 0.098,
                axis=[0.0, 0.0, 1.0]
            )
            pivot_handles.append(handle)
            pivot_joints.append(joint)
            controller.create_matrix_point_constraint(handle, joint)
            handle.mesh.assign_shading_group(body.shaders[side].shading_group)
            cone_x.mesh.assign_shading_group(body.shaders['x'].shading_group)
            cone_y.mesh.assign_shading_group(body.shaders['y'].shading_group)
            cone_z.mesh.assign_shading_group(body.shaders['z'].shading_group)
            size_multiply_plug.connect_to(handle.plugs['size'])
            size_multiply_plug.connect_to(cone_x.plugs['size'])
            size_multiply_plug.connect_to(cone_y.plugs['size'])
            size_multiply_plug.connect_to(cone_z.plugs['size'])
            joint.plugs.set_values(
                overrideEnabled=True,
                overrideDisplayType=2,
                radius=1.0
            )
            cone_x.plugs.set_values(
                overrideEnabled=True,
                overrideDisplayType=2,
            )
            cone_y.plugs.set_values(
                overrideEnabled=True,
                overrideDisplayType=2,
            )
            cone_z.plugs.set_values(
                overrideEnabled=True,
                overrideDisplayType=2,
            )

        front_handle, back_handle, in_handle, out_handle = pivot_handles
        front_joint, back_joint, in_joint, out_joint = pivot_joints
        controller.create_aim_constraint(front_handle, back_joint, aim=[0, 0, 1])
        controller.create_aim_constraint(
            back_handle,
            front_joint,
            aim=[0, 0, -1]
        )

        controller.create_aim_constraint(
            in_handle,
            out_joint,
            aim=[-1, 0, 0],
            worldUpType="scene",
            upVector=[0, 1, 0]
        )
        controller.create_aim_constraint(
            out_handle,
            in_joint,
            aim=[1, 0, 0],
            worldUpType="scene",
            upVector=[0, 1, 0]
        )
        this.pivot_joints = pivot_joints
        this.set_handle_positions(pos.QUADRUPED_POSITIONS)
        limb_utilities.make_ik_plane(this, this.base_handles[0], this.base_handles[3], this.up_handles[0])
        return this

    def get_toggle_blueprint(self):
        blueprint = super(QuadrupedBackLegIkGuide, self).get_toggle_blueprint()
        matrices = [list(x.get_matrix()) for x in self.joints]
        matrices.extend([list(x.get_matrix()) for x in self.pivot_joints])
        blueprint['matrices'] = matrices
        return blueprint

    def post_create(self, **kwargs):
        super(QuadrupedBackLegIkGuide, self).post_create(**kwargs)

        # geometry constrain knee
        self.controller.create_geometry_constraint(self.limb_plane, self.base_handles[1])
        self.controller.create_geometry_constraint(self.limb_plane, self.base_handles[2])


class QuadrupedBackLegIk(Part):

    segment_names = DataProperty(
        name='segment_names',
        default_value=['Hip', 'Knee', 'Ankle', 'Foot', 'Toe']
    )

    hip_handle = ObjectProperty(
        name='hip_handle'
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
    hock_handle = ObjectProperty(
        name='hock_handle'
    )
    foot_handle = ObjectProperty(
        name='foot_handle'
    )
    knee_line = ObjectProperty(
        name='knee_line'
    )

    world_space_foot = DataProperty(
        name='world_space_foot',
        default_value=True
    )

    pole_distance_multiplier = DataProperty(
        name='pole_distance_multiplier',
        default_value=0.5
    )

    stretchable_attr_object = ObjectProperty(
        name='stretchable_attr_object'
    )

    def __init__(self, **kwargs):
        super(QuadrupedBackLegIk, self).__init__(**kwargs)

    @classmethod
    def create(cls, **kwargs):
        matrix_count = len(kwargs.get('matrices', []))
        if matrix_count != 9:
            raise Exception('you must provide exactly 9 matrices to create a %s (Not %s)' % (cls.__name__, matrix_count))
        if 'side' not in kwargs:
            raise Exception('you must provide a "side" keyword argument to create a %s' % cls.__name__)
        this = super(QuadrupedBackLegIk, cls).create(**kwargs)
        return this.build_rig(this, **kwargs)

    @staticmethod
    def build_rig(this, **kwargs):
        controller = this.controller

        # variables

        size = this.size
        side = this.side
        aim_vector = env.side_aim_vectors[side]
        up_vector = env.side_up_vectors[side]

        # positions

        matrices = this.matrices
        thigh_matrix = matrices[0]
        knee_matrix = matrices[1]
        ankle_matrix = matrices[2]
        foot_matrix = matrices[3]
        toe_matrix = matrices[4]
        front_pivot_matrix = matrices[5]
        back_pivot_matrix = matrices[6]
        in_pivot_matrix = matrices[7]
        out_pivot_matrix = matrices[8]
        toe_roll_matrix = Matrix(front_pivot_matrix)
        toe_roll_matrix.set_translation(toe_matrix.get_translation())
        thigh_position = thigh_matrix.get_translation()
        knee_position = knee_matrix.get_translation()
        ankle_position = ankle_matrix.get_translation()
        foot_position = foot_matrix.get_translation()
        thigh_length = (knee_position - thigh_position).mag()
        shin_length = (ankle_position - knee_position).mag()
        ankle_length = (foot_position - ankle_position).mag()
        leg_length = thigh_length + shin_length + ankle_length
        start_length = (foot_position - thigh_position).mag()
        reverse_ankle_vector = (ankle_position - foot_position).normalize()
        ankle_aim_position = foot_position + (reverse_ankle_vector * (leg_length * 1.2))
        foot_side_position = foot_position + Vector([size * 10.0 if side != 'right' else size * -10.0, 0.0, 0.0])

        pole_position = Vector(rmu.calculate_pole_vector_position(
            thigh_position,
            knee_position,
            ankle_position,
            distance=leg_length * this.pole_distance_multiplier
        ))
        reverse_ankle_matrix = compose_matrix(
            foot_position,
            ankle_position,
            pole_position
        )
        if side == 'right':
            reverse_ankle_matrix.flip_y()
            reverse_ankle_matrix.flip_z()

        hip_matrix = compose_matrix(
            thigh_position,
            foot_position,
            pole_position
        )
        thigh_up_position = list(copy.copy(thigh_position))
        thigh_up_position[1] = thigh_up_position[1] + (size * 5)

        #  objects

        root = this.get_root()

        hip_handle = this.create_handle(  # user input for the foot
            handle_type=LocalHandle,
            segment_name='Hip',
            size=size,
            matrix=thigh_matrix,
            shape='cube'
        )
        foot_handle = this.create_handle(  # user input for the foot
            handle_type=WorldHandle,
            segment_name='Foot',
            size=size * 1.5,
            matrix=Matrix(*foot_position) if this.world_space_foot else foot_matrix,
            shape='cube_foot' if this.world_space_foot else 'cube'
        )

        foot_side_transform = foot_handle.create_child(
            Transform,
            segment_name='FootUpTarget',
            matrix=foot_side_position,
        )

        hip_static_transform = hip_handle.create_child(  # positioned at , remains static
            Transform,
            segment_name='HipStatic',
            matrix=hip_matrix,
        )

        hip_aim_transform = hip_handle.create_child(  # Positioned at thigh, aims at foot
            Transform,
            segment_name='HipAim',
            matrix=hip_matrix,
        )

        solver_plane_transform = this.create_child(  # represents the plane of action for the leg
            Transform,
            segment_name='SolverPlane',
            matrix=Matrix(ankle_position),
        )

        ball_pivot = this.create_child(
            Transform,
            segment_name='BallPivot',
            side=side,
            matrix=Matrix(foot_matrix.get_translation()),
            parent=foot_handle.gimbal_handle
        )
        heel_pivot = this.create_child(
            Transform,
            segment_name='HeelPivot',
            side=side,
            matrix=Matrix(back_pivot_matrix.get_translation()),
            parent=ball_pivot
        )
        foot_roll_offset_group = this.create_child(
            Transform,
            segment_name='FootRollOffset',
            side=side,
            parent=heel_pivot,
        )
        rock_in_group_zero = foot_roll_offset_group.create_child(
            Transform,
            segment_name='RockInZero',
            side=side,
            matrix=in_pivot_matrix
        )
        rock_in_group = rock_in_group_zero.create_child(
            Transform,
            segment_name='RockIn',
            side=side,
            matrix=in_pivot_matrix
        )
        rock_out_group_zero = rock_in_group.create_child(
            Transform,
            segment_name='RockOutZero',
            side=side,
            matrix=out_pivot_matrix,
        )
        rock_out_group = rock_out_group_zero.create_child(
            Transform,
            segment_name='RockOut',
            side=side,
            matrix=out_pivot_matrix,
        )
        roll_front_zero = rock_out_group.create_child(
            Transform,
            segment_name='RockFrontZero',
            side=side,
            matrix=front_pivot_matrix,
        )
        roll_front = roll_front_zero.create_child(
            Transform,
            segment_name='RockFront',
            side=side,
            matrix=front_pivot_matrix,
        )
        toe_roll_group_zero = roll_front.create_child(
            Transform,
            segment_name='ToeRollZero',
            side=side,
            matrix=toe_roll_matrix,
        )
        toe_roll_group = toe_roll_group_zero.create_child(
            Transform,
            segment_name='ToeRoll',
            side=side,
            matrix=toe_roll_matrix,
        )
        roll_back_zero = toe_roll_group.create_child(
            Transform,
            segment_name='RockBackZero',
            side=side,
            matrix=back_pivot_matrix,
            parent=toe_roll_group
        )
        roll_back = roll_back_zero.create_child(
            Transform,
            segment_name='RockBack',
            side=side,
            matrix=back_pivot_matrix,
        )
        bend_top = this.create_child(
            Transform,
            segment_name='ToeBendZero',
            side=side,
            matrix=foot_matrix,
            parent=roll_back
        )
        ball_roll_group = this.create_child(
            Transform,
            segment_name='BallRollOrient',
            side=side,
            matrix=foot_matrix,
            parent=roll_back
        )
        ball_roll = ball_roll_group.create_child(
            Transform,
            segment_name='BallRoll',
            matrix=foot_matrix,
        )
        ankle_position_transform = ball_roll.create_child(
            Transform,
            segment_name='AnklePosition',
            matrix=ankle_matrix,
        )

        knee_handle = this.create_handle(
            handle_type=WorldHandle,
            segment_name='Knee',
            size=size,
            side=side,
            matrix=Matrix(*pole_position),
            shape='diamond',
            create_gimbal=False
        )

        hock_handle = this.create_handle(
            handle_type=WorldHandle,
            segment_name='Hock',
            size=size,
            side=side,
            matrix=reverse_ankle_matrix,
            shape='arrow_curved_double',
            axis='z'
        )

        hock_shape_matrix = Matrix()
        hock_shape_matrix.set_translation([size * -0.75 if side != 'right' else size * 0.75, 0, 0])
        hock_shape_matrix.set_scale([size * 2.0 if side != 'right' else size * -2.0, size * 2.0, size * 2.0])
        hock_handle.set_shape_matrix(hock_shape_matrix)

        controller.create_point_constraint(
            ball_roll,
            hock_handle.groups[0]
        )

        hock_auto_tilt_transform = hip_aim_transform.create_child(
            Transform,
            segment_name='HockAutoTilt',
            matrix=Matrix(ankle_aim_position)
        )

        hock_no_tilt_transform = foot_handle.create_child(
            Transform,
            segment_name='HockNoTilt',
            matrix=Matrix(ankle_aim_position)
        )

        hock_aim_target = foot_handle.create_child(
            Transform,
            segment_name='HockAimTarget',
            matrix=Matrix(ankle_aim_position)
        )

        hock_transform = hock_handle.gimbal_handle.create_child(
            Transform,
            segment_name='Hock',
            matrix=Matrix(ankle_matrix)
        )

        hock_reverse = this.create_child(
            DependNode,
            node_type='reverse',
            segment_name='Hock',
        )
        hock_blend_colors = this.create_child(
            DependNode,
            node_type='blendColors',
            segment_name='HockUp',
        )

        hock_remap_node = this.create_child(
            DependNode,
            node_type='remapValue',
            segment_name='Hock',
        )

        toe_ball_remap = this.create_child(
            DependNode,
            node_type='remapValue',
            segment_name='BallRoll',
        )

        distance_node = this.create_child(
            DependNode,
            node_type='distanceBetween',
            segment_name='Hock',
        )
        # create distance node for ankle and limbs to calculate the total length
        hockstretch_transform = foot_handle.gimbal_handle.create_child(
            Transform,
            segment_name='HockStretch',
            matrix=Matrix(ankle_matrix)
        )

        distanceankle_node = this.create_child(
            DependNode,
            node_type='distanceBetween',
            segment_name='Ankle',
        )
        sumlimblength_node = this.create_child(
            DependNode,
            node_type='plusMinusAverage',
            segment_name='Limblength',
        )



        heel_roll_remap = this.create_child(
            DependNode,
            node_type='remapValue',
            segment_name='HeelRoll',
        )
        rock_in_remap = this.create_child(
            DependNode,
            node_type='remapValue',
            segment_name='RockIn',
        )
        rock_out_remap = this.create_child(
            DependNode,
            node_type='remapValue',
            segment_name='RockOut',
        )
        pivot_multiply = this.create_child(
            DependNode,
            node_type='multiplyDivide',
            segment_name='Pivots',
        )

        hock_scale_multiply = this.create_child(
            DependNode,
            node_type='multiplyDivide',
            segment_name='HockScale'
        )

        joints = []
        joint_parent = this.joint_group
        for i, segment_name in enumerate(this.segment_names):
            joint = this.create_child(
                Joint,
                segment_name=segment_name,
                parent=joint_parent,
                matrix=matrices[i],
            )
            joint.zero_rotation()
            root.add_plugs(
                joint.plugs['rx'],
                joint.plugs['ry'],
                joint.plugs['rz']
            )
            joints.append(joint)
            joint_parent = joint

        hip_jnt, knee_jnt, ankle_jnt, foot_jnt, toe_jnt = joints

        controller.create_point_constraint(
            hip_handle,
            hip_jnt,
            mo=False
        )
        ankle_ik_solver = controller.create_ik_handle(
            hip_jnt,
            ankle_jnt,
            parent=hock_transform,
            solver='ikRPsolver'
        )
        controller.create_pole_vector_constraint(
            knee_handle,
            ankle_ik_solver
        )

        hock_ik_solver = controller.create_ik_handle(
            ankle_jnt,
            foot_jnt,
            parent=ball_roll,
            solver='ikSCsolver'
        )

        foot_ik_solver = controller.create_ik_handle(
            foot_jnt,
            toe_jnt,
            parent=ball_roll,
            solver='ikSCsolver'
        )

        ankle_ik_solver.plugs['visibility'].set_value(False)
        hock_ik_solver.plugs['visibility'].set_value(False)
        foot_ik_solver.plugs['visibility'].set_value(False)

        controller.create_aim_constraint(
            hock_aim_target,
            hock_handle.groups[0],
            worldUpType='object',
            worldUpObject=foot_side_transform,
            aimVector=aim_vector,
            upVector=up_vector

        )

        this.controller.create_aim_constraint(
            solver_plane_transform,
            hip_aim_transform,
            worldUpType='object',
            worldUpObject=knee_handle,
            aimVector=[0.0, 1.0, 0.0],
            upVector=[0.0, 0.0, -1.0],
            mo=False
        )

        controller.create_orient_constraint(
            foot_handle,
            solver_plane_transform,
            skip=('x', 'z'),
        )

        controller.create_point_constraint(
            hip_static_transform,
            foot_handle,
            solver_plane_transform,
            mo=False
        )

        controller.create_parent_constraint(
            solver_plane_transform,
            knee_handle.groups[0],
            mo=True
        )

        hock_target_point_constraint = controller.create_point_constraint(
            hock_auto_tilt_transform,
            hock_no_tilt_transform,
            hock_aim_target
        )

        #  stretchy
        limb_utilities.convert_ik_to_stretchable_two_segments(
            part=this,
            start_ctrl=hip_static_transform,
            pv_ctrl=knee_handle,
            end_ctrl=foot_handle,
            ikh=ankle_ik_solver,
            joints=[hip_jnt, knee_jnt, ankle_jnt],
            global_scale_plug=this.scale_multiply_transform.plugs['sy'],
            lock_plug_name='lockKnee',
            stretchMode='translate'
        )

        #  foot roll plugs
        foot_roll_plug = foot_handle.create_plug(
            'footRoll',
            at='double',
            k=True,
            dv=0.0,
        )
        break_plug = foot_handle.create_plug(
            'Break',
            at='double',
            k=True,
            dv=45.0,
            min=0.0
        )
        ball_pivot_plug = foot_handle.create_plug(
            'FootPivot',
            at='double',
            k=True,
            dv=0.0,
        )
        heel_pivot_plug = foot_handle.create_plug(
            'HeelPivot',
            at='double',
            k=True,
            dv=0.0,
        )
        toe_pivot_plug = foot_handle.create_plug(
            'ToePivot',
            at='double',
            k=True,
            dv=0.0
        )
        rock_plug = foot_handle.create_plug(
            'Rock',
            at='double',
            k=True,
            dv=0.0
        )

        auto_ankle_plug = foot_handle.create_plug(
            'AutoAnkle',
            at='double',
            k=True,
            dv=1.0,
            min=0.0,
            max=1.0
        )

        auto_ankle_plug.connect_to(hock_target_point_constraint.plugs['%sW0' % hock_auto_tilt_transform])
        auto_ankle_plug.connect_to(hock_reverse.plugs['inputX'])
        hock_reverse.plugs['outputX'].connect_to(hock_target_point_constraint.plugs['%sW1' % hock_no_tilt_transform])
        hock_blend_colors.plugs['color1R'].set_value(0.0)  # Default color1 value is [1.0, 0.0, 0.0]
        hock_blend_colors.plugs['color2'].set_value(hock_auto_tilt_transform.plugs['translate'].get_value())
        hock_blend_colors.plugs['output'].connect_to(hock_auto_tilt_transform.plugs['translate'])
        hip_static_transform.plugs['worldMatrix'].element(0).connect_to(
            distance_node.plugs['inMatrix1']
        )
        foot_handle.plugs['worldMatrix'].element(0).connect_to(
            distance_node.plugs['inMatrix2']
        )
        distance_node.plugs['distance'].connect_to(
            hock_scale_multiply.plugs['input1X']
        )


        # distance between for ankle length
        hockstretch_transform.plugs['worldMatrix'].element(0).connect_to(
            distanceankle_node.plugs['inMatrix1']
        )
        foot_handle.plugs['worldMatrix'].element(0).connect_to(
            distanceankle_node.plugs['inMatrix2']
        )
        # total limb length
        joint_lengths = [j.plugs['t{0}'.format(env.aim_vector_axis)].get_value() for j in joints[1:3]]
        default_total_length = abs(sum(joint_lengths))
        sumlimblength_node.plugs['input1D'].element(0).set_value(default_total_length)
        distanceankle_node.plugs['distance'].connect_to(sumlimblength_node.plugs['input1D'].element(1))


        # connect the sum to stretch scale multiplyDivide node from limb utils

        this.scale_multiply_transform.plugs['scaleZ'].connect_to(hock_scale_multiply.plugs['input2X'])
        hock_scale_multiply.plugs['operation'].set_value(2)
        hock_scale_multiply.plugs['outputX'].connect_to(
            hock_remap_node.plugs['inputValue']
        )

        hock_remap_node.plugs['value'].element(0).child(0).set_value(start_length)
        hock_remap_node.plugs['value'].element(0).child(1).set_value(0.0)
        hock_remap_node.plugs['value'].element(1).child(0).set_value(leg_length)
        hock_remap_node.plugs['value'].element(1).child(1).set_value(1.0)
        hock_remap_node.plugs['outValue'].connect_to(hock_blend_colors.plugs['blender'])

        # Toe Tip Roll
        toe_roll_pma = this.create_child(
            DependNode,
            node_type='plusMinusAverage',
            segment_name='ToeRoll',
        )
        toe_roll_value_cond = this.create_child(
            DependNode,
            node_type='condition',
            segment_name='ToeRollValue',
        )

        # Toe Roll node creation (for IK toes)
        foot_roll_plug.connect_to(toe_roll_pma.plugs['input1D'].element(0))
        break_plug.connect_to(toe_roll_pma.plugs['input1D'].element(1))
        toe_roll_pma.plugs['operation'].set_value(2)
        toe_roll_pma.plugs['output1D'].connect_to(toe_roll_value_cond.plugs['colorIfFalseR'])
        foot_roll_plug.connect_to(toe_roll_value_cond.plugs['secondTerm'])
        break_plug.connect_to(toe_roll_value_cond.plugs['firstTerm'])
        toe_roll_value_cond.plugs['operation'].set_value(3)
        toe_roll_value_cond.plugs['outColorR'].connect_to(roll_front.plugs['rotateX'])


        # Toe Roll
        foot_roll_plug.connect_to(toe_ball_remap.plugs['inputValue'])
        toe_ball_remap.plugs['value'].element(0).child(0).set_value(0.0)
        toe_ball_remap.plugs['value'].element(0).child(1).set_value(0.0)
        break_plug.connect_to(toe_ball_remap.plugs['value'].element(1).child(0))
        break_plug.connect_to(toe_ball_remap.plugs['value'].element(1).child(1))
        toe_ball_remap.plugs['outValue'].connect_to(toe_roll_group.plugs['rotateX'])

        # Heel Roll
        foot_roll_plug.connect_to(heel_roll_remap.plugs['inputValue'])
        heel_roll_remap.plugs['value'].element(0).child(0).set_value(0.0)
        heel_roll_remap.plugs['value'].element(0).child(1).set_value(0.0)
        heel_roll_remap.plugs['value'].element(1).child(0).set_value(-100.0)
        heel_roll_remap.plugs['value'].element(1).child(1).set_value(-100.0)
        heel_roll_remap.plugs['outValue'].connect_to(roll_back.plugs['rotateX'])


        # rock in
        rock_plug.connect_to(rock_in_remap.plugs['inputValue'])
        rock_in_remap.plugs['value'].element(0).child(0).set_value(0.0)
        rock_in_remap.plugs['value'].element(0).child(1).set_value(0.0)
        rock_in_remap.plugs['value'].element(1).child(0).set_value(-100)
        rock_in_remap.plugs['value'].element(1).child(1).set_value(100)
        rock_in_remap.plugs['outValue'].connect_to(rock_in_group.plugs['rotateZ'])

        # rock out
        rock_plug.connect_to(rock_out_remap.plugs['inputValue'])
        rock_out_remap.plugs['value'].element(0).child(0).set_value(0.0)
        rock_out_remap.plugs['value'].element(0).child(1).set_value(0.0)
        rock_out_remap.plugs['value'].element(1).child(0).set_value(100.0)
        rock_out_remap.plugs['value'].element(1).child(1).set_value(-100.0)
        rock_out_remap.plugs['outValue'].connect_to(rock_out_group.plugs['rotateZ'])

        # pivots
        if side == 'right':
            pivot_multiply.plugs['input2'].set_value([-1.0, -1.0, -1.0])
        else:
            pivot_multiply.plugs['input2'].set_value([1.0, 1.0, 1.0])
        ball_pivot_plug.connect_to(pivot_multiply.plugs['input1X'])
        toe_pivot_plug.connect_to(pivot_multiply.plugs['input1Y'])
        heel_pivot_plug.connect_to(pivot_multiply.plugs['input1Z'])
        pivot_multiply.plugs['outputX'].connect_to(ball_pivot.plugs['rotateY'])
        pivot_multiply.plugs['outputY'].connect_to(roll_front.plugs['rotateY'])
        pivot_multiply.plugs['outputZ'].connect_to(heel_pivot.plugs['rotateY'])
        ankle_ik_solver.plugs['visibility'].set_value(0)

        locator_1 = knee_jnt.create_child(
            Locator,
            segment_name='LineStart'
        )
        locator_2 = knee_handle.create_child(
            Locator,
            segment_name='LineEnd'
        )
        locator_1.plugs['visibility'].set_value(False)
        locator_2.plugs['visibility'].set_value(False)
        this.knee_line = this.create_child(Line)
        locator_1.plugs['worldPosition'].element(0).connect_to(this.knee_line.curve.plugs['controlPoints'].element(0))
        locator_2.plugs['worldPosition'].element(0).connect_to(this.knee_line.curve.plugs['controlPoints'].element(1))

        # keep foot_end (toe) in place when foot rolls
        toe_no_roll_clamp = this.create_child(
            DependNode,
            node_type='clamp',
            segment_name='ToeNoRoll',
        )
        foot_roll_plug.connect_to(toe_no_roll_clamp.plugs['inputR'])
        break_plug.connect_to(toe_no_roll_clamp.plugs['maxR'])
        toe_no_roll_negate = toe_no_roll_clamp.plugs['outputR'].multiply(-1.0)
        toe_no_roll_negate.connect_to(joints[4].plugs['rotateX'])

        # adding visibility plugs
        root.add_plugs(
            [
                foot_handle.plugs['tx'],
                foot_handle.plugs['ty'],
                foot_handle.plugs['tz'],
                foot_handle.plugs['rx'],
                foot_handle.plugs['ry'],
                foot_handle.plugs['rz'],
                foot_handle.plugs['sx'],
                foot_handle.plugs['sy'],
                foot_handle.plugs['sz'],
                hock_handle.plugs['rx'],
                hock_handle.plugs['ry'],
                hock_handle.plugs['rz'],
                knee_handle.plugs['tx'],
                knee_handle.plugs['ty'],
                knee_handle.plugs['tz'],
                hip_handle.plugs['tx'],
                hip_handle.plugs['ty'],
                hip_handle.plugs['tz'],
                rock_plug,
                auto_ankle_plug,
                break_plug,
                foot_roll_plug,
                heel_pivot_plug,
                ball_pivot_plug,
                toe_pivot_plug
            ]
        )

        this.joints = joints
        this.hip_handle = hip_handle
        this.hock_handle = hock_handle
        this.foot_handle = foot_handle
        return this
