import weakref
import importlib
import Snowman3.utilities.allocator as allocator
importlib.reload(allocator)
import Snowman3.utilities.BaseObject as base_obj
importlib.reload(base_obj)
BaseObject = base_obj.BaseObject
from Snowman3.utilities.properties import DataProperty


# ----------------------------------------------------------------------------------------------------------------------
class DependNode(BaseObject):

    node_type = DataProperty( name='node_type' )
    plugs = []
    m_object = None


    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.plugs = Plugs(self)
        self.m_object = None


    @classmethod
    def create(cls, **kwargs):
        m_object = kwargs.pop('m_object', None)
        this = super().create(**kwargs)
        this.m_object = None
        if not m_object:
            this.create_in_scene()
        else:
            this.set_m_object(m_object)
        return this

    def set_m_object(self, m_object):
        self.m_object = m_object
        #self.controller.rename(self, self.name.split(':')[-1])

    def create_in_scene(self):
        self.m_object = allocator.create_m_depend_node( node_type=self.node_type, name=self.name )


# ----------------------------------------------------------------------------------------------------------------------
class Plugs:

    def __init__(self, node):
        self.node = weakref.ref(node)


    def __getitem__(self, key):
        node = self.node()
        if node:
            new_plug = node.initialize_plug(key)
            return new_plug

    def __setitem__(self, key, value):
        node = self.node()
        if node:
            node.existing_plugs[key] = value


    def get_values(self, keys):
        return dict((key, self[key].get_values()) for key in keys)


    def set_values(self, **kwargs):
        for key in kwargs:
            self[key].set_values(kwargs[key])


    def set_locked(self, **kwargs):
        for key in kwargs:
            self[key].set_locked(kwargs[key])


    def set_channel_box(self, **kwargs):
        for key in kwargs:
            self[key].set_channel_box(kwargs[key])


    def set_keyable(self, **kwargs):
        for key in kwargs:
            self[key].set_keyable(kwargs[key])


    def get(self, *args):
        pass
