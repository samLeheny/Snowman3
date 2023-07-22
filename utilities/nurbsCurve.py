import importlib

import Snowman3.utilities.allocator as allocator
importlib.reload(allocator)

import Snowman3.utilities.DagNode as dag_node
importlib.reload(dag_node)
DagNode = dag_node.DagNode

from Snowman3.utilities.properties import DataProperty



class NurbsCurve(DagNode):

    pretty_name = DataProperty(name='pretty_name')
    name = DataProperty(name='name')
    form = DataProperty(name='form', default_value='open')
    suffix = 'Crv'
    degree = 1
    cvs = []
    color = None
    scene_object = None


    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.node_type = 'nurbsCurve'


    def create_in_scene(self, **kwargs):
        self.m_object = allocator.create_nurbs_curve(
            name=self.name,
            color=self.color,
            form=self.form,
            cvs=self.cvs,
            degree=self.degree,
            parent=self.parent.m_object
        )
        return self.m_object
