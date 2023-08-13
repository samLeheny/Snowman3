import Snowman3.rigger.rig_factory as rig_factory
import Snowman3.rigger.rig_factory.environment as env
from Snowman3.rigger.rig_factory.objects.part_objects.part import Part
import Snowman3.rigger.rig_factory.utilities.localize_utilities as locu
from Snowman3.rigger.rig_factory.objects.node_objects.joint import Joint
import Snowman3.rigger.rig_factory.utilities.node_utilities.name_utilities as nmu
from Snowman3.rigger.rig_factory.objects.part_objects.chain_guide import ChainGuide
from Snowman3.rigger.rig_factory.objects.rig_objects.grouped_handle import GroupedHandle, GimbalHandle
from Snowman3.rigger.rig_factory.objects.base_objects.properties import DataProperty, ObjectListProperty


class FeatherSimplePartGuide(ChainGuide):
    """
    This is almost an exact copy of FkChain with the difference that middle joints of the
    chain uniformly spread between first and last joint, ideal for a simple feather.
    """

    default_settings = dict(
        root_name='FeatherSimple',
        ribbon_joint_count=5,
        size=1.0,
        side='center',
        up_vector_indices=[0],
        create_gimbals=True,
        create_tweaks=False
    )
    create_gimbals = DataProperty( name='create_gimbals' )
    create_tweaks = DataProperty( name='create_tweaks' )
    ribbon_joint_count = DataProperty( name='ribbon_joint_count', default_value=10 )

    def __init__(self, **kwargs):
        super(FeatherSimplePartGuide, self).__init__(**kwargs)
        self.toggle_class = FeatherSimplePart.__name__

    @classmethod
    def create(cls, **kwargs):
        kwargs['count'] = 2
        this = super(FeatherSimplePartGuide, cls).create(**kwargs)
        controller = this.controller
        # add ribbon joints
        ribbon_joints = []
        for i in range(this.ribbon_joint_count):
            # create joint
            ribbon_joint = this.create_child(
                Joint,
                parent=this,
                segment_name='{}_{}'.format(
                    this.differentiation_name,
                    'Ribbon_{}'.format(nmu.index_dictionary[i].upper()),
                ),
                differentiation_name=None
            )

            # place the joint between start and end
            wgt = 1.0 / (this.ribbon_joint_count - 1) * i
            controller.create_weight_constraint(
                this.joints[0],
                this.joints[1],
                ribbon_joint,
                type='pointConstraint',
                weights=[1.0 - wgt, wgt],
            )

            # make the joint un-selectable
            ribbon_joint.plugs.set_values(
                overrideEnabled=True,
                overrideDisplayType=2,
            )

            ribbon_joints.append(ribbon_joint)

        # aim ribbon joints to next joint using up handle as up vector
        for i in range(len(ribbon_joints) - 1):
            controller.create_aim_constraint(
                ribbon_joints[i + 1],
                ribbon_joints[i],
                aimVector=(0, 1, 0),
                upVector=(0, 0, -1),
                worldUpType='object',
                worldUpObject=this.up_handles[0],
            )

        # last joint needs to aim to first joint
        controller.create_aim_constraint(
            ribbon_joints[0],
            ribbon_joints[-1],
            aimVector=(0, -1, 0),
            upVector=(0, 0, -1),
            worldUpType='object',
            worldUpObject=this.up_handles[0],
        )

        this.joints = ribbon_joints

        return this


class FeatherSimplePart(Part):

    create_gimbals = DataProperty(
        name='create_gimbals'
    )

    create_tweaks = DataProperty(
        name='create_tweaks'
    )

    base_handles = ObjectListProperty(
        name='base_handles'
    )

    def __init__(self, **kwargs):
        super(FeatherSimplePart, self).__init__(**kwargs)

    @classmethod
    def create(cls, **kwargs):
        this = super(FeatherSimplePart, cls).create(**kwargs)
        matrices = this.matrices
        size = this.size
        side = this.side
        joints = []
        root = this.get_root()
        joint_parent = this.joint_group
        handle_parent = this
        handles = []
        group_suffixes = kwargs.pop('group_suffixes', None)
        group_count = kwargs.pop('group_count', env.standard_group_count)
        for x, matrix in enumerate(matrices):
            segment_name = rig_factory.index_dictionary[x].title()
            joint = this.create_child(
                Joint,
                segment_name=segment_name,
                matrix=matrix,
                parent=joint_parent
            )
            joints.append(joint)
            joint_parent = joint
            joint.zero_rotation()
            joint.plugs.set_values(
                overrideEnabled=1,
                overrideDisplayType=2
            )
            if x != len(matrices)-1:
                handle = this.create_handle(
                    handle_type=GimbalHandle if this.create_gimbals else GroupedHandle,
                    segment_name=segment_name,
                    size=size*2.5,
                    matrix=matrix,
                    side=side,
                    shape='circle',
                    parent=handle_parent,
                    group_suffixes=group_suffixes,
                    group_count=group_count
                )
                handles.append(handle)
                handle_parent = handle.gimbal_handle if this.create_gimbals else handle
                handle.plugs['scale'].connect_to(joint.plugs['scale'])
                handle.plugs['rotateOrder'].connect_to(joint.plugs['rotateOrder'])
                if this.create_tweaks:
                    tweak_handle = this.create_handle(
                        segment_name='Tweak%s' % segment_name,
                        size=size * 2,
                        matrix=matrix,
                        side=side,
                        shape='diamond',
                        create_gimbal=False,
                        parent=handle.gimbal_handle if this.create_gimbals else handle
                    )
                    joint_driver = tweak_handle
                    root.add_plugs(
                        tweak_handle.plugs['rx'],
                        tweak_handle.plugs['ry'],
                        tweak_handle.plugs['rz'],
                        tweak_handle.plugs['tx'],
                        tweak_handle.plugs['ty'],
                        tweak_handle.plugs['tz'],
                        tweak_handle.plugs['sx'],
                        tweak_handle.plugs['sy'],
                        tweak_handle.plugs['sz']
                    )
                elif this.create_gimbals:
                    joint_driver = handle.gimbal_handle
                else:
                    joint_driver = handle
                locu.create_local_parent_constraint(
                    joint_driver,
                    joint
                )
                root.add_plugs(
                    handle.plugs['rx'],
                    handle.plugs['ry'],
                    handle.plugs['rz'],
                    handle.plugs['tx'],
                    handle.plugs['ty'],
                    handle.plugs['tz'],
                    handle.plugs['sx'],
                    handle.plugs['sy'],
                    handle.plugs['sz']
                )
        if len(joints) > 0:
            joints[0].plugs['type'].set_value(1)
            if len(joints) > 1:
                for joint in joints[1:]:
                    joint.plugs['type'].set_value(6)
        this.base_handles = handles
        this.joints = joints

        return this
