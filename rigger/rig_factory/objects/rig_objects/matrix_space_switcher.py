from Snowman3.rigger.rig_factory.objects.base_objects.properties import ObjectProperty, ObjectListProperty
from Snowman3.rigger.rig_factory.objects.base_objects.base_object import BaseObject


class MatrixSpaceSwitcher(BaseObject):
    handle = ObjectProperty( name='handle' )
    targets = ObjectListProperty( name='targets' )
    decompose_matrix = ObjectProperty( name='decompose_matrix' )
    utility_nodes = ObjectListProperty( name='utlity_nodes' )
