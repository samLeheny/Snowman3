from Snowman3.utilities.shapeNode import ShapeNode
from Snowman3.utilities.properties import DataProperty


class NurbsCurve(ShapeNode):

    pretty_name = DataProperty(name='pretty_name')
    suffix = 'Crv'

    def __init__(self, **kwargs):
        kwargs.setdefault('node_type', 'nurbsCurve')
        super().__init__(**kwargs)
