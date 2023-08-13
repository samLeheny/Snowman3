from Snowman3.rigger.rig_factory.objects.base_objects.properties import ObjectProperty, ObjectListProperty, DataProperty
from Snowman3.rigger.rig_factory.objects.biped_objects.biped_leg_fk import BipedLegFk
from Snowman3.rigger.rig_factory.objects.biped_objects.biped_leg_ik import BipedLegIk
from Snowman3.rigger.rig_factory.objects.node_objects.dag_node import DagNode
from Snowman3.rigger.rig_factory.objects.node_objects.depend_node import DependNode
from Snowman3.rigger.rig_factory.objects.node_objects.joint import Joint
from Snowman3.rigger.rig_factory.objects.node_objects.transform import Transform
from Snowman3.rigger.rig_factory.objects.part_objects.chain_guide import ChainGuide
from Snowman3.rigger.rig_factory.objects.part_objects.part import Part
from Snowman3.rigger.rig_factory.objects.rig_objects.cone import Cone
from Snowman3.rigger.rig_factory.objects.rig_objects.curve_handle import CurveHandle
from Snowman3.rigger.rig_factory.objects.rig_objects.grouped_handle import LocalHandle, GroupedHandle
from Snowman3.rigger.rig_math.matrix import Matrix, compose_matrix
from Snowman3.rigger.rig_math.vector import Vector
from Snowman3.rigger.rig_math import vector
import Snowman3.rigger.rig_factory.environment as env
import Snowman3.rigger.rig_math.utilities as rmu
import Snowman3.rigger.rig_factory.positions as pos
import Snowman3.rigger.rig_factory.utilities.limb_utilities as limb_utilities


