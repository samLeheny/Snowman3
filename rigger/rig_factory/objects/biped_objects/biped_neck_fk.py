import rig_factory
from Snowman3.rigger.rig_factory.objects.part_objects.chain_guide import ChainGuide
from Snowman3.rigger.rig_factory.objects.part_objects.part import Part
from Snowman3.rigger.rig_factory.objects.node_objects.joint import Joint
from Snowman3.rigger.rig_factory.objects.rig_objects.grouped_handle import LocalHandle
from Snowman3.rigger.rig_factory.objects.base_objects.properties import ObjectProperty, DataProperty
from Snowman3.rigger.rig_math.matrix import Matrix
import Snowman3.utilities.positions as pos


class BipedNeckFkGuide(ChainGuide):
   default_settings = dict(
       root_name='Neck',
       size=1.0,
       side='center',
       count=5
   )

   def __init__(self, **kwargs):
       super(BipedNeckFkGuide, self).__init__(**kwargs)
       self.toggle_class = BipedNeckFk.__name__

   @classmethod
   def create(cls, **kwargs):
       kwargs['up_vector_indices'] = [0]
       kwargs.setdefault('root_name', 'Spine')
       this = super(BipedNeckFkGuide, cls).create(**kwargs)
       this.set_handle_positions(pos.BIPED_POSITIONS)
       return this

   def get_toggle_blueprint(self):
       blueprint = super(BipedNeckFkGuide, self).get_toggle_blueprint()
       matrices = [list(x.get_matrix()) for x in self.joints]
       blueprint['matrices'] = matrices
       return blueprint


class BipedNeckFk(Part):
   head_handle = ObjectProperty(
       name='head_handle'
   )
   head_matrix = DataProperty(
       name='head_matrix',
       default_value=list(Matrix())
   )

   def __init__(self, **kwargs):
       super(BipedNeckFk, self).__init__(**kwargs)

   @classmethod
   def create(cls, **kwargs):
       if 'side' not in kwargs:
           raise Exception('you must provide a "side" keyword argument to create a %s' % cls.__name__)
       kwargs['head_matrix'] = list(kwargs.pop('head_matrix', Matrix()))
       this = super(BipedNeckFk, cls).create(**kwargs)
       nodes = cls.build_nodes(
           parent_group=this,
           joint_group=this.joint_group,
           matrices=this.matrices,
           head_matrix=this.head_matrix
       )
       handles = nodes['handles']
       head_handle = nodes['head_handle']
       joints = nodes['joints']

       root = this.get_root()
       for handle in handles:
           root.add_plugs([
               handle.plugs['tx'],
               handle.plugs['ty'],
               handle.plugs['tz'],
               handle.plugs['rx'],
               handle.plugs['ry'],
               handle.plugs['rz']
           ])
       this.set_handles(handles)
       this.head_handle = head_handle
       this.joints = joints
       return this

   @staticmethod
   def build_nodes(
           parent_group,
           joint_group,
           matrices,
           head_matrix
   ):
       controller = parent_group.controller
       size = parent_group.size
       root_name = parent_group.root_name
       handle_parent = parent_group
       joint_parent = joint_group
       matrix_count = len(matrices)
       handles = []
       joints = []
       for x, matrix in enumerate(matrices):
           if x == 0:
               segment_name = 'Root'
           else:
               segment_name = rig_factory.index_dictionary[x - 1].title()
           joint = parent_group.create_child(
               Joint,
               root_name=root_name,
               matrix=matrix,
               parent=joint_parent,
               segment_name=segment_name
           )
           joint.zero_rotation()
           joints.append(joint)
           joint_parent = joint

           # Creates handles for all joints except the first, and the
           # final two.
           if x < matrix_count - 2:
               handle = parent_group.create_child(
                   LocalHandle,
                   size=size * 1.25,
                   matrix=matrix,
                   shape='circle',
                   parent=handle_parent,
                   segment_name=segment_name,
                   rotation_order='xzy'
               )
               handle.stretch_shape(matrices[x + 1])
               handle.multiply_shape_matrix(
                   Matrix(scale=[0.85, 0.85, 0.85])
               )
               handle_parent = handle.gimbal_handle
               handles.append(handle)
               controller.create_parent_constraint(handle, joint)

       # Creates the "Head" handle.
       head_handle = parent_group.create_child(
           LocalHandle,
           segment_name='Head',
           size=size,
           matrix=Matrix(matrices[-1].get_translation()),
           shape='cube_head',
           parent=handles[-1].gimbal_handle,
           rotation_order='xzy'
       )
       head_handle.set_shape_matrix(Matrix(head_matrix))

       controller.create_parent_constraint(
           head_handle.gimbal_handle,
           joints[-1],
           mo=True
       )
       handles.append(head_handle)
       return dict(
           handles=handles,
           joints=joints,
           head_handle=head_handle
       )



