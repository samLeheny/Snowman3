from Snowman3.rigger.rig_factory.objects.base_objects.properties import DataProperty, ObjectProperty, ObjectDictProperty
import Snowman3.rigger.rig_factory.common_modules as com
#importlib.reload(com)


# ----------------------------------------------------------------------------------------------------------------------
class BaseObject(object):

    name = DataProperty( name='name' )
    functionality_name = DataProperty( name='functionality_name' )
    segment_name = DataProperty( name='segment_name' )
    differentiation_name = DataProperty( name='differentiation_name' )
    subsidiary_name = DataProperty( name='subsidiary_name' )
    root_name = DataProperty( name='root_name' )
    base_name = DataProperty( name='base_name' )
    size = DataProperty( name='size', default_value=1.0 )
    side = DataProperty( name='side' )
    parent = ObjectProperty( name='parent' )
    relationships = ObjectDictProperty( name='relationships' )
    object_metadata = DataProperty( name='object_metadata', default_value=dict() )
    suffix = None
    children = []
    controller = None
    namespace = None
    layer = None


    @classmethod
    def pre_process_kwargs(cls, **kwargs):
        controller = com.controller_utils.get_controller() # com.controller_utilities.get_controller()
        kwargs.setdefault('namespace', controller.namespace)
        kwargs.setdefault('suffix', cls.suffix)
        kwargs.setdefault('klass', cls.__name__)
        return kwargs


    @classmethod
    def get_predicted_name(cls, **kwargs):
        return com.name_utils.create_name_string(**cls.pre_process_kwargs(**kwargs))


    @classmethod
    def create(cls, **kwargs):
        controller = com.controller_utils.get_controller() # com.controller_utilities.get_controller()
        processed_kwargs = cls.pre_process_kwargs(**kwargs)
        name = com.name_utils.create_name_string(**processed_kwargs)
        if name in controller.named_objects:
            raise Exception(f"An object with name '{name}' already exists.")
        parent = kwargs.get('parent', None)
        if parent is not None and not isinstance(parent, BaseObject):
            raise Exception(f"You must provide either a BaseObject instance or None for parent argument."
                            f"Not {parent} type:{type(parent)}")
        this = cls(**kwargs)
        this.name = name
        this.controller = controller
        controller.named_objects[name] = this
        return this


    def extract_name(self, **kwargs):
        """
        Used to build name strings on the properties of this node
        Essentially used to ask hypothetical questions like:
        If this node was created with side='right' and segment_name='foo', what WOULD the name be?
        """
        kwargs = self.pre_process_kwargs(**kwargs)
        for key in [
            'root_name',
            'segment_name',
            'functionality_name',
            'differentiation_name',
            'subsidiary_name',
            'side'
        ]:
            value = getattr(self, key)
            if key not in kwargs:
                kwargs[key] = value
        return com.name_utils.create_name_string(**kwargs)


    def __init__(self, **kwargs):
        super().__init__()
        for key in kwargs:
            if hasattr(self, key):
                setattr(self, key, kwargs[key])
        if self.parent:
            self.parent.children.append(self)
        self.children = []


    def create_child(self, object_type, *args, **kwargs):
        for key in [
            'root_name',
            'segment_name',
            'functionality_name',
            'differentiation_name',
            'side',
            'size',
            'subsidiary_name'
        ]:
            if key not in kwargs:
                kwargs[key] = self.__getattribute__(key)
        if 'parent' not in kwargs or kwargs['parent'] is None:
            kwargs['parent'] = self

        node = self.controller.create_object( object_type, *args, **kwargs )
        return node


    def unparent(self):
        self.controller.unparent(self)


    def set_parent(self, parent, **kwargs):
        self.controller.set_parent(self, parent, **kwargs)


    def __repr__(self):
        return f"<{self.__class__.__name__} name='{self.name}'>"


    def __str__(self):
        return self.__repr__()


    def __unicode__(self):
        return self.__str__()


    def set_name(self, name):
        self.controller.set_name(self, name)


    def serialize(self):
        self.controller.serialize(self)


    def get_ancestors(self, include_self=True):
        ancestors = [include_self] if include_self else []
        owner = self.parent
        while owner:
            ancestors.insert(0, owner)
            owner = owner.parent
        return ancestors


    def get_descendants(self, *types, **kwargs):
        descendants = []
        include_self = kwargs.get('include_self', False)
        if include_self:
            descendants.append(self)
        children = [x for x in self.children if not types or isinstance(x, types)]
        descendants.extend(children)
        for child in children:
            descendants.extend(child.get_descendants(*types))
        return descendants


    def teardown(self):
        if self.parent:
            parent = self.parent
            self.unparent()


    def __setattr__(self, name, value):
        if not hasattr(self, name):
            raise Exception(f"The '{name}' attribute is not registered with the {self.__class__.__name__} class")
        else:
            try:
                super().__setattr__(name, value)
            except Exception as e:
                raise Exception(f"The property '{name}' on the '{type(self)}' named '{self.name}'"
                                f"could not be set to: type<{type(value)}> {str(value)}. See log for details")
