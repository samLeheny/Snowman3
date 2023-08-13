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
import Snowman3.rigger.rig_math.vector as vec

class QuadrupedNeckIkGuide(ChainGuide):

    head_matrix = DataProperty(
        name='head_matrix',
        default_value=list(Matrix())
    )
    head_cube = ObjectProperty(
        name='head_cube'
    )
    default_settings = dict(
        root_name='Neck',
        size=1.0,
        side='center',
        count=6
    )

    def __init__(self, **kwargs):
        super(QuadrupedNeckIkGuide, self).__init__(**kwargs)
        self.toggle_class = QuadrupedNeckIk.__name__

    @classmethod
    def create(cls, **kwargs):
        kwargs['up_vector_indices'] = [0]
        kwargs.setdefault('root_name', 'Neck')
        this = super(QuadrupedNeckIkGuide, cls).create(**kwargs)
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
        # this.set_handle_positions(pos.QUADRUPED_POSITIONS)

        return this

    def get_toggle_blueprint(self):
        blueprint = super(QuadrupedNeckIkGuide, self).get_toggle_blueprint()
        blueprint['head_matrix'] = list(self.head_cube.get_matrix(world_space=False))
        return blueprint


class QuadrupedNeckIk(Part):

    head_matrix = DataProperty(
        name='head_matrix',
        default_value=list(Matrix())
    )

    head_handle = ObjectProperty(
        name='head_handle'
    )
    default_head_scale = 4

    @classmethod
    def create(cls, **kwargs):
        if 'side' not in kwargs:
            raise Exception('you must provide a "side" keyword argument to create a ' + cls.__name__)
        this = super(QuadrupedNeckIk, cls).create(**kwargs)
        cls.build_rig(this)
        return this

    @staticmethod
    def build_rig(this):
        controller = this.controller
        matrices = this.matrices
        matrices_len = len(matrices)
        if matrices_len < 5:
            raise Exception('you must provide at least 4 matrices to create a ' + this.__class__.__name__)
        size = this.size
        side = this.side
        root = this.get_root()

        center_handles = []
        joint_parent = this.joint_group
        joints = []

        for i, matrix in enumerate(matrices):
            if i == 0:
                segment_name = 'Root'
            else:
                segment_name = rig_factory.index_dictionary[i - 1].title()
            joint = this.create_child(
                Joint,
                segment_name=segment_name,
                matrix=matrix,
                parent=joint_parent
            )
            joint.zero_rotation()
            joint.plugs.set_values(
                drawStyle=2
            )
            joints.append(joint)
            joint_parent = joint

        head_handle = this.create_handle(
            handle_type=WorldHandle,
            segment_name='Head',
            shape='cube',
            matrix=Matrix(matrices[-1].get_translation()),
            parent=this,
            size=size,
            rotation_order='zxy'
        )

        controller.create_parent_constraint(
            head_handle.gimbal_handle,
            joints[-2],
            mo=True
        )
        mid_start_transform = this.create_child(
            Transform,
            segment_name='MidStart',
            matrix=matrices[1]
        )

        mid_end_transform = head_handle.create_child(
            Transform,
            segment_name='MidEnd',
            matrix=matrices[-2]
        )
        controller.create_parent_constraint(
            this,
            joints[0],
            mo=True
        )

        center_total_vector = mid_end_transform.get_translation() - mid_start_transform.get_translation()
        for i in range(len(joints)):
            if i > 1 and i < len(joints) - 2:
                center_handle = this.create_handle(
                    handle_type=LocalHandle,
                    segment_name='Mid%s' % rig_factory.index_dictionary[len(center_handles)].upper(),
                    size=size,
                    matrix=matrices[i],
                    side=side,
                    shape='circle',
                    rotation_order='xzy'
                )
                center_handles.append(center_handle)

                controller.create_point_constraint(
                    center_handle,
                    joints[i]
                )


                closest_point = vec.find_closest_point_on_line(
                    matrices[i].get_translation(),
                    mid_start_transform.get_translation(),
                    mid_end_transform.get_translation()
                )

                weight = (closest_point - mid_start_transform.get_translation()).mag() / center_total_vector.mag()
                constraint = controller.create_point_constraint(
                    mid_start_transform,
                    mid_end_transform,
                    center_handle.zro,
                    mo=False
                )
                constraint.get_weight_plug(constraint.targets[0]).set_value(1.0 - weight)
                constraint.get_weight_plug(constraint.targets[1]).set_value(weight)

                controller.create_aim_constraint(
                    mid_end_transform,
                    center_handle.zro,
                    aimVector=env.side_aim_vectors[side],
                    upVector=env.side_up_vectors[side],
                    worldUpObject=mid_start_transform,
                    worldUpType='objectrotation',
                    worldUpVector=env.side_up_vectors[side],
                    mo=False
                )

                center_handle.ofs.set_matrix(matrices[i])

                center_handle.plugs.set_values(
                    overrideEnabled=True,
                    overrideRGBColors=True,
                    overrideColorRGB=env.secondary_colors[side]
                )
                root.add_plugs([
                    center_handle.plugs['tx'],
                    center_handle.plugs['ty'],
                    center_handle.plugs['tz'],
                    center_handle.plugs['rx'],
                    center_handle.plugs['ry'],
                    center_handle.plugs['rz']
                ])

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
