import os
import Snowman3.rigger.rig_factory as rig_factory
from Snowman3.rigger.rig_math.matrix import Matrix
import Snowman3.rigger.rig_factory.positions as pos
import Snowman3.rigger.rig_factory.environment as env
from Snowman3.rigger.rig_factory.objects.part_objects.part import Part
from Snowman3.rigger.rig_factory.objects.node_objects.joint import Joint
from Snowman3.rigger.rig_factory.objects.node_objects.locator import Locator
from Snowman3.rigger.rig_factory.objects.node_objects.transform import Transform
from Snowman3.rigger.rig_factory.objects.part_objects.chain_guide import ChainGuide
from Snowman3.rigger.rig_factory.objects.node_objects.depend_node import DependNode
from Snowman3.rigger.rig_factory.objects.biped_objects.biped_spine_ik import BipedSpineIk
from Snowman3.rigger.rig_factory.objects.biped_objects.biped_spine_fk import BipedSpineFk
from Snowman3.rigger.rig_factory.objects.rig_objects.grouped_handle import CogHandle, GroupedHandle
from Snowman3.rigger.rig_factory.objects.base_objects.properties import ObjectProperty, ObjectListProperty, DataProperty


class BipedSpineIkFkGuide(ChainGuide):
    default_settings = dict(
        root_name='Spine',
        size=15.0,
        side='center',
        joint_count=9,
        count=5,
        squash=0.0,
        rename_cog=True,
        align_to_guide=False,
        use_plugins=os.getenv('USE_RIG_PLUGINS', False),
        legacy_orientation=False
    )
    squash = DataProperty( name='squash' )
    cog_handle = ObjectProperty( name='cog_handle' )
    rename_cog = DataProperty( name='rename_cog', default_value=True )
    align_to_guide = DataProperty( name='align_to_guide' )
    base_joints = ObjectListProperty( name='base_joints' )
    legacy_orientation = DataProperty( name='legacy_orientation', default_value=False )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.toggle_class = BipedSpineIkFk.__name__

    @classmethod
    def create(cls, **kwargs):
        kwargs.setdefault('root_name', 'Spine')
        segment_names = []
        count = kwargs.get('count', cls.default_settings['count'])
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
        this = super(BipedSpineIkFkGuide, cls).create(**kwargs)
        root = this.get_root()
        size_plug = this.plugs['size']
        side = kwargs.get('side', 'center')
        shader = root.shaders[side].shading_group

        hip_joint = this.create_child(
            Joint,
            segment_name='SplineHip',
            matrix=this.joints[0].get_matrix()
        )
        hip_joint.plugs.set_values(
            overrideEnabled=True,
            overrideDisplayType=2,
        )
        this.controller.create_point_constraint(
            this.joints[0],
            hip_joint,
            mo=False
        )
        cog_position = this.joints[1].get_matrix().get_translation()
        cog_handle = this.create_handle(
            segment_name='Cog',
            matrix=cog_position,
            rotation_order='xzy',
        )
        size_plug.connect_to(cog_handle.plugs['size'])
        cog_handle.mesh.assign_shading_group(shader)
        this.cog_handle = cog_handle
        return this

    def after_first_create(self):
        self.set_handle_positions(pos.BIPED_POSITIONS)

    def get_toggle_blueprint(self):
        blueprint = super(BipedSpineIkFkGuide, self).get_toggle_blueprint()
        blueprint['cog_matrix'] = list(self.cog_handle.get_matrix())
        return blueprint


