import Snowman3.rigger.rig_factory as rig_factory
from Snowman3.rigger.rig_factory.objects.part_objects.chain_guide import ChainGuide
from Snowman3.rigger.rig_factory.objects.base_objects.properties import ObjectProperty, DataProperty
from Snowman3.rigger.rig_factory.objects.rig_objects.grouped_handle import LocalHandle, WorldHandle
from Snowman3.rigger.rig_factory.objects.node_objects.transform import Transform
from Snowman3.rigger.rig_factory.objects.node_objects.joint import Joint
from Snowman3.rigger.rig_factory.objects.node_objects.mesh import Mesh
from Snowman3.rigger.rig_factory.objects.node_objects.depend_node import DependNode
from Snowman3.rigger.rig_factory.objects.part_objects.part import Part
from Snowman3.rigger.rig_math.matrix import Matrix
import Snowman3.rigger.rig_factory.environment as env
import Snowman3.rigger.rig_factory.positions as pos


class BipedNeckIkGuide(ChainGuide):

    head_matrix = DataProperty( name='head_matrix', default_value=list(Matrix()) )
    head_cube = ObjectProperty( name='head_cube' )
    default_settings = dict(
        root_name='Neck',
        size=1.0,
        side='center',
        joint_count=5,
        count=5
    )

    def __init__(self, **kwargs):
        super(BipedNeckIkGuide, self).__init__(**kwargs)
        self.toggle_class = BipedNeckIk.__name__

    @classmethod
    def create(cls, **kwargs):
        kwargs['up_vector_indices'] = [0]
        kwargs.setdefault('root_name', 'Neck')
        this = super(BipedNeckIkGuide, cls).create(**kwargs)
        head_matrix = this.head_matrix
        size = this.size

        if head_matrix is None:
            head_scale = size * this.default_head_scale
            head_matrix = Matrix([0.0, head_scale * .5, 0.0])
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
        this.head_cube = cube_transform
        this.set_handle_positions(pos.BIPED_POSITIONS)

        return this

    def get_toggle_blueprint(self):
        blueprint = super(BipedNeckIkGuide, self).get_toggle_blueprint()
        blueprint['head_matrix'] = list(self.head_cube.get_matrix(world_space=False))
        return blueprint


