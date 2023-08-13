import copy
from Snowman3.rigger.rig_factory.objects.part_objects.chain_guide import ChainGuide
from Snowman3.rigger.rig_factory.objects.part_objects.part import Part
from Snowman3.rigger.rig_factory.objects.rig_objects.cone import Cone
from Snowman3.rigger.rig_factory.objects.rig_objects.line import Line
from Snowman3.rigger.rig_factory.objects.node_objects.transform import Transform
from Snowman3.rigger.rig_factory.objects.node_objects.joint import Joint
from Snowman3.rigger.rig_factory.objects.node_objects.locator import Locator
from Snowman3.rigger.rig_factory.objects.node_objects.depend_node import DependNode
from Snowman3.rigger.rig_factory.objects.rig_objects.grouped_handle import LocalHandle, WorldHandle
from Snowman3.rigger.rig_factory.objects.rig_objects.reverse_pole_vector import ReversePoleVector
import Snowman3.rigger.rig_factory.environment as env
import Snowman3.rigger.rig_math.utilities as rmu
from Snowman3.rigger.rig_factory.utilities import face_panel_utilities as utl
from Snowman3.rigger.rig_factory.objects.base_objects.properties import ObjectProperty, ObjectListProperty, DataProperty
from Snowman3.rigger.rig_math.matrix import Matrix
from Snowman3.rigger.rig_math.vector import Vector
import Snowman3.rigger.rig_factory.positions as pos
import Snowman3.rigger.rig_factory.utilities.limb_utilities as limb_utilities


