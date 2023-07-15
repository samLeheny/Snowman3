from Snowman3.utilities.DagNode import DagNode
from Snowman3.utilities.properties import DataProperty


class ShapeNode(DagNode):

    pretty_name = DataProperty(name='pretty_name')

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
