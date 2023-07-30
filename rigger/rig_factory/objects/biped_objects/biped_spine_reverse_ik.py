import rig_factory
import rig_math.matrix as mtx
from Snowman3.rigger.rig_factory.objects.part_objects.chain_guide import ChainGuide
from Snowman3.rigger.rig_factory.objects.part_objects.part import Part
import rig_factory.environment as env
from Snowman3.rigger.rig_math.matrix import Matrix
from rig_factory.objects.node_objects.transform import Transform
from Snowman3.rigger.rig_factory.objects.node_objects.joint import Joint
from Snowman3.rigger.rig_factory.objects.rig_objects.grouped_handle import LocalHandle, WorldHandle
from Snowman3.rigger.rig_factory.objects.base_objects.properties import ObjectProperty, ObjectListProperty, DataProperty
import Snowman3.utilities.positions as pos


class BipedSpineReverseIkGuide(ChainGuide):
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
        super(BipedSpineReverseIkGuide, self).__init__(**kwargs)
        self.toggle_class = BipedSpineReverseIk.__name__

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
        this = super(BipedSpineReverseIkGuide, cls).create(**kwargs)
        return this

    def after_first_create(self):
        self.set_handle_positions(pos.BIPED_POSITIONS)

    def get_toggle_blueprint(self):
        blueprint = super(BipedSpineReverseIkGuide, self).get_toggle_blueprint()
        matrices = [list(x.get_matrix()) for x in self.joints]
        blueprint['matrices'] = matrices
        return blueprint


