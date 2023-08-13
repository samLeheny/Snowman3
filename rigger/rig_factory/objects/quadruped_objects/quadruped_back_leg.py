from Snowman3.rigger.rig_factory.objects.part_objects.chain_guide import ChainGuide
from Snowman3.rigger.rig_factory.objects.base_objects.properties import ObjectProperty, DataProperty, ObjectListProperty
from Snowman3.rigger.rig_factory.objects.part_objects.part import Part
from Snowman3.rigger.rig_factory.objects.quadruped_objects.quadruped_back_leg_ik import QuadrupedBackLegIk, QuadrupedBackLegIkGuide
from Snowman3.rigger.rig_factory.objects.quadruped_objects.quadruped_back_leg_fk import QuadrupedBackLegFk
from Snowman3.rigger.rig_factory.objects.node_objects.dag_node import DagNode
from Snowman3.rigger.rig_factory.objects.node_objects.depend_node import DependNode
from Snowman3.rigger.rig_factory.objects.node_objects.joint import Joint
from Snowman3.rigger.rig_factory.objects.node_objects.transform import Transform
from Snowman3.rigger.rig_factory.objects.rig_objects.grouped_handle import LocalHandle
from Snowman3.rigger.rig_factory.objects.rig_objects.grouped_handle import GroupedHandle
from Snowman3.rigger.rig_factory.objects.rig_objects.cone import Cone
from Snowman3.rigger.rig_math.matrix import compose_matrix
from Snowman3.rigger.rig_math.matrix import Matrix
from Snowman3.rigger.rig_math.vector import Vector
import Snowman3.rigger.rig_factory.environment as env
import Snowman3.rigger.rig_factory.positions as pos
import Snowman3.rigger.rig_factory.utilities.limb_utilities as limb_utilities


class QuadrupedBackLegGuide(ChainGuide):
    segment_names = DataProperty(
        name='segment_names',
        default_value=['Base', 'Hip', 'Knee', 'Ankle', 'Foot', 'Toe'],
        foot_placement_depth=1.0,
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
        world_space_foot=True,
        create_plane=True
    )

    limb_plane = ObjectProperty(
        name='limb_plane'
    )

    foot_placement_depth = DataProperty(
        name='foot_placement_depth'
    )
    create_plane = DataProperty(
        name='create_plane',
        default_value=True
    )

    def __init__(self, **kwargs):
        super(QuadrupedBackLegGuide, self).__init__(**kwargs)
        self.toggle_class = QuadrupedBackLeg.__name__

    @classmethod
    def create(cls, **kwargs):
        kwargs['count'] = 6
        kwargs['up_vector_indices'] = [0, 1, 4]
        this = super(QuadrupedBackLegGuide, cls).create(**kwargs)
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
        this.handles[2].plugs['translateZ'].set_value(size*0.1)
        this.set_handle_positions(pos.QUADRUPED_POSITIONS)
        limb_utilities.make_ik_plane(this, this.base_handles[1], this.base_handles[4], this.up_handles[1])
        return this

    def get_toggle_blueprint(self):
        blueprint = super(QuadrupedBackLegGuide, self).get_toggle_blueprint()
        matrices = [list(x.get_matrix()) for x in self.joints]
        matrices.extend([list(x.get_matrix()) for x in self.pivot_joints])
        blueprint['matrices'] = matrices
        return blueprint

    def post_create(self, **kwargs):
        super(QuadrupedBackLegGuide, self).post_create(**kwargs)
        if self.create_plane:
            # geometry constrain knee
            self.controller.create_geometry_constraint(self.limb_plane, self.base_handles[2])
            self.controller.create_geometry_constraint(self.limb_plane, self.base_handles[3])


