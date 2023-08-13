from Snowman3.rigger.rig_factory.objects.base_objects.properties import ObjectListProperty, DataProperty
from Snowman3.rigger.rig_factory.objects.part_objects.chain_guide import ChainGuide
from Snowman3.rigger.rig_factory.objects.rig_objects.grouped_handle import LocalHandle, WorldHandle
from Snowman3.rigger.rig_factory.objects.part_objects.part import Part
import Snowman3.rigger.rig_factory.positions as pos


class QuadrupedBackLegFkGuide(ChainGuide):

    segment_names = DataProperty(
        name='segment_names',
        default_value=['Hip', 'Knee', 'Ankle', 'Foot', 'Toe']
    )


    default_settings = dict(
        root_name='BackLeg',
        size=4.0,
        side='left'
    )

    def __init__(self, **kwargs):
        super(QuadrupedBackLegFkGuide, self).__init__(**kwargs)
        self.toggle_class = QuadrupedBackLegFk.__name__

    @classmethod
    def create(cls, **kwargs):
        kwargs['count'] = 5
        kwargs['up_vector_indices'] = [0, 3]
        kwargs.setdefault('root_name', 'BackLeg')
        this = super(QuadrupedBackLegFkGuide, cls).create(**kwargs)
        this.set_handle_positions(pos.QUADRUPED_POSITIONS)
        return this

    def get_toggle_blueprint(self):
        blueprint = super(QuadrupedBackLegFkGuide, self).get_toggle_blueprint()
        matrices = [list(x.get_matrix()) for x in self.joints]
        blueprint['matrices'] = matrices
        return blueprint


class QuadrupedBackLegFk(Part):

    fk_handles = ObjectListProperty(
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
        default_value=['Hip', 'Knee', 'Ankle', 'Foot', 'Toe']
    )

    def __init__(self, **kwargs):
        super(QuadrupedBackLegFk, self).__init__(**kwargs)

    @classmethod
    def create(cls, **kwargs):
        if len(kwargs.get('matrices', [])) != 5:
            raise Exception('you must provide exactly 5 matrices to create a %s' % cls.__name__)
        if 'side' not in kwargs:
            raise Exception('you must provide a "side" keyword argument to create a %s' % cls.__name__)
        this = super(QuadrupedBackLegFk, cls).create(**kwargs)
        cls.build_rig(this)
        return this

    @staticmethod
    def build_rig(this):
        controller = this.controller
        size = this.size
        side = this.side
        matrices = this.matrices
        joints = []
        joint_parent = this.joint_group
        handle_parent = this
        root = this.get_root()
        for i in range(5):
            segment_name = this.segment_names[i]
            is_last = i == 4
            joint = this.create_child(
                'Joint',
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
            if not is_last:  # No need to create a handle for tip of limb
                handle = this.create_handle(
                    handle_type=LocalHandle,
                    segment_name=segment_name,
                    index=i,
                    size=size * 1.75,
                    matrix=matrices[i],
                    side=side,
                    shape='circle',
                    parent=handle_parent
                )
                controller.create_parent_constraint(
                    handle.gimbal_handle,
                    joint
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
                #handle.stretch_shape(matrices[i+1])
                handle_parent = handle.gimbal_handle
        this.joints = joints
        return this
