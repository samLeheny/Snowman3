import weakref
import Snowman3.utilities.BaseObject as base_object
BaseObject = base_object.BaseObject
DataProperty = base_object.DataProperty


# ----------------------------------------------------------------------------------------------------------------------
class DependNode(BaseObject):

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
        print('Created in scene.')


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
