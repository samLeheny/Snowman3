import Snowman3.rigger.rig_factory as rig_factory
import Snowman3.rigger.rig_factory.environment as env
from Snowman3.rigger.rig_factory.objects.part_objects.chain_guide import ChainGuide
from Snowman3.rigger.rig_factory.objects.node_objects.transform import Transform
from Snowman3.rigger.rig_factory.objects.node_objects.depend_node import DependNode
from Snowman3.rigger.rig_factory.objects.part_objects.part import Part
from Snowman3.rigger.rig_factory.objects.node_objects.joint import Joint
from Snowman3.rigger.rig_factory.objects.rig_objects.grouped_handle import GroupedHandle, GimbalHandle
from Snowman3.rigger.rig_factory.objects.base_objects.properties import DataProperty, ObjectListProperty


class FkChainGuide(ChainGuide):

    default_settings = dict(
        root_name='Chain',
        count=5,
        size=1.0,
        side='center',
        up_vector_indices=[0],
        create_gimbals=True,
        create_tweaks=False,
        scale_compensate=False
    )

    create_gimbals = DataProperty( name='create_gimbals' )
    create_tweaks = DataProperty( name='create_tweaks' )
    scale_compensate = DataProperty( name='scale_compensate', default_value=False )
    allowed_modes = DataProperty( name='allowed_modes', default_value=['translation', 'orientation'] )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.toggle_class = FkChain.__name__

    @classmethod
    def create(cls, **kwargs):
        this = super().create(**kwargs)
        return this


