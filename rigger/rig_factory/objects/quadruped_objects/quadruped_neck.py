from Snowman3.rigger.rig_factory.objects.part_objects.spline_chain_guide import SplineChainGuide
from Snowman3.rigger.rig_factory.objects.quadruped_objects.quadruped_neck_ik import QuadrupedNeckIk
from Snowman3.rigger.rig_factory.objects.quadruped_objects.quadruped_neck_fk import QuadrupedNeckFk
from Snowman3.rigger.rig_factory.objects.node_objects.depend_node import DependNode
from Snowman3.rigger.rig_factory.objects.node_objects.nurbs_curve import NurbsCurve
from Snowman3.rigger.rig_factory.objects.rig_objects.grouped_handle import GroupedHandle
from Snowman3.rigger.rig_factory.objects.base_objects.properties import ObjectProperty, ObjectListProperty, DataProperty
from Snowman3.rigger.rig_factory.objects.node_objects.transform import Transform
from Snowman3.rigger.rig_factory.objects.node_objects.locator import Locator
from Snowman3.rigger.rig_factory.objects.node_objects.joint import Joint
from Snowman3.rigger.rig_factory.objects.node_objects.mesh import Mesh
from Snowman3.rigger.rig_factory.objects.part_objects.part import Part
from Snowman3.rigger.rig_math.matrix import Matrix
import Snowman3.rigger.rig_factory.environment as env
import Snowman3.rigger.rig_factory.utilities.node_utilities.ik_handle_utilities as iks
import Snowman3.rigger.rig_factory as rig_factory


class QuadrupedNeckGuide(SplineChainGuide):

    default_head_scale = 4

    head_cube = ObjectProperty(
        name='head_cube'
    )
    base_joints = ObjectListProperty(
        name='base_joints'
    )
    default_settings = dict(
        root_name='Neck',
        size=5.0,
        side='center',
        joint_count=25,
        count=6
    )

    def __init__(self, **kwargs):
        super(QuadrupedNeckGuide, self).__init__(**kwargs)
        self.toggle_class = QuadrupedNeck.__name__

    @classmethod
    def create(cls, **kwargs):
        if kwargs.get('count', 9) < 5:
            raise Exception('Minimum count is 5')
        this = super(QuadrupedNeckGuide, cls).create(**kwargs)
        controller = this.controller
        root = this.get_root()
        side = this.side
        size = this.size

        head_matrix = kwargs.get('head_matrix', None)
        if head_matrix is None:
            head_scale = size*cls.default_head_scale
            head_matrix = Matrix([0.0, head_scale*.5, 0.0])
            head_matrix.set_scale([head_scale] * 3)
        cube_group_transform = this.create_child(
            Transform,
            root_name='HeadTop'
        )
        cube_transform = cube_group_transform.create_child(
            Transform,
            root_name='Head'
        )
        cube_node = cube_transform.create_child(
            DependNode,
            node_type='polyCube',
        )
        cube_mesh = cube_transform.create_child(
            Mesh
        )
        cube_node.plugs['output'].connect_to(cube_mesh.plugs['inMesh'])
        cube_transform.set_matrix(
            head_matrix,
            world_space=False
        )
        cube_mesh.assign_shading_group(root.shaders[side].shading_group)
        root.add_plugs([
            cube_transform.plugs['tx'],
            cube_transform.plugs['ty'],
            cube_transform.plugs['tz'],
            cube_transform.plugs['rx'],
            cube_transform.plugs['ry'],
            cube_transform.plugs['rz'],
            cube_transform.plugs['sx'],
            cube_transform.plugs['sy'],
            cube_transform.plugs['sz']
        ])
        controller.create_point_constraint(
            this.joints[-1],
            cube_group_transform
        )
        this.head_cube = cube_transform
        this.base_joints = list(this.joints)
        this.joints.extend(this.spline_joints)
        return this

    def get_blueprint(self):
        blueprint = super(QuadrupedNeckGuide, self).get_blueprint()
        blueprint['head_matrix'] = list(self.head_cube.get_matrix(world_space=False))
        return blueprint

    def get_toggle_blueprint(self):
        blueprint = super(QuadrupedNeckGuide, self).get_toggle_blueprint()
        blueprint['head_matrix'] = list(self.head_cube.get_matrix(world_space=False))
        blueprint['matrices'] = [list(x.get_matrix()) for x in self.base_joints]
        return blueprint