class BipedLegGuide(ChainGuide):

    default_settings = dict(
        root_name='Leg',
        size=4.0,
        side='left',
        foot_placement_depth=1.0,
        master_foot=False,
        world_space_foot=True,
        pole_distance_multiplier=1.0,
        create_plane=True
    )

    pole_distance_multiplier = DataProperty(
        name='pole_distance_multiplier',
        default_value=1.0
    )
    pivot_joints = ObjectListProperty(
        name='pivot_joints'
    )
    foot_placement_depth = DataProperty(
        name='foot_placement_depth',
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
    limb_plane = ObjectProperty(
        name='limb_plane'
    )
    create_plane = DataProperty(
        name='create_plane',
        default_value=True
    )

    def __init__(self, **kwargs):
        super(BipedLegGuide, self).__init__(**kwargs)
        self.toggle_class = BipedLeg.__name__

    @classmethod
    def create(cls, **kwargs):
        kwargs['count'] = 6
        kwargs['up_vector_indices'] = [0, 1, 3]
        kwargs.setdefault('root_name', 'Leg')
        this = super(BipedLegGuide, cls).create(**kwargs)
        controller = this.controller
        body = this.get_root()
        size = this.size
        side = this.side
        pivot_handles = []
        pivot_joints = []
        master_joint = []
        root = this.get_root()
        size_plug = this.plugs['size']
        size_multiply_node = this.create_child(
            'DependNode',
            node_type='multiplyDivide',
            segment_name='Size'
        )
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
            size_multiply_node.plugs['outputX'].connect_to(master_guide.plugs['size'])
            size_multiply_node.plugs['outputX'].connect_to(cone_x.plugs['size'])
            size_multiply_node.plugs['outputX'].connect_to(cone_y.plugs['size'])
            size_multiply_node.plugs['outputX'].connect_to(cone_z.plugs['size'])
            master_guide.plugs['radius'].set_value(size * 0.5)
            master_guide.mesh.assign_shading_group(root.shaders[this.side].shading_group)

        size_plug.connect_to(size_multiply_node.plugs['input1X'])
        size_multiply_node.plugs['input2X'].set_value(0.5)
        size_multiply_plug = size_multiply_node.plugs['outputX']
        for pivot_segment_name in ['Toe', 'Heel', 'InFoot', 'OutFoot']:

            handle = this.create_handle(
                segment_name=pivot_segment_name,
                functionality_name='Pivot'
            )
            joint = handle.create_child(
                Joint,
                segment_name=pivot_segment_name
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
                radius=0.0
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
        if this.master_foot:
            pivot_handles.append(master_guide)
            pivot_joints.append(master_guide_jnt)
        controller.create_aim_constraint(front_handle, back_joint, aim=[0, 0, 1])
        controller.create_aim_constraint(back_handle, front_joint, aim=[0, 0, -1])
        controller.create_aim_constraint(in_handle, out_joint, aim=[-1, 0, 0], worldUpType="scene", upVector=[0, 1, 0])
        controller.create_aim_constraint(out_handle, in_joint, aim=[1, 0, 0], worldUpType="scene", upVector=[0, 1, 0])
        this.pivot_joints = pivot_joints
        this.set_handle_positions(pos.BIPED_POSITIONS)
        limb_utilities.make_ik_plane(this, this.base_handles[1], this.base_handles[3], this.up_handles[1])

        if this.master_foot:
            controller.create_aim_constraint(
                this.base_handles[-1],
                master_joint,
                aim=[0, 0, -1],
                worldUpType='scene',
                upVector=[0, 1, 0],
                maintainOffset=False
            )

        return this

    def get_toggle_blueprint(self):
        blueprint = super(BipedLegGuide, self).get_toggle_blueprint()
        matrices = [list(x.get_matrix()) for x in self.joints]
        matrices.extend([list(x.get_matrix()) for x in self.pivot_joints])
        blueprint['matrices'] = matrices
        return blueprint

    def post_create(self, **kwargs):
        super(BipedLegGuide, self).post_create(**kwargs)
        if self.create_plane:
            # geometry constrain elbow
            self.controller.create_geometry_constraint(self.limb_plane, self.base_handles[2])


class BipedLeg(Part):

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

    def __init__(self, **kwargs):
        super(BipedLeg, self).__init__(**kwargs)

    @classmethod
    def create(cls, **kwargs):
        this = super(BipedLeg, cls).create(**kwargs)
        cls.build_rig(this)
        return this

    @staticmethod
    def build_rig(this):
        controller = this.controller
        size = this.size
        side = this.side
        matrices = this.matrices
        foot_placement_depth = this.foot_placement_depth
        aim_vector = env.side_aim_vectors[side]
        joint_parent = this.joint_group
        joints = []
        for i in range(6):
            if i != 0:
                joint_parent = joints[-1]
            joint = this.create_child(
                Joint,
                segment_name=this.segment_names[i].title(),
                parent=joint_parent,
                matrix=matrices[i],
                index=i
            )
            joint.zero_rotation()
            joints.append(joint)
            joint.plugs['overrideEnabled'].set_value(True)
            joint.plugs['overrideDisplayType'].set_value(2)
        hip_handle = this.create_handle(
            handle_type=LocalHandle,
            segment_name=this.segment_names[0],
            size=size * 2.5,
            matrix=matrices[0],
            shape='c_curve',
            rotation_order='xyz'
        )
        shape_scale = [
            -1 if side == 'right' else 1,
            1,
            1
            ]
        hip_handle.multiply_shape_matrix(Matrix(scale=shape_scale))
        controller.create_parent_constraint(
            hip_handle.gimbal_handle,
            joints[0]
        )

        # Prepare to create Fk Leg
        origonal_segment_names = this.segment_names
        this.segment_names = this.segment_names[1:]  # Fk/Ik Legs do not have a base joint
        this.handles = []
        this.differentiation_name = 'Fk'
        fk_group = this.create_child(
            Transform,
            segment_name='SubPart',
            parent=hip_handle.gimbal_handle
        )
        this.top_group = fk_group
        this.matrices = matrices[1:]
        # Create Fk Leg
        BipedLegFk.build_rig(this)
        fk_joints = list(this.joints)
        fk_handles = list(this.handles)

        # Prepare to create Ik Leg
        this.handles = []
        this.joints = []
        this.differentiation_name = 'Ik'
        ik_group = this.create_child(
            Transform,
            segment_name='SubPart',
            parent=hip_handle.gimbal_handle
        )
        this.top_group = ik_group
        this.matrices = matrices[1:]
        # Create Ik Leg
        BipedLegIk.build_rig(this)
        ik_joints = list(this.joints)
        kinematic_joints = list(this.ik_joints)
        ik_handles = list(this.handles)

        # Finish creating Ik/Fk Legs
        handles = [hip_handle]
        handles.extend(fk_handles)  # reorder handles
        handles.extend(ik_handles)  # reorder handles
        this.handles = handles
        this.differentiation_name = None
        this.matrices = matrices
        this.top_group = this
        this.segment_names = origonal_segment_names

        fk_joints[0].set_parent(joints[0])
        ik_joints[0].set_parent(joints[0])
        kinematic_joints[0].set_parent(joints[0])
        part_ik_plug = this.create_plug(
            'ik_switch',
            at='double',
            k=True,
            dv=0.0,
            min=0.0,
            max=1.0
        )
        for i in range(5):
            pair_blend = joints[i+1].create_child(
                DependNode,
                node_type='pairBlend',
                parent=this
            )
            blend_colors = joints[i+1].create_child(
                DependNode,
                node_type='blendColors',
                parent=this
            )
            ik_joints[i].plugs['translate'].connect_to(pair_blend.plugs['inTranslate2'])
            fk_joints[i].plugs['translate'].connect_to(pair_blend.plugs['inTranslate1'])
            ik_joints[i].plugs['rotate'].connect_to(pair_blend.plugs['inRotate2'])
            fk_joints[i].plugs['rotate'].connect_to(pair_blend.plugs['inRotate1'])
            ik_joints[i].plugs['scale'].connect_to(blend_colors.plugs['color1'])
            fk_joints[i].plugs['scale'].connect_to(blend_colors.plugs['color2'])
            pair_blend.plugs['outTranslate'].connect_to(joints[i+1].plugs['translate'])
            pair_blend.plugs['outRotate'].connect_to(joints[i+1].plugs['rotate'])
            blend_colors.plugs['output'].connect_to(joints[i+1].plugs['scale'])
            pair_blend.plugs['rotInterpolation'].set_value(1)
            part_ik_plug.connect_to(pair_blend.plugs['weight'])
            part_ik_plug.connect_to(blend_colors.plugs['blender'])

        settings_position = matrices[3].get_translation() + Vector(
            [
                size * -1.5 if side == 'right' else size * 1.5,
                0.0,
                0.0
            ])
        settings_handle = this.create_handle(
            handle_type=GroupedHandle,
            parent=joints[3],
            segment_name='Settings',
            shape='gear_simple',
            axis='z',
            matrix=Matrix(settings_position),
            size=size*0.5,
            group_count=1
        )
        settings_handle.plugs.set_values(
            overrideEnabled=True,
            overrideRGBColors=True,
            overrideColorRGB=env.colors['highlight'],
        )
        ik_plug = settings_handle.create_plug(
            'ikSwitch',
            at='double',
            k=True,
            dv=1.0,
            min=0.0,
            max=1.0
        )
        ik_plug.connect_to(part_ik_plug)

        for ik_handle in ik_handles:
            part_ik_plug.connect_to(ik_handle.groups[0].plugs['visibility'])
        part_ik_plug.connect_to(this.knee_line.plugs['visibility'])

        reverse_node = this.create_child(
            DependNode,
            node_type='reverse'
        )
        part_ik_plug.connect_to(reverse_node.plugs['inputX'])
        for fk_handle in fk_handles:
            reverse_node.plugs['outputX'].connect_to(fk_handle.groups[0].plugs['visibility'])
        ik_joints[0].plugs['visibility'].set_value(False)
        fk_joints[0].plugs['visibility'].set_value(False)
        this.ik_match_joint = fk_joints[2].create_child(
            Joint,
            segment_name='IkMatch',
            matrix=this.ankle_handle.get_matrix()
        )
        joints[1].plugs['type'].set_value(2)
        joints[2].plugs['type'].set_value(3)
        joints[3].plugs['type'].set_value(4)
        joints[4].plugs['type'].set_value(5)
        for joint in joints:
            joint.plugs['side'].set_value({'center': 0, 'left': 1, 'right': 2, None: 3}[side])
        this.joints = joints
        root = this.get_root()
        root.add_plugs(
            ik_plug,
            hip_handle.plugs['tx'],
            hip_handle.plugs['ty'],
            hip_handle.plugs['tz'],
            hip_handle.plugs['rx'],
            hip_handle.plugs['ry'],
            hip_handle.plugs['rz']
        )

        this.settings_handle = settings_handle

        (
            front_pivot_matrix,
            back_pivot_matrix,
            in_pivot_matrix,
            out_pivot_matrix,
        ) = matrices[6:10]  # offset by ONE

        front_pivot_position = front_pivot_matrix.get_translation()
        back_pivot_position = back_pivot_matrix.get_translation()
        out_pivot_position = out_pivot_matrix.get_translation()
        in_pivot_position = in_pivot_matrix.get_translation()

        center_pivot_position = (
            front_pivot_position
            + back_pivot_position
        ) / 2

        ball_pivot_matrix = compose_matrix(
            (center_pivot_position + front_pivot_position) / 2,
            front_pivot_position,
            out_pivot_position
        )
        heel_pivot_matrix = compose_matrix(
            (center_pivot_position + back_pivot_position) / 2,
            front_pivot_position,
            out_pivot_position
        )

        heel_placement = this.joints[3].create_child(
            Transform,
            segment_name='HeelPlacement',
            matrix=heel_pivot_matrix,
        )
        translate_z = heel_placement.plugs['translateZ'].get_value()
        placement_offset = foot_placement_depth * 0.5 if side == 'left' else foot_placement_depth * -0.5
        heel_placement.plugs.set_values(
            translateZ=translate_z + placement_offset
        )
        heel_placement_mesh = heel_placement.create_child(
            DagNode,
            node_type='mesh',
            segment_name='HeelPlacement'
        )
        heel_placement_mesh.plugs['hideOnPlayback'].set_value(True)
        heel_placement_poly_cube = this.create_child(
            DependNode,
            node_type='polyCube',
            segment_name='HeelPlacement'
        )
        heel_placement_poly_cube.plugs['output'].connect_to(
            heel_placement_mesh.plugs['inMesh'],
        )
        heel_placement_poly_cube.plugs.set_values(
            width=foot_placement_depth,
            height=(center_pivot_position - back_pivot_position).magnitude(),
            depth=(in_pivot_position - out_pivot_position).magnitude(),
        )
        this.heel_placement_node = heel_placement


        ball_placement = this.joints[4].create_child(
            Transform,
            segment_name='BallPlacement',
            matrix=ball_pivot_matrix,
        )
        translate_z = ball_placement.plugs['translateZ'].get_value()
        placement_offset = foot_placement_depth * 0.5 if side == 'left' else foot_placement_depth * -0.5
        ball_placement.plugs.set_values(
            translateZ=translate_z + placement_offset
        )
        ball_placement_mesh = ball_placement.create_child(
            DagNode,
            node_type='mesh',
            segment_name='BallPlacement',
        )
        ball_placement_mesh.plugs['hideOnPlayback'].set_value(True)
        ball_placement_poly_cube = this.create_child(
            DependNode,
            node_type='polyCube',
            segment_name='BallPlacement',
        )
        ball_placement_poly_cube.plugs['output'].connect_to(
            ball_placement_mesh.plugs['inMesh'],
        )
        ball_placement_poly_cube.plugs.set_values(
            width=foot_placement_depth,
            height=(front_pivot_position - center_pivot_position).magnitude(),
            depth=(in_pivot_position - out_pivot_position).magnitude(),
        )

        heel_placement_mesh.assign_shading_group(root.shaders[side].shading_group)
        ball_placement_mesh.assign_shading_group(root.shaders[side].shading_group)

        this.ball_placement_node = ball_placement
        this.ik_joints = ik_joints
        this.ik_handles = ik_handles
        this.fk_handles = fk_handles
        this.fk_joints = fk_joints

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
        for i in range(len(positions[0:4])):
            self.fk_handles.handles[i].set_matrix(Matrix(positions[i]))

    def match_to_ik(self):
        self.settings_handle.plugs['ikSwitch'].set_value(1.0)
        positions = [x.get_matrix() for x in self.fk_joints]
        pole_position = rmu.calculate_pole_vector_position(
                positions[0].get_translation(),
                positions[1].get_translation(),
                positions[2].get_translation(),
                distance=self.size*10
            )
        self.knee_handle.set_matrix(Matrix(pole_position))
        self.ankle_handle.set_matrix(self.ik_match_joint.get_matrix())
        self.toe_handle.set_matrix(positions[3])