class FkChain(Part):

    create_gimbals = DataProperty( name='create_gimbals' )
    create_tweaks = DataProperty( name='create_tweaks' )
    scale_compensate = DataProperty( name='scale_compensate', default_value=False )
    base_handles = ObjectListProperty( name='base_handles' )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.allowed_modes = ['translation', 'orientation']

    @classmethod
    def create(cls, **kwargs):
        this = super().create(**kwargs)
        root = this.get_root()
        nodes = cls.build_nodes(
            this,
            this.joint_group,
            this.matrices,
            group_suffixes=kwargs.pop('group_suffixes', None),
            group_count=kwargs.pop('group_count', env.standard_group_count),
            create_gimbals=this.create_gimbals,
            create_tweaks=this.create_tweaks,
            scale_compensate=this.scale_compensate
        )
        for handle in nodes['handles']:
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
        this.set_handles(nodes['handles'])
        this.base_handles = nodes['handles']
        this.joints = nodes['joints']
        return this

    @staticmethod
    def build_nodes(
            parent_group,
            joint_group,
            matrices,
            group_suffixes=None,
            group_count=env.standard_group_count,
            create_gimbals=False,
            create_tweaks=False,
            scale_compensate=False,
            connect_drivers=True
    ):
        controller = parent_group.controller
        joint_drivers = []
        handles = []
        size = parent_group.size
        side = parent_group.side
        joint_parent = joint_group
        handle_parent = parent_group
        joints = []
        base_handles = []
        tweak_handles = []
        for x, matrix in enumerate(matrices):
            segment_name = rig_factory.index_dictionary[x].title()
            joint = parent_group.create_child(
                Joint,
                segment_name=segment_name,
                matrix=matrix,
                parent=joint_parent
            )

            joint_parent = joint
            joint.zero_rotation()
            joint.plugs.set_values(
                overrideEnabled=1,
                overrideDisplayType=2
            )
            joints.append(joint)
            if x != len(matrices)-1:
                handle = parent_group.create_child(
                    GimbalHandle if create_gimbals else GroupedHandle,
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
                base_handles.append(handle)
                handle_parent = handle.gimbal_handle if create_gimbals else handle
                handle.plugs['rotateOrder'].connect_to(joint.plugs['rotateOrder'])

                if create_tweaks:
                    tweak_handle = parent_group.create_child(
                        GroupedHandle,
                        segment_name=segment_name,
                        subsidiary_name='Tweak',
                        size=size * 2,
                        matrix=matrix,
                        side=side,
                        shape='diamond',
                        create_gimbal=False,
                        parent=handle.gimbal_handle if create_gimbals else handle
                    )
                    joint_driver = tweak_handle
                    handles.append(tweak_handle)
                    tweak_handles.append(tweak_handle)
                elif create_gimbals:
                    joint_driver = handle.gimbal_handle
                else:
                    joint_driver = handle
                joint_drivers.append(joint_driver)

        for i, joint in enumerate(joints[:-1]):
            joint.plugs['scale'].connect_to(joints[i + 1].plugs['inverseScale'])

        # Deal with inverse scaling to allow for fk chain to scale without scaling rest of chain
        if scale_compensate:
            for i, handle in enumerate(handles[:-1]):  # Exclude last handle
                handle_parent = handle.gimbal_handle if create_gimbals else handle
                handle_child_matrix = handles[i + 1].get_matrix()
                inverse_translate_matrix = handle_child_matrix.get_translation()
                inverse_group = handle_parent.create_child(
                    Transform,
                    segment_name=handles[i + 1].segment_name,
                    suffix='Inv',
                    matrix=handle.parent.get_matrix().set_translation(inverse_translate_matrix),
                    subsidiary_name=handles[i + 1].subsidiary_name
                )

                inverse_scale_md = parent_group.create_child(
                    DependNode,
                    node_type='multiplyDivide',
                    segment_name=handles[i + 1].segment_name,
                    functionality_name='InverseScale',
                    subsidiary_name=handle.subsidiary_name
                )
                inverse_scale_md.plugs['operation'].set_value(2)
                inverse_scale_md.plugs['input1'].set_value((1.0, 1.0, 1.0))
                handle.plugs['scale'].connect_to(inverse_scale_md.plugs['input2'])
                inverse_scale_md.plugs['output'].connect_to(inverse_group.plugs['scale'])

                handles[i + 1].drv.set_parent(inverse_group)
                handles[i + 1].drv.set_matrix(handle_child_matrix)

        scale_constraints = []
        if connect_drivers:
            # Constraint joints. Using Point+Orient to fix issue with weird twisting when scaling non uniformly
            for i, joint_driver in enumerate(joint_drivers):
                controller.create_point_constraint(
                    joint_driver,
                    joints[i]
                )
                controller.create_orient_constraint(
                    joint_driver,
                    joints[i]
                )
                scale_constraint = controller.create_scale_constraint(
                    joint_driver,
                    joints[i]
                )
                scale_constraints.append(scale_constraint)

            # Deal with final joint that does not have a control for
            controller.create_point_constraint(
                joint_drivers[-1],
                joints[-1],
                mo=True
            )
            controller.create_orient_constraint(
                joint_drivers[-1],
                joints[-1],
                mo=True
            )
            scale_constraint = controller.create_scale_constraint(
                joint_drivers[-1],
                joints[-1],
                mo=True
            )
            scale_constraints.append(scale_constraint)

            # Do a stupid bandaid fix for scaling issue when scaling parent joint/control
            for i, scale_constraint in enumerate(scale_constraints[1:], start=1):
                for axis in ['X', 'Y', 'Z']:
                    scale_condition = scale_constraint.create_child(
                        DependNode,
                        node_type='condition',
                        functionality_name='Scale{0}'.format(axis)
                    )
                    scale_condition.plugs['operation'].set_value(1)
                    scale_constraint.plugs['constraintScale{0}'.format(axis)].connect_to(
                        scale_condition.plugs['firstTerm']
                    )
                    parent_group.plugs['scale{0}'.format(axis)].connect_to(
                        scale_condition.plugs['secondTerm']
                    )

                    scale_constraint.plugs['constraintScale{0}'.format(axis)].divide(
                        parent_group.scale_multiply_transform.plugs['scale{0}'.format(axis)]).connect_to(
                        scale_condition.plugs['colorIfTrueR']
                    )
                    scale_condition.plugs['colorIfFalseR'].set_value(1.0)

                    controller.scene.disconnectAttr(
                        scale_constraint.plugs['constraintScale{0}'.format(axis)].name,
                        joints[i].plugs['scale{0}'.format(axis)].name
                    )
                    scale_condition.plugs['outColorR'].connect_to(
                        joints[i].plugs['scale{0}'.format(axis)]
                    )

        if len(joints) > 0:
            joints[0].plugs['type'].set_value(1)
            if len(joints) > 1:
                for joint in joints[1:]:
                    joint.plugs['type'].set_value(6)

        return dict(
            handles=handles,
            tweak_handles=tweak_handles,
            base_handles=base_handles,
            joints=joints
        )