class BipedNeckIk(Part):

    head_matrix = DataProperty( name='head_matrix', default_value=list(Matrix()) )
    head_handle = ObjectProperty( name='head_handle' )
    default_head_scale = 4

    @classmethod
    def create(cls, **kwargs):
        if 'side' not in kwargs:
            raise Exception('you must provide a "side" keyword argument to create a ' + cls.__name__)
        this = super(BipedNeckIk, cls).create(**kwargs)
        cls.build_rig(this)
        return this

    @staticmethod
    def build_rig(this):
        controller = this.controller
        matrices = this.matrices
        matrices_len = len(matrices)
        if matrices_len < 4:
            raise Exception('you must provide at least 4 matrices to create a ' + this.__class__.__name__)
        size = this.size
        side = this.side
        root = this.get_root()
        head_matrix = this.head_matrix

        lower_neck_transform = this.create_child(
            Transform,
            segment_name='LowerNeck',
            matrix=Matrix(matrices[1].get_translation())
        )

        center_handles = []
        joint_parent = this.joint_group
        joints = []
        for i, matrix in enumerate(matrices):

            joint = this.create_child(
                Joint,
                segment_name=rig_factory.index_dictionary[i].upper(),
                matrix=matrix,
                parent=joint_parent
            )
            joint.zero_rotation()
            joint.plugs.set_values(
                overrideEnabled=1,
                overrideDisplayType=2,
                visibility=False
            )
            joints.append(joint)
            joint_parent = joint
            if i > 1 and i < len(matrices) - 2:
                center_handle = this.create_handle(
                    handle_type=LocalHandle,
                    segment_name='Mid%s' % rig_factory.index_dictionary[len(center_handles)].title(),
                    size=size,
                    matrix=matrix,
                    side=side,
                    shape='circle',
                    rotation_order='xzy'
                )
                controller.create_parent_constraint(
                    center_handle,
                    joint
                )
                center_handle.plugs.set_values(
                    overrideEnabled=True,
                    overrideRGBColors=True,
                    overrideColorRGB=env.secondary_colors[side]
                )
                center_handles.append(center_handle)

                root.add_plugs([
                    center_handle.plugs['tx'],
                    center_handle.plugs['ty'],
                    center_handle.plugs['tz'],
                    center_handle.plugs['rx'],
                    center_handle.plugs['ry'],
                    center_handle.plugs['rz']
                ])

        head_handle = this.create_handle(
            handle_type=WorldHandle,
            segment_name='Head',
            shape='partial_cube_x',
            matrix=Matrix(matrices[-1].get_translation()),
            parent=this,
            size=size,
            rotation_order='xzy'
        )
        head_handle.plugs['shapeMatrix'].set_value(list(head_matrix))

        tangent_plug = head_handle.create_plug(
            'break_tangent',
            at='double',
            k=True,
            dv=(matrices[-1].get_translation() - matrices[-2].get_translation()).mag() * 0.9,
            max=(matrices[-1].get_translation() - matrices[-2].get_translation()).mag() * 0.9,
            min=(matrices[-2].get_translation() - matrices[-3].get_translation()).mag() * -0.9
        )
        tangent_base = head_handle.create_child(
            Transform,
            segment_name='TangentBase',
            matrix=matrices[-2]
        )
        tangent_gp = tangent_base.create_child(
            Transform,
            segment_name='Tangent',
            matrix=matrices[-2]
        )
        joint_base_group = this.create_child(
            Transform,
            segment_name='JointBase',
            matrix=matrices[0]
        )
        tangent_plug.connect_to(tangent_gp.plugs['ty'])

        controller.create_parent_constraint(
            head_handle.gimbal_handle,
            joints[-1],
            mo=True
        )
        controller.create_parent_constraint(
            tangent_gp,
            joints[-2],
        )

        controller.create_parent_constraint(
            joint_base_group,
            joints[0],
        )
        lower_aim_transform = this.create_child(
            Transform,
            segment_name='LowerAim',
        )

        controller.create_point_constraint(
            lower_neck_transform,
            lower_aim_transform,
            mo=False
        )

        controller.create_aim_constraint(
            head_handle.gimbal_handle,
            lower_aim_transform,
            aimVector=env.aim_vector,
            upVector=env.up_vector,
            worldUpObject=lower_neck_transform,
            worldUpType='objectrotation',
            worldUpVector=[0.0, 0.0, -1.0]
        )

        center_handles_len = len(center_handles)
        for i, center_handle in enumerate(center_handles):
            lower_aim_transform.plugs['rotate'].connect_to(center_handle.groups[0].plugs['rotate'])
            constraint = controller.create_point_constraint(
                lower_neck_transform,
                tangent_gp,
                center_handle.groups[0],
                mo=False
            )
            value = 1.0 / (center_handles_len + 1) * (i + 1)
            constraint.plugs[tangent_gp.name + 'W1'].set_value(value)
            constraint.plugs[lower_neck_transform.name + 'W0'].set_value(1.0 - value)

            matrix = center_handle.get_matrix()
            center_handle.ofs.set_matrix(matrix)
            controller.create_aim_constraint(
                center_handle,
                joints[i + 1],
                mo=True,
                aimVector=env.aim_vector,
                upVector=env.up_vector,
                worldUpObject=lower_neck_transform,
                worldUpType='objectrotation',
                worldUpVector=[0.0, 0.0, -1.0]
            )

        root.add_plugs([
            head_handle.plugs['tx'],
            head_handle.plugs['ty'],
            head_handle.plugs['tz'],
            head_handle.plugs['rx'],
            head_handle.plugs['ry'],
            head_handle.plugs['rz']
        ])

        this.head_handle = head_handle
        this.joints = joints

        return this
