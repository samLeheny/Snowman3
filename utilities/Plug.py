import maya.cmds as mc
import pymel.core as pm
import maya.api.OpenMaya as om
import Snowman3.utilities.BaseObject as base_obj
BaseObject = base_obj


def initialize_plug(owner, key):
    node_functions = om.MFnDependencyNode(owner)
    m_attribute = node_functions.attribute(key)
    return node_functions.findPlug(m_attribute, False)


def create_m_plug(owner, key, **kwargs):
    mc.addAttr( get_selection_string(owner), longName=key, **kwargs )
    return initialize_plug(owner, key)


def get_selection_string(m_object):
    sel_list = om.MSelectionList()
    sel_list.add(m_object)
    sel_strings = sel_list.getSelectionStrings(0)
    return pm.PyNode(sel_strings[0])


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


class Plug(BaseObject):

    m_plug = None
    child_plug_names = {}

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.m_plug = None
        self.child_plug_names = {}  # Dict of ints

    @classmethod
    def create(cls, **kwargs):
        parent = kwargs.get('parent', None)
        root_name = kwargs.get('root_name', None)
        m_plug = create_m_plug(parent.m_object, root_name, **{'keyable': True, 'attributeType': 'float'})
        this = super(Plug, cls).create(**kwargs)
        this.m_plug = m_plug
        this.parent = parent
        return this

    def set_value(self, value):
        set_plug_value(self.m_plug, value)