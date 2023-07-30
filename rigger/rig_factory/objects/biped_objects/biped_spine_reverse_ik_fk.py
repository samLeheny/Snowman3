import os
import rig_factory
from Snowman3.rigger.rig_math.matrix import Matrix
import Snowman3.utilities.positions as pos
import rig_factory.environment as env
from Snowman3.rigger.rig_factory.objects.part_objects.part import Part
from Snowman3.rigger.rig_factory.objects.node_objects.joint import Joint
from rig_factory.objects.node_objects.transform import Transform
from Snowman3.rigger.rig_factory.objects.part_objects.chain_guide import ChainGuide
from rig_factory.objects.node_objects.depend_node import DependNode
from rig_factory.objects.biped_objects.biped_spine_ik import BipedSpineIk
from rig_factory.objects.biped_objects.biped_spine_fk import BipedSpineFk
from rig_factory.objects.biped_objects.biped_spine_reverse_fk import BipedSpineReverseFk
from rig_factory.objects.biped_objects.biped_spine_reverse_ik import BipedSpineReverseIk

from rig_factory.objects.rig_objects.grouped_handle import CogHandle, GroupedHandle
from Snowman3.rigger.rig_factory.objects.base_objects.properties import ObjectProperty, ObjectListProperty, DataProperty


class BipedSpineReverseIkFkGuide(ChainGuide):

   default_settings = dict(
       root_name='Spine',
       size=15.0,
       side='center',
       count=5,
       squash=0.0,
       rename_cog=True,
       align_to_guide=False,
       use_plugins=os.getenv('USE_RIG_PLUGINS', False)
   )
   squash = DataProperty(
       name='squash',
   )
   cog_handle = ObjectProperty(
       name='cog_handle',
   )
   rename_cog = DataProperty(
       name='rename_cog',
       default_value=True,
   )
   align_to_guide = DataProperty(
       name='align_to_guide',
   )
   base_joints = ObjectListProperty(
       name='base_joints'
   )

   def __init__(self, **kwargs):
       super(BipedSpineReverseIkFkGuide, self).__init__(**kwargs)
       self.toggle_class = BipedSpineReverseIkFk.__name__

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
       this = super(BipedSpineReverseIkFkGuide, cls).create(**kwargs)
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
       blueprint = super(BipedSpineReverseIkFkGuide, self).get_toggle_blueprint()
       blueprint['cog_matrix'] = list(self.cog_handle.get_matrix())
       return blueprint


