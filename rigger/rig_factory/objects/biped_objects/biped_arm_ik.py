from Snowman3.rigger.rig_factory.objects.part_objects.chain_guide import ChainGuide
from Snowman3.rigger.rig_factory.objects.base_objects.properties import ObjectProperty, ObjectListProperty, DataProperty
from Snowman3.rigger.rig_factory.objects.node_objects.joint import Joint
from Snowman3.rigger.rig_factory.objects.node_objects.locator import Locator
from Snowman3.rigger.rig_factory.objects.part_objects.part import Part
from Snowman3.rigger.rig_factory.objects.rig_objects.line import Line
from Snowman3.rigger.rig_factory.objects.rig_objects.cone import Cone
from Snowman3.rigger.rig_factory.objects.node_objects.transform import Transform
from Snowman3.rigger.rig_factory.objects.node_objects.depend_node import DependNode
from Snowman3.rigger.rig_factory.objects.rig_objects.grouped_handle import LocalHandle, WorldHandle
from Snowman3.rigger.rig_factory.objects.rig_objects.reverse_pole_vector import ReversePoleVector
import Snowman3.rigger.rig_math.utilities as rmu
from Snowman3.rigger.rig_math.matrix import Matrix
import Snowman3.rigger.rig_factory.environment as env
import Snowman3.rigger.rig_factory.positions as pos
import Snowman3.rigger.rig_factory.utilities.limb_utilities as limb_utilities


