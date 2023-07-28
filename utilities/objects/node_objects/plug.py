from Snowman3.utilities.objects.base_objects.base_object import BaseObject



class Plug(BaseObject):
    pass
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
        m_plug = cls.controller.create_m_plug(parent.m_object, root_name, **{'keyable': True, 'attributeType': 'float'})
        this = super().create(**kwargs)
        this.m_plug = m_plug
        this.parent = parent
        return this


    def set_value(self, value):
        self.controller.set_plug_value(self.m_plug, value)


    def get_value(self):
        return self.controller.get_plug_value(self)
