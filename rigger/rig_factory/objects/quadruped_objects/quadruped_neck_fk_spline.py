import Snowman3.rigger.rig_factory as rig_factory
import os
from Snowman3.rigger.rig_factory.objects.part_objects.spline_chain_guide import SplineChainGuide
from Snowman3.rigger.rig_factory.objects.quadruped_objects.quadruped_neck_fk import QuadrupedNeckFk
from Snowman3.rigger.rig_factory.objects.rig_objects.grouped_handle import CogHandle, GroupedHandle
from Snowman3.rigger.rig_factory.objects.node_objects.depend_node import DependNode
from Snowman3.rigger.rig_factory.objects.node_objects.nurbs_curve import NurbsCurve
from Snowman3.rigger.rig_factory.objects.base_objects.properties import ObjectProperty, ObjectListProperty, DataProperty
from Snowman3.rigger.rig_factory.objects.node_objects.transform import Transform
from Snowman3.rigger.rig_factory.objects.node_objects.locator import Locator
from Snowman3.rigger.rig_factory.objects.node_objects.joint import Joint
from Snowman3.rigger.rig_factory.objects.node_objects.mesh import Mesh
from Snowman3.rigger.rig_math.matrix import Matrix
import Snowman3.rigger.rig_factory.environment as env
import Snowman3.rigger.rig_factory.utilities.node_utilities.ik_handle_utilities as iks
from Snowman3.rigger.rig_factory.objects.part_objects.part import Part
import Snowman3.rigger.rig_factory.positions as pos


