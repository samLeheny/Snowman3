import importlib
import Snowman3.utilities.properties as properties
DataProperty = properties.DataProperty
ObjectProperty = properties.ObjectProperty
import Snowman3.utilities.common_modules as com
#importlib.reload(com)


# ----------------------------------------------------------------------------------------------------------------------
class BaseObject(object):

    name = DataProperty(name='name')
    parent = ObjectProperty(name='parent')
    suffix = None
    children = []
    controller = []
    namespace = None


    def __init__(self, **kwargs):
        super().__init__()
        for key in kwargs:
            if hasattr(self, key):
                setattr(self, key, kwargs[key])
        if self.parent:
            self.parent.children.append(self)
        self.children = []


    def get_controller(self):
        controller = com.controller_utils.get_controller()
        return controller


    @classmethod
    def pre_process_kwargs(cls, **kwargs):
        controller = cls.get_controller(cls) # com.controller_utilities.get_controller()
        # kwargs.setdefault('namespace', controller.namespace)
        kwargs.setdefault('suffix', cls.suffix)
        kwargs.setdefault('klass', cls.__name__)
        return kwargs


    @classmethod
    def create(cls, **kwargs):
        controller = cls.get_controller(cls) # com.controller_utilities.get_controller()
        processed_kwargs = cls.pre_process_kwargs(**kwargs)
        name = kwargs['name'] # com.name_utilities.create_name_string(processed_kwargs)
        if name in controller.named_objects:
            raise Exception(f"An object with name '{name}' already exists.")
        parent = kwargs.get('parent', None)
        if parent is not None and isinstance(parent, BaseObject):
            raise Exception(f"You must provide either a BaseNode instance or None for parent argument."
                            f"Not {parent} type:{type(parent)}")
        this = cls(**kwargs)
        this.name = name
        this.controller = controller
        controller.named_objects[name] = this
        return this
