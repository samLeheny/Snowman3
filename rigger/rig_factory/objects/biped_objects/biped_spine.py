import logging
import os
import Snowman3.rigger.rig_factory as rig_factory
import Snowman3.rigger.rig_factory.positions as pos
from Snowman3.rigger.rig_factory.objects.part_objects.part import Part
import Snowman3.rigger.rig_factory.utilities.biped_spine_spline as spine_spline
from Snowman3.rigger.rig_factory.objects.node_objects.joint import Joint
from Snowman3.rigger.rig_factory.objects.node_objects.transform import Transform
from Snowman3.rigger.rig_factory.objects.rig_objects.grouped_handle import LocalHandle
from Snowman3.rigger.rig_factory.objects.biped_objects.biped_spine_ik_fk import BipedSpineIkFk
from Snowman3.rigger.rig_factory.objects.part_objects.spline_chain_guide import SplineChainGuide
from Snowman3.rigger.rig_factory.objects.base_objects.properties import ObjectProperty, ObjectListProperty, DataProperty


class BipedSpineGuide(SplineChainGuide):

    default_settings = dict(
        root_name='Spine',
        size=15.0,
        side='center',
        joint_count=9,
        count=5,
        squash=0.0,
        twist_type=0,
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
    degree = DataProperty( name='degree' )
    twist_type = DataProperty( name='twist_type', default_value=0 )
    legacy_orientation = DataProperty( name='legacy_orientation', default_value=False )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.toggle_class = BipedSpine.__name__

    @classmethod
    def create(cls, **kwargs):
        kwargs.setdefault('root_name', 'Spine')
        count = kwargs.get('count', cls.default_settings['count'])
        kwargs['segment_names'] = build_segment_names(count)
        this = super().create(**kwargs)
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
        if this.spline_joints:
            cog_position = this.spline_joints[1].get_matrix().get_translation()
            this.spline_joints[0].set_parent(hip_joint)
        else:
            cog_position = this.joints[1].get_matrix().get_translation()
        this.spline_joints.insert(0, hip_joint)

        cog_handle = this.create_handle(
            segment_name='Cog',
            matrix=cog_position,
            rotation_order='xzy',
        )
        size_plug.connect_to(cog_handle.plugs['size'])
        cog_handle.mesh.assign_shading_group(shader)
        this.cog_handle = cog_handle
        this.base_joints = list(this.joints)
        this.joints.extend(this.spline_joints)
        return this

    def after_first_create(self):
        self.set_handle_positions(pos.BIPED_POSITIONS)

    def get_toggle_blueprint(self):
        blueprint = super().get_toggle_blueprint()
        blueprint['cog_matrix'] = list(self.cog_handle.get_matrix())
        blueprint['matrices'] = [list(x.get_matrix()) for x in self.base_joints]
        blueprint['joint_count'] = len(self.spline_joints)
        blueprint['twist_type'] = self.twist_type
        return blueprint


class BipedSpine(Part):

    spline_joints = ObjectListProperty( name='spline_joints' )
    settings_handle = ObjectProperty( name='settings_handle' )
    cog_handle = ObjectProperty( name='cog_handle' )
    squash = DataProperty( name='squash' )
    align_to_guide = DataProperty( name='align_to_guide' )
    degree = DataProperty( name='degree' )
    twist_type = DataProperty( name='twist_type', default_value=0 )
    legacy_orientation = DataProperty( name='legacy_orientation', default_value=False )

    def __init__(self, **kwargs):
        super(BipedSpine, self).__init__(**kwargs)

    cog_matrix = None

    @classmethod
    def create(cls, **kwargs):
        this = super(BipedSpine, cls).create(**kwargs)
        if 'joint_matrices' in kwargs:
            logging.getLogger('rig_build').warning(
                '%s found legacy data "joint_matrices" found. converting to "joint_count"' % cls.__name__
            )
            joint_count = len(kwargs['joint_matrices'])
        elif 'joint_count' in kwargs:
            joint_count = kwargs['joint_count']
        else:
            joint_count = 0
            logging.getLogger('rig_build').warning(
                '%s unable to resolve joint count.  defaulting to 0' % cls.__name__
            )
        segment_names = build_segment_names(len(this.matrices))
        nodes = cls.build_nodes(
            parent_group=this,
            joint_group=this.joint_group,
            matrices=this.matrices,
            joint_count=joint_count,
            align_to_guide=this.align_to_guide,
            squash=this.squash,
            cog_matrix=this.cog_matrix,
            segment_names=segment_names,
            degree=this.degree,
            twist_type=this.twist_type,
            legacy_orientation=this.legacy_orientation
        )

        root = this.get_root()
        joints = nodes['joints']
        spline_joints = nodes['spline_joints']
        settings_handle = nodes['settings_handle']
        cog_handle = nodes['cog_handle']
        handles = nodes['handles']
        ik_handles = nodes['ik_handles']
        fk_handles = nodes['fk_handles']
        tweak_handles = nodes['tweak_handles']

        for ik_handle in ik_handles:
            root.add_plugs(
                [ ik_handle.plugs['tx'],
                  ik_handle.plugs['ty'],
                  ik_handle.plugs['tz'],
                  ik_handle.plugs['rx'],
                  ik_handle.plugs['ry'],
                  ik_handle.plugs['rz'],
                  ik_handle.plugs['sx'],
                  ik_handle.plugs['sy'],
                  ik_handle.plugs['sz'] ]
            )

        for fk_handle in fk_handles:
            root.add_plugs(
                [ fk_handle.plugs['tx'],
                  fk_handle.plugs['ty'],
                  fk_handle.plugs['tz'],
                  fk_handle.plugs['rx'],
                  fk_handle.plugs['ry'],
                  fk_handle.plugs['rz'],
                  fk_handle.plugs['sx'],
                  fk_handle.plugs['sy'],
                  fk_handle.plugs['sz'] ]
            )
        for tweak_handle in tweak_handles:
            root.add_plugs(
                [ tweak_handle.plugs['tx'],
                  tweak_handle.plugs['ty'],
                  tweak_handle.plugs['tz'],
                  tweak_handle.plugs['rx'],
                  tweak_handle.plugs['ry'],
                  tweak_handle.plugs['rz'],
                  tweak_handle.plugs['sx'],
                  tweak_handle.plugs['sy'],
                  tweak_handle.plugs['sz'] ]
            )
        root.add_plugs(
            [ cog_handle.plugs['tx'],
              cog_handle.plugs['ty'],
              cog_handle.plugs['tz'],
              cog_handle.plugs['rx'],
              cog_handle.plugs['ry'],
              cog_handle.plugs['rz'],
              cog_handle.plugs['rotateOrder'],
              settings_handle.plugs['ikSwitch'],
              settings_handle.plugs['squash'],
              settings_handle.plugs['squashMin'],
              settings_handle.plugs['squashMax'] ],
        )
        root.add_plugs(
            [ settings_handle.plugs['cogVis'],
              settings_handle.plugs['TweakCtrlVis'],
              settings_handle.plugs['TwistStyle'] ],
            keyable=False
        )
        this.set_handles(handles)
        this.joints = joints
        this.spline_joints = spline_joints
        this.settings_handle = settings_handle
        this.cog_handle = cog_handle
        return this

    @staticmethod
    def build_nodes(
            parent_group,
            joint_group,
            matrices,
            joint_count,
            cog_matrix,
            align_to_guide,
            squash,
            segment_names,
            degree,
            twist_type,
            legacy_orientation

    ):
        controller = parent_group.controller
        size = parent_group.size
        nodes = BipedSpineIkFk.build_nodes(
            parent_group=parent_group,
            joint_group=joint_group,
            matrices=matrices,
            align_to_guide=align_to_guide,
            cog_matrix=cog_matrix,
            segment_names=segment_names,
            legacy_orientation=legacy_orientation
        )

        settings_handle = nodes['settings_handle']
        cog_handle = nodes['cog_handle']
        base_joints = nodes['joints']
        base_handles = nodes['handles']
        ik_handles = nodes['ik_handles']
        fk_handles = nodes['fk_handles']
        driver_transforms = []
        tweak_handles = []
        for i in range(len(base_joints)):
            base_joint = base_joints[i]
            driver = base_joint
            if 0 < i < len(base_joints) - 1:
                tweak_handle = parent_group.create_child(
                    LocalHandle,
                    size=size * 1.25,
                    matrix=matrices[i],
                    shape='square',
                    parent=base_joint,
                    segment_name=segment_names[i],
                    rotation_order='xzy',
                    create_gimbal=False,
                    subsidiary_name='Tweak'
                )
                tweak_handles.append(tweak_handle)
                driver = tweak_handle

            driver_transform = parent_group.create_child(
                Transform,
                segment_name='%sDriver' % base_joint.segment_name,
                parent=joint_group
            )
            controller.create_parent_constraint(driver, driver_transform)
            controller.create_scale_constraint(driver, driver_transform)
            driver_transforms.append(driver_transform)

        settings_handle.create_plug(
            'squash',
            attributeType='float',
            keyable=True,
            defaultValue=squash,
        )
        settings_handle.create_plug(
            'squashMin',
            attributeType='float',
            keyable=True,
            defaultValue=0.1,
        )
        settings_handle.create_plug(
            'squashMax',
            attributeType='float',
            keyable=True,
            defaultValue=5,
        )
        tweak_vis_plug = settings_handle.create_plug(
            'TweakCtrlVis',
            attributeType='bool',
            keyable=False,
            defaultValue=False,
        )
        twist_style_plug = settings_handle.create_plug(
            'TwistStyle',
            attributeType='enum',
            en='StartEnd:Segments:',
            defaultValue=0,
            keyable=False
        )
        twist_style_plug.set_channel_box(True)
        tweak_vis_plug.set_channel_box(True)
        twist_style_plug.set_value(twist_type)

        for tweak_handle in tweak_handles:
            for crv in tweak_handle.curves:
                tweak_vis_plug.connect_to(crv.plugs['v'])

        spline_nodes = spine_spline.create_rig_spline(
            parent_group=parent_group,
            joint_group=joint_group,
            driver_transforms=driver_transforms,
            count=joint_count,
            degree=degree,
            twist_type=twist_type

        )
        spline_joints = spline_nodes['spline_joints']
        spline_node = spline_nodes['spline_node']
        twist_style_plug.connect_to(spline_node.plugs['twistType'])
        all_handles = []
        all_handles.extend(base_handles)
        all_handles.extend(tweak_handles)
        return dict(
            joints=base_joints + spline_joints,
            spline_joints=spline_joints,
            handles=all_handles,
            ik_handles=ik_handles,
            fk_handles=fk_handles,
            tweak_handles=tweak_handles,
            settings_handle=settings_handle,
            cog_handle=cog_handle
        )

    def get_toggle_blueprint(self):
        blueprint = super(BipedSpine, self).get_toggle_blueprint()
        blueprint['twist_type'] = self.twist_type
        blueprint['legacy_orientation'] = self.legacy_orientation
        return blueprint

    def get_blueprint(self):
        blueprint = super(BipedSpine, self).get_blueprint()
        blueprint['joint_count'] = len(self.spline_joints)
        blueprint['squash'] = self.settings_handle.plugs['squash'].get_value()
        blueprint['cog_matrix'] = list(self.cog_matrix)
        blueprint['twist_type'] = self.twist_type
        return blueprint


def build_segment_names(count):
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
    return segment_names
