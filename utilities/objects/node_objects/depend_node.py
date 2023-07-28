import weakref
from Snowman3.utilities.objects.base_objects.base_object import BaseObject
from Snowman3.utilities.objects.node_objects.plug import Plug
from Snowman3.utilities.objects.base_objects.properties import DataProperty, ObjectDictProperty
from Snowman3.utilities.objects.base_objects.weak_list import WeakList


# ----------------------------------------------------------------------------------------------------------------------
class DependNode(BaseObject):

    existing_plugs = ObjectDictProperty( name='existing_plugs' )
    node_type = DataProperty( name='node_type' )
    plugs = []
    m_object = None


    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.plugs = Plugs(self)
        self.m_object = None


    @classmethod
    def create(cls, **kwargs):
        root_name = kwargs.get('root_name', None)
        if root_name is not None and '.' in root_name and 'root_name':
            raise Exception(f"The keyword argument 'root_name' has an invalid character: {root_name}")
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
        self.controller.rename(self, self.name.split(':')[-1])


    def create_in_scene(self):
        self.m_object = self.controller.create_m_depend_node( node_type=self.node_type, name=self.name )


    def initialize_plug(self, key):
        if key in self.existing_plugs:
            return self.existing_plugs[key]
        else:
            plug = self.create_child(
                Plug,
                root_name=key,
                name=f'{self.name}.{key}',
                check_name=False
            )
            self.existing_plugs[key] = plug
            return plug


    def rename(self, name):
        self.controller.rename(self, name)


    def create_plug(self, name, **kwargs):
        use_existing = kwargs.pop('use_existing', False)
        if use_existing and name in self.existing_plugs:
            return self.existing_plugs['name']
        return self.create_child(
            Plug,
            root_name = name,
            create_kwargs = kwargs,
            user_defined = True
        )


    def get_selection_string(self):
        #if self.controller.scene.mock or not self.m_object:
        if not self.m_object:
            return self.name
        return self.controller.get_selection_string(self.m_object)


    def __str__(self):
        return self.get_selection_string()


    def teardown(self):
        self.controller.nodes_scheduled_for_deletion.append(self.get_selection_string())
        self.m_object = None
        super().teardown()

    def is_visible(self):
        self.controller.check_visibility(self)


    def create_node_math_instance(self, plug):
        return NodeMath(plug)



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
        return WeakList([self[x] for x in args])


    def exists(self, *args):
        node = self.node()
        if not node:
            return False
        else:
            for attribute_name in args:
                if not node.controller.objExists(f'{node.get_selection_string()}.{attribute_name}'):
                    return False
        return True



# ----------------------------------------------------------------------------------------------------------------------
class NodeMath:

    def __init__(self, plug):
        super().__init__()
        self.plug = plug


    def connect_to(self, target):
        if isinstance(target, NodeMath):
            target = target.plug
        self.plug.connect_to(target)