class QuadrupedBackLeg(Part):
    settings_handle = ObjectProperty(
        name='settings_handle'
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

    pole_distance_multiplier = DataProperty(
        name='pole_distance_multiplier',
        default_value=0.5
    )
    knee_line = ObjectProperty(
        name='knee_line'
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

    stretchable_attr_object = ObjectProperty(
        name='stretchable_attr_object'
    )

    rollfixjoints =  ObjectListProperty(
        name='rollfixjoints'
    )

    segment_names = DataProperty(
        name='segment_names',
        default_value=['Base', 'Hip', 'Knee', 'Ankle', 'Foot', 'Toe']
    )
    world_space_foot = DataProperty(
        name='world_space_foot',
        default_value=True
    )

    foot_placement_depth = DataProperty(
        name='foot_placement_depth',
        default_value=1.0
    )
    ball_placement_node = ObjectProperty(
        name='ball_placement_node'
    )

    @classmethod
    def create(cls, **kwargs):
        if 'side' not in kwargs:
            raise Exception('you must provide a "side" keyword argument to create a %s' % cls.__name__)
        this = super(QuadrupedBackLeg, cls).create(**kwargs)
        cls.build_rig(this)
        return this

    @staticmethod
    def build_rig(this):
        controller = this.controller
        root_name = this.root_name
        matrices = this.matrices
        side = this.side
        size = this.size
        joint_parent = this.joint_group
        foot_placement_depth = this.foot_placement_depth

        joints = []
        for i in range(6):
            segment_name = this.segment_names[i]
            joint = this.create_child(
                Joint,
                segment_name=segment_name,
                parent=joint_parent,
                matrix=matrices[i]
            )
            joint.zero_rotation()
            joints.append(joint)
            joint_parent = joint
            joint.plugs['overrideEnabled'].set_value(True)
            joint.plugs['overrideDisplayType'].set_value(2)

        hip_vector = matrices[1].get_translation() - matrices[0].get_translation()
        hip_length = hip_vector.mag() if side != 'right' else hip_vector.mag() * -1.0

        hip_shape_matrix = Matrix(
            hip_length * 0.5,
            hip_length * 0.5,
            0.0,
            scale=
            [
                size * 2 if side != 'right' else size * -2,
                size * 2,
                size * 2
            ])

        hip_handle = this.create_handle(
            handle_type=LocalHandle,
            segment_name=this.segment_names[0],
            matrix=matrices[0],
            shape='c_curve',
            axis='y',
            rotation_order='xzy',
            size=size
        )

        # hip_handle.stretch_shape(matrices[1])

        hip_handle.set_shape_matrix(hip_shape_matrix)

        # Prepare to create Fk Leg
        origonal_segment_names = this.segment_names
        this.segment_names = this.segment_names[1:]  # Fk/Ik Arms do not have a base joint
        this.handles = []
        this.differentiation_name = 'Fk'
        fk_group = this.create_child(
            Transform,
            segment_name='SubPart',
            parent=hip_handle.gimbal_handle,
            matrix=Matrix()
        )
        this.top_group = fk_group
        this.matrices = matrices[1:]
        # Create Fk Leg
        QuadrupedBackLegFk.build_rig(this)
        fk_joints = list(this.joints)
        fk_handles = list(this.handles)

        # Prepare to create Ik Leg
        this.handles = []
        this.joints = []
        this.differentiation_name = 'Ik'
        ik_group = this.create_child(
            Transform,
            segment_name='SubPart',
            parent=hip_handle.gimbal_handle,
            matrix=Matrix()
        )
        this.top_group = ik_group
        this.matrices = matrices[1:]
        # Create Ik Leg
        QuadrupedBackLegIk.build_rig(this)
        ik_joints = list(this.joints)
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
        this.hip_handle.groups[0].set_parent(hip_handle.gimbal_handle)
        fk_handles[0].groups[0].set_parent(hip_handle.gimbal_handle)

        part_ik_plug = this.create_plug(
            'ik_switch',
            at='double',
            k=True,
            dv=0.0,
            min=0.0,
            max=1.0
        )

        for i in range(len(joints)):
            joint = joints[i]
            segment_name = this.segment_names[i]
            if i > 0 :
                pair_blend = this.create_child(
                    DependNode,
                    node_type='pairBlend',
                    segment_name=segment_name
                )
                x = i - 1
                ik_joints[x].plugs['translate'].connect_to(pair_blend.plugs['inTranslate2'])
                fk_joints[x].plugs['translate'].connect_to(pair_blend.plugs['inTranslate1'])
                ik_joints[x].plugs['rotate'].connect_to(pair_blend.plugs['inRotate2'])
                fk_joints[x].plugs['rotate'].connect_to(pair_blend.plugs['inRotate1'])
                pair_blend.plugs['outTranslate'].connect_to(joint.plugs['translate'])
                pair_blend.plugs['outRotate'].connect_to(joint.plugs['rotate'])
                pair_blend.plugs['rotInterpolation'].set_value(1)
                part_ik_plug.connect_to(pair_blend.plugs['weight'])
                joint.plugs['rotateOrder'].connect_to(fk_joints[x].plugs['rotateOrder'])
                joint.plugs['rotateOrder'].connect_to(ik_joints[x].plugs['rotateOrder'])

        controller.create_parent_constraint(
            hip_handle.gimbal_handle,
            joints[0],
            mo=True
        )
        fk_joints[0].set_parent(joints[0])
        ik_joints[0].set_parent(joints[0])
        # ik_leg.ik_joints[0].set_parent(joints[0])

        settings_position = matrices[4].get_translation() + Vector(
            [
                size * -2 if side == 'right' else size * 2,
                0.0,
                0.0
            ])
        settings_handle = this.create_handle(
            handle_type=GroupedHandle,
            segment_name='Settings',
            shape='gear_simple',
            axis='z',
            matrix=Matrix(settings_position),
            parent=joints[4],
            size=size * 0.75,
            group_count=1
        )
        settings_handle.plugs.set_values(
            overrideEnabled=True,
            overrideRGBColors=True,
            overrideColorRGB=env.colors['highlight']
        )

        ik_plug = settings_handle.create_plug(
            'ik_switch',
            at='double',
            k=True,
            dv=1.0,
            min=0.0,
            max=1.0
        )

        ik_hip_visibility_plug = settings_handle.create_plug(
            'ik_hip_visibility',
            at='double',
            k=True,
            dv=1.0,
            min=0.0,
            max=1.0
        )

        part_ik_plug.connect_to(this.knee_line.plugs['visibility'])
        ik_hip_visibility_plug.connect_to(this.hip_handle.groups[0].plugs['visibility'])
        ik_plug.connect_to(part_ik_plug)
        for handle in ik_handles:
            part_ik_plug.connect_to(handle.plugs['visibility'])
        reverse_node = this.create_child(
            DependNode,
            node_type='reverse'
        )
        part_ik_plug.connect_to(reverse_node.plugs['inputX'])
        for handle in fk_handles:
            reverse_node.plugs['outputX'].connect_to(handle.plugs['visibility'])
        ik_joints[0].plugs['visibility'].set_value(False)
        fk_joints[0].plugs['visibility'].set_value(False)

        # toe roll
        toe_roll_clamp_plug = this.create_plug('ToeRollClamp', at='double')
        toe_roll_clamp = this.create_child(
            DependNode,
            node_type='clamp',
            segment_name='ToeRollClamp',
        )
        toe_roll_md = this.create_child(
            DependNode,
            node_type='multiplyDivide',
            segment_name='ToeRollMD',
        )
        this.foot_handle.plugs['footRoll'].connect_to(toe_roll_clamp.plugs['inputR'])
        this.foot_handle.plugs['Break'].connect_to(toe_roll_clamp.plugs['maxR'])
        toe_roll_clamp.plugs['outputR'].connect_to(toe_roll_md.plugs['input1X'])
        toe_roll_md.plugs['input2X'].set_value(-1)
        toe_roll_md.plugs['outputX'].connect_to(toe_roll_clamp_plug)

        fk_joints[3].create_child(
            Joint,
            segment_name='IkMatch',
            matrix=ik_joints[3].get_matrix()
        )

        # add foot placement box
        front_pivot_position = matrices[6].get_translation()
        back_pivot_position = matrices[7].get_translation()
        out_pivot_position = matrices[8].get_translation()
        in_pivot_position = matrices[9].get_translation()

        center_pivot_position = (
            front_pivot_position
            + back_pivot_position
        ) / 2

        ball_pivot_matrix = compose_matrix(
            (center_pivot_position + front_pivot_position) / 2,
            front_pivot_position,
            out_pivot_position
        )

        ball_placement = joints[5].create_child(
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

        # unhide needed attrs
        root = this.get_root()
        root.add_plugs(
            [
                hip_handle.plugs['tx'],
                hip_handle.plugs['ty'],
                hip_handle.plugs['tz'],
                hip_handle.plugs['rx'],
                hip_handle.plugs['ry'],
                hip_handle.plugs['rz'],
                ik_plug,
                ik_hip_visibility_plug
            ]
        )
        ball_placement_mesh.assign_shading_group(root.shaders[side].shading_group)
        this.ball_placement_node = ball_placement
        this.hip_handle = hip_handle
        fk_joints = fk_joints
        ik_joints = ik_joints
        ik_joints[0].plugs['visibility'].set_value(False)
        fk_joints[0].plugs['visibility'].set_value(False)
        this.joints = joints
        this.settings_handle = settings_handle

        return this