class QuadrupedNeck(Part):

    spline_joints = ObjectListProperty(
        name='spline_joints'
    )

    settings_handle = ObjectProperty(
        name='settings_handle'
    )
    head_matrix = DataProperty(
        name='head_matrix',
        default_value=list(Matrix())
    )
    tangent_group = ObjectProperty(
        name='tangent_group'
    )
    head_handle = ObjectProperty(
        name='head_handle'
    )

    fk_head_handle = ObjectProperty(
        name='fk_head_handle'
    )

    ik_head_handle = ObjectProperty(
        name='ik_head_handle'
    )

    fk_handles = ObjectListProperty(
        name='fk_handles'
    )

    ik_handles = ObjectListProperty(
        name='ik_handles'
    )

    ik_joints = ObjectListProperty(
        name='ik_joints'
    )

    fk_joints = ObjectListProperty(
        name='fk_joints'
    )

    joint_matrices = []

    def __init__(self, **kwargs):
        super(QuadrupedNeck, self).__init__(**kwargs)

    @classmethod
    def create(cls, **kwargs):
        this = super(QuadrupedNeck, cls).create(**kwargs)
        controller = this.controller
        root = this.get_root()
        size = this.size
        matrices = this.matrices

        joint_matrices = this.joint_matrices
        curve_degree = 3
        root = this.get_root()

        # FkNeck
        this.differentiation_name = 'Fk'
        fk_group = this.create_child(
            Transform,
            segment_name='SubPart',
            matrix=Matrix()
        )
        this.top_group = fk_group
        QuadrupedNeckFk.build_rig(this)
        fk_head_handle = this.head_handle
        fk_joints = list(this.joints)
        fk_handles = list(this.handles)
        this.handles = []
        this.joints = []
        this.top_group = None

        # IkNeck
        this.differentiation_name = 'Ik'
        ik_group = this.create_child(
            Transform,
            segment_name='SubPart',
            matrix=Matrix()
        )
        this.top_group = ik_group
        QuadrupedNeckIk.build_rig(this)
        ik_head_handle = this.head_handle
        ik_joints = list(this.joints)
        ik_handles = list(this.handles)
        this.differentiation_name = None
        this.top_group = this

        joints = []
        joint_parent = this.joint_group
        for i in range(len(matrices)):
            if i == 0:
                segment_name = 'Root'
            else:
                segment_name = rig_factory.index_dictionary[i - 1].title()
            joint = this.create_child(
                Joint,
                parent=joint_parent,
                matrix=matrices[i],
                segment_name=segment_name
            )
            joint_parent = joint
            joint.zero_rotation()
            joints.append(joint)

        settings_offset_mx = Matrix(
            0, -1, 0, 0,
            1, 0, 0, 0,
            0, 0, 1, 0,
            0, 0, -2*size, 1
        )
        settings_handle = this.create_handle(
            handle_type=GroupedHandle,
            segment_name='Settings',
            shape='gear_simple',
            matrix=Matrix(matrices[0]) * settings_offset_mx,
            size=size * 0.5,
            group_count=1,
        )
        settings_handle.plugs.set_values(
            overrideEnabled=True,
            overrideRGBColors=True,
            overrideColorRGB=env.colors['highlight'],
        )

        ik_plug = settings_handle.create_plug(
            'IkSwitch',
            at='double',
            k=True,
            dv=0.0,
            min=0.0,
            max=1.0
        )
        ik_plug.connect_to(ik_group.plugs['visibility'])
        root.add_plugs(ik_plug)

        for i, joint in enumerate(joints):

            index_character = rig_factory.index_dictionary[i].upper()
            joint.plugs['overrideEnabled'].set_value(True)
            joint.plugs['overrideDisplayType'].set_value(2)
            joint.plugs['rotateOrder'].connect_to(fk_joints[i].plugs['rotateOrder'])

            pair_blend = this.create_child(
                DependNode,
                node_type='pairBlend',
                segment_name='Blend%s' % index_character
            )
            # pair_blend.plugs['rotInterpolation'].set_value(1)
            ik_joints[i].plugs['translate'].connect_to(pair_blend.plugs['inTranslate2'])
            fk_joints[i].plugs['translate'].connect_to(pair_blend.plugs['inTranslate1'])
            ik_joints[i].plugs['rotate'].connect_to(pair_blend.plugs['inRotate2'])
            fk_joints[i].plugs['rotate'].connect_to(pair_blend.plugs['inRotate1'])
            pair_blend.plugs['outTranslate'].connect_to(joint.plugs['translate'])
            pair_blend.plugs['outRotate'].connect_to(joint.plugs['rotate'])
            ik_plug.connect_to(pair_blend.plugs['weight'])

        visibility_reverse = this.create_child(
            DependNode,
            segment_name='Visibility',
            node_type='reverse'
        )
        ik_plug.connect_to(visibility_reverse.plugs['inputX'])
        visibility_reverse.plugs['outputX'].connect_to(fk_group.plugs['visibility'])

        for joint in joints[0:-1]:
            joint.plugs['type'].set_value(7)

        curve_locators = []
        for deform_joint in joints:
            blend_locator = deform_joint.create_child(Locator)
            blend_locator.plugs['v'].set_value(0)
            curve_locators.append(blend_locator)

        for deform_joint in joints[1:-1]:
            deform_joint.plugs['drawStyle'].set_value(2)

        nurbs_curve_transform = this.create_child(
            Transform,
            segment_name='Spline'
        )

        nurbs_curve = nurbs_curve_transform.create_child(
            NurbsCurve,
            degree=curve_degree,
            positions=[[0.0] * 3 for _ in curve_locators]
        )
        nurbs_curve_transform.plugs['inheritsTransform'].set_value(False)
        nurbs_curve_transform.plugs['visibility'].set_value(False)

        curve_info = this.create_child(
            DependNode,
            segment_name='CurveInfo',
            node_type='curveInfo'
        )

        scale_divide = this.create_child(
            DependNode,
            segment_name='Scale',
            node_type='multiplyDivide'
        )
        scale_divide.plugs['operation'].set_value(2)
        this.scale_multiply_transform.plugs['scale'].connect_to(scale_divide.plugs['input2'])
        curve_info.plugs['arcLength'].connect_to(scale_divide.plugs['input1X'])
        curve_info.plugs['arcLength'].connect_to(scale_divide.plugs['input1Y'])
        curve_info.plugs['arcLength'].connect_to(scale_divide.plugs['input1Z'])
        nurbs_curve.plugs['worldSpace'].element(0).connect_to(curve_info.plugs['inputCurve'])

        length_divide = this.create_child(
            DependNode,
            segment_name='Length',
            node_type='multiplyDivide'
        )
        length_divide.plugs['operation'].set_value(2)
        length_divide.plugs['input2Y'].set_value(len(joint_matrices) - 1)
        scale_divide.plugs['output'].connect_to(length_divide.plugs['input1'])

        for i, blend_locator in enumerate(curve_locators):
            blend_locator.plugs['worldPosition'].element(0).connect_to(
                nurbs_curve.plugs['controlPoints'].element(i)
            )
        spline_joint_parent = joints[0]

        spline_joints = []
        if len(joint_matrices) > 1:
            for i, matrix in enumerate(joint_matrices):

                if i == len(joint_matrices) - 1:
                    spline_segment_name = 'Head'
                else:
                    spline_segment_name = 'Secondary%s' % rig_factory.index_dictionary[i].title()

                spline_joint = spline_joint_parent.create_child(
                    Joint,
                    segment_name=spline_segment_name,
                    matrix=matrix
                )
                spline_joint.plugs.set_values(
                    overrideEnabled=True,
                    overrideRGBColors=True,
                    overrideColorRGB=env.colors['bindJoints'],
                    overrideDisplayType=0
                )
                spline_joint.zero_rotation()
                spline_joints.append(spline_joint)
                spline_joint_parent = spline_joint

                root.add_plugs(
                    [
                        spline_joint.plugs['rx'],
                        spline_joint.plugs['ry'],
                        spline_joint.plugs['rz']
                    ],
                    keyable=False
                )

                if i != 0:
                    length_divide.plugs['outputY'].connect_to(
                        spline_joint.plugs['t' + env.aim_vector_axis]
                    )
            controller.create_point_constraint(
                joints[0],
                spline_joints[0]
            )
            controller.create_parent_constraint(
                joints[-1],
                spline_joints[-1]
            )

            spline_ik_handle = iks.create_spline_ik(
                spline_joints[0],
                spline_joints[-2],
                nurbs_curve,
                world_up_object=joints[0],
                world_up_object_2=joints[-1],
                up_vector=[-1.0, 0.0, 0.0],
                up_vector_2=[-1.0, 0.0, 0.0],
                world_up_type=4
            )
            spline_ik_handle.plugs['visibility'].set_value(False)

        joints.extend(spline_joints)
        handles = [settings_handle]
        handles.extend(ik_handles)
        handles.extend(fk_handles)
        this.spline_joints = spline_joints
        this.ik_handles = ik_handles
        this.ik_joints = ik_joints
        this.ik_head_handle = ik_head_handle
        this.fk_head_handle = fk_head_handle
        this.settings_handle = settings_handle
        this.set_handles(handles)
        this.joints = joints
        return this

    def get_blueprint(self):
        blueprint = super(QuadrupedNeck, self).get_blueprint()
        blueprint['joint_matrices'] = [list(x) for x in self.joint_matrices]
        blueprint['head_matrix'] = self.head_matrix
        return blueprint



