import copy
from Snowman3.rigger.rig_factory.objects.base_objects.properties import ObjectListProperty, DataProperty
from Snowman3.rigger.rig_factory.objects.part_objects.chain_guide import ChainGuide
from Snowman3.rigger.rig_factory.objects.part_objects.part import Part
from Snowman3.rigger.rig_factory.objects.node_objects.joint import Joint
from Snowman3.rigger.rig_factory.objects.rig_objects.grouped_handle import LocalHandle
from Snowman3.rigger.rig_math.matrix import Matrix
import Snowman3.rigger.rig_factory.positions as pos


class BipedLegFkGuide(ChainGuide):

    segment_names = DataProperty(
        name='segment_names',
        default_value=['Hip', 'Knee', 'Foot', 'Toe', 'ToeTip']
    )
    default_settings = dict(
        root_name='Leg',
        size=1.0,
        side='left'
    )

    def __init__(self, **kwargs):
        super(BipedLegFkGuide, self).__init__(**kwargs)
        self.toggle_class = BipedLegFk.__name__

    @classmethod
    def create(cls, **kwargs):
        kwargs['count'] = 5
        kwargs['up_vector_indices'] = [0, 2]
        kwargs.setdefault('root_name', 'Leg')
        this = super(BipedLegFkGuide, cls).create(**kwargs)
        size_plug = this.plugs['size']
        size_multiply_node = this.create_child('DependNode', node_type='multiplyDivide')
        size_plug.connect_to(size_multiply_node.plugs['input1X'])
        size_multiply_node.plugs['input2X'].set_value(0.5)
        this.set_handle_positions(pos.BIPED_POSITIONS)
        return this

    def get_toggle_blueprint(self):
        blueprint = super(BipedLegFkGuide, self).get_toggle_blueprint()
        matrices = [list(x.get_matrix()) for x in self.joints]
        blueprint['matrices'] = matrices
        return blueprint


class BipedLegFk(Part):

    fk_handles = ObjectListProperty(  # this should just be "handles"
        name='fk_handles'
    )
    fk_joints = ObjectListProperty(
        name='fk_joints'
    )
    fk_handle_gimbals = ObjectListProperty(
        name='fk_handle_gimbals'
    )
    segment_names = DataProperty(
        name='segment_names',
        default_value=['Hip', 'Knee', 'Foot', 'Toe', 'ToeTip']
    )

    def __init__(self, **kwargs):
        super(BipedLegFk, self).__init__(**kwargs)

    @classmethod
    def create(cls, **kwargs):
        if 'side' not in kwargs:
            raise Exception('you must provide a "side" keyword argument to create a %s' % cls.__name__)
        this = super(BipedLegFk, cls).create(**kwargs)
        cls.build_rig(this)
        return this

    @staticmethod
    def build_rig(this):
        controller = this.controller
        size = this.size
        side = this.side
        matrices = this.matrices
        root = this.get_root()
        joints = []
        joint_parent = this.joint_group
        handle_parent = this
        handles = []
        for i in range(5):
            segment_name = this.segment_names[i]
            is_last = i > 3
            matrix = matrices[i]
            joint = this.create_child(
                Joint,
                matrix=matrix,
                segment_name=segment_name,
                parent=joint_parent
            )
            joint_parent = joint
            joint.zero_rotation()
            if not is_last:  # No need to create a handle for tip of limb
                handle = this.create_handle(
                    handle_type=LocalHandle,
                    segment_name=segment_name,
                    size=size * 1.5,
                    matrix=matrix,
                    side=side,
                    shape='circle',
                    parent=handle_parent
                )

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

                controller.create_parent_constraint(
                    handle.gimbal_handle,
                    joint,
                    mo=True,
                )
                handle.plugs['scale'].connect_to(joint.plugs['scale'])
                handle_parent = handle.gimbal_handle
                handles.append(handle)

            joint.plugs.set_values(
                overrideEnabled=1,
                overrideDisplayType=2
            )
            joints.append(joint)

        thigh_handle, calf_handle, ankle_handle, toe_handle = handles
        thigh_handle.set_rotation_order('xyz')
        calf_handle.set_rotation_order('xyz')
        ankle_handle.set_rotation_order('xyz')
        toe_handle.set_rotation_order('xyz')
        this.joints = joints

        return this
