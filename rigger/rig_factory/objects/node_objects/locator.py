from dag_node import DagNode
from Snowman3.rigger.rig_factory.objects.base_objects.properties import DataProperty


class Locator(DagNode):

    node_type = DataProperty( name='node_type', default_value='locator' )

    suffix = 'Loc'


    def __init__(self, **kwargs):
        super().__init__(**kwargs)