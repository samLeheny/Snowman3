import os
import logging
import weakref
import maya.api.OpenMaya as om
import Snowman3.rigger.rig_factory.objects as obs
import Snowman3.rigger.rig_factory.common_modules as com
import Snowman3.rigger.utilities.curve_utils as curve_utils
import Snowman3.rigger.rig_factory.utilities.rig_utilities as rig_utils
import Snowman3.rigger.rig_factory.utilities.node_utilities.node_utilities as node_utils
import Snowman3.rigger.rig_factory.utilities.handle_utilities as handle_utils
import Snowman3.rigger.rig_factory.utilities.decorators as dec
import Snowman3.rigger.rig_factory.build.utilities.mirror_utilities as mirror_utils
import Snowman3.utilities.PySignal as PySignal
from Snowman3.rigger.rig_factory.scene.maya_scene import MayaScene
from Snowman3.rigger.managers.blueprint_manager import BlueprintManager
from Snowman3.rigger.rig_factory.objects.node_objects.transform import Transform
from Snowman3.rigger.rig_math.matrix import Matrix
from Snowman3.rigger.rig_factory.objects.base_objects.weak_list import WeakList
from collections import OrderedDict


###########################
######## Variables ########
# -
ARMATURE_STATE_TAG = 'Armature'
RIG_STATE_TAG = 'Rig'
# -
###########################
###########################


