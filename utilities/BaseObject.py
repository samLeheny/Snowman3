import Snowman3.utilities.properties as properties
DataProperty = properties.DataProperty
ObjectProperty = properties.ObjectProperty


# ----------------------------------------------------------------------------------------------------------------------
class BaseObject(object):

    name = DataProperty(name='name')
    parent = ObjectProperty(name='parent')
    children = []


    def __init__(self, **kwargs):
        super().__init__()
        for key in kwargs:
            if hasattr(self, key):
                setattr(self, key, kwargs[key])
        if self.parent:
            self.parent.children.append(self)
        self.children = []


    @classmethod
    def create(cls, **kwargs):
        name = kwargs['name']
        #parent = kwargs.get('parent', None)
        this = cls(**kwargs)
        this.name = name
        return this
