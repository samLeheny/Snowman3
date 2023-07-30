import os
import rig_factory
from Snowman3.rigger.rig_math.matrix import Matrix
import Snowman3.utilities.positions as pos
from Snowman3.rigger.rig_factory.objects.part_objects.part import Part
import rig_factory.utilities.biped_spine_spline as sps
from Snowman3.rigger.rig_factory.objects.node_objects.joint import Joint
from rig_factory.objects.biped_objects.biped_spine_reverse_ik_fk import BipedSpineReverseIkFk
from rig_factory.objects.part_objects.spline_chain_guide import SplineChainGuide
from Snowman3.rigger.rig_factory.objects.base_objects.properties import ObjectProperty, ObjectListProperty, DataProperty


class BipedReverseSpineGuide(SplineChainGuide):

   default_settings = dict(
       root_name='Spine',
       size=15.0,
       side='center',
       joint_count=9,
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
       super(BipedReverseSpineGuide, self).__init__(**kwargs)
       self.toggle_class = BipedReverseSpine.__name__

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
       this = super(BipedReverseSpineGuide, cls).create(**kwargs)
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
       blueprint = super(BipedReverseSpineGuide, self).get_toggle_blueprint()
       blueprint['cog_matrix'] = list(self.cog_handle.get_matrix())
       blueprint['matrices'] = [list(x.get_matrix()) for x in self.base_joints]
       return blueprint


class BipedReverseSpine(Part):

   spline_joints = ObjectListProperty(
       name='spline_joints'
   )
   settings_handle = ObjectProperty(
       name='settings_handle',
   )
   cog_handle = ObjectProperty(
       name='cog_handle',
   )
   squash = DataProperty(
       name='squash',
   )
   align_to_guide = DataProperty(
       name='align_to_guide',
   )
   segment_names = DataProperty(
       name='segment_names'
   )
   joint_matrices = []

   def __init__(self, **kwargs):
       super(BipedReverseSpine, self).__init__(**kwargs)

   cog_matrix = None

   @classmethod
   def create(cls, **kwargs):
       this = super(BipedReverseSpine, cls).create(**kwargs)
       nodes = cls.build_nodes(
           parent_group=this,
           joint_group=this.joint_group,
           matrices=this.matrices,
           spline_matrices=this.joint_matrices,
           utility_group=this.utility_group,
           scale_multiply_transform=this.scale_multiply_transform,
           align_to_guide=this.align_to_guide,
           squash=this.squash,
           cog_matrix=Matrix(this.cog_matrix),
           segment_names=this.segment_names
       )

       root = this.get_root()
       joints = nodes['joints']
       spline_joints = nodes['spline_joints']
       settings_handle = nodes['settings_handle']
       cog_handle = nodes['cog_handle']
       handles = nodes['handles']
       ik_handles = nodes['ik_handles']
       fk_handles = nodes['fk_handles']
       driver_spline_joints = nodes['driver_spline_joints']

       for spline_joint in spline_joints:
           root.add_plugs(
               [
                   spline_joint.plugs['rx'],
                   spline_joint.plugs['ry'],
                   spline_joint.plugs['rz']
               ],
               keyable=False
           )
       for driver_spline_joint in driver_spline_joints:
           root.add_plugs(
               [
                   driver_spline_joint.plugs['rx'],
                   driver_spline_joint.plugs['ry'],
                   driver_spline_joint.plugs['rz']
               ],
               keyable=False
           )

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
               settings_handle.plugs['reverse'],
               settings_handle.plugs['squash'],
               settings_handle.plugs['squashMin'],
               settings_handle.plugs['squashMax'],
           ],
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
           utility_group,
           scale_multiply_transform,
           matrices,
           spline_matrices,
           cog_matrix,
           align_to_guide,
           squash,
           segment_names

   ):
       nodes = BipedSpineReverseIkFk.build_nodes(
           parent_group=parent_group,
           joint_group=joint_group,
           matrices=matrices,
           align_to_guide=align_to_guide,
           cog_matrix=cog_matrix,
           segment_names=segment_names
       )

       settings_handle = nodes['settings_handle']
       cog_handle = nodes['cog_handle']
       base_joints = nodes['joints']
       base_handles = nodes['handles']
       ik_handles = nodes['ik_handles']
       fk_handles = nodes['fk_handles']

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

       spline_nodes = sps.create_spline(
           base_joints,
           parent_group,
           utility_group,
           spline_matrices,
           settings_handle,
           scale_multiply_transform
       )
       spline_joints = spline_nodes['spline_joints']
       driver_spline_joints = spline_nodes['driver_spline_joints']

       return dict(
           joints=base_joints + spline_joints,
           spline_joints=spline_joints,
           handles=base_handles,
           ik_handles=ik_handles,
           fk_handles=fk_handles,
           settings_handle=settings_handle,
           driver_spline_joints=driver_spline_joints,
           cog_handle=cog_handle
       )

   def get_blueprint(self):
       blueprint = super(BipedReverseSpine, self).get_blueprint()
       blueprint['joint_matrices'] = [list(x) for x in self.joint_matrices]
       blueprint['squash'] = self.settings_handle.plugs['squash'].get_value()
       blueprint['cog_matrix'] = list(self.cog_matrix)
       return blueprint

