from Snowman3.rigger.rig_factory.objects.node_objects.dag_node import DagNode
from Snowman3.rigger.rig_factory.objects.base_objects.properties import DataProperty


class NurbsSurface(DagNode):

    positions = DataProperty( name='positions' )
    knots_u = DataProperty( name='knots_u' )
    knots_v = DataProperty( name='knots_v' )
    degree_u = DataProperty( name='degree_u' )
    degree_v = DataProperty( name='degree_v' )
    form_u = DataProperty( name='form_u' )
    form_v = DataProperty( name='form_v' )
    suffix = 'Nsf'

    def __init__(self, **kwargs):
        super(NurbsSurface, self).__init__(**kwargs)
        self.node_type = 'nurbsSurface'

    def get_surface_data(self):
        return self.controller.get_surface_data(self)

    def create_in_scene(self):
        if self.positions:
            self.m_object = self.controller.scene.draw_nurbs_surface(
                self.positions,
                self.knots_u,
                self.knots_v,
                self.degree_u,
                self.degree_v,
                self.form_u,
                self.form_v,
                self.name,
                self.parent.m_object
            )
        else:
            self.m_object = self.controller.scene.create_dag_node(
                self.node_type,
                self.name,
                self.parent.m_object
            )

    def update(self):
        self.controller.scene.update_surface(self.m_object)

    def set_surface_data(self, *data):
        self.controller.scene.update_surface_shape(
            self.m_object,
            *data
        )

