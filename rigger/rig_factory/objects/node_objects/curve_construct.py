import Snowman3.rigger.rig_factory.objects.node_objects.transform as transform
Transform = transform.Transform

import Snowman3.rigger.rig_factory.objects.node_objects.nurbs_curve as nurbs_curves
NurbsCurve = nurbs_curves.NurbsCurve



class CurveConstruct(Transform):

    shape = []
    scale = 1
    shape_offset = None
    curves = []
    color = None
    scene_object = None
    up_direction = None
    forward_direction = None
    composed_cv_data = None
    nurbs_curves = []


    def __init__(self, **kwargs):
        super().__init__(**kwargs)


    @classmethod
    def create(cls, **kwargs):
        this = super().create(**kwargs)
        this.composed_cv_data = this.controller.compose_curve_construct_cvs(
            curve_data=this.shape, scale=this.scale, shape_offset=this.shape_offset, up_direction=this.up_direction,
            forward_direction=this.forward_direction)
        return this


    def create_in_scene(self, **kwargs):
        super().create_in_scene()
        #self.scene_object = pm.shadingNode('transform', name=self.name, au=1) Create m_object automatically upon creation (in DependNode class)
        for i, shp in enumerate(self.shape):
            self.nurbs_curves.append(
                NurbsCurve.create(
                    name = f'{self.name}Shape{i}',
                    form = shp['form'],
                    degree = shp['degree'],
                    cvs = shp['cvs'],
                    color = self.color,
                    parent = self
                )
            )
        #return self.scene_object


