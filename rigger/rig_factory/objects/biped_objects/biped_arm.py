import copy
import Snowman3.rigger.rig_factory as rig_factory
import Snowman3.rigger.rig_factory.environment as env
from Snowman3.rigger.rig_factory.objects.base_objects.properties import ObjectProperty, ObjectListProperty, DataProperty
from Snowman3.rigger.rig_factory.objects.biped_objects.biped_arm_fk import BipedArmFk
from Snowman3.rigger.rig_factory.objects.biped_objects.biped_arm_ik import BipedArmIk
from Snowman3.rigger.rig_factory.objects.node_objects.depend_node import DependNode
from Snowman3.rigger.rig_factory.objects.node_objects.transform import Transform
from Snowman3.rigger.rig_factory.objects.node_objects.joint import Joint
from Snowman3.rigger.rig_factory.objects.part_objects.chain_guide import ChainGuide
from Snowman3.rigger.rig_factory.objects.part_objects.part import Part
from Snowman3.rigger.rig_factory.objects.rig_objects.cone import Cone
from Snowman3.rigger.rig_factory.objects.rig_objects.grouped_handle import LocalHandle, GroupedHandle
from Snowman3.rigger.rig_math.matrix import Matrix
from Snowman3.rigger.rig_math.vector import Vector
from Snowman3.rigger.rig_math import vector
import Snowman3.rigger.rig_factory.positions as pos
import Snowman3.rigger.rig_factory.utilities.limb_utilities as limb_utilities