class BipedSpineReverseIkFk(Part):
   align_to_guide = DataProperty(
       name='align_to_guide',
   )
   settings_handle = ObjectProperty(
       name='settings_handle',
   )
   cog_handle = ObjectProperty(
       name='cog_handle',
   )
   segment_names = DataProperty(
       name='segment_names'
   )
   cog_matrix = None

   @classmethod
   def create(cls, **kwargs):
       this = super(BipedSpineReverseIkFk, cls).create(**kwargs)
       nodes = cls.build_nodes(
           parent_group=this,
           joint_group=this.joint_group,
           matrices=this.matrices,
           align_to_guide=this.align_to_guide,
           cog_matrix=Matrix(kwargs.get('cog_matrix', this.matrices[1])),
           segment_names=this.segment_names
       )
       settings_handle = nodes['settings_handle']
       cog_handle = nodes['cog_handle']
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
               settings_handle.plugs['ikSwitch'],
               settings_handle.plugs['reverse']

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
       return this

   @staticmethod
   def build_nodes(
           parent_group,
           joint_group,
           matrices,
           align_to_guide,
           cog_matrix,
           segment_names
   ):
       size = parent_group.size
       controller = parent_group.controller
       if not matrices:
           raise Exception('you must provide matrices to create a spine %s' % matrices)
       if not align_to_guide:
           cog_matrix = Matrix(cog_matrix.get_translation())
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
       cog_handle = parent_group.create_child(
           CogHandle,
           segment_name='Cog',
           shape='square',
           line_width=3,
           matrix=cog_matrix,
           size=size*2.0,
           rotation_order='xzy',
       )

       # Sub-Part Groups
       base_group = parent_group.create_child(
           Transform,
           segment_name='SubPart',
           differentiation_name='Base',
           matrix=Matrix(),
           parent=cog_handle.gimbal_handle
       )
       reverse_base_group = parent_group.create_child(
           Transform,
           segment_name='SubPart',
           differentiation_name='ReverseBase',
           matrix=Matrix(),
           parent=cog_handle.gimbal_handle
       )
       fk_group = parent_group.create_child(
           Transform,
           segment_name='SubPart',
           differentiation_name='Fk',
           matrix=Matrix(),
           parent=base_group
       )
       ik_group = parent_group.create_child(
           Transform,
           segment_name='SubPart',
           differentiation_name='Ik',
           matrix=Matrix(),
           parent=base_group
       )
       reverse_fk_group = parent_group.create_child(
           Transform,
           segment_name='SubPart',
           differentiation_name='FkRev',
           matrix=Matrix(),
           parent=reverse_base_group
       )
       reverse_ik_group = parent_group.create_child(
           Transform,
           segment_name='SubPart',
           differentiation_name='IkRev',
           matrix=Matrix(),
           parent=reverse_base_group
       )

       # Fk Spine
       fk_nodes = BipedSpineFk.build_nodes(
           parent_group=fk_group,
           joint_group=joint_group,
           matrices=parent_group.matrices,
           align_to_guide=parent_group.align_to_guide,
           segment_names=segment_names
       )
       fk_joints = fk_nodes['joints']
       fk_handles = fk_nodes['handles']
       hip_handle = fk_nodes['hip_handle']

       # Ik Spine
       ik_nodes = BipedSpineIk.build_nodes(
           parent_group=ik_group,
           joint_group=joint_group,
           matrices=parent_group.matrices,
           align_to_guide=parent_group.align_to_guide,
           legacy_orientation=False
       )
       ik_joints = ik_nodes['joints']
       ik_handles = ik_nodes['handles']

       # Reverse Fk Spine
       reverse_fk_nodes = BipedSpineReverseFk.build_nodes(
           parent_group=reverse_fk_group,
           joint_group=joint_group,
           matrices=matrices,
           align_to_guide=parent_group.align_to_guide,
           segment_names=segment_names
       )
       reverse_fk_joints = reverse_fk_nodes['joints']
       reverse_fk_handles = reverse_fk_nodes['handles']
       # Reverse Ik Spine
       reverse_ik_nodes = BipedSpineReverseIk.build_nodes(
           parent_group=reverse_ik_group,
           joint_group=joint_group,
           matrices=matrices,
           align_to_guide=parent_group.align_to_guide
       )
       reverse_ik_joints = reverse_ik_nodes['joints']
       reverse_ik_handles = reverse_ik_nodes['handles']

       #  Joints
       joint_parent = joint_group
       joints = []
       for i in range(len(matrices)):
           joint = parent_group.create_child(
               Joint,
               parent=joint_parent,
               matrix=matrices[i],
               segment_name=segment_names[i]
           )
           joint_parent = joint
           joints.append(joint)
           joint.zero_rotation()

       #  Forward Joints
       joint_parent = joint_group
       forward_joints = []
       for i in range(len(matrices)):
           joint = parent_group.create_child(
               Joint,
               parent=joint_parent,
               matrix=matrices[i],
               segment_name='%sFwd' % segment_names[i]
           )
           joint_parent = joint
           forward_joints.append(joint)
           joint.zero_rotation()

       #  Reversed Joints
       joint_parent = joint_group
       reverse_joints = []
       for i in reversed(range(len(reverse_fk_joints))):
           reverse_joint = parent_group.create_child(
               Joint,
               parent=joint_parent,
               matrix=reverse_fk_joints[i].get_matrix(),
               segment_name='%sRev' % segment_names[i]
           )
           reverse_joints.insert(0, reverse_joint)
           reverse_joint.zero_rotation()
           joint_parent = reverse_joint

       #  Inverted Joints
       joint_parent = joint_group
       inverted_joints = []
       for i in range(len(matrices)):
           inverted_joint = parent_group.create_child(
               Joint,
               parent=joint_parent,
               matrix=matrices[i],
               segment_name='%sInverted' % segment_names[i]
           )
           joint_parent = inverted_joint
           inverted_joints.append(inverted_joint)
           inverted_joint.zero_rotation()
           controller.create_parent_constraint(
               reverse_joints[i],
               inverted_joint,
               mo=True
           )

       settings_handle = parent_group.create_child(
           GroupedHandle,
           segment_name='Settings',
           shape='gear_simple',
           size=size*0.5,
           group_count=1,
           parent=joints[0],
           rotation_order='xzy',
       )
       settings_handle.groups[0].plugs.set_values(
           rz=-90,
           tz=-1.5*size
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
       reversed_plug = settings_handle.create_plug(
           'reverse',
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

       blend_joints(
           fk_joints,
           ik_joints,
           forward_joints,
           ik_plug
       )

       blend_joints(
           reverse_fk_joints,
           reverse_ik_joints,
           reverse_joints,
           ik_plug
       )

       blend_joints(
           forward_joints,
           inverted_joints,
           joints,
           reversed_plug
       )

       ik_plug.connect_to(ik_group.plugs['visibility'])
       ik_plug.connect_to(reverse_ik_group.plugs['visibility'])
       reversed_plug.connect_to(reverse_base_group.plugs['visibility'])
       visibility_reverse = parent_group.create_child(
           DependNode,
           segment_name='Visibility',
           node_type='reverse'
       )
       ik_plug.connect_to(visibility_reverse.plugs['inputX'])
       visibility_reverse.plugs['outputX'].connect_to(fk_group.plugs['visibility'])
       visibility_reverse.plugs['outputX'].connect_to(reverse_fk_group.plugs['visibility'])
       reverse_reverse = parent_group.create_child(
           DependNode,
           segment_name='Reverse',
           node_type='reverse'
       )
       reversed_plug.connect_to(reverse_reverse.plugs['inputX'])
       reverse_reverse.plugs['outputX'].connect_to(base_group.plugs['visibility'])

       ik_fk_joints = ik_joints + fk_joints + reverse_ik_joints + reverse_fk_joints
       all_joints = ik_fk_joints + inverted_joints + forward_joints + reverse_joints
       for joint in all_joints:
           joint.plugs.set_values(
               drawStyle=2
           )

       handles = list(fk_handles)
       handles.extend(ik_handles)
       handles.extend(reverse_ik_handles)
       handles.extend(reverse_fk_handles)
       handles.append(settings_handle)
       handles.append(cog_handle)

       return dict(
           joints=joints,
           handles=handles,
           ik_handles=ik_handles + reverse_ik_handles,
           fk_handles=fk_handles + reverse_fk_handles,
           cog_handle=cog_handle,
           settings_handle=settings_handle
       )

   def get_blueprint(self):
       blueprint = super(BipedSpineReverseIkFk, self).get_blueprint()
       blueprint['cog_matrix'] = list(self.cog_matrix)
       return blueprint


def blend_joints(
       joint_list_1,
       joint_list_2,
       target_joints,
       weight_plug
):
   if not len(joint_list_1) == len(joint_list_2) == len(target_joints):
       raise Exception(
           'Joint counts did not match: %s, %s, %s' % (
               len(joint_list_1),
               len(joint_list_1),
               len(target_joints))
       )
   for i in range(len(target_joints)):
       pair_blend = target_joints[i].create_child(
           DependNode,
           node_type='pairBlend',
           segment_name='%sBlend' % target_joints[i].segment_name
       )
       target_joints[i].plugs['overrideEnabled'].set_value(True)
       target_joints[i].plugs['overrideDisplayType'].set_value(2)
       target_joints[i].plugs['drawStyle'].set_value(False)
       joint_list_1[i].plugs['translate'].connect_to(pair_blend.plugs['inTranslate1'])
       joint_list_1[i].plugs['rotate'].connect_to(pair_blend.plugs['inRotate1'])
       joint_list_2[i].plugs['translate'].connect_to(pair_blend.plugs['inTranslate2'])
       joint_list_2[i].plugs['rotate'].connect_to(pair_blend.plugs['inRotate2'])
       pair_blend.plugs['outTranslate'].connect_to(target_joints[i].plugs['translate'])
       pair_blend.plugs['outRotate'].connect_to(target_joints[i].plugs['rotate'])
       pair_blend.plugs['rotInterpolation'].set_value(1)
       weight_plug.connect_to(pair_blend.plugs['weight'])
       target_joints[i].plugs['rotateOrder'].connect_to(joint_list_2[i].plugs['rotateOrder'])
       target_joints[i].plugs['rotateOrder'].connect_to(joint_list_1[i].plugs['rotateOrder'])