class QuadrupedNeckFkSplineGuide(SplineChainGuide):

    default_head_scale = 2.0

    head_cube = ObjectProperty(
        name='ik_neck'
    )
    head_matrix = DataProperty(
        name='head_matrix',
        default_value=list(Matrix())
    )
    base_joints = ObjectListProperty(
        name='base_joints'
    )

    default_settings = dict(
        root_name='Neck',
        size=8.0,
        side='center',
        joint_count=9,
        count=5,
        use_plugins=os.getenv('USE_RIG_PLUGINS', False)
    )

    def __init__(self, **kwargs):
        kwargs.setdefault('root_name', 'Spine')
        super(QuadrupedNeckFkSplineGuide, self).__init__(**kwargs)
        self.toggle_class = QuadrupedNeckFkSpline.__name__

    @classmethod
    def create(cls, **kwargs):
        this = super(QuadrupedNeckFkSplineGuide, cls).create(**kwargs)
        controller = this.controller
        root = this.get_root()
        side = this.side
        size = this.size
        head_matrix = kwargs.get('head_matrix', None)
        if head_matrix is None:
            head_scale = size*cls.default_head_scale
            head_matrix = Matrix([0.0, 0.0, head_scale*0.5])
            head_matrix.set_scale([head_scale] * 3)
        cube_group_transform = this.create_child(
            Transform,
            segment_name='HeadTop'
        )
        cube_transform = cube_group_transform.create_child(
            Transform,
            segment_name='Head'
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
        head_joint = this.joints[-1].create_child(
            Joint,
            segment_name='Head',
        )
        controller.create_point_constraint(
            this.joints[-1],
            cube_group_transform
        )
        controller.create_point_constraint(
            cube_group_transform,
            head_joint,
            mo=False
        )
        this.head_cube = cube_transform

        this.base_joints = list(this.joints)
        this.joints.extend(this.spline_joints)
        this.joints.append(head_joint)

        this.set_handle_positions(pos.QUADRUPED_POSITIONS)

        return this

    def get_blueprint(self):
        blueprint = super(QuadrupedNeckFkSplineGuide, self).get_blueprint()
        blueprint['head_matrix'] = list(self.head_cube.get_matrix(world_space=False))
        return blueprint

    def get_toggle_blueprint(self):
        blueprint = super(QuadrupedNeckFkSplineGuide, self).get_toggle_blueprint()
        blueprint['head_matrix'] = list(self.head_cube.get_matrix(world_space=False))
        blueprint['matrices'] = [list(x.get_matrix()) for x in self.base_joints]
        return blueprint


class QuadrupedNeckFkSpline(Part):

    spline_joints = ObjectListProperty(
        name='spline_joints'
    )
    head_handle = ObjectProperty(
        name='head_handle'
    )
    tangent_group = ObjectProperty(
        name='tangent_group'
    )
    head_matrix = DataProperty(
        name='head_matrix',
        default_value=list(Matrix())
    )
    settings_handle = ObjectProperty(
        name='settings_handle'
    )

    joint_matrices = []

    def __init__(self, **kwargs):
        super(QuadrupedNeckFkSpline, self).__init__(**kwargs)

    @classmethod
    def create(cls, **kwargs):
        this = super(QuadrupedNeckFkSpline, cls).create(**kwargs)
        controller = this.controller
        QuadrupedNeckFk.build_rig(this)
        fk_joints = this.joints
        matrices = this.matrices
        root = this.get_root()
        size = this.size
        settings_handle = this.create_handle(
            handle_type=GroupedHandle,
            segment_name='Settings',
            shape='gear_simple',
            size=size * 0.5,
            group_count=1,
            parent=this.handles[0]
        )
        settings_handle.groups[0].plugs.set_values(
            rz=-90,
            tz=-1.5 * size
        )
        settings_handle.plugs.set_values(
            overrideEnabled=True,
            overrideRGBColors=True,
            overrideColorRGB=env.colors['highlight']
        )
        settings_handle.create_plug(
            'squash',
            attributeType='float',
            keyable=True,
            defaultValue=0.0,
        )
        settings_handle.create_plug(
            'squashMin',
            attributeType='float',
            keyable=True,
            defaultValue=-0.75,
        )
        settings_handle.create_plug(
            'squashMax',
            attributeType='float',
            keyable=True,
            defaultValue=1,
        )
        root.add_plugs(
            [
                settings_handle.plugs['squash'],
                settings_handle.plugs['squashMin'],
                settings_handle.plugs['squashMax'],
            ]
        )
        head_tangent_target_group = this.head_handle.gimbal_handle.create_child(
            Transform,
            segment_name='HeadTangentTarget',
            matrix=matrices[-2]
        )
        tangent_group = this.create_child(
            Transform,
            segment_name='Tangent',
            matrix=matrices[-2]
        )
        constraint = controller.create_parent_constraint(
            head_tangent_target_group,
            this.head_handle.gimbal_handle,
            tangent_group
        )
        tangent_plug = this.head_handle.create_plug(
            'breakTangent',
            at='double',
            k=True,
            dv=0.0,
            max=1.0,
            min=0.0
        )
        reverse_node = this.create_child(
            DependNode,
            node_type='reverse',
            segment_name='Tangent',
        )
        tangent_plug.connect_to(reverse_node.plugs['inputX'])
        tangent_plug.connect_to(
            constraint.plugs['%sW0' % head_tangent_target_group]
        )
        reverse_node.plugs['outputX'].connect_to(
            constraint.plugs['%sW1' % this.head_handle.gimbal_handle]
        )

        controller = this.controller
        joint_matrices = this.joint_matrices
        curve_degree = 3
        root = this.get_root()


        spline_joint_parent = fk_joints[0]
        spline_joints = []
        for i, matrix in enumerate(joint_matrices):
            spline_segment_name = 'Secondary%s' % rig_factory.index_dictionary[i].title()
            spline_joint = spline_joint_parent.create_child(
                Joint,
                segment_name=spline_segment_name,
                matrix=matrix
            )
            spline_joint.plugs.set_values(
                drawStyle=2
            )
            if spline_joints:
                spline_joints[-1].plugs['scale'].connect_to(
                    spline_joint.plugs['inverseScale'],
                )
            spline_joint.zero_rotation()
            spline_joints.append(spline_joint)
            spline_joint_parent = spline_joint

        head_joint = fk_joints[-1].create_child(
            Joint,
            segment_name='Head',
        )

        curve_locators = []
        for joint in fk_joints:
            blend_locator = joint.create_child(Locator)
            blend_locator.plugs['v'].set_value(0)
            curve_locators.append(blend_locator)

        nurbs_curve_transform = this.create_child(
            Transform,
            segment_name='Spline',
        )

        nurbs_curve = nurbs_curve_transform.create_child(
            NurbsCurve,
            degree=curve_degree,
            positions=[[0.0] * 3 for _ in curve_locators]
        )
        nurbs_curve_transform.plugs['inheritsTransform'].set_value(False)
        nurbs_curve_transform.plugs['visibility'].set_value(False)

        curve_info = nurbs_curve.create_child(
            DependNode,
            node_type='curveInfo'
        )

        scale_divide = nurbs_curve.create_child(
            DependNode,
            segment_name='ScaleDivide',
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
            segment_name='LengthDivide',
            node_type='multiplyDivide'
        )
        length_divide.plugs['operation'].set_value(2)
        length_divide.plugs['input2Y'].set_value(len(joint_matrices) - 1)
        scale_divide.plugs['output'].connect_to(length_divide.plugs['input1'])

        for i, blend_locator in enumerate(curve_locators):
            blend_locator.plugs['worldPosition'].element(0).connect_to(
                nurbs_curve.plugs['controlPoints'].element(i)
            )
        for i, spline_joint in enumerate(spline_joints):
            root.add_plugs(
                [
                    spline_joint.plugs['rx'],
                    spline_joint.plugs['ry'],
                    spline_joint.plugs['rz']
                ],
                keyable=False
            )
            if i not in (0, len(joint_matrices) - 1):
                length_divide.plugs['outputY'].connect_to(
                    spline_joint.plugs['t' + env.aim_vector_axis]
                )
        controller.create_point_constraint(
            fk_joints[0],
            spline_joints[0]
        )
        controller.create_parent_constraint(
            fk_joints[-1],
            spline_joints[-1]
        )
        spline_ik_handle = iks.create_spline_ik(
            spline_joints[0],
            spline_joints[-2],
            nurbs_curve,
            world_up_object=fk_joints[0],
            world_up_object_2=fk_joints[-1],
            up_vector=[-1.0, 0.0, 0.0],
            up_vector_2=[-1.0, 0.0, 0.0],
            world_up_type=4
        )
        spline_ik_handle.plugs['visibility'].set_value(False)
        this.spline_joints = spline_joints
        this.joints.extend(spline_joints)
        this.joints.append(head_joint)
        this.tangent_group = tangent_group
        this.settings_handle = settings_handle
        return this


    def get_blueprint(self):
        blueprint = super(QuadrupedNeckFkSpline, self).get_blueprint()
        blueprint['joint_matrices'] = [list(x) for x in self.joint_matrices]
        blueprint['head_matrix'] = self.head_matrix

        return blueprint

