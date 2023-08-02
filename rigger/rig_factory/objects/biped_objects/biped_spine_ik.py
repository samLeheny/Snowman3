import Snowman3.rigger.rig_factory as rig_factory
from Snowman3.rigger.rig_factory.objects.part_objects.chain_guide import ChainGuide
from Snowman3.rigger.rig_factory.objects.part_objects.part import Part
import Snowman3.rigger.rig_factory.environment as env
from Snowman3.rigger.rig_math.matrix import Matrix
from Snowman3.rigger.rig_factory.objects.node_objects.transform import Transform
from Snowman3.rigger.rig_factory.objects.node_objects.joint import Joint
from Snowman3.rigger.rig_factory.objects.rig_objects.grouped_handle import LocalHandle, WorldHandle
from Snowman3.rigger.rig_factory.objects.base_objects.properties import ObjectProperty, ObjectListProperty, DataProperty
import Snowman3.rigger.rig_factory.positions as pos



class BipedSpineIkGuide(ChainGuide):
    default_settings = dict(
        root_name='Spine',
        size=15.0,
        side='center',
        count=5,
        align_to_guide=False,
        legacy_orientation=False
    )

    align_to_guide = DataProperty( name='align_to_guide', )
    legacy_orientation = DataProperty( name='legacy_orientation', default_value=False )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.toggle_class = BipedSpineIk.__name__

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
        this = super().create(**kwargs)
        return this

    def after_first_create(self):
        self.set_handle_positions(pos.BIPED_POSITIONS)

    def get_toggle_blueprint(self):
        blueprint = super().get_toggle_blueprint()
        matrices = [list(x.get_matrix()) for x in self.joints]
        blueprint['matrices'] = matrices
        return blueprint


class BipedSpineIk(Part):

    lower_torso_handle = ObjectProperty(
        name='lower_torso_handle'
    )
    hip_handle = ObjectProperty(
        name='hip_handle'
    )
    chest_handle = ObjectProperty(
        name='chest_handle'
    )

    upper_torso_handle = ObjectProperty(
        name='upper_torso_handle'
    )
    center_handles = ObjectListProperty(
        name='center_handles'
    )
    align_to_guide = DataProperty(
        name='align_to_guide',
    )
    legacy_orientation = DataProperty(
        name='legacy_orientation',
        default_value=False
    )

    def __init__(self, **kwargs):
        super(BipedSpineIk, self).__init__(**kwargs)

    @classmethod
    def create(cls, **kwargs):
        if 'side' not in kwargs:
            raise Exception('you must provide a "side" keyword argument to create a %s' % cls.__name__)
        this = super(BipedSpineIk, cls).create(**kwargs)
        nodes = cls.build_nodes(
            parent_group=this,
            joint_group=this.joint_group,
            matrices=this.matrices,
            align_to_guide=this.align_to_guide,
            legacy_orientation=this.legacy_orientation
        )
        handles = nodes['handles']
        joints = nodes['joints']
        hip_handle = nodes['hip_handle']
        chest_handle = nodes['chest_handle']
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
            align_to_guide,
            legacy_orientation
    ):
        controller = parent_group.controller
        if len(matrices) < 5:
            raise Exception('you must provide at least 5 matrices to create a %s' % cls.__name__)
        size = parent_group.size
        side = parent_group.side
        joints = []
        center_handles = []

        if align_to_guide:
            hip_matrix = matrices[1]
            chest_matrix = matrices[-2]
        else:
            hip_matrix = Matrix(matrices[1].get_translation())
            chest_matrix = Matrix(matrices[-2].get_translation())

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
        for x, matrix in enumerate(matrices):
            segment_name = rig_factory.index_dictionary[x].title()
            joint = parent_group.create_child(
                Joint,
                segment_name=segment_name,
                matrix=matrix,
                parent=joint_parent
            )
            joint.zero_rotation()
            joints.append(joint)
            joint_parent = joint
            if x not in [0, 1, len(matrices)-1, len(matrices)-2]:
                center_handle = parent_group.create_child(
                    LocalHandle,
                    segment_name='Mid%s' % rig_factory.index_dictionary[len(center_handles)].title(),
                    size=size,
                    matrix=matrix,
                    side=side,
                    shape='circle',
                    rotation_order='xzy'
                )
                controller.create_parent_constraint(
                    center_handle.gimbal_handle,
                    joint,
                    mo=True
                )
                controller.create_scale_constraint(
                    center_handle.gimbal_handle,
                    joint
                )
                center_handle.plugs.set_values(
                    overrideEnabled=True,
                    overrideRGBColors=True,
                    overrideColorRGB=env.secondary_colors[side]
                )
                center_handles.append(center_handle)
        controller.create_parent_constraint(
            hip_handle.gimbal_handle,
            joints[0],
            mo=True
        )
        controller.create_scale_constraint(
            hip_handle.gimbal_handle,
            joints[0]
        )
        controller.create_parent_constraint(
            chest_handle.gimbal_handle,
            joints[-2],
            mo=True
        )
        controller.create_scale_constraint(
            chest_handle.gimbal_handle,
            joints[-2],
        )

        lower_aim_transform = parent_group.create_child(
            Transform,
            segment_name='LowerAim',
            matrix=Matrix() if legacy_orientation else matrices[0]
        )
        if not legacy_orientation:
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
            controller.create_aim_constraint(
                center_handle,
                joints[i+1],
                mo=True,
                aimVector=env.aim_vector,
                upVector=env.up_vector,
                worldUpObject=hip_handle.gimbal_handle,
                worldUpType='objectrotation',
                worldUpVector=[0.0, 0.0, -1.0]
            )
        handles = [hip_handle, chest_handle]
        handles.extend(center_handles)
        return dict(
            hip_handle=hip_handle,
            chest_handle=chest_handle,
            center_handles=center_handles,
            joints=joints,
            handles=handles
        )

    def get_toggle_blueprint(self):
        blueprint = super(BipedSpineIk, self).get_toggle_blueprint()
        blueprint['legacy_orientation'] = self.legacy_orientation
        return blueprint