class RigController:
    # Signals on the controller are all being phased out and moved to system_signals.py
    sdk_network_changed_signal = PySignal.ClassSignal()
    start_sdk_ownership_signal = PySignal.ClassSignal()
    end_sdk_ownership_signal = PySignal.ClassSignal()
    start_sdk_disown_signal = PySignal.ClassSignal()
    end_sdk_disown_signal = PySignal.ClassSignal()
    progress_signal = PySignal.ClassSignal()
    failed_signal = PySignal.ClassSignal()
    deleted_signal = PySignal.ClassSignal()
    raise_warning_signal = PySignal.ClassSignal()  # Get rid of this and refactor
    raise_error_signal = PySignal.ClassSignal()
    item_changed_signal = PySignal.ClassSignal()  # This is not efficient, it should be split by types
    use_module_versions = not (os.environ.get('PIPE_DEV_MODE') == 'TRUE')  # only use module versions on production
    active_controllers = []
    ordered_vertex_selection_enabled = False
    ordered_vertex_selection = []
    registered_parts = OrderedDict()
    registered_containers = []
    build_warnings = []
    currently_saving = False
    build_directory = None
    log_path = None
    failed_state = False
    face_network = None
    locked_face_drivers = False
    disable_warnings = False
    debug_garbage_collection = True  # Display referents for objects that fail to garbage collect
    root = None
    deleted_object_names = []
    # self.get_class_function = None
    DEBUG = os.getenv('PIPE_DEV_MODE') == 'TRUE'
    objects_scheduled_for_deletion = WeakList()
    current_layer = None
    namespace = None
    object_layers = dict()
    named_objects = None
    nodes_scheduled_for_deletion = []
    uuid = None
    scene = None

    '''
    # -
    asset_name = None
    dirpath = None
    blueprint_manager = None
    state = None
    # -
    root = None
    current_layer = None
    namespace = None
    build_directory = None
    named_objects = None
    scene = None
    '''



    def __init__(self):
        super().__init__()
        #self.uuid = str(uuid.uuid4())
        self.named_objects = weakref.WeakValueDictionary()



    def __setattr__(self, name, value):
        if hasattr(self, name):
            try:
                super().__setattr__(name, value)
            except Exception:
                raise Exception(f'The property "{name}" on the {type(self)} named "{self}" could not be set to:'
                                f'type<{type(value)}> {value}.')

        else:
            raise Exception(f'The "{name}" attribute is not registered with the {self.__class__.__name__} class')



    @classmethod
    def get_controller(cls, mock=False):
        this = cls()
        this.scene = MayaScene()
        this.build_directory = None
        #sig.build_directory_changed.connect(this.set_build_directory)
        return this



    '''def create_managers(self, asset_name, dirpath, prefab_key=None):
        self.blueprint_manager = BlueprintManager(asset_name=asset_name, dirpath=dirpath, prefab_key=prefab_key)
        self.scene.create_armature_manager()
        self.scene.create_rig_manager()



    def build_armature_from_latest_version(self):
        self.scene.build_armature_from_latest_version(self.blueprint_manager)'''



    '''def build_rig(self):
        self.scene.build_rig(self.blueprint_manager)
        self.state = RIG_STATE_TAG'''



    def create_m_plug(self, owner, key, **kwargs):
        return self.scene.create_m_plug(owner, key, **kwargs)



    def rename(self, node, name):
        """
        Renaming objects after creation is NOT a preferred workflow...
        It should only be used when pipe demands a specific name for a node
        """
        name = name.split(':')[-1]
        self.named_objects.pop(node.name, None)
        long_name = name
        if self.namespace:
            long_name = '%s:%s' % (self.namespace, name)

        if node.get_selection_string() == long_name:
            logging.getLogger('rig_build').warning('The node was already named: %s. skipping rename' % long_name)
            return name

        node.name = long_name

        if self.scene.objExists(long_name):
            raise Exception('A node with the name "%s" already exists.' % long_name)
        self.scene.rename( node.get_selection_string(), name )

        self.named_objects[long_name] = node

        # Rename plugs of object
        if hasattr(node, 'existing_plugs') and node.existing_plugs:
            for plug in node.existing_plugs.values():
                plug.update_name()

        return name



    '''
    @staticmethod
    def create_m_depend_node(**kwargs):
        if kwargs.get('parent', None) is not None:
            depend_node = om.MFnDependencyNode().create(
                kwargs['node_type'],
                kwargs['name'],
                kwargs['parent'] )
        else:
            depend_node = om.MFnDependencyNode().create(
                kwargs['node_type'],
                kwargs['name'] )
        return depend_node
    '''



    @staticmethod
    def compose_curve_construct_cvs(**kwargs):
        return curve_utils.compose_curve_construct_cvs(**kwargs)



    '''def create_nurbs_curve(self, **kwargs):
        self.scene.create_nurbs_curve(**kwargs)'''



    def set_plug_value(self, plug, value):
        self.scene.set_plug_value(plug.m_plug, value)



    def get_plug_value(self, plug, *args):
        return self.scene.get_plug_value(plug.m_plug, *args)



    @staticmethod
    def zero_joint_rotation(joint):
        node_utils.zero_joint_rotation(joint)



    def xform(self, item, **kwargs):
        return self.scene.xform( item, **kwargs )



    def create_standard_handle(self, owner, **kwargs):
        return handle_utils.create_standard_handle( owner, **kwargs )



    def create_guide_handle(self, owner, **kwargs):
        return handle_utils.create_guide_handle( owner, **kwargs )



    def remove_offset_from_snap(self, handle):
        return handle_utils.remove_offset_from_snap( self, handle )



    def assign_selected_vertices_to_handle(self, handle, mo=False):
        return handle_utils.assign_selected_vertices( self, handle, mo=mo )



    def snap_handle_to_vertices(self, handle, vertices, mo=False, differ_vec=None, scale=0):
        return handle_utils.assign_vertices( self, handle, vertices, mo=mo, differ_vec=differ_vec, scale=scale )



    def update_assign_vertices(self, handle):
        return handle_utils.update_assign_vertices( self, handle, )



    def create_object(self, object_type, *args, **kwargs):
        if object_type is None:
            raise Exception('Object type is None')

        elif isinstance(object_type, str):
            if object_type in obs.__dict__:
                object_type = obs.__dict__[object_type]
            else:
                raise Exception(f"Object type '{object_type}' not supported")
        elif not issubclass(object_type, obs.BaseObject):
            raise Exception(f'Object type is not a subclass of {obs.BaseObject}')
        this = object_type.create(*args, **kwargs)
        if this is None:
            raise Exception(f"The create function '{object_type.__name__}.create' returned None")
        self.register_item(this)
        return this



    @dec.flatten_args
    def create_matrix_point_constraint(self, *args, **kwargs):
        return self.create_object( obs.PointMatrixConstraint, *args, **kwargs )



    @dec.flatten_args
    def create_matrix_orient_constraint(self, *args, **kwargs):
        return self.create_object( obs.OrientMatrixConstraint, *args, **kwargs )



    @dec.flatten_args
    def create_matrix_parent_constraint(self, *args, **kwargs):
        return self.create_object( obs.ParentMatrixConstraint, *args, **kwargs )



    @dec.flatten_args
    def create_matrix_parent_blend_constraint(self, *args, **kwargs):
        return self.create_object( obs.ParentMatrixBlendConstraint, *args, **kwargs )



    @dec.flatten_args
    def create_handle_to_joint_constraint(self, *args, **kwargs):
        return self.create_object( obs.AddLocalsConstraint, *args, **kwargs )



    @dec.flatten_args
    def create_orient_constraint(self, *args, **kwargs):
        return self.create_object( obs.OrientConstraint, *args, **kwargs )



    @dec.flatten_args
    def create_parent_constraint(self, *args, **kwargs):
        return self.create_object( obs.ParentConstraint, *args, **kwargs )



    @dec.flatten_args
    def create_point_constraint(self, *args, **kwargs):
        return self.create_object( obs.PointConstraint, *args, **kwargs )



    @dec.flatten_args
    def create_scale_constraint(self, *args, **kwargs):
        return self.create_object( obs.ScaleConstraint, *args, **kwargs )



    @dec.flatten_args
    def create_aim_constraint(self, *args, **kwargs):
        return self.create_object( obs.AimConstraint, *args, **kwargs )



    @dec.flatten_args
    def create_pole_vector_constraint(self, *args, **kwargs):
        return self.create_object( obs.PoleVectorConstraint, *args, **kwargs )



    @dec.flatten_args
    def create_tangent_constraint(self, *args, **kwargs):
        return self.create_object( obs.TangentConstraint, *args, **kwargs )



    @dec.flatten_args
    def create_geometry_constraint(self, *args, **kwargs):
        return self.create_object( obs.GeometryConstraint, *args, **kwargs )



    def register_item(self, item):
        item.layer = self.current_layer



    def snap_handles_to_mesh_positions(self, rig):
        return handle_utils.snap_handles_to_mesh_positions(rig)



    @staticmethod
    def create_root(*args, **kwargs):
        return com.part_tools.create_root(*args, **kwargs)



    @staticmethod
    def create_rig_shaders(rig):
        rig_utils.create_rig_shaders(rig)



    def get_matrix(self, transform, world_space=True):
        if not isinstance(transform, Transform):
            raise TypeError('Invalid object type "%s"' % transform.__class__.__name__)
        matrix = self.scene.xform(
            transform.get_selection_string(),
            ws=world_space,
            m=True,
            q=True
        )
        if matrix:
            return Matrix(*matrix)

        return Matrix()



    def set_matrix(self, transform, matrix, world_space=True):
        if not isinstance(transform, Transform):
            raise TypeError('Invalid object type "%s"' % transform.__class__.__name__)
        self.scene.xform( transform.get_selection_string(), ws=world_space, m=list(matrix) )



    def assign_shading_group(self, shading_group, *nodes):
        for node in nodes:
            node.shader = shading_group
        self.scene.assign_shading_group(shading_group, *[x.name for x in nodes])



    def mirror_part(self, part):
        mirror_utils.mirror_part(part)



    def register_standard_parts(self):
        self.registered_parts['General'] = OrderedDict((
            ('Root', obs.RootGuide.__name__),
            ('Fk Chain', obs.FkChainGuide.__name__),
            #('Ik Chain', obs.IkChainGuide.__name__),
            ('Handle', obs.HandleGuide.__name__),
            #('Handle Part Array', obs.HandlePartArrayGuide.__name__),
            #('Transform', obs.TransformPartGuide.__name__),
            #('Joint', obs.JointPartGuide.__name__),
            ('Part Group', obs.PartGroupGuide.__name__),
            #('Follicle Handle', obs.FollicleHandleGuide.__name__),
            #('Layered Ribbon Spline Chain', obs.LayeredRibbonSplineChainGuide.__name__),
            #('Layered Ribbon Chain', obs.LayeredRibbonChainGuide.__name__),
            #('Simple Ribbon', obs.SimpleRibbonGuide.__name__),
            #('Surface Spline', obs.SurfaceSplineGuide.__name__),
            #('Double Surface Spline', obs.DoubleSurfaceSplineGuide.__name__),
            #('Rig Spline (Deformation)', obs.RigSplinePartGuide.__name__),
            #('Shard Handle', obs.ShardHandlePartGuide.__name__),
            #('Roll', obs.RollGuide.__name__),
            #('Shotception Part', obs.ShotceptionPartGuide.__name__),
            #('Shotception Part Array', obs.ShotceptionPartArrayGuide.__name__),
            #('Visualization Handle', obs.VisualizationHandleGuide.__name__),
            #('Variation Textures', obs.VariationPartGuide.__name__),
            #('Screen Handle(Obsolete)', obs.ScreenHandlePartGuide.__name__),
            #('Double Surface Spline Up Vectors (obsolete)', obs.DoubleSurfaceSplineUpvectorsGuide.__name__),
            #('Handle Array (obsolete)', obs.HandleArrayGuide.__name__),
        ))

        self.registered_parts['Biped'] = OrderedDict((
            #('Biped Arm Bendy', obs.BipedArmBendyGuide.__name__),
            #('Biped Arm Fk', obs.BipedArmFkGuide.__name__),
            #('Biped Arm', obs.BipedArmGuide.__name__),
            #('Biped Arm Ik', obs.BipedArmIkGuide.__name__),
            #('Biped Breath', obs.BipedBreathGuide.__name__),
            #('Biped Finger', obs.BipedFingerGuide.__name__),
            #('Biped Hand', obs.BipedHandGuide.__name__),
            #('Biped Leg Bendy', obs.BipedLegBendyGuide.__name__),
            #('Biped Leg Fk', obs.BipedLegFkGuide.__name__),
            #('Biped Leg', obs.BipedLegGuide.__name__),
            #('Biped Leg Ik', obs.BipedLegIkGuide.__name__),
            ('Biped Neck Fk', obs.BipedNeckFkGuide.__name__),
            ('Biped Neck Ik', obs.BipedNeckIkGuide.__name__),
            ('Biped Neck Fk Spline', obs.BipedNeckFkSplineGuide.__name__),
            ('Biped Neck', obs.BipedNeckGuide.__name__),
            ('Biped Spine Ik', obs.BipedSpineIkGuide.__name__),
            ('Biped Spine Fk', obs.BipedSpineFkGuide.__name__),
            ('Biped Spine Ik/FK', obs.BipedSpineIkFkGuide.__name__),
            ('Biped Spine', obs.BipedSpineGuide.__name__),
            #('Biped Reverse Spine Fk', obs.BipedSpineReverseFkGuide.__name__),
            ('Biped Reverse Spine Ik', obs.BipedSpineReverseIkGuide.__name__),
            ('Biped Reverse Spine Ik/Fk', obs.BipedSpineReverseIkFkGuide.__name__),
            ('Biped Reverse Spine', obs.BipedReverseSpineGuide.__name__),
        ))

        self.registered_parts['Quadruped'] = OrderedDict((
            #('Quadruped Neck', obs.QuadrupedNeckGuide.__name__),
            #('Quadruped Neck Fk', obs.QuadrupedNeckFkGuide.__name__),
            #('Quadruped Neck Ik', obs.QuadrupedNeckIkGuide.__name__),
            #('Quadruped Neck Fk Spline', obs.QuadrupedNeckFkSplineGuide.__name__),
            #('Quadruped Spine Fk', obs.QuadrupedSpineFkGuide.__name__),
            #('Quadruped Spine', obs.QuadrupedSpineGuide.__name__),
            #('Quadruped Spine Ik', obs.QuadrupedSpineIkGuide.__name__),
            #('Quadruped Back Leg Ik', obs.QuadrupedBackLegIkGuide.__name__),
            #('Quadruped Back Leg Fk', obs.QuadrupedBackLegFkGuide.__name__),
            #('Quadruped Back Leg', obs.QuadrupedBackLegGuide.__name__),
            #('Quadruped Back Leg Array', obs.QuadrupedBackLegArrayGuide.__name__),
            #('Quadruped Bendy Back Leg', obs.QuadrupedBendyBackLegGuide.__name__),
            #('Quadruped Foot', obs.QuadrupedFootGuide.__name__),
            #('Quadruped Toe', obs.QuadrupedToeGuide.__name__),
        ))

        self.registered_parts['FacePanel'] = OrderedDict((
            #('Blink Slider', obs.BlinkSliderGuide.__name__),
            #('Brow Slider', obs.BrowSliderGuide.__name__),
            #('Brow Waggle Slider', obs.BrowWaggleSliderGuide.__name__),
            #('Cheek Slider', obs.CheekSliderGuide.__name__),
            #('Double Slider', obs.DoubleSliderGuide.__name__),
            #('Custom Slider', obs.CustomSliderGuide.__name__),
            #('Eye Slider', obs.EyeSliderGuide.__name__),
            #('Eye Lid Slider', obs.EyeLidSliderGuide.__name__),
            #('Face Panel', obs.FacePanelGuide.__name__),
            #('Mouth Slider', obs.MouthSliderGuide.__name__),
            #('Nose Slider', obs.NoseSliderGuide.__name__),
            #('Teeth Slider', obs.TeethSliderGuide.__name__),
            #('Tongue Slider', obs.TongueSliderGuide.__name__),
            #('Vertical Slider', obs.VerticalSliderGuide.__name__),
            #('Open Eye Regions Slider', obs.OpenEyeRegionsSliderGuide.__name__),
        ))

        self.registered_parts['Face'] = OrderedDict((
            #('Projection Eye Array', obs.ProjectionEyeArrayGuide.__name__),
            #('Projection Eye', obs.ProjectionEyeGuide.__name__),
            #('Eye Lash', obs.EyeLashPartGuide.__name__),
            #('Eyebrow', obs.EyebrowPartGuide.__name__),
            #('Face', obs.FaceGuide.__name__),
            #('Jaw', obs.JawGuide.__name__),
            #('Eye', obs.EyeGuide.__name__),
            #('Split Brow', obs.SplitBrowGuide.__name__),
            #('Eye Array (obsolete)', obs.EyeArrayGuide.__name__),
            #('Face Handle Array (obsolete)', obs.FaceHandleArrayGuide.__name__),
        ))

        self.registered_parts['Deformers'] = OrderedDict((
            #('New Lattice Squish', obs.NewLatticeSquishGuide.__name__),
            #('Lattice Squish', obs.LatticeSquishGuide.__name__),
            #('Lattice', obs.LatticePartGuide.__name__),
            #('Bend', obs.BendPartGuide.__name__),
            #('Flare', obs.FlarePartGuide.__name__),
            #('Sine', obs.SinePartGuide.__name__),
            #('Squash', obs.SquashPartGuide.__name__),
            #('Twist', obs.TwistPartGuide.__name__),
            #('Wave', obs.WavePartGuide.__name__),
            #('Squish (obsolete)', obs.SquishPartGuide.__name__),
        ))

        self.registered_parts['Dynamic'] = OrderedDict((
            #('Dynamics', obs.DynamicsGuide.__name__),
            #('Dynamic Fk Chain', obs.DynamicFkChainGuide.__name__),
            #('Dynamic Layered Ribbon Chain', obs.DynamicLayeredRibbonChainGuide.__name__),
            #('Cloth', obs.ClothGuide.__name__),
        ))

        self.registered_parts['Creature'] = OrderedDict((
            #('Tentacle', obs.TentacleGuide.__name__),
            #('Tail', obs.TailGuide.__name__),
            #('Bat Wing', obs.BatWingGuide.__name__),
            #('Bird Wing', obs.BirdWingGuide.__name__),
            #('Feather Simple', obs.FeatherSimplePartGuide.__name__),
            #('Feather Ribbon (obsolete)', obs.FeatherRibbonPartGuide.__name__)
        ))

        self.registered_parts['Vehicle'] = OrderedDict((
            #('Auto Wheel', obs.AutowheelGuide.__name__),
            #('Suspension Bank', obs.SuspensionBankGuide.__name__),
            #('Piston', obs.PistonGuide.__name__),
            #('Drive Path', obs.DrivePathGuide.__name__),
            #('Wheel', obs.WheelGuide.__name__),
        ))

        self.registered_parts['Misc'] = OrderedDict((
            #('Corrective', obs.CorrectiveJointGuide.__name__),
            #('Push', obs.PushJointGuide.__name__),
            #('Push Plus', obs.PushPlusGuide.__name__),
        ))

        for category in self.registered_parts:
            for part_class in self.registered_parts[category].values():
                if not issubclass(obs.__dict__[part_class], (obs.PartGuide, obs.ContainerGuide, obs.PartGroupGuide)):
                    raise Exception('Unable to register the part "%s" as it was not a Guide State part' % part_class)



    def register_standard_containers(self):
        self.registered_containers = [
            #obs.CharacterGuide.__name__,
            #obs.EnvironmentGuide.__name__,
            #obs.PropGuide.__name__,
            obs.BipedGuide.__name__,
            #obs.QuadrupedGuide.__name__,
            #obs.VehicleGuide.__name__
        ]


