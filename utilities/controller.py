import importlib
import math
import weakref

import maya.cmds as mc
import pymel.core as pm
import maya.api.OpenMaya as om

import Snowman3.utilities.maya_scene as maya_scene
importlib.reload(maya_scene)
MayaScene = maya_scene.MayaScene

import Snowman3.riggers.utilities.curve_utils as curve_utils
importlib.reload(curve_utils)

import Snowman3.riggers.managers.blueprint_manager as blueprint_manager_util
importlib.reload(blueprint_manager_util)
BlueprintManager = blueprint_manager_util.BlueprintManager

import Snowman3.utilities.node_utilities.node_utilities as node_utils


###########################
######## Variables ########
# -
ARMATURE_STATE_TAG = 'Armature'
RIG_STATE_TAG = 'Rig'
# -
###########################
###########################


class Controller:

    # -
    asset_name = None
    dirpath = None
    blueprint_manager = None
    state = None
    # -
    namespace = None
    build_directory = None
    named_objects = None
    scene = None


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
    def get_controller(cls):
        this = cls()
        this.scene = MayaScene()
        this.build_directory = None
        #sig.build_directory_changed.connect(this.set_build_directory)
        return this


    def create_managers(self, asset_name, dirpath, prefab_key=None):
        self.blueprint_manager = BlueprintManager(asset_name=asset_name, dirpath=dirpath, prefab_key=prefab_key)
        self.scene.create_armature_manager()
        self.scene.create_rig_manager()


    def build_armature_from_latest_version(self):
        self.scene.build_armature_from_latest_version(self.blueprint_manager)


    def build_rig(self):
        self.scene.build_rig(self.blueprint_manager)
        self.state = RIG_STATE_TAG


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
        '''if self.namespace:
            long_name = '%s:%s' % (self.namespace, name)'''

        if node.get_selection_string() == long_name:
            #logging.getLogger('rig_build').warning('The node was already named: %s. skipping rename' % long_name)
            return name

        node.name = long_name

        if self.scene.objExists(long_name):
            raise Exception(f"A node with the name '{long_name}' already exists.")
        self.scene.rename( node.get_selection_string(), name )

        self.named_objects[long_name] = node

        # Rename plugs of object
        if hasattr(node, 'existing_plugs') and node.existing_plugs:
            for plug in node.existing_plugs.values():
                plug.update_name()

        return name


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


    @staticmethod
    def compose_curve_construct_cvs(**kwargs):
        return curve_utils.compose_curve_construct_cvs(**kwargs)


    def create_nurbs_curve(self, **kwargs):
        self.scene.create_nurbs_curve(**kwargs)


    @staticmethod
    def set_plug_value(plug, value, force=False):
        if not isinstance(plug, om.MPlug):
            raise Exception('Plug is not type "MPlug"')
        locked = plug.isLocked()
        if force and locked:
            plug.setLocked(0)
        if plug.isCompound():
            for i in range(plug.numChildren()):
                set_plug_value(plug.child(i), value[i])
        elif plug.isArray():
            for i in range(plug.numElements()):
                set_plug_value(plug.elementByPhysicalIndex(i), value[i])
        else:
            attribute = plug.attribute()
            if attribute.hasFn(om.MFn.kNumericAttribute):
                attribute_type = om.MFnNumericAttribute(attribute).unitType()
                if attribute_type == om.MFnNumericData.kFloat:
                    plug.setFloat(value)
        if locked:
            plug.setLocked(1)


    @staticmethod
    def get_plug_value(plug):
        if not isinstance(plug, om.MPlug):
            raise Exception("Plug is not type 'MPlug'")
        m_plug = plug
        '''if m_plug.isCompound():
            plugs = []
            for i in range(m_plug.numChildren()):
                plugs.append(m_plug.child(i))
            return [get_plug_value(x) for x in plugs]'''
        '''if m_plug.isArray():
            plugs = []
            for i in range(m_plug.numElements()):
                plugs.append(m_plug.elementByPhysicalIndex(i))
            return [get_plug_value(x) for x in plugs]'''
        attribute = m_plug.attribute()
        # Numeric
        if attribute.hasFn(om.MFn.kNumericAttribute):
            attribute_type = om.MFnNumericAttribute(attribute).unitType()
            # Boolean
            if attribute_type in [om.MFnNumericData.kBoolean]:
                return m_plug.asBool()
            # Char
            elif attribute_type == om.MFnNumericData.kChar:
                return m_plug.asChar()
            # Short
            elif attribute_type == om.MFnNumericData.kShort:
                return m_plug.asShort()
            # Int, Long, Byte
            elif attribute_type in (
                    om.MFnNumericData.kInt,
                    om.MFnNumericData.kLong,
                    om.MFnNumericData.kByte
            ):
                return m_plug.asInt()
            # Float
            elif attribute_type == om.MFnNumericData.kFloat:
                return m_plug.asFloat()
            # Double
            elif attribute_type == om.MFnNumericData.kDouble:
                return m_plug.asDouble()
            else:
                return m_plug.asFloat()
                #print 'Plug type not supported', attribute_type

        elif attribute.hasFn(om.MFn.kUnitAttribute):
            unit_type = om.MFnUnitAttribute(attribute).unitType()
            if unit_type == om.MFnUnitAttribute.kAngle:
                return math.degrees(m_plug.asMAngle().value())
            elif unit_type == om.MFnUnitAttribute.kDistance:
                return m_plug.asMDistance().value()
            elif unit_type == om.MFnUnitAttribute.kTime:
                return m_plug.asMTime().value()
            else:
                return m_plug.asFloat()
                #print 'Plug type "%s" not supported' % unit_type

        elif attribute.hasFn(om.MFn.kTypedAttribute):
            attr_type = om.MFnTypedAttribute(attribute).attrType()
            if attr_type == om.MFnData.kString:
                return m_plug.asString()
            if attr_type == om.MFnData.kMatrix:
                matrix_data = om.MFnMatrixData(m_plug.asMObject())
                m = matrix_data.matrix()
                return [
                    m(0, 0), m(0, 1), m(0, 2), m(0, 3),
                    m(1, 0), m(1, 1), m(1, 2), m(1, 3),
                    m(2, 0), m(2, 1), m(2, 2), m(2, 3),
                    m(3, 0), m(3, 1), m(3, 2), m(3, 3)
                ]
            if attr_type == om.MFnData.kPointArray:
                point_array_data = om.MFnPointArrayData(m_plug.asMObject())
                point_array = point_array_data.array()
                point_data = []
                for i in range(point_array.length()):
                    m_point = point_array[i]
                    point_data.append((m_point[0], m_point[1], m_point[2]))
                return point_data

            else:
                raise Exception('Plug type "%s" not supported' % attr_type)


        elif attribute.hasFn(om.MFn.kMatrixAttribute):
            matrix_data = om.MFnMatrixData(m_plug.asMObject())
            m = matrix_data.matrix()
            return [
                m(0, 0), m(0, 1), m(0, 2), m(0, 3),
                m(1, 0), m(1, 1), m(1, 2), m(1, 3),
                m(2, 0), m(2, 1), m(2, 2), m(2, 3),
                m(3, 0), m(3, 1), m(3, 2), m(3, 3)
            ]

        else:
            #print 'Plug type not supported "%s"' % plug
            return mc.getAttr(get_selection_string(plug))


    @staticmethod
    def get_selection_string(m_object):
        sel_list = om.MSelectionList()
        sel_list.add(m_object)
        sel_strings = sel_list.getSelectionStrings(0)
        return pm.PyNode(sel_strings[0])


    @staticmethod
    def zero_joint_rotation(joint):
        node_utils.zero_joint_rotation(joint)