class BipedSpineReverseIk(Part):

    hip_handle = ObjectProperty(
        name='hip_handle'
    )
    chest_handle = ObjectProperty(
        name='chest_handle'
    )
    center_handles = ObjectListProperty(
        name='center_handles'
    )

    align_to_guide = DataProperty(
        name='align_to_guide',
    )

    def __init__(self, **kwargs):
        super(BipedSpineReverseIk, self).__init__(**kwargs)

    @classmethod
    def create(cls, **kwargs):
        if 'side' not in kwargs:
            raise Exception('you must provide a "side" keyword argument to create a %s' % cls.__name__)
        this = super(BipedSpineReverseIk, cls).create(**kwargs)
        nodes = cls.build_nodes(
            parent_group=this,
            joint_group=this.joint_group,
            matrices=this.matrices,
            align_to_guide=this.align_to_guide
        )
        handles = nodes['handles']
        joints = nodes['joints']
        chest_handle = nodes['chest_handle']
        hip_handle = nodes['hip_handle']
        center_handles = nodes['center_handles']
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
        this.hip_handle = hip_handle
        this.chest_handle = chest_handle
        this.center_handles = center_handles
        this.set_handles(handles)
        this.joints = joints

        return this

    @staticmethod
    def build_nodes(
            parent_group,
            joint_group,
            matrices,
            align_to_guide
    ):
        controller = parent_group.controller
        if len(matrices) < 5:
            raise Exception('you must provide at least 5 matrices to create a Spine')
        inverted_matrices = mtx.invert_matrices(matrices)

        size = parent_group.size
        side = parent_group.side
        joints = []
        center_handles = []
        if align_to_guide:
            hip_matrix = inverted_matrices[1]
            tip_position = inverted_matrices[-1].get_translation()
            chest_position = inverted_matrices[-2].get_translation()
            chest_matrix = mtx.compose_matrix_from_vectors(
                chest_position,
                tip_position - chest_position,
                inverted_matrices[-1].z_vector() * -1.0
            )
        else:
            hip_matrix = Matrix(inverted_matrices[1].get_translation())
            chest_matrix = Matrix(inverted_matrices[-2].get_translation())
            hip_matrix.flip_x()
            hip_matrix.flip_y()
            chest_matrix.flip_x()
            chest_matrix.flip_y()
        hip_handle = parent_group.create_child(
            WorldHandle,
            segment_name='Hip',
            shape='cube',
            matrix=hip_matrix,
            size=size,
            rotation_order='xzy'
        )

        chest_handle = parent_group.create_child(
            WorldHandle,
            segment_name='Chest',
            shape='cube',
            matrix=chest_matrix,
            size=size,
            rotation_order='xzy'

        )
        joint_parent = joint_group
        for i in reversed(range(len(inverted_matrices))):
            segment_name = rig_factory.index_dictionary[i].title()
            joint = parent_group.create_child(
                Joint,
                segment_name=segment_name,
                matrix=inverted_matrices[i],
                parent=joint_parent
            )
            joint.zero_rotation()
            joints.insert(0, joint)
            joint_parent = joint
            if i not in [0, 1, len(matrices)-1, len(matrices)-2]:
                if align_to_guide:
                    center_matrix = inverted_matrices[i]
                else:
                    center_matrix = Matrix(inverted_matrices[i].get_translation())
                    center_matrix.flip_x()
                    center_matrix.flip_y()
                center_handle = parent_group.create_child(
                    LocalHandle,
                    segment_name='Mid%s' % rig_factory.index_dictionary[len(center_handles)].title(),
                    size=size,
                    matrix=center_matrix,
                    side=side,
                    shape='circle',
                    rotation_order='xzy'
                )
                controller.create_parent_constraint(
                    center_handle.gimbal_handle,
                    joint,
                    mo=True
                )
                center_handle.plugs.set_values(
                    overrideEnabled=True,
                    overrideRGBColors=True,
                    overrideColorRGB=env.secondary_colors[side]
                )

                center_handles.append(center_handle)
        controller.create_parent_constraint(
            chest_handle.gimbal_handle,
            joints[-1],
            mo=True
        )
        controller.create_parent_constraint(
            chest_handle.gimbal_handle,
            joints[-2],
            mo=True
        )
        controller.create_parent_constraint(
            hip_handle.gimbal_handle,
            joints[0],
            mo=True
        )
        controller.create_parent_constraint(
            hip_handle.gimbal_handle,
            joints[1],
            mo=True
        )
        lower_aim_transform = parent_group.create_child(
            Transform,
            segment_name='LowerAim',
            matrix=inverted_matrices[0]
        )
        controller.create_point_constraint(
            hip_handle.gimbal_handle,
            lower_aim_transform,
            mo=True
        )
        controller.create_aim_constraint(
            chest_handle.gimbal_handle,
            lower_aim_transform,
            aimVector=env.aim_vector,
            upVector=env.up_vector,
            worldUpObject=hip_handle.gimbal_handle,
            worldUpType='objectrotation',
            worldUpVector=[0.0, 0.0, -1.0]
        )
        sub_handle_count = len(center_handles)
        for i, center_handle in enumerate(center_handles):
            matrix = center_handle.get_matrix()
            lower_aim_transform.plugs['rotate'].connect_to(center_handle.groups[0].plugs['rotate'])
            constraint = controller.create_point_constraint(
                hip_handle.gimbal_handle,
                chest_handle.gimbal_handle,
                center_handle.groups[0],
                mo=True
            )
            value = 1.0/(sub_handle_count+1)*(i+1)
            constraint.get_weight_plug(hip_handle.gimbal_handle).set_value(1.0-value)
            constraint.get_weight_plug(chest_handle.gimbal_handle).set_value(value)
            center_handle.ofs.set_matrix(matrix)
            # controller.create_aim_constraint(
            #     center_handle,
            #     joints[i+1],
            #     mo=True,
            #     aimVector=env.aim_vector,
            #     upVector=env.up_vector,
            #     worldUpObject=lower_torso_handle.gimbal_handle,
            #     worldUpType='objectrotation',
            #     worldUpVector=[0.0, 0.0, -1.0]
            # )
        handles = [hip_handle, chest_handle]
        handles.extend(center_handles)
        return dict(
            hip_handle=hip_handle,
            chest_handle=chest_handle,
            center_handles=center_handles,
            joints=joints,
            handles=handles
        )
