import importlib

import Snowman3.rigger.rig_factory.objects.node_objects.dag_node as dag_node
importlib.reload(dag_node)
DagNode = dag_node.DagNode

from Snowman3.rigger.rig_factory.objects.base_objects.properties import DataProperty



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
        self.m_object = self.controller.create_nurbs_curve(
            name=self.name,
            color=self.color,
            form=self.form,
            cvs=self.cvs,
            degree=self.degree,
            parent=self.parent.m_object
        )
        return self.m_object