class BipedArmIkGuide(ChainGuide):

    segment_names = DataProperty(
        name='segment_names',
        default_value=['Shoulder', 'Elbow', 'Hand', 'HandEnd']
    )

    pole_distance_multiplier = DataProperty(
        name='pole_distance_multiplier',
        default_value=1.0
    )

    make_hand_roll = DataProperty(
        name='make_hand_roll',
        default_value=False
    )

    default_settings = dict(
        root_name='Arm',
        size=4.0,
        side='left',
        pole_distance_multiplier=1.0,
        make_hand_roll=False
    )

    limb_plane = ObjectProperty(
        name='limb_plane'
    )

    pivot_joints = ObjectListProperty(
        name='pivot_joints'
    )

    def __init__(self, **kwargs):
        super(BipedArmIkGuide, self).__init__(**kwargs)
        self.toggle_class = BipedArmIk.__name__

    @classmethod
    def create(cls, **kwargs):
        kwargs['count'] = 4
        kwargs['segment_names'] = ['Shoulder', 'Elbow', 'Hand', 'HandEnd']
        if 'make_hand_roll' in kwargs:
            if kwargs['make_hand_roll']:
                kwargs['count'] = 5
                kwargs['segment_names'] = ['Shoulder', 'Elbow', 'Hand', 'HandEnd', 'FingersTip']
        kwargs['up_vector_indices'] = [0, 2]
        kwargs.setdefault('root_name', 'Arm')
        this = super(BipedArmIkGuide, cls).create(**kwargs)
        this.set_handle_positions(pos.BIPED_POSITIONS)
        limb_utilities.make_ik_plane(this, this.base_handles[0], this.base_handles[2], this.up_handles[0])

        if this.make_hand_roll:
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
            pivot_data = {
                'HandTip': this.joints[4].get_matrix().get_translation(),
                'HandBase': this.joints[2].get_matrix().get_translation(),
                'InHand': this.joints[3].get_matrix().get_translation(),
                'OutHand': this.joints[3].get_matrix().get_translation()
            }
            for pivot_segment_name in ['HandTip', 'HandBase', 'InHand', 'OutHand']:
                handle = this.create_handle(
                    segment_name=pivot_segment_name,
                    functionality_name='Pivot',
                    matrix=Matrix(pivot_data[pivot_segment_name])
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
            inhand_pos = list(in_handle.get_translation())
            inhand_offset = inhand_pos[2] + 5
            in_handle.plugs['tz'].set_value(inhand_offset)
            outhand_pos = list(out_handle.get_translation())
            outhand_offset = outhand_pos[2] - 5
            out_handle.plugs['tz'].set_value(outhand_offset)
            in_handle.plugs['ry'].set_value(0)
            out_handle.plugs['ry'].set_value(0)
            in_handle_name = in_handle.name
            controller.create_aim_constraint(front_handle, back_joint, aim=[0, 1, 0], worldUpType="object",
                                             wuo=in_handle_name, upVector=[0, 0, 1])
            controller.create_aim_constraint(back_handle, front_joint, aim=[0, -1, 0], worldUpType="object",
                                             wuo=in_handle_name, upVector=[0, 0, 1])
            front_handle_name = front_handle.name
            controller.create_aim_constraint(in_handle, out_joint, aim=[0, 0, 1], worldUpType="object",
                                             wuo=front_handle_name, upVector=[0, 1, 0])
            controller.create_aim_constraint(out_handle, in_joint, aim=[0, 0, -1], worldUpType="object",
                                             wuo=front_handle_name, upVector=[0, 1, 0])
            this.pivot_joints = pivot_joints

        return this

    def get_toggle_blueprint(self):
        blueprint = super(BipedArmIkGuide, self).get_toggle_blueprint()
        matrices = [list(x.get_matrix()) for x in self.joints]
        if blueprint['make_hand_roll']:
            matrices.extend([list(x.get_matrix()) for x in self.pivot_joints])
        blueprint['matrices'] = matrices
        return blueprint

    def post_create(self, **kwargs):
        kwargs['index_handle_positions'] = self.get_index_handle_positions()
        super(BipedArmIkGuide, self).post_create(**kwargs)

        # geometry constrain elbow
        self.controller.create_geometry_constraint(self.limb_plane, self.base_handles[1])


class BipedArmIk(Part):
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
    elbow_line = ObjectProperty(
        name='elbow_line'
    )
    stretchable_plugs = ObjectListProperty(
        name='stretchable_plugs'
    )

    segment_names = DataProperty(
        name='segment_names',
        default_value=['Shoulder', 'Elbow', 'Hand', 'HandEnd']
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
        super(BipedArmIk, self).__init__(**kwargs)

    @classmethod
    def create(cls, **kwargs):
        if 'side' not in kwargs:
            raise Exception('you must provide a "side" keyword argument to create a %s' % cls.__name__)
        this = super(BipedArmIk, cls).create(**kwargs)
        cls.build_rig(this)
        return this

    @staticmethod
    def build_rig(this):
        controller = this.controller
        size = this.size
        side = this.side
        matrices = this.matrices
        utility_group = this.utility_group
        shoulder_matrix = matrices[0]
        elbow_matrix = matrices[1]
        wrist_matrix = matrices[2]
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
            ik_joint.plugs['scale'].connect_to(joint.plugs['scale'])
            root.add_plugs(
                ik_joint.plugs['rx'],
                ik_joint.plugs['ry'],
                ik_joint.plugs['rz'],
                keyable=False
            )
        wrist_handle = this.create_handle(
            handle_type=LocalHandle,
            segment_name=this.segment_names[2],
            size=size,
            side=side,
            matrix=wrist_matrix,
            shape='trapezoid',
            axis='-y',
            rotation_order='xyz',
        )
        wrist_handle_matrix = Matrix(scale=[size, size if side == 'left' else size * -1, size * 1.4])
        wrist_handle.set_shape_matrix(wrist_handle_matrix)

        controller.create_scale_constraint(
            wrist_handle,
            ik_joints[2],
            mo=False
        )

        pole_position = rmu.calculate_pole_vector_position(
            shoulder_matrix.get_translation(),
            elbow_matrix.get_translation(),
            wrist_matrix.get_translation(),
            distance=((size/10) + 1) * 50 * this.pole_distance_multiplier
        )
        elbow_handle = this.create_handle(
            handle_type=WorldHandle,
            parent=this,
            segment_name='Elbow',
            size=size*0.5,
            side=side,
            matrix=Matrix(*pole_position),
            shape='ball',
            rotation_order='xyz',
            create_gimbal=False
        )
        ik_handle = controller.create_ik_handle(
            ik_joints[0],
            ik_joints[2],
            parent=this,
            solver='ikRPsolver'
        )
        shoulder_root = this.top_group.create_child(
            Transform,
            segment_name='ClavicleRoot',
            matrix=ik_joints[0].get_matrix(),
        )
        shoulder_root.plugs['visibility'].set_value(False)

        controller.create_orient_constraint(
            wrist_handle.gimbal_handle,
            ik_joints[2],
            mo=True,
        )
        twist_plug = wrist_handle.create_plug(
            'twist',
            at='double',
            k=True,
            dv=0.0
        )

        twist_plug.connect_to(ik_handle.plugs['twist'])
        locator_1 = joints[1].create_child(
            Locator,
            segment_name='RootLine'
        )
        locator_2 = elbow_handle.create_child(
            Locator,
            segment_name='TipLine'
        )
        locator_1.plugs['visibility'].set_value(False)
        locator_2.plugs['visibility'].set_value(False)
        this.elbow_line = this.top_group.create_child(
            Line,
            segment_name='Line'
        )
        locator_1.plugs['worldPosition'].element(0).connect_to(this.elbow_line.curve.plugs['controlPoints'].element(0))
        locator_2.plugs['worldPosition'].element(0).connect_to(this.elbow_line.curve.plugs['controlPoints'].element(1))
        controller.create_pole_vector_constraint(
            elbow_handle,
            ik_handle
        )

        wrist_pole_transform = this.top_group.create_child(
            Transform,
            segment_name='WristPole',
        )

        controller.create_point_constraint(
            shoulder_root,
            ik_joints[0]
        )

        controller.create_point_constraint(
            shoulder_root,
            wrist_handle.gimbal_handle,
            wrist_pole_transform
        )

        utility_group.plugs['visibility'].set_value(True)
        controller.create_parent_constraint(
            ik_joints[2],
            joints[2],
            mo=False
        )

        ik_handle.plugs['visibility'].set_value(False)
        utility_group.plugs['visibility'].set_value(True)

        if this.make_hand_roll:

            # parent extra joint on chain
            controller.create_parent_constraint(
                ik_joints[3],
                joints[3],
                mo=False
            )

            handend_matrix = matrices[3]
            fingertip_matrix = matrices[4]
            front_pivot_matrix = matrices[5]
            back_pivot_matrix = matrices[6]
            in_pivot_matrix = matrices[7]
            out_pivot_matrix = matrices[8]

            ball_pivot_zro = this.create_child(
                Transform,
                segment_name='BallPivotZro',
                matrix=handend_matrix,
                parent=wrist_handle.gimbal_handle
            )
            ball_pivot = ball_pivot_zro.create_child(
                Transform,
                segment_name='BallPivot'
            )
            heel_pivot_zro = this.create_child(
                Transform,
                segment_name='HeelPivotZro',
                side=side,
                matrix=back_pivot_matrix,
                parent=ball_pivot
            )
            heel_pivot = heel_pivot_zro.create_child(
                Transform,
                segment_name='HeelPivot'
            )
            toe_pivot_zro = this.create_child(
                Transform,
                segment_name='ToePivotZro',
                side=side,
                matrix=fingertip_matrix,
                parent=heel_pivot
            )
            toe_pivot = toe_pivot_zro.create_child(
                Transform,
                segment_name='ToePivot'
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
                matrix=handend_matrix
            )
            toe_rotate = this.create_child(
                Transform,
                segment_name='ToeRotate',
                side=side,
                matrix=fingertip_matrix,
                parent=bend_top
            )
            ball_roll_group = heel_roll_grp.create_child(
                Transform,
                segment_name='BallRollOrient',
                side=side,
                matrix=handend_matrix
            )
            heel_raise_grp = ball_roll_group.create_child(
                Transform,
                segment_name='HeelRaise'
            )
            ball_roll = heel_raise_grp.create_child(
                Transform,
                segment_name='BallRoll',
                matrix=handend_matrix,
            )
            wrist_position_transform = ball_roll.create_child(
                Transform,
                segment_name='AnklePosition',
                matrix=wrist_matrix,
            )

            foot_roll_plug = wrist_handle.create_plug(
                'handRoll',
                at='double',
                k=True,
                dv=0.0,
            )
            break_plug = wrist_handle.create_plug(
                'break',
                at='double',
                k=True,
                dv=45.0,
                min=0.0
            )
            toe_end_roll_plug = wrist_handle.create_plug(
                'fingerEndRoll',
                at='double',
                k=True,
                dv=0.0
            )
            heel_raise_plug = wrist_handle.create_plug(
                'wristRaise',
                at='double',
                k=True,
                dv=0.0
            )
            heel_roll_plug = wrist_handle.create_plug(
                'wristRoll',
                at='double',
                k=True,
                dv=0.0
            )
            toe_pivot_plug = wrist_handle.create_plug(
                'fingerPivot',
                at='double',
                k=True,
                dv=0.0,
            )
            toe_rotate_plug = wrist_handle.create_plug(
                'fingerRotate',
                at='double',
                k=True,
                dv=0.0,
            )
            ball_pivot_plug = wrist_handle.create_plug(
                'ballPivot',
                at='double',
                k=True,
                dv=0.0,
            )
            heel_pivot_plug = wrist_handle.create_plug(
                'wristPivot',
                at='double',
                k=True,
                dv=0.0,
            )
            rock_plug = wrist_handle.create_plug(
                'rock',
                at='double',
                k=True,
                dv=0.0
            )
            wrist_wiggle_plug = wrist_handle.create_plug(
                'handWiggle',
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
            if this.side == 'right':
                toe_tip_remap.plugs['outValue'].connect_to(rock_front.plugs['rotateZ'])
            else:
                reverse_value = toe_tip_remap.plugs['outValue'].multiply(-1.0)
                reverse_value.connect_to(rock_front.plugs['rotateZ'])

            # Toe end roll
            if this.side == 'right':
                reverse_value = toe_end_roll_plug.multiply(-1.0)
                reverse_value.connect_to(toe_end_grp.plugs['rotateZ'])
            else:
                toe_end_roll_plug.connect_to(toe_end_grp.plugs['rotateZ'])

            # Toe rotation
            toe_rotate_plug.connect_to(toe_rotate.plugs['rotateZ'])

            # Heel Roll
            if this.side == 'right':
                reverse_value = heel_roll_plug.multiply(-1.0)
                reverse_value.connect_to(heel_roll_grp.plugs['rotateZ'])
            else:
                heel_roll_plug.connect_to(heel_roll_grp.plugs['rotateZ'])

            # Heel Raise
            reverse_value = heel_raise_plug.multiply(-1.0)
            reverse_value.connect_to(heel_raise_grp.plugs['rotateZ'])

            # Wrist Wiggle
            wrist_wiggle_plug.connect_to(ball_roll.plugs['rotateY'])

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
            reverse_value = toe_ball_remap.plugs['outValue'].multiply(-1.0)
            reverse_value.connect_to(ball_roll.plugs['rotateZ'])

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
            if this.side == 'right':
                reverse_value = heel_roll_remap.plugs['outValue'].multiply(-1.0)
                reverse_value.connect_to(roll_back.plugs['rotateZ'])
            else:
                heel_roll_remap.plugs['outValue'].connect_to(roll_back.plugs['rotateZ'])

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
            if this.side == 'right':
                reverse_value = rock_in_remap.plugs['outValue'].multiply(-1.0)
                reverse_value.connect_to(rock_in_group.plugs['rotateY'])
            else:
                rock_in_remap.plugs['outValue'].connect_to(rock_in_group.plugs['rotateY'])

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
            if this.side == 'right':
                reverse_value = rock_out_remap.plugs['outValue'].multiply(-1.0)
                reverse_value.connect_to(rock_out_group.plugs['rotateY'])
            else:
                rock_out_remap.plugs['outValue'].connect_to(rock_out_group.plugs['rotateY'])

            # pivots
            pivot_multiply = this.create_child(
                DependNode,
                node_type='multiplyDivide',
                segment_name='Pivots'
            )

            # connect
            foot_roll_plug.connect_to(toe_tip_remap.plugs['inputValue'])
            foot_roll_plug.connect_to(toe_ball_remap.plugs['inputValue'])
            foot_roll_plug.connect_to(heel_roll_remap.plugs['inputValue'])
            rock_plug.connect_to(rock_in_remap.plugs['inputValue'])
            rock_plug.connect_to(rock_out_remap.plugs['inputValue'])
            if side == 'right':
                pivot_multiply.plugs['input2'].set_value([-1.0, -1.0, -1.0])
                reverse_value_a = ball_pivot_plug.multiply(-1.0)
                reverse_value_a.connect_to(pivot_multiply.plugs['input1X'])
                reverse_value_b = toe_pivot_plug.multiply(-1.0)
                reverse_value_b.connect_to(pivot_multiply.plugs['input1Y'])
                reverse_value_b = heel_pivot_plug.multiply(-1.0)
                reverse_value_b.connect_to(pivot_multiply.plugs['input1Z'])
            else:
                pivot_multiply.plugs['input2'].set_value([1.0, 1.0, 1.0])
                ball_pivot_plug.connect_to(pivot_multiply.plugs['input1X'])
                toe_pivot_plug.connect_to(pivot_multiply.plugs['input1Y'])
                heel_pivot_plug.connect_to(pivot_multiply.plugs['input1Z'])
            pivot_multiply.plugs['outputX'].connect_to(ball_pivot.plugs['rotateX'])
            pivot_multiply.plugs['outputY'].connect_to(toe_pivot.plugs['rotateX'])
            pivot_multiply.plugs['outputZ'].connect_to(heel_pivot.plugs['rotateX'])

            # missing IKs and toe (fingers) handle
            # ik_hip_joint, ik_knee_joint, ik_foot_joint, ik_toe_joint, ik_toe_tip_joint = ik_joints
            ik_shoulder_joint, ik_elbow_joint, ik_wrist_joint, ik_handend_joint, ik_fingertips_joint = ik_joints

            foot_ball_ik_solver = controller.create_ik_handle(
                ik_wrist_joint,
                ik_handend_joint,
                parent=ball_roll,
                solver='ikSCsolver'
            )

            finger_handle = this.create_handle(
                handle_type=LocalHandle,
                segment_name=this.segment_names[3].title(),
                size=size,
                side=side,
                matrix=handend_matrix,
                shape='frame_x',
                parent=toe_rotate,
                rotation_order='xyz',
            )

            finger_handle.stretch_shape(fingertip_matrix.get_translation())
            if side == 'left':
                finger_handle.multiply_shape_matrix(Matrix(scale=[-1.0, 1.0, 1.0]))
            toe_bend = finger_handle.gimbal_handle.create_child(
                Transform,
                segment_name='ToeBend',
                side=side,
                matrix=handend_matrix
            )

            toe_tip_ik_solver = controller.create_ik_handle(
                ik_handend_joint,
                ik_fingertips_joint,
                parent=toe_bend,
                solver='ikSCsolver'
            )
            toe_tip_ik_solver.plugs['visibility'].set_value(False)
            foot_ball_ik_solver.plugs['visibility'].set_value(False)

            # ball joint following the wrist joint when auto stretch is off
            ball_position_transform = joints[2].create_child(
                Transform,
                segment_name='BallPosition',

                matrix=Matrix(handend_matrix.get_translation()),
            )
            controller.create_point_constraint(
                ball_position_transform,
                finger_handle.groups[0],
                mo=False
            )

            # add new handle plugs to root
            root.add_plugs(
                [
                    finger_handle.plugs['rx'],
                    finger_handle.plugs['ry'],
                    finger_handle.plugs['rz'],
                    foot_roll_plug,
                    break_plug,
                    toe_end_roll_plug,
                    heel_raise_plug,
                    heel_roll_plug,
                    toe_pivot_plug,
                    toe_rotate_plug,
                    ball_pivot_plug,
                    heel_pivot_plug,
                    rock_plug,
                    wrist_wiggle_plug
                 ]
            )
            this.finger_handle = finger_handle
        else:
            wrist_position_transform = this.create_child(
                Transform,
                segment_name='WristPosition',
                matrix=wrist_matrix,
            )

            controller.create_point_constraint(
                wrist_handle.gimbal_handle,
                wrist_position_transform,
                mo=True,
            )

        ik_handle.set_parent(wrist_position_transform)

        # stretch
        lock_plug_name = 'lockElbow'
        limb_utilities.convert_ik_to_stretchable_two_segments(
            part=this,
            start_ctrl=shoulder_root,
            pv_ctrl=elbow_handle,
            end_ctrl=wrist_handle,
            ikh=ik_handle,
            joints=(ik_joints[0], ik_joints[1], ik_joints[2]),
            global_scale_plug=this.scale_multiply_transform.plugs['sy'],
            lock_plug_name=lock_plug_name,
        )

        ik_joints[0].plugs['translate'].connect_to(joints[0].plugs['translate'])
        ik_joints[1].plugs['translate'].connect_to(joints[1].plugs['translate'])
        ik_joints[2].plugs['translate'].connect_to(joints[2].plugs['translate'])

        ik_joints[0].plugs['rotate'].connect_to(joints[0].plugs['rotate'])
        ik_joints[1].plugs['rotate'].connect_to(joints[1].plugs['rotate'])
        ik_joints[2].plugs['rotate'].connect_to(joints[2].plugs['rotate'])

        # add plugs to root
        root.add_plugs(
            [
                wrist_handle.plugs['tx'],
                wrist_handle.plugs['ty'],
                wrist_handle.plugs['tz'],
                wrist_handle.plugs['rx'],
                wrist_handle.plugs['ry'],
                wrist_handle.plugs['rz'],
                wrist_handle.plugs['sx'],
                wrist_handle.plugs['sy'],
                wrist_handle.plugs['sz'],
                wrist_handle.plugs['auto_stretch'],
                wrist_handle.plugs['soft_ik'],
                wrist_handle.plugs[lock_plug_name],
                wrist_handle.plugs['length'],
                wrist_handle.plugs['lengthA'],
                wrist_handle.plugs['lengthB'],
                elbow_handle.plugs['tx'],
                elbow_handle.plugs['ty'],
                elbow_handle.plugs['tz'],
                twist_plug,
            ]
        )

        this.wrist_handle = wrist_handle
        this.elbow_handle = elbow_handle
        this.joints = joints
        this.ik_joints = ik_joints
        return this
