import importlib

import Snowman3.utilities.allocator as allocator
importlib.reload(allocator)

import Snowman3.utilities.transform as transform
importlib.reload(transform)
Transform = transform.Transform

import Snowman3.utilities.nurbsCurve as nurbs_curves
importlib.reload(nurbs_curves)
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
        self.composed_cv_data = allocator.compose_curve_construct_cvs(
            curve_data=self.shape, scale=self.scale, shape_offset=self.shape_offset, up_direction=self.up_direction,
            forward_direction=self.forward_direction)


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


