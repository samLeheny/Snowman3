from Snowman3.rigger.rig_factory.objects.part_objects.chain_guide import ChainGuide
from Snowman3.rigger.rig_factory.objects.part_objects.part import Part
from Snowman3.rigger.rig_factory.objects.node_objects.joint import Joint
from Snowman3.rigger.rig_factory.objects.rig_objects.grouped_handle import LocalHandle
from Snowman3.rigger.rig_factory.objects.base_objects.properties import DataProperty
from Snowman3.rigger.rig_math.matrix import Matrix
import Snowman3.rigger.rig_factory.positions as pos


class BipedArmFkGuide(ChainGuide):
    segment_names = DataProperty(
        name='segment_names',
        default_value=['Shoulder', 'Elbow', 'Hand', 'HandEnd']
    )

    default_settings = dict(
        root_name='Arm',
        size=4.0,
        side='left'
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.toggle_class = BipedArmFk.__name__

    @classmethod
    def create(cls, **kwargs):
        kwargs['count'] = 4
        kwargs['up_vector_indices'] = [0, 2]
        kwargs.setdefault('root_name', 'Arm')
        this = super(BipedArmFkGuide, cls).create(**kwargs)
        this.set_handle_positions(pos.BIPED_POSITIONS)
        return this

    def get_toggle_blueprint(self):
        blueprint = super().get_toggle_blueprint()
        matrices = [list(x.get_matrix()) for x in self.joints]
        blueprint['matrices'] = matrices
        return blueprint


class BipedArmFk(Part):
    segment_names = DataProperty(
        name='segment_names',
        default_value=['Shoulder', 'Elbow', 'Hand', 'HandEnd']
    )

    def __init__(self, **kwargs):
        super(BipedArmFk, self).__init__(**kwargs)

    @classmethod
    def create(cls, **kwargs):
        if 'side' not in kwargs:
            raise Exception('you must provide a "side" keyword argument to create a %s' % cls.__name__)
        this = super(BipedArmFk, cls).create(**kwargs)
        cls.build_rig(this)
        return this

    @staticmethod
    def build_rig(this):
        controller = this.controller
        size = this.size
        side = this.side
        matrices = this.matrices
        joints = []
        handle_parent = this.top_group
        joint_parent = this.joint_group
        root = this.get_root()

        handles = []
        for i, segment_name in enumerate(this.segment_names):
            joint = this.top_group.create_child(
                Joint,
                segment_name=segment_name,
                matrix=matrices[i],
                parent=joint_parent
            )
            joint.zero_rotation()
            joint.plugs.set_values(
                overrideEnabled=1,
                overrideDisplayType=2
            )
            joints.append(joint)
            joint_parent = joint
            if i < len(matrices) - 1:
                handle = this.create_handle(
                    handle_type=LocalHandle,
                    segment_name=segment_name,
                    size=size * 1.5,
                    matrix=matrices[i],
                    shape='circle',
                    parent=handle_parent,
                )
                if i == 0:
                    handle.set_rotation_order('yxz')  # up_arm
                elif i == 1:
                    handle.set_rotation_order('xyz')  # forearm
                elif i == 2:
                    handle.set_rotation_order('zxy')  # wrist

                controller.create_parent_constraint(
                    handle.gimbal_handle,
                    joint,
                    mo=False
                )
                handle.plugs['scale'].connect_to(joint.plugs['scale'])
                root.add_plugs(
                    [
                        handle.plugs['tx'],
                        handle.plugs['ty'],
                        handle.plugs['tz'],
                        handle.plugs['rx'],
                        handle.plugs['ry'],
                        handle.plugs['rz'],
                        handle.plugs['sx'],
                        handle.plugs['sy'],
                        handle.plugs['sz']
                    ]
                )
                handle_parent = handle.gimbal_handle
                handles.append(handle)
        #up_arm_handle, forearm_handle, wrist_handle = handles
        #up_arm_handle.set_rotation_order('zyx')
        #forearm_handle.set_rotation_order('xyz')
        #wrist_handle.set_rotation_order('xzy')
        this.joints = joints
        return this