class BipedArmGuide(ChainGuide):
    segment_names = DataProperty(
        name='segment_names',
        default_value=['Clavicle', 'Shoulder', 'Elbow', 'Hand', 'HandEnd']
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

    default_settings = dict(
        root_name='Arm',
        size=5.0,
        side='left',
        pole_distance_multiplier=1.0,
        make_hand_roll=False,
        create_plane=True
    )

    limb_plane = ObjectProperty(
        name='limb_plane'
    )

    pivot_joints = ObjectListProperty(
        name='pivot_joints'
    )
    create_plane = DataProperty(
        name='create_plane',
        default_value=True
    )
    def __init__(self, **kwargs):
        super(BipedArmGuide, self).__init__(**kwargs)
        self.toggle_class = BipedArm.__name__

    @classmethod
    def create(cls, **kwargs):
        kwargs['count'] = 5
        kwargs['segment_names'] = ['Clavicle', 'Shoulder', 'Elbow', 'Hand', 'HandEnd']
        if 'make_hand_roll' in kwargs:
            if kwargs['make_hand_roll']:
                kwargs['count'] = 6
                kwargs['segment_names'] = ['Clavicle', 'Shoulder', 'Elbow', 'Hand', 'HandEnd', 'FingersTip']
        kwargs['up_vector_indices'] = [0, 1, 3]
        kwargs.setdefault('root_name', 'Arm')
        this = super(BipedArmGuide, cls).create(**kwargs)
        this.set_handle_positions(pos.BIPED_POSITIONS)
        this.base_joints = list(this.joints)
        limb_utilities.make_ik_plane(
            this,
            this.base_handles[1],
            this.base_handles[3],
            this.up_handles[1]
        )
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
                'HandTip': this.joints[5].get_matrix().get_translation(),
                'HandBase': this.joints[3].get_matrix().get_translation(),
                'InHand': this.joints[4].get_matrix().get_translation(),
                'OutHand': this.joints[4].get_matrix().get_translation()
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
        blueprint = super(BipedArmGuide, self).get_toggle_blueprint()
        matrices = [list(x.get_matrix()) for x in self.joints]
        if blueprint['make_hand_roll']:
            matrices.extend([list(x.get_matrix()) for x in self.pivot_joints])
        blueprint['matrices'] = matrices
        return blueprint

    def post_create(self, **kwargs):
        kwargs['index_handle_positions'] = self.get_index_handle_positions()
        super(BipedArmGuide, self).post_create(**kwargs)
        if self.create_plane:
            # geometry constrain elbow
            self.controller.create_geometry_constraint(self.limb_plane, self.base_handles[2])


class BipedArm(Part):
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

    def __init__(self, **kwargs):
        super(BipedArm, self).__init__(**kwargs)

    @classmethod
    def create(cls, **kwargs):
        this = super(BipedArm, cls).create(**kwargs)
        cls.build_rig(this)
        return this

    @staticmethod
    def build_rig(this):
        controller = this.controller
        root = this.get_root()
        size = this.size
        side = this.side
        matrices = this.matrices
        joint_parent = this.joint_group
        segment_names = this.segment_names

        count = 5
        if this.make_hand_roll:
            count = 6
        joints = []
        for i in range(count):
            joint = this.create_child(
                Joint,
                parent=joint_parent,
                matrix=matrices[i],
                segment_name=segment_names[i]
            )
            joint.zero_rotation()
            joint_parent = joint
            joint.plugs['overrideEnabled'].set_value(True)
            joint.plugs['overrideDisplayType'].set_value(2)
            joints.append(joint)

        clavicle_handle = this.create_handle(
            handle_type=LocalHandle,
            segment_name=segment_names[0],
            size=size * 1.5,
            side=side,
            matrix=matrices[0],
            shape='c_curve',
            rotation_order='xyz'
        )
        handles = [clavicle_handle]
        root.add_plugs([
            clavicle_handle.plugs[m + a]
            for m in 'trs'
            for a in 'xyz'
        ])
        clavicle_handle.stretch_shape(matrices[1])
        shape_scale = [
            1.5 if side == 'right' else -1.5,
            1,
            1
        ]
        clavicle_handle.multiply_shape_matrix(Matrix(scale=shape_scale))

        controller.create_parent_constraint(
            clavicle_handle.gimbal_handle,
            joints[0],
            mo=True,
        )

        # Fk Arm
        this.handles = []
        this.differentiation_name = 'Fk'
        fk_group = this.create_child(
            Transform,
            segment_name='SubPart',
            parent=clavicle_handle.gimbal_handle,
            matrix=Matrix()
        )
        this.top_group = fk_group
        this.segment_names = segment_names[1:]
        this.matrices = matrices[1:]
        BipedArmFk.build_rig(this)
        fk_joints = list(this.joints)
        fk_handles = list(this.handles)
        if len(fk_handles) > 3:
            fk_handles[-1].plugs['visibility'].set_value(0)
        this.handles = []
        this.joints = []

        this.differentiation_name = 'Ik'
        ik_group = this.create_child(
            Transform,
            segment_name='SubPart',
            parent=clavicle_handle.gimbal_handle,
            matrix=Matrix()
        )
        this.top_group = ik_group
        this.matrices = matrices[1:]
        # Ik Arm

        BipedArmIk.build_rig(this)

        ik_joints = list(this.joints)
        kinematic_joints = list(this.ik_joints)
        ik_handles = list(this.handles)
        handles.extend(fk_handles)  # reorder handles
        handles.extend(ik_handles)  # reorder handles
        this.handles = handles
        this.differentiation_name = None
        this.matrices = matrices
        this.top_group = this
        this.ik_handles = ik_handles
        this.ik_joints = ik_joints
        this.fk_handles = fk_handles
        this.ik_handles = ik_handles

        fk_joints[0].set_parent(joints[0])
        ik_joints[0].set_parent(joints[0])
        kinematic_joints[0].set_parent(joints[0])
        this.segment_names = segment_names

        part_ik_plug = this.create_plug(
            'ikSwitch',
            at='double',
            k=True,
            dv=0.0,
            min=0.0,
            max=1.0
        )

        blend_count = 3
        if this.make_hand_roll:
            blend_count = 4
        for i in range(blend_count):
            index_character = rig_factory.index_dictionary[i].title()
            pair_blend = this.create_child(
                DependNode,
                node_type='pairBlend',
                segment_name='Blend%s' % index_character
            )
            blend_colors = this.create_child(
                DependNode,
                node_type='blendColors',
                segment_name='Blend%s' % index_character
            )
            ik_joints[i].plugs['translate'].connect_to(pair_blend.plugs['inTranslate2'])
            fk_joints[i].plugs['translate'].connect_to(pair_blend.plugs['inTranslate1'])
            ik_joints[i].plugs['rotate'].connect_to(pair_blend.plugs['inRotate2'])
            fk_joints[i].plugs['rotate'].connect_to(pair_blend.plugs['inRotate1'])
            pair_blend.plugs['outTranslate'].connect_to(joints[i + 1].plugs['translate'])
            pair_blend.plugs['outRotate'].connect_to(joints[i + 1].plugs['rotate'])
            blend_colors.plugs['output'].connect_to(joints[i + 1].plugs['scale'])
            ik_joints[i].plugs['scale'].connect_to(blend_colors.plugs['color1'])
            fk_joints[i].plugs['scale'].connect_to(blend_colors.plugs['color2'])
            pair_blend.plugs['rotInterpolation'].set_value(1)
            part_ik_plug.connect_to(pair_blend.plugs['weight'])
            part_ik_plug.connect_to(blend_colors.plugs['blender'])
            joints[i + 1].plugs['rotateOrder'].connect_to(fk_joints[i].plugs['rotateOrder'])
            joints[i + 1].plugs['rotateOrder'].connect_to(ik_joints[i].plugs['rotateOrder'])
        settings_handle = this.create_handle(
            handle_type=GroupedHandle,
            segment_name='Settings',
            shape='gear_simple',
            axis='z',
            matrix=matrices[-2],
            parent=joints[-1],
            size=size * 0.5,
            group_count=1
        )
        settings_handle.groups[0].plugs.set_values(
            tx=size * 2.0 if side == 'right' else size * -2.0
        )
        settings_handle.plugs.set_values(
            overrideEnabled=True,
            overrideRGBColors=True,
            overrideColorRGB=env.colors['highlight']
        )

        ik_plug = settings_handle.create_plug(
            'ikSwitch',
            at='double',
            k=True,
            dv=0.0,
            min=0.0,
            max=1.0
        )

        ik_plug.connect_to(part_ik_plug)

        for ik_handle in ik_handles:
            part_ik_plug.connect_to(ik_handle.groups[0].plugs['visibility'])
        part_ik_plug.connect_to(this.elbow_line.plugs['visibility'])

        reverse_node = this.create_child(
            DependNode,
            node_type='reverse'
        )
        part_ik_plug.connect_to(reverse_node.plugs['inputX'])
        for fk_handle in fk_handles:
            reverse_node.plugs['outputX'].connect_to(fk_handle.groups[0].plugs['visibility'])
        ik_joints[0].plugs['visibility'].set_value(False)
        fk_joints[0].plugs['visibility'].set_value(False)
        root = this.get_root()
        joints[0].plugs['type'].set_value(9)
        joints[1].plugs['type'].set_value(10)
        joints[2].plugs['type'].set_value(11)
        joints[3].plugs['type'].set_value(12)
        root.add_plugs(
            ik_plug,
            keyable=True
        )
        this.fk_joints = fk_joints
        this.ik_joints = ik_joints
        this.fk_handles = fk_handles
        this.ik_handles = ik_handles
        this.joints = joints
        this.base_joints = list(joints)
        this.settings_handle = settings_handle
        this.clavicle_handle = clavicle_handle

        return this

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
