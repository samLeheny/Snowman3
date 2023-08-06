import Snowman3.rigger.rig_factory.objects.node_objects.dag_node as dag_node
DagNode = dag_node.DagNode

from Snowman3.rigger.rig_factory.objects.base_objects.properties import DataProperty



class NurbsCurve(DagNode):

    positions = DataProperty( name='positions' )
    degree = DataProperty( name='degree', default_value=2 )
    form = DataProperty( name='form', default_value=0 )
    create_2d = DataProperty( name='create_2d', default_value=False )
    rational = DataProperty( name='rational', default_value=False )
    suffix = 'Ncv'
    '''
    pretty_name = DataProperty(name='pretty_name')
    name = DataProperty(name='name')
    form = DataProperty(name='form', default_value='open')
    suffix = 'Crv'
    degree = 1
    cvs = []
    color = None
    scene_object = None
    '''

    def __init__(self, **kwargs):
        kwargs['positions'] = [list(x) for x in kwargs.get('positions', [])]
        super().__init__(**kwargs)
        self.node_type = 'nurbsCurve'


    '''def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.node_type = 'nurbsCurve'
    '''

    @classmethod
    def create(cls, **kwargs):
        if not kwargs['parent']:
            raise Exception('Cannot create a NurbsCurve without a parent')
        this = super().create(**kwargs)
        return this


    def get_curve_data(self):
        return self.controller.get_curve_data(self)


    def get_curve_cv_positions(self):
        return self.controller.scene.get_curve_cv_positions(self.m_object)


    def create_in_scene(self):
        if self.positions:
            self.m_object = self.controller.scene.draw_nurbs_curve(
                name=self.name,
                #color=self.color,
                form=self.form,
                cvs=self.positions,
                degree=self.degree,
                parent=self.parent.m_object
            )
            '''self.m_object = self.controller.scene.draw_nurbs_curve(
                self.positions,
                self.degree,
                self.form,
                self.name,
                self.parent.m_object,
                create_2d=self.create_2d,
                rational=self.rational
            )'''
        else:
            self.m_object = self.controller.scene.create_dag_node(
                self.node_type,
                self.name,
                self.parent.m_object
            )


    '''def create_in_scene(self, **kwargs):
        self.m_object = self.controller.create_nurbs_curve(
            name=self.name,
            color=self.color,
            form=self.form,
            cvs=self.cvs,
            degree=self.degree,
            parent=self.parent.m_object
        )
        return self.m_object
    '''