class BipedSpineIkFk(Part):
    align_to_guide = DataProperty(
        name='align_to_guide',
    )
    settings_handle = ObjectProperty(
        name='settings_handle',
    )
    cog_handle = ObjectProperty(
        name='cog_handle',
    )
    fk_match_transforms = ObjectListProperty(
        name='fk_match_transforms',
    )
    segment_names = DataProperty(
        name='segment_names',
    )
    legacy_orientation = DataProperty(
        name='legacy_orientation',
        default_value=False
    )
    cog_matrix = None

    def __init__(self, **kwargs):
        super(BipedSpineIkFk, self).__init__(**kwargs)

    @classmethod
    def create(cls, **kwargs):
        this = super(BipedSpineIkFk, cls).create(**kwargs)
        nodes = cls.build_nodes(
            parent_group=this,
            joint_group=this.joint_group,
            matrices=this.matrices,
            align_to_guide=this.align_to_guide,
            cog_matrix=this.cog_matrix,
            segment_names=this.segment_names,
            legacy_orientation=this.legacy_orientation
        )
        settings_handle = nodes['settings_handle']
        cog_handle = nodes['cog_handle']
        fk_match_transforms = nodes['fk_match_transforms']
        handles = nodes['handles']
        ik_handles = nodes['ik_handles']
        fk_handles = nodes['fk_handles']

        joints = nodes['joints']

        root = this.get_root()
        for ik_handle in ik_handles:
            root.add_plugs(
                [
                    ik_handle.plugs['tx'],
                    ik_handle.plugs['ty'],
                    ik_handle.plugs['tz'],
                    ik_handle.plugs['rx'],
                    ik_handle.plugs['ry'],
                    ik_handle.plugs['rz']
                ]
            )

        for fk_handle in fk_handles:
            root.add_plugs(
                [
                    fk_handle.plugs['tx'],
                    fk_handle.plugs['ty'],
                    fk_handle.plugs['tz'],
                    fk_handle.plugs['rx'],
                    fk_handle.plugs['ry'],
                    fk_handle.plugs['rz']
                ]
            )
        root.add_plugs(
            [
                cog_handle.plugs['tx'],
                cog_handle.plugs['ty'],
                cog_handle.plugs['tz'],
                cog_handle.plugs['rx'],
                cog_handle.plugs['ry'],
                cog_handle.plugs['rz'],
                cog_handle.plugs['rotateOrder'],
                settings_handle.plugs['ikSwitch']
            ]
        )
        root.add_plugs(
            [settings_handle.plugs['cogVis']],
            keyable=False
        )
        this.set_handles(handles)
        this.joints = joints
        this.settings_handle = settings_handle
        this.cog_handle = cog_handle
        this.fk_match_transforms = fk_match_transforms
        return this

    @staticmethod
    def build_nodes(
            parent_group,
            joint_group,
            matrices,
            align_to_guide,
            cog_matrix,
            segment_names,
            legacy_orientation
    ):
        controller = parent_group.controller
        size = parent_group.size

        if not matrices:
            raise Exception('you must provide matrices to create a spine %s' % matrices)

        if align_to_guide:
            cog_matrix = matrices[1]
        else:
            cog_matrix = Matrix(Matrix(cog_matrix).get_translation())

        cog_handle = parent_group.create_child(
            CogHandle,
            segment_name='Cog',
            shape='square',
            line_width=3,
            matrix=cog_matrix,
            size=size * 2.0,
            rotation_order='xzy',
        )

        # Fk Spine
        parent_group.differentiation_name = 'Fk'
        fk_group = parent_group.create_child(
            Transform,
            segment_name='SubPart',
            matrix=Matrix()
        )
        parent_group.differentiation_name = None

        controller.create_parent_constraint(
            cog_handle.gimbal_handle,
            fk_group,
            mo=True
        )
        fk_nodes = BipedSpineFk.build_nodes(
            parent_group=fk_group,
            joint_group=joint_group,
            matrices=parent_group.matrices,
            align_to_guide=parent_group.align_to_guide,
            segment_names=segment_names
        )
        fk_joints = fk_nodes['joints']
        fk_handles = fk_nodes['handles']
        fk_hip_handle = fk_nodes['hip_handle']
        # Ik Spine
        parent_group.differentiation_name = 'Ik'
        ik_group = parent_group.create_child(
            Transform,
            segment_name='SubPart',
            matrix=Matrix()
        )
        parent_group.differentiation_name = None

        controller.create_parent_constraint(
            cog_handle.gimbal_handle,
            ik_group,
            mo=True
        )

        ik_nodes = BipedSpineIk.build_nodes(
            parent_group=ik_group,
            joint_group=joint_group,
            matrices=parent_group.matrices,
            align_to_guide=parent_group.align_to_guide,
            legacy_orientation=legacy_orientation
        )
        ik_joints = ik_nodes['joints']
        ik_handles = ik_nodes['handles']
        ik_hip_handle = ik_nodes['hip_handle']
        ik_chest_handle = ik_nodes['chest_handle']

        joints = []
        joint_parent = parent_group.joint_group
        for i in range(len(matrices)):
            if i == 0:
                segment_name = 'Hip'
            elif i == len(matrices) - 2:
                segment_name = 'Chest'
            elif i == len(matrices) - 1:
                segment_name = 'ChestEnd'
            else:
                segment_name = rig_factory.index_dictionary[i - 1].title()
            joint = parent_group.create_child(
                Joint,
                parent=joint_parent,
                matrix=matrices[i],
                segment_name=segment_name
            )
            joint_parent = joint
            joint.zero_rotation()
            joints.append(joint)

        settings_handle = parent_group.create_child(
            GroupedHandle,
            segment_name='Settings',
            shape='gear_simple',
            size=size * 0.5,
            group_count=1,
            parent=cog_handle.gimbal_handle,
            rotation_order='xzy',
        )
        settings_handle.groups[0].plugs.set_values(
            rz=-90,
            tz=-1.5 * size
        )
        settings_handle.plugs.set_values(
            overrideEnabled=True,
            overrideRGBColors=True,
            overrideColorRGB=env.colors['highlight']
        )
        ik_plug = settings_handle.create_plug(
            'ikSwitch',
            at='double',
            k=True,
            dv=0.0,
            min=0.0,
            max=1.0
        )

        cog_vis_plug = settings_handle.create_plug(
            'cogVis',
            at='double',
            k=True,
            dv=0.0,
            min=0.0,
            max=1.0
        )

        for crv in cog_handle.curves:
            cog_vis_plug.connect_to(crv.plugs['visibility'])

        for i, joint in enumerate(joints):
            index_character = rig_factory.index_dictionary[i].title(),
            pair_blend = parent_group.create_child(
                DependNode,
                node_type='pairBlend',
                segment_name='%sBlend' % index_character
            )
            blend_colors = parent_group.create_child(
                DependNode,
                node_type='blendColors',
                segment_name='%sColorBlend' % index_character
            )
            joint.plugs['overrideEnabled'].set_value(True)
            joint.plugs['overrideDisplayType'].set_value(2)
            joint.plugs['drawStyle'].set_value(False)
            ik_joints[i].plugs['translate'].connect_to(pair_blend.plugs['inTranslate2'])
            ik_joints[i].plugs['rotate'].connect_to(pair_blend.plugs['inRotate2'])
            fk_joints[i].plugs['translate'].connect_to(pair_blend.plugs['inTranslate1'])
            fk_joints[i].plugs['rotate'].connect_to(pair_blend.plugs['inRotate1'])
            pair_blend.plugs['outTranslate'].connect_to(joint.plugs['translate'])
            pair_blend.plugs['outRotate'].connect_to(joint.plugs['rotate'])
            pair_blend.plugs['rotInterpolation'].set_value(1)
            ik_plug.connect_to(pair_blend.plugs['weight'])
            ik_joints[i].plugs['scale'].connect_to(blend_colors.plugs['color1'])
            fk_joints[i].plugs['scale'].connect_to(blend_colors.plugs['color2'])
            blend_colors.plugs['output'].connect_to(joint.plugs['scale'])
            ik_plug.connect_to(blend_colors.plugs['blender'])
            joint.plugs['rotateOrder'].connect_to(fk_joints[i].plugs['rotateOrder'])
            joint.plugs['rotateOrder'].connect_to(ik_joints[i].plugs['rotateOrder'])

        fk_match_transforms = []
        for i, fk_handle in enumerate(fk_handles):
            index_character = rig_factory.index_dictionary[i].title(),
            fk_match_transform = ik_joints[i].create_child(
                Transform,
                parent=ik_joints[i],
                matrix=fk_handle.get_matrix(),
                segment_name='%sFkMatch' % index_character
            )
            fk_match_transform.create_child(Locator)
            fk_match_transforms.append(fk_match_transform)

        ik_plug.connect_to(ik_group.plugs['visibility'])

        visibility_reverse = parent_group.create_child(
            DependNode,
            segment_name='Visibility',
            node_type='reverse'
        )
        ik_plug.connect_to(visibility_reverse.plugs['inputX'])

        # Temporary solution to fix ikSwitch from connecting to spine top group
        visibility_reverse.plugs['outputX'].connect_to(fk_group.plugs['visibility'])

        lower_ik_match_joint = fk_joints[0].create_child(
            Transform,
            segment_name='LowerIkMatch',
            matrix=ik_hip_handle.get_matrix()
        )
        upper_ik_match_joint = fk_joints[-2].create_child(
            Transform,
            segment_name='UpperIkMatch',
            matrix=ik_chest_handle.get_matrix()
        )
        hip_fk_match_joint = ik_joints[0].create_child(
            Transform,
            segment_name='HipFkMatch',
            matrix=fk_hip_handle.get_matrix()
        )
        joints[0].plugs['type'].set_value(2)
        for joint in joints[1:]:
            joint.plugs['type'].set_value(6)

        for ik_joint in ik_joints:
            ik_joint.plugs.set_values(
                drawStyle=2
            )
        for fk_joint in fk_joints:
            fk_joint.plugs.set_values(
                drawStyle=2
            )
        handles = list(fk_handles)
        handles.extend(ik_handles)
        handles.append(settings_handle)
        handles.insert(0, cog_handle)

        return dict(
            joints=joints,
            handles=handles,
            cog_handle=cog_handle,
            settings_handle=settings_handle,
            fk_handles=fk_handles,
            ik_handles=ik_handles,
            fk_match_transforms=fk_match_transforms,
            lower_ik_match_joint=lower_ik_match_joint,
            upper_ik_match_joint=upper_ik_match_joint,
            hip_fk_match_joint=hip_fk_match_joint
        )

    def get_toggle_blueprint(self):
        blueprint = super(BipedSpineIkFk, self).get_toggle_blueprint()
        blueprint['legacy_orientation'] = self.legacy_orientation
        return blueprint

    def get_blueprint(self):
        blueprint = super(BipedSpineIkFk, self).get_blueprint()
        blueprint['cog_matrix'] = list(self.cog_matrix),
        return blueprint