'''
import os
import gc
import copy
import uuid
import types
import inspect
import logging
import weakref
import traceback
import rig_factory.objects as obs
from rig_math.vector import Vector
from collections import OrderedDict
import rig_factory.common_modules as com
import rig_factory.system_signals as sig
import iRig.utilities.PySignal as PySignal
import rig_factory.utilities.decorators as dec
import rig_factory.utilities.rig_utilities as rtl
import rig_factory.utilities.shard_utilities as sht
import rig_factory.utilities.handle_utilities as htl
from rig_factory.objects.node_objects.mesh import Mesh
import rig_factory.utilities.deformer_utilities as dtl
from rig_factory.objects.sdk_objects.sdk_group import SDKGroup
import rig_factory.utilities.geometry_normals_utilities as gnu
from rig_factory.objects.base_objects.weak_list import WeakList
import rig_factory.utilities.node_utilities.node_utilities as ntl
from rig_factory.objects.sdk_objects.sdk_network import SDKNetwork
from rig_factory.objects.node_objects.depend_node import DependNode
from rig_factory.objects.sdk_objects.keyframe_group import KeyframeGroup
from rig_factory.objects.node_objects.animation_curve import AnimationCurve, KeyFrame


class RigController(object):

   # Signals on the controller are all being phased out and moved to system_signals.py
   sdk_network_changed_signal = PySignal.ClassSignal()
   start_sdk_ownership_signal = PySignal.ClassSignal()
   end_sdk_ownership_signal = PySignal.ClassSignal()
   start_sdk_disown_signal = PySignal.ClassSignal()
   end_sdk_disown_signal = PySignal.ClassSignal()
   progress_signal = PySignal.ClassSignal()
   failed_signal = PySignal.ClassSignal()
   deleted_signal = PySignal.ClassSignal()
   raise_warning_signal = PySignal.ClassSignal()  # Get rid of this and refactor
   raise_error_signal = PySignal.ClassSignal()
   item_changed_signal = PySignal.ClassSignal()  # This is not efficient, it should be split by types
   use_module_versions = not (os.environ.get('PIPE_DEV_MODE') == 'TRUE')  # only use module versions on production
   active_controllers = []
   ordered_vertex_selection_enabled = False
   ordered_vertex_selection = []
   registered_parts = OrderedDict()
   registered_containers = []
   build_warnings = []
   currently_saving = False
   build_directory = None
   log_path = None
   failed_state = False
   face_network = None
   locked_face_drivers = False
   disable_warnings = False
   debug_garbage_collection = True  # Display referents for objects that fail to garbage collect
   root = None
   deleted_object_names = []
   # self.get_class_function = None
   DEBUG = os.getenv('PIPE_DEV_MODE') == 'TRUE'
   objects_scheduled_for_deletion = WeakList()
   current_layer = None
   namespace = None
   object_layers = dict()
   named_objects = None
   nodes_scheduled_for_deletion = []
   uuid = None
   scene = None

   def __init__(self):
       super().__init__()
       self.uuid = str(uuid.uuid4())
       self.named_objects = weakref.WeakValueDictionary()

   def __setattr__(self, name, value):
       if hasattr(self, name):
           try:
               super().__setattr__(name, value)
           except Exception:
               raise Exception(
                   'The property "%s" on the %s named "%s" could not be set to: type<%s> %s.' % (
                       name,
                       type(self),
                       self,
                       type(value),
                       value
                   )
               )

       else:
           raise Exception('The "%s" attribute is not registered with the %s class' % (
               name,
               self.__class__.__name__
           ))

   @classmethod
   def get_controller(cls, mock=False):
       this = cls()
       if mock:
           from rig_factory.scene.mock_scene import MockScene
           this.scene = MockScene()
       else:
           from rig_factory.scene.maya_scene import MayaScene
           this.scene = MayaScene()
       this.build_directory = None
       sig.build_directory_changed.connect(this.set_build_directory)
       return this

   def set_build_directory(self, build_directory):
       if not os.path.exists(build_directory):
           logging.getLogger('rig_build').warning('Build directory does not exist: %s' % build_directory)
       self.build_directory = build_directory

   def reset(self, *args):
       self.object_layers = dict()
       self.set_root(None)
       gc.collect()
       self.named_objects = weakref.WeakValueDictionary()
       self.objects_scheduled_for_deletion = WeakList()
       self.deleted_object_names = []
       if self.named_objects:
           raise Exception('named_objects is not empty')

       self.scene.remove_namespaces()
       self.current_layer = None
       self.namespace = None
       self.ordered_vertex_selection = []
       self.build_warnings = []
       self.failed_state = False
       self.set_face_network(None)

   @dec.flatten_args
   def select(self, *items, **kwargs):
       remaining_items = []
       for item in items:
           if isinstance(item, obs.KeyframeGroup):
               self.scene.update_keyframe_selection(
                   [x.animation_curve.get_selection_string() for x in item.keyframes],
                   in_value=item.in_value
               )
           elif isinstance(item, obs.FaceTarget):
               if item.keyframe_group:
                   self.select(
                       item.keyframe_group,
                       add=True
                   )
           elif isinstance(item, obs.FaceGroup):
               if item.sdk_group:
                   self.select(
                       item.sdk_group.animation_curves,
                       add=True
                   )
           else:
               remaining_items.append(item)
       self.scene.select(*[x.get_selection_string() for x in items if isinstance(x, DependNode)], **kwargs)


   def initialize_node(self, node_name, **kwargs):
       return ntl.initialize_node(self, node_name, **kwargs)


   def freeze_module_versions(self):
       if self.root:
           module_versions = dict()
           parts = self.root.get_parts(include_self=True)
           module_names = list(set([x.__class__.__module__ for x in parts]))
           for module_name in module_names:
               module = sys.modules[module_name]
               module_version = module.__dict__.get('__version__', None)
               if module_version:
                   self.root.module_versions[module.__name__.split('.')[-1]] = module_version
           self.root.module_versions = module_versions

   def get_deformer_weights(self, deformer, precision=None, skip_if_default_weights=False):
       return self.scene.get_deformer_weights(
           deformer.m_object, precision=precision, skip_if_default_weights=skip_if_default_weights)

   def set_deformer_weights(self, deformer, weights):
       self.scene.set_deformer_weights(
           deformer.m_object,
           weights
       )

   ## Commented out as assumed Obsolete - but could be used externally somewhere?
   # def get_deformer_data(self, rig, precision=None):  ## Obsolete?
   #     return dtl.get_deformer_data(rig, precision=precision)


   def expand_handle_shapes(self, rig):
       return htl.expand_handle_shapes(
           self,
           rig
       )

   def collapse_handle_shapes(self, rig):
       return htl.collapse_handle_shapes(
           self,
           rig
       )

   def get_handle_shapes(self, rig, local):
       return htl.get_handle_shapes(rig, local)

   def get_handle_colors(self, rig):
       return htl.get_handle_colors(rig)

   def get_handle_default_colors(self, rig):
       return htl.get_handle_default_colors(rig)

   def set_handle_color(self, handle, color, hover):
       return htl.set_handle_color(
           handle,
           color,
           hover
       )

   def set_gimbal_handle_color(self, handle, color, hover):
       return htl.set_gimbal_handle_color(
           handle,
           color,
           hover
       )



   def set_default_color(self, handle, gimb, main):
       return htl.set_default_color(
           handle,
           gimb,
           main
       )

   def get_input_transforms(self,rig):
       return htl.get_input_transforms(rig)

   def set_handle_shapes(self, rig, shapes):
       htl.set_handle_shapes(
           rig,
           shapes,
           namespace=self.namespace
       )

   def set_input_transforms(self, rig, input_transforms):
       htl.set_input_transforms(
           rig,
           input_transforms
       )

   def snap_handle_to_mesh_positions(self, handle):
       return htl.snap_handle_to_mesh_positions(
           self,
           handle
       )

   def assign_closest_vertices(self, part, mesh_name):
       htl.assign_closest_vertices(
           part,
           str(mesh_name)
       )

   def snap_part_to_mesh(self, part, mesh):
       return htl.snap_part_to_mesh(
           part,
           mesh
       )

   def set_handle_mesh_positions(self, rig, positions):
       return htl.set_handle_mesh_positions(
           self,
           rig,
           positions
       )

   def get_handle_mesh_positions(self, rig):
       return htl.get_handle_mesh_positions(
           self,
           rig
       )

   def get_handle_data(self, rig):
       return htl.get_handle_data(rig)

   def create_parent_capsule(self, part, parent_joint):
       return rtl.create_parent_capsule(
           self,
           part,
           parent_joint
       )

   def create_skin_cluster(self, geometry, influences, **kwargs):
       return dtl.create_skin_cluster(
           self,
           geometry,
           influences,
           **kwargs
       )

   def get_delta_mush_data(self, rig, precision=None):
       data = []
       delta_mush_nodes = self.scene.get_delta_mush_nodes(
           *[x.name for x in rig.geometry.values() if x.layer == rig.controller.current_layer]
       )
       if delta_mush_nodes:
           for delta_mush in delta_mush_nodes:
               delta_mush_data = self.scene.get_delta_mush_data(delta_mush, precision=precision)
               if delta_mush_data:
                   data.append(delta_mush_data)
       return data

   def set_delta_mush_data(self, rig, data):
       logger = logging.getLogger('rig_build')

       if not isinstance(data, list):
           self.raise_warning('Legacy DeltaMush data found. Please recreate yur delta mush deformers')
           return
       failed_nodes = []
       for delta_mush_data in data:
           try:
               self.scene.create_delta_mush(delta_mush_data, namespace=self.namespace)
           except Exception as e:
               failed_nodes.append(delta_mush_data['name'])
               logger.error(traceback.format_exc())

       if failed_nodes:
           g = [failed_nodes[x] for x in range(len(failed_nodes)) if x < 10]
           self.raise_warning(
               'Unable to create delta mush :\n%s\n\nCheck the script editor for details..' % '\n'.join(g)
           )

   def get_skin_cluster_data(self, rig, precision=4):
       return dtl.get_skin_cluster_data(
           self,
           rig,
           precision
       )

   def get_deformer_stack_data(self, rig):
       return dtl.get_deformer_stack_data(
           self,
           rig
       )

   def set_skin_cluster_data(self, rig, data):
       return dtl.set_skin_cluster_data(
           self,
           rig,
           data
       )

   def set_deformer_stack_data(self, rig, data):
       return dtl.set_deformer_stack_data(
           self,
           rig,
           data
       )

   def find_skin_cluster(self, node):
       return self.scene.find_skin_cluster(node.m_object)

   def find_skin_clusters(self, node):
       return self.scene.find_skin_clusters(node.m_object)

   def get_shard_skin_cluster_data(self, *args):
       return sht.get_shard_skin_cluster_data(*args)

   def set_shard_skin_cluster_data(self, data):
       failed_skin_clusters = []
       for skin_data in data:
           try:
               self.scene.create_from_skin_data(
                   skin_data,
                   namespace=self.namespace
               )
           except Exception as e:
               failed_skin_clusters.append(skin_data['geometry'])
               logging.getLogger('rig_build').error(traceback.format_exc())
       if failed_skin_clusters:
           self.raise_warning_signal.emit(
               'Failed to create shard skins. See script editor for details: \n\n%s' % '\n'.join(
                   failed_skin_clusters[:10]
               )
           )

   def get_shards(self):
       return [h.shard for h in self.root.get_handles() if isinstance(h, obs.FaceHandle)]

   def smooth_normals(self, *args, **kwargs):
       return gnu.smooth_normals(*args, **kwargs)

   def create_lattice(self, *geometry, **kwargs):
       return dtl.create_lattice(
           self,
           *geometry,
           **kwargs
       )

   def create_softMod(self, *geometry, **kwargs):
       return dtl.create_softMod(self, *geometry, **kwargs)

   def create_wire_deformer(self, curve, *geometry, **kwargs):

       return dtl.create_wire_deformer(
           self,
           curve,
           *geometry,
           **kwargs
       )

   def add_deformer_geometry(self, deformer, geometry):
       self.scene.add_deformer_geometry(
           deformer,
           geometry
       )

   def remove_deformer_geometry(self, deformer, geometry):
       self.scene.remove_deformer_geometry(
           deformer,
           geometry
       )

   def bind_rig_geometry(self, rig, geometry):
       return rtl.bind_rig_geometry(
           self,
           rig,
           geometry
       )

   def get_handles(self, part):
       return htl.get_handles(part)

   def get_joints(self, part):
       return htl.get_joints(part)

   def get_deform_joints(self, part):
       return htl.get_deform_joints(part)

   def get_base_joints(self, part):
       return htl.get_base_joints(part)

   @staticmethod
   def create_rig_groups(rig):
       rtl.create_rig_groups(rig)

   def delete_keyframe(self, keyframe):
       self.scene.delete_keyframe(
           keyframe.animation_curve.m_object,
           keyframe.in_value
       )
       keyframe.unparent()

   def find_similar_geometry(self, *geometry):
       similar_geometry = []
       for x in geometry:
           similar_mesh = self.find_similar_mesh(x)
           if similar_mesh:
               similar_geometry.append(similar_mesh)
       return similar_geometry

   def find_similar_mesh(self, mesh_name, geometry=None):
       """
       Move this to a utility file!
       """

       vertex_count = self.scene.get_vertex_count(mesh_name)
       matching_meshs = []
       # if not geometry:
       #     geometry = mtl.gather_mesh_children(self.root.root_geometry_group)
       for mesh in geometry:
           list_meshs = self.scene.ls(mesh.name)
           if list_meshs and len(list_meshs) > 1:
               self.raise_warning('Duplicate meshs detected: %s' % mesh.name)
           if self.scene.get_vertex_count(mesh.get_selection_string()) == vertex_count:
               matching_meshs.append(mesh)
       if len(matching_meshs) == 0:
           return None
       if len(matching_meshs) == 1:
           return matching_meshs[0]
       bounding_box_center = Vector(self.scene.get_bounding_box_center(mesh_name))
       transform = self.scene.listRelatives(mesh_name, p=True)[0]
       transform_position = Vector(self.scene.xform(
           transform,
           q=True,
           ws=True,
           t=True
       ))
       local_position = bounding_box_center - transform_position

       closest_mesh = None
       closest_distance = float('inf')
       for matching_mesh in matching_meshs:
           matching_bounding_box_center = Vector(self.scene.get_bounding_box_center(matching_mesh))
           matching_transform = self.scene.listRelatives(matching_mesh, p=True)[0]
           matching_transform_position = Vector(self.scene.xform(
               matching_transform,
               q=True,
               ws=True,
               t=True
           ))
           matching_local_position = matching_bounding_box_center - matching_transform_position

           if not matching_local_position[0] * local_position[0] < 0.0:
               distance_vector = Vector(matching_local_position) - local_position
               if distance_vector.magnitude() == 0:
                   return matching_mesh
               x_distance = abs(distance_vector.data[0])
               if x_distance < closest_distance:
                   closest_distance = x_distance
                   closest_mesh = matching_mesh
       return closest_mesh

   def copy_mesh_in_place(self, mesh_1, mesh_2):
       self.scene.copy_mesh_in_place(
           mesh_1.m_object,
           mesh_2.m_object
       )

   def get_closest_vertex_index(self, mesh, position):
       return self.scene.get_closest_vertex_index(
           mesh.m_object,
           position
       )

   def mirror_all(self, rigs, **kwargs):
       htl.mirror_all(rigs, **kwargs)

   def mirror_handle_positions(self, rigs, **kwargs):
       htl.mirror_handle_positions(rigs, **kwargs)

   def mirror_handle_vertices(self, rigs, **kwargs):
       htl.mirror_handle_vertices(rigs, **kwargs)

   def mirror_handle_attributes(self, rigs, **kwargs):
       htl.mirror_handle_attributes(rigs, **kwargs)

   def transfer_handle_vertices(self, rig, mesh, side='left'):
       htl.transfer_handle_vertices(rig, mesh, side=side)

   def transfer_handle_vertices_to_selected_mesh(self, rig, side='left'):
       mesh_names = self.get_selected_mesh_names()
       if mesh_names:
           mesh_name = mesh_names[0]
           rig_root = rig.get_root()
           if mesh_name in rig_root.geometry:
               htl.transfer_handle_vertices(
                   rig,
                   rig_root.geometry[mesh_name],
                   side=side
               )
           else:
               raise Exception('Mesh is not part of rig')
       else:
           raise Exception('Select a mesh')

   @dec.flatten_args
   def create_matrix_point_constraint(self, *args, **kwargs):
       return self.create_object(
           obs.PointMatrixConstraint,
           *args,
           **kwargs
       )

   @dec.flatten_args
   def create_matrix_orient_constraint(self, *args, **kwargs):
       return self.create_object(
           obs.OrientMatrixConstraint,
           *args,
           **kwargs
       )

   @dec.flatten_args
   def create_matrix_parent_constraint(self, *args, **kwargs):
       return self.create_object(
           obs.ParentMatrixConstraint,
           *args,
           **kwargs
       )

   @dec.flatten_args
   def create_matrix_parent_blend_constraint(self, *args, **kwargs):
       return self.create_object(
           obs.ParentMatrixBlendConstraint,
           *args,
           **kwargs
       )

   @dec.flatten_args
   def create_orient_constraint(self, *args, **kwargs):
       return self.create_object(
           obs.OrientConstraint,
           *args,
           **kwargs
       )

   @dec.flatten_args
   def create_parent_constraint(self, *args, **kwargs):
       return self.create_object(
           obs.ParentConstraint,
           *args,
           **kwargs
       )

   @dec.flatten_args
   def create_point_constraint(self, *args, **kwargs):
       return self.create_object(
           obs.PointConstraint,
           *args,
           **kwargs
       )

   @dec.flatten_args
   def create_scale_constraint(self, *args, **kwargs):
       return self.create_object(
           obs.ScaleConstraint,
           *args,
           **kwargs
       )

   @dec.flatten_args
   def create_aim_constraint(self, *args, **kwargs):
       return self.create_object(
           obs.AimConstraint,
           *args,
           **kwargs
       )

   @dec.flatten_args
   def create_pole_vector_constraint(self, *args, **kwargs):
       return self.create_object(
           obs.PoleVectorConstraint,
           *args,
           **kwargs
       )

   @dec.flatten_args
   def create_tangent_constraint(self, *args, **kwargs):
       return self.create_object(
           obs.TangentConstraint,
           *args,
           **kwargs
       )

   @dec.flatten_args
   def create_geometry_constraint(self, *args, **kwargs):
       return self.create_object(
           obs.GeometryConstraint,
           *args,
           **kwargs
       )

   def create_ik_handle(self, start_joint, end_joint, **kwargs):
       return self.create_object(
           obs.IkHandle,
           start_joint,
           end_joint,
           **kwargs
       )

   def enable_ordered_vertex_selection(self):
       if not self.ordered_vertex_selection_enabled:
           self.ordered_vertex_selection_enabled = True
           sig.maya_callback_signals['selection_changed'].connect(self.update_ordered_vertex_selection)

   def disable_ordered_vertex_selection(self):
       if self.ordered_vertex_selection_enabled:
           self.ordered_vertex_selection_enabled = False
           sig.maya_callback_signals['selection_changed'].disconnect(self.update_ordered_vertex_selection)

   def update_ordered_vertex_selection(self, *args):
       current_selection = self.list_selected_vertices()
       if current_selection:
           for vertex in copy.copy(self.ordered_vertex_selection):
               if vertex not in current_selection:
                   self.ordered_vertex_selection.remove(vertex)
           for selected_vertex in current_selection:
               if selected_vertex not in self.ordered_vertex_selection:
                   self.ordered_vertex_selection.append(selected_vertex)
       else:
           self.ordered_vertex_selection = []

   def export_alembic(self, path, *roots):
       self.scene.export_alembic(
           path,
           *roots
       )



   def get_wrap_data(self, container):
       logger = logging.getLogger('rig_build')
       data = []
       wraps = []
       for geometry in container.geometry:
           if container.geometry[geometry].layer == self.current_layer:
               wrap = self.scene.find_deformer_node(geometry, 'wrap')  # None or first wrap only
               if wrap:
                   wraps.append(wrap)
       for wrap in wraps:
           try:
               data.append(self.scene.get_wrap_data(wrap))
           except Exception as e:
               logger.error(traceback.format_exc())
               self.raise_warning('Unable to get_wrap_data for %s.\nSee log for details.' % wrap)
       return data

   def set_wrap_data(self, container, data):
       logger = logging.getLogger('rig_build')
       failed_wraps = []

       wrap_data = []  # cleanup duplicate wrap nodes coming from blueprint
       for wrap in data:
           if wrap not in wrap_data:
               wrap_data.append(wrap)

       for x in wrap_data:
           try:
               # wrap = self.scene.find_deformer_node(geometry, 'wrap')
               self.scene.create_wrap(x, namespace=self.namespace)
           except Exception as e:
               logger.error(traceback.format_exc())
               failed_wraps.append(x['target_geometry'])
       if failed_wraps:
           self.raise_warning(
               'Failed to create wraps on:\n%s' % '\n'.join(failed_wraps)
           )

   def get_cvwrap_data(self, container):
       logger = logging.getLogger('rig_build')
       data = []
       cvwraps = []
       for geometry in container.geometry:
           if container.geometry[geometry].layer == self.current_layer:
               cvwrap = self.scene.find_deformer_node(geometry, 'cvWrap')  # None or first wrap only
               if cvwrap:
                   cvwraps.append(cvwrap)
       for cvwrap in cvwraps:
           try:
               data.append(self.scene.get_cvwrap_data(cvwrap))
           except Exception as e:
               logger.error(traceback.format_exc())
               self.raise_warning('Unable to get_cvwrap_data for %s.\nSee log for details.' % cvwrap)
       return data

   def set_cvwrap_data(self, container, data):
       logger = logging.getLogger('rig_build')
       failed_cvwraps = []

       cvwraps_data = []  # cleanup duplicate wrap nodes coming from blueprint
       for cvwrap in data:
           if cvwrap not in cvwraps_data:
               cvwraps_data.append(cvwrap)

       for x in cvwraps_data:
           try:
               # wrap = self.scene.find_deformer_node(geometry, 'wrap')
               self.scene.create_cvwrap(x, namespace=self.namespace)
           except Exception as e:
               logger.error(traceback.format_exc())
               failed_cvwraps.append(x['target_geometry'])
       if failed_cvwraps:
           self.raise_warning(
               'Failed to create cvWraps on:\n%s' % '\n'.join(failed_cvwraps)
           )

   def create_weight_constraint(self, *args, **kwargs):
       return self.scene.create_weight_constraint(*args, **kwargs)

   def set_face_network(self, face_network):
       if not isinstance(face_network, obs.FaceNetwork) and face_network is not None:
           raise Exception('Invalid type "%s"' % type(face_network))
       sig.face_network_signals['network_about_to_change'].emit()
       self.face_network = face_network
       sig.face_network_signals['network_finished_change'].emit(face_network)

   def copy_mesh(self, mesh_name, parent_transform, name=None):

       if not isinstance(mesh_name, str):
           raise TypeError('"%s" was not string' % mesh_name)
       if not isinstance(parent_transform, Transform):
           raise TypeError('"%s" was not mesh' % parent_transform)

       if name is None:
           name = '%sShape' % Mesh.get_predicted_name(
               root_name=parent_transform.root_name,
               segment_name=parent_transform.segment_name,
               side=parent_transform.side,
               suffix=Mesh.suffix
           )

       return parent_transform.create_child(
           Mesh,
           root_name=parent_transform.root_name,
           segment_name=parent_transform.segment_name,
           side=parent_transform.side,
           parent=parent_transform,
           name=name,
           m_object=self.scene.copy_mesh(
               self.scene.get_m_object(mesh_name),
               parent_transform.m_object
           )
       )

   def copy_mesh_shape(self, target_mesh, base_mesh):
       self.scene.copy_mesh_shape(
           self.scene.get_m_object(target_mesh),
           base_mesh.m_object
       )

   def change_keyframe(self, item, **kwargs):
       if isinstance(item, KeyFrame):
           if 'in_value' in kwargs:
               item.in_value = kwargs['in_value']
           self.scene.change_keyframe(
               item.animation_curve.m_object,
               item.in_value,
               **kwargs
           )
           for key in kwargs:
               setattr(item, key, kwargs[key])

       elif isinstance(item, KeyframeGroup):
           for keyframe in item.keyframes:
               self.change_keyframe(
                   keyframe,
                   **kwargs
               )
       else:
           raise Exception('Unsupported type "%s"' % type(item))


   def create_sdk_network(self, **kwargs):
       this = self.create_object(
           SDKNetwork,
           **kwargs
       )
       return this


   def get_skin_weights(self, node, precision=4):
       return self.scene.get_skin_weights(node, precision)

   def get_skin_blend_weights(self, node):
       return self.scene.get_skin_blend_weights(node)

   def get_skin_influences(self, node):
       return self.scene.get_skin_influences(node)

   def set_skin_weights(self, node, weights):
       self.scene.set_skin_weights(node, weights)

   def set_skin_blend_weights(self, node, weights):
       self.scene.set_skin_blend_weights(node, weights)

   def skin_as(self, skin_cluster, mesh):
       return self.scene.skin_as(skin_cluster, mesh)

   def get_curve_data(self, nurbs_curve):
       return self.scene.get_curve_data(nurbs_curve.m_object)

   def get_surface_data(self, nurbs_surface):
       return self.scene.get_surface_data(nurbs_surface.m_object)


   def connect_plug(self, plug_1, plug_2):
       return plug_1.connect_to(plug_2)

   def unparent(self, child):
       if child.parent:
           child.parent.children.remove(child)
           child.parent = None

   def set_parent(self, child, parent, relative=False):
       if not isinstance(parent, obs.BaseNode):
           raise Exception('Cannot parent to type "%s"' % type(parent))
       if child.parent == parent:
           raise Exception('%s is already parented to %s' % (child, child.parent))
       if child.parent:
           self.unparent(child)
       child.parent = parent
       parent.children.append(child)

       self.scene.parent(child, parent, relative=relative)

   def set_name(self, item, name):
       if '.' in name or ' ' in name or '|' in name:
           raise Exception('Invalid name characters "%s"' % name)
       self.named_objects.pop(item.name, None)
       self.named_objects[name] = item
       item.name = name
       self.item_changed_signal.emit(item)
       self.scene.rename(item, name)

   def plug_exists(self, node, plug_name):
       return self.scene.objExists('{0}.{1}'.format(node, plug_name))

   def delete_plug(self, plug):
       return self.scene.plug_exists(plug)

   def lock_plugs(self, *nodes):
       self.scene.lock_plugs(*nodes)

   def set_plug_locked(self, plug, value):
       self.scene.set_plug_locked(plug, value)

   def get_plug_locked(self, plug):
       return self.scene.get_plug_locked(plug)

   def set_plug_hidden(self, plug, value):
       self.scene.set_plug_hidden(plug, value)

   def get_plug_hidden(self, plug):
       return self.scene.get_plug_hidden(plug)

   def raise_warning(self, message):
       if not self.disable_warnings:
           self.raise_warning_signal.emit(message)

   def raise_error(self, message):
       self.raise_error_signal.emit(message)

   def list_selected_vertices(self):
       return self.scene.list_selected_vertices()

   def list_selected_edges(self, *args, **kwargs):
       return self.scene.polyListComponentConversion(*args, **kwargs)

   def get_selected_nodes(self):
       return [self.initialize_node(x) for x in self.scene.get_selected_nodes()]

   def get_selected_mesh_names(self):
       return self.scene.get_selected_mesh_names()

   def get_selected_mesh_objects(self):
       return self.scene.get_selected_mesh_objects()

   def get_selected_transform_names(self):
       return self.scene.get_selected_transform_names()

   def get_selected_transforms(self):
       return self.scene.get_selected_transforms()

   def get_selected_plugs(self):
       plugs = []
       for node in self.get_selected_nodes():
           for attr in self.scene.get_selected_attribute_names():
               plugs.append(node.plugs[attr])
       return plugs

   def get_selected_plug_strings(self):
       plugs_strings = []
       for node in self.scene.get_selected_node_names():
           for attr in self.scene.get_selected_attribute_names():
               plugs_strings.append('%s.%s' % (node, attr))
       return plugs_strings

   def get_selected_user_plug_strings(self):
       """
       :return: selected user defined plugs (node.attribute)
       """
       selected_user_plugs = []
       for node in self.scene.get_selected_node_names():
           all_user_plugs = self.scene.get_user_plugs(node)
           user_plugs = [x for x in all_user_plugs
                         if x in self.get_selected_plug_strings()]
           selected_user_plugs.extend(user_plugs)
       return selected_user_plugs

   def isolate(self, *objects):
       self.scene.isolate(*[x.get_selection_string() for x in objects])

   def deisolate(self, *objects):
       self.scene.deisolate(*[x.get_selection_string() for x in objects])

   def get_bounding_box_center(self, *nodes):
       return self.scene.get_bounding_box_center(*nodes)

   def get_bounding_box_scale(self, *nodes):
       return self.scene.get_bounding_box_scale(*nodes)

   def get_bounding_box(self, *nodes):
       return self.scene.get_bounding_box(*nodes)

   def hide(self, *objects):
       self.scene.hide(*objects)

   def showHidden(self, *objects):
       self.scene.showHidden(*objects)

   def listRelatives(self, *args, **kwargs):
       return self.scene.listRelatives(*args, **kwargs)

   def getAttr(self, *args, **kwargs):
       return self.scene.getAttr(*args, **kwargs)

   def setAttr(self, *args, **kwargs):
       return self.scene.setAttr(*args, **kwargs)

   def objExists(self, *args, **kwargs):
       return self.scene.objExists(*args, **kwargs)

   def delete_connection(self, connection):
       self.scene.delete_connection(connection)

   def get_file_info(self):
       return self.scene.get_file_info()

   def update_file_info(self, **kwargs):
       self.scene.update_file_info(**kwargs)

   def file(self, *args, **kwargs):
       self.scene.file(*args, **kwargs)

   def select(self, *items, **kwargs):
       self.scene.select(*[x.get_selection_string() for x in items if isinstance(x, DependNode)], **kwargs)

   def fit_view(self, *args):
       self.scene.fit_view(*args)

   def refresh(self):
       self.scene.refresh()

   def dg_dirty(self):
       self.scene.dg_dirty()

   def lock_node(self, *nodes, **kwargs):
       self.scene.lock_node(*nodes, **kwargs)

   def get_dag_path(self, node):
       return str(self.scene.get_dag_path(node.m_object).fullPathName())

   def listConnections(self, *args, **kwargs):
       return self.scene.listConnections(*args, **kwargs)

   def disconnectAttr(self, *args, **kwargs):
       return self.scene.disconnectAttr(*args, **kwargs)

   def connectAttr(self, *args, **kwargs):
       return self.scene.connectAttr(*args, **kwargs)

   def load_plugin(self, plugin_name):
       self.scene.loadPlugin(plugin_name)

   def check_visibility(self, node):
       return self.scene.check_visibility(node)

   def finish_delete_objects(self):
       if self.nodes_scheduled_for_deletion:
           evaluation_mode = str(self.scene.evaluationManager(q=True, mode=True)[0])
           self.scene.evaluationManager(mode="off")
           existing_nodes = [x for x in self.nodes_scheduled_for_deletion if self.scene.objExists(x)]
           if existing_nodes:
               self.scene.lock_node(
                   existing_nodes,
                   lock=False
               )
               self.scene.delete(existing_nodes)
           self.nodes_scheduled_for_deletion = []
           self.scene.evaluationManager(mode=evaluation_mode)


   def add_layer(self, name):
       if not name:
           return
       elif name in self.object_layers:
           return self.object_layers[name]
       else:
           new_layer = ObjectLayer(name)
           self.object_layers[name] = new_layer
           return new_layer

   def set_root(self, root):
       com.system_signals.root_signals['start_change'].emit()
       self.root = root
       com.system_signals.root_signals['end_change'].emit(root)

   @dec.flatten_args
   def schedule_objects_for_deletion(self, *args):
       for o in args:
           if isinstance(o, obs.BaseObject):
               if o.name not in self.deleted_object_names:
                   self.deleted_object_names.append(o.name)
                   o.teardown()
               else:
                   logging.getLogger('rig_build').warning('%s was already deleted.' % o.name)
           else:
               logging.getLogger('rig_build').warning('%s cannot be deleted by controller' % type(o))

   def delete_scheduled_objects(self):
       if self.deleted_object_names:
           gc.collect()
           failed_object_names = [x for x in self.deleted_object_names if x in self.named_objects]
           self.deleted_object_names = []
           if self.debug_garbage_collection:
               if failed_object_names:
                   message = 'Failed to delete: %s\n\n' % ', '.join(failed_object_names)
                   message += self.get_referrer_message(failed_object_names)
                   file_path = '%s/undeleted.log' % os.environ['TEMP'].replace('\\', '/')  # USe tempdir module
                   with open(file_path, mode='w') as f:
                       f.write(message)
                   os.system('start %s' % file_path)
                   raise Exception('Garbage collection failed. See Referrers: %s' % file_path)
           self.finish_delete_objects()

   @dec.flatten_args
   def get_referrer_message(self, *object_names):
       message = ''
       for node_name in object_names:
           referrers = gc.get_referrers(self.named_objects[node_name])
           for r in referrers:
               if isinstance(r, types.FrameType):
                   message += '\nThe object "%s" existed in Frame : %s\n\n\n' % (
                       node_name,
                       inspect.getframeinfo(r)
                   )
               else:
                   message += '\nThe object "%s" existed in %s: %s\n\n\n' % (
                       node_name,
                       type(r),
                       r
                   )
       return message


class ObjectLayer(object):
   def __init__(self, name, locked=False):
       super().__init__()
       self.name = name
       self.locked = locked
       self.objects = weakref.WeakSet()

   def __repr__(self):
       return self.name


'''