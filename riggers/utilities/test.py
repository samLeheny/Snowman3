import os
import copy
import weakref
#from rig_factory.objects.base_objects.weak_list import WeakList

DEBUG = os.getenv('PIPE_DEV_MODE') == 'TRUE'


class Plugs(object):
    def __init__(self, node):
        self.node = weakref.ref(node)

    def __getitem__(self, key):
        node = self.node()
        if node:
            new_plug = node.initialize_plug(key)
            return new_plug

    def __setitem__(self, key, val):
        node = self.node()
        if node:
            node.existing_plugs[key] = val

    def get_values(self, keys):
        return dict((key, self[key].get_value()) for key in keys)

    def set_values(self, **kwargs):
        for key in kwargs:
            self[key].set_value(kwargs[key])

    def set_locked(self, **kwargs):
        for key in kwargs:
            self[key].set_locked(kwargs[key])

    def set_channel_box(self, **kwargs):
        for key in kwargs:
            self[key].set_channel_box(kwargs[key])

    def set_keyable(self, **kwargs):
        for key in kwargs:
            self[key].set_keyable(kwargs[key])

    '''def get(self, *args):
        return WeakList([self[x] for x in args])'''


class DataProperty(object):
    map = weakref.WeakKeyDictionary()
    default_value = None

    def __init__(self, **kwargs):
        self.name = kwargs.get('name')
        self.default_value = kwargs.get(
            'default_value',
            copy.copy(self.__class__.default_value)
        )

    def __get__(self, instance, owner):
        if instance is None:
            raise Exception('instance is None something has gone wrong')
        properties = self.map.setdefault(instance, weakref.WeakKeyDictionary())
        return properties.setdefault(self, copy.copy(self.default_value))

    def __set__(self, instance, value):
        if DEBUG:
            import json
            try:
                json.dumps(value)
            except Exception as e:
                raise Exception('failed to serialize %s, %s' % (self.name, value))
        properties = self.map.setdefault(instance, weakref.WeakKeyDictionary())
        properties[self] = value


class ObjectProperty(object):
    map = weakref.WeakKeyDictionary()

    def __init__(self, **kwargs):
        self.name = kwargs.get('name')

    def __get__(self, instance, owner):
        properties = self.map.setdefault(instance, weakref.WeakKeyDictionary())
        item = properties.get(self, None)
        if item:
            return item()

    def __set__(self, instance, value):
        properties = self.map.setdefault(instance, weakref.WeakKeyDictionary())
        if value:
            properties[self] = weakref.ref(value)
        else:
            properties.pop(self, None)


'''class ObjectListProperty(object):
    map = weakref.WeakKeyDictionary()

    def __init__(self, **kwargs):
        self.name = kwargs.get('name')

    def __get__(self, instance, owner):
        properties = self.map.setdefault(instance, weakref.WeakKeyDictionary())
        object_list = properties.get(self, None)
        if object_list:
            return object_list
        object_list = WeakList()
        properties[self] = object_list
        return object_list

    def __set__(self, instance, value):

        if not isinstance(value, (list, set, tuple)):
            raise Exception('You must use type(list) when setting class property : %s' % self.name)
        properties = self.map.setdefault(instance, weakref.WeakKeyDictionary())
        properties[self] = WeakList(value)'''


class ObjectDictProperty(DataProperty):
    map = weakref.WeakKeyDictionary()

    def __get__(self, instance, owner):
        properties = self.map.setdefault(instance, weakref.WeakKeyDictionary())
        weak_dict = properties.get(self, None)
        if weak_dict:
            return weak_dict
        weak_dict = weakref.WeakValueDictionary()
        properties[self] = weak_dict
        return weak_dict

    def __set__(self, instance, value):
        if not isinstance(value, weakref.WeakValueDictionary):
            raise Exception('You must use type(WeakValueDictionary) when setting class property : %s' % self.name)
        properties = self.map.setdefault(instance, weakref.WeakKeyDictionary())
        properties[self] = value


class BaseObject(object):
    name = DataProperty(name='name')
    parent = ObjectProperty(name='parent')
    children = []

    @classmethod
    def create(cls, **kwargs):
        print(2)
        name = kwargs['name']
        parent = kwargs.get('parent', None)
        this = cls(**kwargs)
        this.name = name
        return this

    def __init__(self, **kwargs):
        super(BaseObject, self).__init__()
        for key in kwargs:
            if hasattr(self, key):
                setattr(self, key, kwargs[key])
        if self.parent:
            self.parent.children.append(self)
        self.children = []


class DependNode(BaseObject):
    existing_plugs = ObjectDictProperty(name='existing_plugs')
    node_type = DataProperty(name='node_type')
    plugs = []
    m_object = None

    def __init__(self, **kwargs):
        super(DependNode, self).__init__(**kwargs)
        self.plugs = Plugs(self)
        self.m_object = None

    @classmethod
    def create(cls, **kwargs):
        m_object = kwargs.pop('m_object', None)
        print(1)
        this = super(DependNode, cls).create(**kwargs)
        print(3)
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
        print('Created in scene.')


a = DependNode.create(name='A')