from Snowman3.rigger.rig_factory.objects.node_objects.depend_node import DependNode
from Snowman3.rigger.rig_factory.objects.base_objects.properties import ObjectListProperty, DataProperty


class ShadingGroup(DependNode):

    shaders = ObjectListProperty( name='shaders' )
    node_type = DataProperty( name='node_type', default_value='shadingEngine' )
    suffix = 'Sgp'

    def __init__(self, **kwargs):
        super(ShadingGroup, self).__init__(**kwargs)

    def create_in_scene(self):
        self.m_object = self.controller.scene.create_shading_group( self.name )
