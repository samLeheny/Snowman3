import Snowman3.rigger.rig_factory as rig_factory
from Snowman3.rigger.rig_factory.objects.part_objects.chain_guide import ChainGuide
from Snowman3.rigger.rig_factory.objects.part_objects.part import Part
from Snowman3.rigger.rig_factory.objects.node_objects.joint import Joint
from Snowman3.rigger.rig_factory.objects.rig_objects.grouped_handle import LocalHandle, WorldHandle
from Snowman3.rigger.rig_factory.objects.base_objects.properties import ObjectProperty, DataProperty
from Snowman3.rigger.rig_math.matrix import Matrix
import Snowman3.rigger.rig_factory.positions as pos


class QuadrupedNeckFkGuide(ChainGuide):
    default_settings = dict(
        root_name='Neck',
        size=5.0,
        side='center',
        count=6
    )

    def __init__(self, **kwargs):
        super(QuadrupedNeckFkGuide, self).__init__(**kwargs)
        self.toggle_class = QuadrupedNeckFk.__name__

    @classmethod
    def create(cls, **kwargs):
        kwargs['up_vector_indices'] = [0]
        kwargs.setdefault('root_name', 'Neck')
        this = super(QuadrupedNeckFkGuide, cls).create(**kwargs)
        # this.set_handle_positions(pos.QUADRUPED_POSITIONS)
        return this

    def get_toggle_blueprint(self):
        blueprint = super(QuadrupedNeckFkGuide, self).get_toggle_blueprint()
        matrices = [list(x.get_matrix()) for x in self.joints]
        blueprint['matrices'] = matrices
        return blueprint


class QuadrupedNeckFk(Part):
    head_handle = ObjectProperty(
        name='head_handle'
    )

    head_matrix = DataProperty(
        name='head_matrix',
        default_value=list(Matrix())
    )

    def __init__(self, **kwargs):
        super(QuadrupedNeckFk, self).__init__(**kwargs)

    @classmethod
    def create(cls, **kwargs):
        if 'side' not in kwargs:
            raise Exception('you must provide a "side" keyword argument to create a %s' % cls.__name__)
        kwargs['head_matrix'] = list(kwargs.pop('head_matrix', Matrix()))
        this = super(QuadrupedNeckFk, cls).create(**kwargs)
        return this.build_rig(this)

    @staticmethod
    def build_rig(this):
        controller = this.controller
        size = this.size
        root = this.get_root()
        matrices = this.matrices
        handle_parent = this
        joint_parent = this.joint_group
        matrix_count = len(matrices)
        handles = []
        joints = []
        for x, matrix in enumerate(matrices):
            if x == 0:
                segment_name = 'Root'
            else:
                segment_name = rig_factory.index_dictionary[x - 1].title()
            joint = this.create_child(
                Joint,
                matrix=matrix,
                parent=joint_parent,
                segment_name=segment_name
            )
            joint.zero_rotation()
            joint.plugs.set_values(
                overrideEnabled=1,
                overrideDisplayType=2
            )
            joints.append(joint)
            joint_parent = joint

            # Creates handles for all joints except the first, and the
            # final two.
            if 0 < x < matrix_count - 2:
                handle = this.create_handle(
                    handle_type=LocalHandle,
                    size=size,
                    matrix=matrix,
                    shape='circle',
                    parent=handle_parent,
                    segment_name=segment_name,
                    rotation_order='xzy'
                )

                handle_parent = handle.gimbal_handle
                handles.append(handle)

                root.add_plugs([
                    handle.plugs['tx'],
                    handle.plugs['ty'],
                    handle.plugs['tz'],
                    handle.plugs['rx'],
                    handle.plugs['ry'],
                    handle.plugs['rz']
                ])
                controller.create_parent_constraint(handle, joint)

        # Creates the "Head" handle.
        head_handle = this.create_handle(
            handle_type=LocalHandle,
            segment_name='Head',
            size=size,
            matrix=Matrix(matrices[-1].get_translation()),
            shape='cube_head',
            parent=handles[-1].gimbal_handle,
            rotation_order='zxy'
        )
        head_handle.set_shape_matrix(Matrix(this.head_matrix))

        root.add_plugs(
            [
                head_handle.plugs['tx'],
                head_handle.plugs['ty'],
                head_handle.plugs['tz'],
                head_handle.plugs['rx'],
                head_handle.plugs['ry'],
                head_handle.plugs['rz']
            ]
        )

        controller.create_parent_constraint(
            head_handle.gimbal_handle,
            joints[-2],
            mo=True
        )

        controller.create_parent_constraint(
            this,
            joints[0],
            mo=True
        )

        this.head_handle = head_handle
        this.joints = joints
        return this