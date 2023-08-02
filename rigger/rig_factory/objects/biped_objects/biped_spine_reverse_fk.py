import Snowman3.rigger.rig_factory as rig_factory
import Snowman3.rigger.rig_math.matrix as mtx
from Snowman3.rigger.rig_math.matrix import Matrix
import Snowman3.rigger.rig_factory.positions as pos
from Snowman3.rigger.rig_factory.objects.part_objects.part import Part
from Snowman3.rigger.rig_factory.objects.node_objects.joint import Joint
from Snowman3.rigger.rig_factory.objects.part_objects.chain_guide import ChainGuide
from Snowman3.rigger.rig_factory.objects.rig_objects.grouped_handle import LocalHandle
from Snowman3.rigger.rig_factory.objects.base_objects.properties import ObjectProperty, DataProperty


class BipedSpineReverseFkGuide(ChainGuide):
    default_settings = dict(
        root_name='Spine',
        size=15.0,
        side='center',
        count=5,
        align_to_guide=False
    )
    align_to_guide = DataProperty(
        name='align_to_guide',
    )

    def __init__(self, **kwargs):
        super(BipedSpineReverseFkGuide, self).__init__(**kwargs)
        self.toggle_class = BipedSpineReverseFk.__name__

    @classmethod
    def create(cls, **kwargs):
        kwargs['up_vector_indices'] = [0]
        count = kwargs.get('count', cls.default_settings['count'])
        segment_names = []
        for i in range(count):
            if i == 0:
                segment_names.append('Hip')
            elif i == count - 2:
                segment_names.append('Chest')
            elif i == count - 1:
                segment_names.append('ChestEnd')
            else:
                segment_names.append(rig_factory.index_dictionary[i - 1].title())
        kwargs['segment_names'] = segment_names
        this = super(BipedSpineReverseFkGuide, cls).create(**kwargs)
        return this

    def after_first_create(self):
        self.set_handle_positions(pos.BIPED_POSITIONS)

    def get_toggle_blueprint(self):
        blueprint = super(BipedSpineReverseFkGuide, self).get_toggle_blueprint()
        matrices = [list(x.get_matrix()) for x in self.joints]
        blueprint['matrices'] = matrices
        return blueprint


class BipedSpineReverseFk(Part):

    align_to_guide = DataProperty(
        name='align_to_guide',
    )
    segment_names = DataProperty(
        name='segment_names',
    )

    def __init__(self, **kwargs):
        super(BipedSpineReverseFk, self).__init__(**kwargs)

    @classmethod
    def create(cls, **kwargs):
        if 'side' not in kwargs:
            raise Exception('you must provide a "side" keyword argument to create a %s' % cls.__name__)
        this = super(BipedSpineReverseFk, cls).create(**kwargs)
        nodes = cls.build_nodes(
            parent_group=this,
            joint_group=this.joint_group,
            matrices=this.matrices,
            align_to_guide=this.align_to_guide,
            segment_names=this.segment_names
        )
        handles = nodes['handles']
        joints = nodes['joints']
        root = this.get_root()
        for handle in handles:
            root.add_plugs(
                [
                    handle.plugs['tx'],
                    handle.plugs['ty'],
                    handle.plugs['tz'],
                    handle.plugs['rx'],
                    handle.plugs['ry'],
                    handle.plugs['rz']
                ]
            )
        this.set_handles(handles)
        this.joints = joints
        return this

    @staticmethod
    def build_nodes(
            parent_group,
            joint_group,
            matrices,
            align_to_guide,
            segment_names
    ):
        if segment_names is None:
            segment_names = []
            count = len(matrices)
            for i in range(count):
                if i == 0:
                    segment_names.append('Hip')
                elif i == count - 2:
                    segment_names.append('Chest')
                elif i == count - 1:
                    segment_names.append('ChestEnd')
                else:
                    segment_names.append(rig_factory.index_dictionary[i - 1].title())
        joint_parent = joint_group
        handle_parent = parent_group
        inverted_matrices = mtx.invert_matrices(matrices)
        controller = parent_group.controller
        size = parent_group.size
        joints = []
        segment_handles = []
        for x in reversed(range(len(inverted_matrices))):

            joint = parent_group.create_child(
                Joint,
                matrix=inverted_matrices[x],
                parent=joint_parent,
                segment_name=segment_names[x]
            )
            joint.zero_rotation()
            joints.insert(0, joint)
            joint_parent = joint
            if not x == 0 and not x == len(inverted_matrices) - 1:
                if align_to_guide:
                    handle_matrix = inverted_matrices[x]
                else:
                    handle_matrix = Matrix(inverted_matrices[x].get_translation())
                    handle_matrix.flip_x()
                    handle_matrix.flip_y()
                handle = parent_group.create_child(
                    LocalHandle,
                    size=size,
                    matrix=handle_matrix,
                    shape='circle_wavy',
                    parent=handle_parent,
                    segment_name=segment_names[x-1],
                    rotation_order='xzy'
                )
                if handle.segment_name == 'Hip':
                    hip_shape_matrix = Matrix()
                    hip_shape_matrix.set_translation([0, size * -0.1, 0])
                    hip_shape_matrix.set_scale([size * 1.25, size * -5.0, size * 1.25])
                    handle.set_shape_matrix(hip_shape_matrix)
                else:
                    shape_matrix = Matrix()
                    shape_matrix.set_translation([0, size * 0.25, 0])
                    shape_matrix.set_scale([size, size * -1.0, size])
                    handle.set_shape_matrix(shape_matrix)

                controller.create_parent_constraint(
                    handle.gimbal_handle,
                    joint,
                    mo=True
                )
                handle_parent = handle.gimbal_handle
                segment_handles.append(handle)

        if align_to_guide:
            chest_matrix = inverted_matrices[-2]
            chest_position = chest_matrix.get_translation()
            chest_matrix = mtx.compose_matrix_from_vectors(
                chest_position,
                matrices[-1].get_translation() - chest_position,
                chest_matrix.z_vector() * -1.0
            )
        else:
            chest_matrix = Matrix(inverted_matrices[-2].get_translation())
            chest_matrix.flip_x()
            chest_matrix.flip_y()
        chest_handle = parent_group.create_child(
            LocalHandle,
            segment_name=segment_names[-2],
            shape='circle_wavy',
            matrix=chest_matrix,
            rotation_order='xzy'
        )
        controller.create_parent_constraint(
            chest_handle.gimbal_handle,
            joints[-1],
            mo=True
        )
        shape_matrix = Matrix()
        shape_matrix.set_translation([0, size * -0.7, 0])
        shape_matrix.set_scale([size * 1.25, size * -7.0, size * 1.25])
        chest_handle.set_shape_matrix(shape_matrix)

        handles = [chest_handle]
        handles.extend(segment_handles)
        return dict(
            handles=handles,
            joints=joints,
            chest_handle=chest_handle
        )