class BipedLegIkGuide(ChainGuide):

    default_settings = dict(
        root_name='Leg',
        size=1.0,
        side='left',
        master_foot=False,
        world_space_foot=True,
        pole_distance_multiplier=1.0
    )

    pivot_joints = ObjectListProperty(
        name='pivot_joints'
    )

    segment_names = DataProperty(
        name='segment_names',
        default_value=['Hip', 'Knee', 'Foot', 'Toe', 'ToeTip']
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

    limb_plane = ObjectProperty(
        name='limb_plane'
    )

    def __init__(self, **kwargs):
        super(BipedLegIkGuide, self).__init__(**kwargs)
        self.toggle_class = BipedLegIk.__name__

    @classmethod
    def create(cls, **kwargs):
        kwargs['count'] = 5
        kwargs['up_vector_indices'] = [0, 2]
        kwargs.setdefault('root_name', 'Leg')
        this = super(BipedLegIkGuide, cls).create(**kwargs)
        cls.build_rig(this)
        return this

    @staticmethod
    def build_rig(this):
        controller = this.controller
        body = this.get_root()
        size = this.size
        side = this.side
        size_plug = this.plugs['size']
        size_multiply_node = this.create_child('DependNode', node_type='multiplyDivide')
        size_plug.connect_to(size_multiply_node.plugs['input1X'])
        size_multiply_node.plugs['input2X'].set_value(0.5)
        size_multiply_plug = size_multiply_node.plugs['outputX']
        pivot_handles = []
        pivot_joints = []
        master_joint = []
        root = this.get_root()

        if this.master_foot:

            master_guide = this.create_handle(
                segment_name='MasterFoot',
                side=this.side
            )

            master_guide_jnt = master_guide.create_child(
                Joint,
                segment_name='MasterFoot',
                side=this.side
            )

            cone_x = master_guide_jnt.create_child(
                Cone,
                segment_name='%sConeX' % 'MasterFoot',
                functionality_name='Pivot',
                size=size * 0.1,
                axis=[1.0, 0.0, 0.0]
            )
            cone_y = master_guide_jnt.create_child(
                Cone,
                segment_name='%sConeY' % 'MasterFoot',
                functionality_name='Pivot',
                size=size * 0.099,
                axis=[0.0, 1.0, 0.0]
            )
            cone_z = master_guide_jnt.create_child(
                Cone,
                segment_name='%sConeZ' % 'MasterFoot',
                functionality_name='Pivot',
                size=size * 0.098,
                axis=[0.0, 0.0, 1.0]
            )
            master_joint.append(master_guide_jnt)

            cone_x.mesh.assign_shading_group(body.shaders['x'].shading_group)
            cone_y.mesh.assign_shading_group(body.shaders['y'].shading_group)
            cone_z.mesh.assign_shading_group(body.shaders['z'].shading_group)
            master_guide.plugs['translateX'].set_value(7.5)
            master_guide.plugs['translateZ'].set_value(25.0)
            size_multiply_node.plugs['outputX'].connect_to(master_guide.plugs['size'])
            master_guide.plugs['radius'].set_value(size * 0.5)
            master_guide.mesh.assign_shading_group(root.shaders[this.side].shading_group)
        else:
            pass

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
                functionality_name='Pivot',
                size=size * 0.1,
                axis=[1.0, 0.0, 0.0]
            )
            cone_y = joint.create_child(
                Cone,
                segment_name='%sConeY' % pivot_segment_name,
                functionality_name='Pivot',
                size=size * 0.099,
                axis=[0.0, 1.0, 0.0]
            )
            cone_z = joint.create_child(
                Cone,
                segment_name='%sConeZ' % pivot_segment_name,
                functionality_name='Pivot',
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
        pivot_joints = pivot_joints + master_joint
        controller.create_aim_constraint(front_handle, back_joint, aim=[0, 0, 1])
        controller.create_aim_constraint(back_handle, front_joint, aim=[0, 0, -1])
        controller.create_aim_constraint(in_handle, out_joint, aim=[-1, 0, 0], worldUpType="scene", upVector=[0, 1, 0])
        controller.create_aim_constraint(out_handle, in_joint, aim=[1, 0, 0], worldUpType="scene", upVector=[0, 1, 0])
        this.pivot_joints = pivot_joints
        this.set_handle_positions(pos.BIPED_POSITIONS)
        limb_utilities.make_ik_plane(this, this.base_handles[0], this.base_handles[2], this.up_handles[0])

        if this.master_foot:
            controller.create_aim_constraint(
                this.base_handles[-1],
                master_joint,
                aim=[0, 0, -1],
                worldUpType='scene',
                upVector=[0, 1, 0],
                maintainOffset=True
            )

        return this

    def get_toggle_blueprint(self):
        blueprint = super(BipedLegIkGuide, self).get_toggle_blueprint()
        matrices = [list(x.get_matrix()) for x in self.joints]
        matrices.extend([list(x.get_matrix()) for x in self.pivot_joints])
        blueprint['matrices'] = matrices
        return blueprint

    def post_create(self, **kwargs):
        super(BipedLegIkGuide, self).post_create(**kwargs)

        # geometry constrain elbow
        self.controller.create_geometry_constraint(self.limb_plane, self.base_handles[1])


class BipedLegIk(Part):

    ankle_handle = ObjectProperty(
        name='ankle_handle'
    )
    knee_handle = ObjectProperty(
        name='knee_handle'
    )
    toe_handle = ObjectProperty(
        name='toe_handle'
    )
    knee_line = ObjectProperty(
        name='knee_line'
    )
    ik_joints = ObjectListProperty(
        name='ik_joints'
    )
    segment_names = DataProperty(
        name='segment_names',
        default_value=['Hip', 'Knee', 'Foot', 'Toe', 'ToeTip']
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

    def __init__(self, **kwargs):
        super(BipedLegIk, self).__init__(**kwargs)

    @classmethod
    def create(cls, **kwargs):
        if 'side' not in kwargs:
            raise Exception('you must provide a "side" keyword argument to create a %s' % cls.__name__)
        this = super(BipedLegIk, cls).create(**kwargs)
        cls.build_rig(this)
        return this

    @staticmethod
    def build_rig(this):
        controller = this.controller
        size = this.size
        side = this.side
        matrices = this.matrices
        utility_group = this.utility_group
        hip_matrix = matrices[0]
        knee_matrix = matrices[1]
        ankle_matrix = matrices[2]
        foot_matrix = matrices[3]
        toe_matrix = matrices[4]
        front_pivot_matrix = matrices[5]
        back_pivot_matrix = matrices[6]
        in_pivot_matrix = matrices[7]
        out_pivot_matrix = matrices[8]
        root = this.get_root()
        ik_joints = []
        joints = []
        joint_parent = this.joint_group
        ik_joint_parent = this.joint_group

        for i, segment_name in enumerate(this.segment_names):
            if i != 0:
                joint_parent = joints[-1]
                ik_joint_parent = ik_joints[-1]
            ik_joint = this.create_child(
                Joint,
                segment_name='%sKinematic' % segment_name,
                parent=ik_joint_parent,
                matrix=matrices[i],
            )
            ik_joint.zero_rotation()
            ik_joints.append(ik_joint)
            joint = this.create_child(
                Joint,
                segment_name=segment_name,
                parent=joint_parent,
                matrix=matrices[i],
            )
            joint.zero_rotation()
            joints.append(joint)
            ik_joint.plugs['v'].set_value(False)
            root.add_plugs(
                ik_joint.plugs['rx'],
                ik_joint.plugs['ry'],
                ik_joint.plugs['rz'],
                keyable=False
            )
            ik_joint.plugs['scale'].connect_to(joint.plugs['scale'])

        hip_transform = this.create_child(
            Transform,
            segment_name='Hip',
            matrix=Matrix(*hip_matrix.get_translation()),
        )
        hip_transform.plugs['visibility'].set_value(False)

        controller.create_point_constraint(
            hip_transform,
            ik_joints[0]
        )

        if this.world_space_foot:
            ankle_ctrl_matrix = Matrix(*ankle_matrix.get_translation())
        else:
            ankle_ctrl_matrix = ankle_matrix.aimed_towards_axis('y', aim_axis='y', up_axis='z', up_matrix=foot_matrix)
        ankle_handle = this.create_handle(
            handle_type=WorldHandle,
            segment_name=this.segment_names[2].title(),
            size=size,
            side=side,
            matrix=ankle_ctrl_matrix,
            shape='cube_foot',
            rotation_order='xzy',
        )
        pole_position = rmu.calculate_pole_vector_position(
            hip_matrix.get_translation(),
            knee_matrix.get_translation(),
            ankle_matrix.get_translation(),
            distance=((size * 0.1) + 1.0) * 50 * this.pole_distance_multiplier
        )

        ankle_pole_transform = this.create_child(
            Transform,
            segment_name='AnklePole',
            matrix=ankle_matrix,
        )

        controller.create_orient_constraint(
            ankle_handle,
            ankle_pole_transform,
            skip=('x', 'z'),
        )

        controller.create_point_constraint(
            hip_transform,
            ankle_handle,
            ankle_pole_transform
        )

        knee_handle = this.create_handle(
            segment_name='Knee',
            size=size*0.5,
            side=side,
            matrix=Matrix(*pole_position),
            shape='ball',
            create_gimbal=False
        )
        locator_1 = joints[1].create_child(
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

        ball_pivot = this.create_child(
            Transform,
            segment_name='BallPivot',
            matrix=Matrix(ankle_ctrl_matrix).set_translation(foot_matrix.get_translation()),
            parent=ankle_handle.gimbal_handle
        )
        heel_pivot = this.create_child(
            Transform,
            segment_name='HeelPivot',
            side=side,
            matrix=Matrix(ankle_ctrl_matrix).set_translation(back_pivot_matrix.get_translation()),
            parent=ball_pivot
        )
        toe_pivot = this.create_child(
            Transform,
            segment_name='ToePivot',
            side=side,
            matrix=Matrix(ankle_ctrl_matrix).set_translation(toe_matrix.get_translation()),
            parent=heel_pivot
        )
        foot_roll_offset_group = this.create_child(
            Transform,
            segment_name='FootRollOffset',
            side=side,
            parent=toe_pivot,
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
        rock_front_zero = rock_out_group.create_child(
            Transform,
            segment_name='RockFrontZero',
            side=side,
            matrix=front_pivot_matrix,
        )
        rock_front = rock_front_zero.create_child(
            Transform,
            segment_name='RockFront',
            side=side,
            matrix=front_pivot_matrix,
        )
        toe_end_grp = rock_front.create_child(
            Transform,
            segment_name='ToeEndRoll',
            side=side,
            matrix=front_pivot_matrix
        )
        roll_back_zero = toe_end_grp.create_child(
            Transform,
            segment_name='RockBackZero',
            side=side,
            matrix=back_pivot_matrix
        )
        roll_back = roll_back_zero.create_child(
            Transform,
            segment_name='RockBack',
            side=side,
            matrix=back_pivot_matrix
        )
        heel_roll_grp = roll_back.create_child(
            Transform,
            segment_name='HeelRoll',
            side=side,
            matrix=back_pivot_matrix
        )
        bend_top = heel_roll_grp.create_child(
            Transform,
            segment_name='ToeBendZero',
            side=side,
            matrix=foot_matrix
        )
        toe_rotate = this.create_child(
            Transform,
            segment_name='ToeRotate',
            side=side,
            matrix=toe_matrix,
            parent=bend_top
        )
        ball_roll_group = heel_roll_grp.create_child(
            Transform,
            segment_name='BallRollOrient',
            side=side,
            matrix=foot_matrix
        )
        heel_raise_grp = ball_roll_group.create_child(
            Transform,
            segment_name='HeelRaise',
            matrix=foot_matrix,
        )
        ball_roll = heel_raise_grp.create_child(
            Transform,
            segment_name='BallRoll',
            matrix=foot_matrix,
        )
        ankle_position_transform = ball_roll.create_child(
            Transform,
            segment_name='AnklePosition',
            matrix=ankle_matrix,
        )
        ankle_position_transform.plugs['visibility'].set_value(False)

        foot_roll_plug = ankle_handle.create_plug(
            'footRoll',
            at='double',
            k=True,
            dv=0.0,
        )
        break_plug = ankle_handle.create_plug(
            'break',
            at='double',
            k=True,
            dv=45.0,
            min=0.0
        )
        toe_end_roll_plug = ankle_handle.create_plug(
            'toeEndRoll',
            at='double',
            k=True,
            dv=0.0
        )
        heel_raise_plug = ankle_handle.create_plug(
            'heelRaise',
            at='double',
            k=True,
            dv=0.0
        )
        heel_roll_plug = ankle_handle.create_plug(
            'heelRoll',
            at='double',
            k=True,
            dv=0.0
        )
        toe_pivot_plug = ankle_handle.create_plug(
            'toePivot',
            at='double',
            k=True,
            dv=0.0,
        )
        toe_rotate_plug = ankle_handle.create_plug(
            'toeRotate',
            at='double',
            k=True,
            dv=0.0,
        )
        ball_pivot_plug = ankle_handle.create_plug(
            'ballPivot',
            at='double',
            k=True,
            dv=0.0,
        )
        heel_pivot_plug = ankle_handle.create_plug(
            'heelPivot',
            at='double',
            k=True,
            dv=0.0,
        )
        rock_plug = ankle_handle.create_plug(
            'rock',
            at='double',
            k=True,
            dv=0.0
        )
        ankle_wiggle_plug = ankle_handle.create_plug(
            'ankleWiggle',
            at='double',
            k=True,
            dv=0.0
        )

        # Front Roll
        toe_tip_remap = this.create_child(
            DependNode,
            node_type='remapValue',
            segment_name='RollTip'
        )
        break_plug.connect_to(toe_tip_remap.plugs['value'].element(0).child(0))
        toe_tip_remap.plugs['value'].element(0).child(1).set_value(0.0)
        toe_tip_remap.plugs['value'].element(1).child(0).set_value(245.0)
        toe_tip_remap.plugs['value'].element(1).child(1).set_value(200.0)
        toe_tip_remap.plugs['outValue'].connect_to(rock_front.plugs['rotateX'])

        # Toe end roll
        toe_end_roll_plug.connect_to(toe_end_grp.plugs['rotateX'])

        # Toe rotation
        toe_rotate_plug.connect_to(toe_rotate.plugs['rotateX'])

        # Heel Roll
        heel_roll_plug.connect_to(heel_roll_grp.plugs['rotateX'])

        # Heel Raise
        heel_raise_plug.connect_to(heel_raise_grp.plugs['rotateX'])

        # Ankle Wiggle
        ankle_wiggle_plug.connect_to(ball_roll.plugs['rotateY'])

        # Ball Roll
        toe_ball_remap = this.create_child(
            DependNode,
            node_type='remapValue',
            segment_name='BallRoll'
        )
        toe_ball_remap.plugs['value'].element(0).child(0).set_value(0.0)
        toe_ball_remap.plugs['value'].element(0).child(1).set_value(0.0)
        break_plug.connect_to(toe_ball_remap.plugs['value'].element(1).child(0))
        break_plug.connect_to(toe_ball_remap.plugs['value'].element(1).child(1))
        toe_ball_remap.plugs['outValue'].connect_to(ball_roll.plugs['rotateX'])

        # Heel Roll
        heel_roll_remap = this.create_child(
            DependNode,
            node_type='remapValue',
            segment_name='HeelRoll'
        )
        heel_roll_remap.plugs['value'].element(0).child(0).set_value(0.0)
        heel_roll_remap.plugs['value'].element(0).child(1).set_value(0.0)
        heel_roll_remap.plugs['value'].element(1).child(0).set_value(-100.0)
        heel_roll_remap.plugs['value'].element(1).child(1).set_value(-100.0)
        heel_roll_remap.plugs['outValue'].connect_to(roll_back.plugs['rotateX'])

        # rock in
        rock_in_remap = this.create_child(
            DependNode,
            node_type='remapValue',
            segment_name='RockIn'
        )
        rock_in_remap.plugs['value'].element(0).child(0).set_value(0.0)
        rock_in_remap.plugs['value'].element(0).child(1).set_value(0.0)
        rock_in_remap.plugs['value'].element(1).child(0).set_value(-100)
        rock_in_remap.plugs['value'].element(1).child(1).set_value(100)
        rock_in_remap.plugs['outValue'].connect_to(rock_in_group.plugs['rotateZ'])

        # rock out
        rock_out_remap = this.create_child(
            DependNode,
            node_type='remapValue',
            segment_name='RockOut'
        )
        rock_out_remap.plugs['value'].element(0).child(0).set_value(0.0)
        rock_out_remap.plugs['value'].element(0).child(1).set_value(0.0)
        rock_out_remap.plugs['value'].element(1).child(0).set_value(100.0)
        rock_out_remap.plugs['value'].element(1).child(1).set_value(-100.0)
        rock_out_remap.plugs['outValue'].connect_to(rock_out_group.plugs['rotateZ'])

        # pivots
        pivot_multiply = this.create_child(
            DependNode,
            node_type='multiplyDivide',
            segment_name='Pivots'
        )

        if this.master_foot:

            master_container = this.create_handle(
                segment_name='MasterContainer',
                shape='square',
                side=this.side,
                size=size * 2,
                matrix=matrices[-1],
                parent=ankle_handle
            )
            master_foot_handle = this.create_handle(
                segment_name='MasterFoot',
                shape='star_four',
                side=this.side,
                size=size,
                matrix=matrices[-1],
                parent=master_container
            )
            master_toe_handle = this.create_handle(
                segment_name='MasterToe',
                shape='arrow_curved_double',
                side=this.side,
                size=size,
                matrix=matrices[-1] * Matrix(0.0,0.0,(size * 0.3)),
                parent=master_foot_handle
            )
            master_toe_handle.groups[0].plugs['rotateY'].set_value(90)
            master_heel_handle = this.create_handle(
                segment_name='MasterHeel',
                shape='arrow_curved_double',
                side=this.side,
                size=size,
                matrix=matrices[-1] * Matrix(0.0,0.0,(size * -0.3)),
                parent=master_foot_handle
            )
            master_heel_handle.groups[0].plugs['rotateY'].set_value(-90)
            if this.side == 'right':
                master_container.groups[0].plugs['rotateY'].set_value(180)
                master_container.groups[0].plugs['rotateX'].set_value(-180)
                master_toe_handle.groups[0].plugs['rotateZ'].set_value(0)
                master_heel_handle.groups[0].plugs['rotateZ'].set_value(0)

            # roll
            roll_toe_adl = this.create_child(
                DependNode,
                node_type='addDoubleLinear',
                segment_name='RollToe'
            )

            roll_ball_adl = this.create_child(
                DependNode,
                node_type='addDoubleLinear',
                segment_name='RollBall'
            )

            roll_heel_adl = this.create_child(
                DependNode,
                node_type='addDoubleLinear',
                segment_name='RollHeel'
            )

            roll_md = this.create_child(
                DependNode,
                node_type='multiplyDivide',
                segment_name='Roll'
            )

            rock_in_adl = this.create_child(
                DependNode,
                node_type='addDoubleLinear',
                segment_name='RockIn'
            )

            rock_out_adl = this.create_child(
                DependNode,
                node_type='addDoubleLinear',
                segment_name='RockOut'
            )

            rock_md = this.create_child(
                DependNode,
                node_type='multiplyDivide',
                segment_name='Rock'
            )

            master_foot_handle.plugs['tx'].connect_to(rock_md.plugs['input1X'])
            rock_md.plugs['input2X'].set_value(60/size)

            master_foot_handle.plugs['tz'].connect_to(roll_md.plugs['input1X'])
            roll_md.plugs['input2X'].set_value(45/size)

            roll_md.plugs['outputX'].connect_to(roll_toe_adl.plugs['input1'])
            roll_md.plugs['outputX'].connect_to(roll_ball_adl.plugs['input1'])
            roll_md.plugs['outputX'].connect_to(roll_heel_adl.plugs['input1'])
            rock_md.plugs['outputX'].connect_to(rock_in_adl.plugs['input1'])
            rock_md.plugs['outputX'].connect_to(rock_out_adl.plugs['input1'])

            foot_roll_plug.connect_to(roll_toe_adl.plugs['input2'])
            foot_roll_plug.connect_to(roll_ball_adl.plugs['input2'])
            foot_roll_plug.connect_to(roll_heel_adl.plugs['input2'])
            rock_plug.connect_to(rock_in_adl.plugs['input2'])
            rock_plug.connect_to(rock_out_adl.plugs['input2'])

            roll_toe_adl.plugs['output'].connect_to(toe_tip_remap.plugs['inputValue'])
            roll_ball_adl.plugs['output'].connect_to(toe_ball_remap.plugs['inputValue'])
            roll_heel_adl.plugs['output'].connect_to(heel_roll_remap.plugs['inputValue'])
            rock_in_adl.plugs['output'].connect_to(rock_in_remap.plugs['inputValue'])
            rock_out_adl.plugs['output'].connect_to(rock_out_remap.plugs['inputValue'])

            # pivots

            ball_piv_adl = this.create_child(
                DependNode,
                node_type='addDoubleLinear',
                segment_name='BallPiv'
            )

            toe_piv_adl = this.create_child(
                DependNode,
                node_type='addDoubleLinear',
                segment_name='ToePiv'
            )

            heel_piv_adl = this.create_child(
                DependNode,
                node_type='addDoubleLinear',
                segment_name='HeelPiv'
            )


            if side == 'right':
                pivot_multiply.plugs['input2'].set_value([-1.0, -1.0, -1.0])
            else:
                pivot_multiply.plugs['input2'].set_value([1.0, 1.0, 1.0])
            ball_pivot_plug.connect_to(ball_piv_adl.plugs['input1'])
            toe_pivot_plug.connect_to(toe_piv_adl.plugs['input1'])
            heel_pivot_plug.connect_to(heel_piv_adl.plugs['input1'])
            master_foot_handle.plugs['ry'].connect_to(ball_piv_adl.plugs['input2'])
            master_toe_handle.plugs['ry'].connect_to(toe_piv_adl.plugs['input2'])
            master_heel_handle.plugs['ry'].connect_to(heel_piv_adl.plugs['input2'])
            ball_piv_adl.plugs['output'].connect_to(pivot_multiply.plugs['input1X'])
            toe_piv_adl.plugs['output'].connect_to(pivot_multiply.plugs['input1Y'])
            heel_piv_adl.plugs['output'].connect_to(pivot_multiply.plugs['input1Z'])
            pivot_multiply.plugs['outputX'].connect_to(ball_pivot.plugs['rotateY'])
            pivot_multiply.plugs['outputY'].connect_to(toe_pivot.plugs['rotateY'])
            pivot_multiply.plugs['outputZ'].connect_to(heel_pivot.plugs['rotateY'])

            root.add_plugs(
                [
                    master_foot_handle.plugs['tx'],
                    master_foot_handle.plugs['tz'],
                    master_foot_handle.plugs['ry'],
                    master_toe_handle.plugs['ry'],
                    master_heel_handle.plugs['ry']
                ]
            )

        else:
            foot_roll_plug.connect_to(toe_tip_remap.plugs['inputValue'])
            foot_roll_plug.connect_to(toe_ball_remap.plugs['inputValue'])
            foot_roll_plug.connect_to(heel_roll_remap.plugs['inputValue'])
            rock_plug.connect_to(rock_in_remap.plugs['inputValue'])
            rock_plug.connect_to(rock_out_remap.plugs['inputValue'])
            if side == 'right':
                pivot_multiply.plugs['input2'].set_value([-1.0, -1.0, -1.0])
            else:
                pivot_multiply.plugs['input2'].set_value([1.0, 1.0, 1.0])
            ball_pivot_plug.connect_to(pivot_multiply.plugs['input1X'])
            toe_pivot_plug.connect_to(pivot_multiply.plugs['input1Y'])
            heel_pivot_plug.connect_to(pivot_multiply.plugs['input1Z'])
            pivot_multiply.plugs['outputX'].connect_to(ball_pivot.plugs['rotateY'])
            pivot_multiply.plugs['outputY'].connect_to(toe_pivot.plugs['rotateY'])
            pivot_multiply.plugs['outputZ'].connect_to(heel_pivot.plugs['rotateY'])

        # Stretchable
        ik_hip_joint, ik_knee_joint, ik_foot_joint, ik_toe_joint, ik_toe_tip_joint = ik_joints

        ankle_ik_solver = controller.create_ik_handle(
            ik_hip_joint,
            ik_foot_joint,
            parent=ankle_position_transform,
            solver='ikRPsolver'
        )
        foot_ball_ik_solver = controller.create_ik_handle(
            ik_foot_joint,
            ik_toe_joint,
            parent=ball_roll,
            solver='ikSCsolver'
        )

        toe_handle = this.create_handle(
            handle_type=LocalHandle,
            segment_name=this.segment_names[3].title(),
            size=size,
            side=side,
            matrix=foot_matrix,
            shape='frame_z',
            parent=toe_rotate,
            rotation_order='xyz',
        )

        toe_handle.stretch_shape(toe_matrix.get_translation())
        if side == 'left':
            toe_handle.multiply_shape_matrix(Matrix(scale=[1.0, 1.0, -1.0]))
        toe_bend = toe_handle.gimbal_handle.create_child(
            Transform,
            segment_name='ToeBend',
            side=side,
            matrix=foot_matrix
        )

        toe_tip_ik_solver = controller.create_ik_handle(
            ik_toe_joint,
            ik_toe_tip_joint,
            parent=toe_bend,
            solver='ikSCsolver'
        )
        toe_tip_ik_solver.plugs['visibility'].set_value(False)
        ankle_ik_solver.plugs['visibility'].set_value(False)
        foot_ball_ik_solver.plugs['visibility'].set_value(False)

        controller.create_pole_vector_constraint(
            knee_handle,
            ankle_ik_solver
        )

        # stretch
        lock_plug_name = 'lockKnee'
        limb_utilities.convert_ik_to_stretchable_two_segments(
            part=this,
            start_ctrl=hip_transform,
            pv_ctrl=knee_handle,
            end_ctrl=ankle_handle,
            ikh=ankle_ik_solver,
            joints=[ik_hip_joint, ik_knee_joint, ik_foot_joint],
            global_scale_plug=this.scale_multiply_transform.plugs['sy'],
            lock_plug_name=lock_plug_name,
        )

        ik_hip_joint.plugs['translate'].connect_to(joints[0].plugs['translate'])
        ik_knee_joint.plugs['translate'].connect_to(joints[1].plugs['translate'])
        ik_foot_joint.plugs['translate'].connect_to(joints[2].plugs['translate'])

        ik_hip_joint.plugs['rotate'].connect_to(joints[0].plugs['rotate'])
        ik_knee_joint.plugs['rotate'].connect_to(joints[1].plugs['rotate'])
        ik_foot_joint.plugs['rotate'].connect_to(joints[2].plugs['rotate'])

        #
        utility_group.plugs['visibility'].set_value(True)
        controller.create_parent_constraint(
            ik_foot_joint,
            joints[2],
            mo=False
        )
        controller.create_scale_constraint(
            ankle_handle,
            ik_foot_joint,
            mo=False
        )

        controller.create_parent_constraint(
            toe_handle.gimbal_handle,
            joints[3],
            mo=False
        )
        controller.create_scale_constraint(
            toe_handle.gimbal_handle,
            ik_toe_joint,
            mo=False
        )
        ik_foot_joint.plugs['scale'].connect_to(joints[2].plugs['scale'])

        # ball joint following the ankle joint when auto stretch is off
        ball_position_transform = joints[2].create_child(
            Transform,
            segment_name='BallPosition',

            matrix=Matrix(foot_matrix.get_translation()),
        )
        controller.create_point_constraint(
            ball_position_transform,
            toe_handle.groups[0],
            mo=False
        )

        # adding plug access
        root.add_plugs(
            [
                knee_handle.plugs['tx'],
                knee_handle.plugs['ty'],
                knee_handle.plugs['tz'],
                toe_handle.plugs['tx'],
                toe_handle.plugs['ty'],
                toe_handle.plugs['tz'],
                toe_handle.plugs['rx'],
                toe_handle.plugs['ry'],
                toe_handle.plugs['rz'],
                toe_handle.plugs['sx'],
                toe_handle.plugs['sy'],
                toe_handle.plugs['sz'],
                ankle_handle.plugs['tx'],
                ankle_handle.plugs['ty'],
                ankle_handle.plugs['tz'],
                ankle_handle.plugs['rx'],
                ankle_handle.plugs['ry'],
                ankle_handle.plugs['rz'],
                ankle_handle.plugs['sx'],
                ankle_handle.plugs['sy'],
                ankle_handle.plugs['sz'],
                ankle_handle.plugs['auto_stretch'],
                ankle_handle.plugs['soft_ik'],
                ankle_handle.plugs[lock_plug_name],
                ankle_handle.plugs['length'],
                ankle_handle.plugs['lengthA'],
                ankle_handle.plugs['lengthB'],
                foot_roll_plug,
                heel_roll_plug,
                toe_end_roll_plug,
                rock_plug,
                toe_pivot_plug,
                toe_rotate_plug,
                heel_raise_plug,
                ball_pivot_plug,
                heel_pivot_plug,
                break_plug,
            ]
        )

        this.ankle_handle = ankle_handle
        this.knee_handle = knee_handle
        this.toe_handle = toe_handle
        this.joints = joints
        this.ik_joints = ik_joints
        return this
