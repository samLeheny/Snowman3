from Snowman3.utilities.shapeNode import ShapeNode
from Snowman3.utilities.properties import DataProperty


class NurbsCurve(ShapeNode):

    pretty_name = DataProperty(name='pretty_name')
    name = DataProperty(name='name')
    form = DataProperty(name='form', default_value='open')
    suffix = 'Crv'
    degree = 1
    cvs = []
    color = None


    def __init__(self, **kwargs):
        kwargs.setdefault('node_type', 'nurbsCurve')
        super().__init__(**kwargs)


    def create_in_scene(self):
        self.m_object = self.interactor.create_nurbs_curve(name=self.name, degree=self.degree, point=self.cvs,
                                                           form=self.form, color=self.color)
