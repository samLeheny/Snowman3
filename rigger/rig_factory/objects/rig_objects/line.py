from Snowman3.rigger.rig_factory.objects.node_objects.transform import Transform
from Snowman3.rigger.rig_factory.objects.node_objects.nurbs_curve import NurbsCurve
from Snowman3.rigger.rig_factory.objects.base_objects.properties import ObjectProperty


class Line(Transform):

    curve = ObjectProperty( name='curve' )

    @classmethod
    def create(cls, **kwargs):
        this = super().create(**kwargs)
        curve = this.create_child( NurbsCurve, degree=1, positions=[ [0.0, 0.0, 0.0], [0.0, 1.0, 0.0] ] )
        curve.plugs['overrideDisplayType'].set_value(1)
        curve.plugs['overrideEnabled'].set_value(True)

        curve.plugs.set_values( overrideDisplayType=1, overrideEnabled=True )
        this.plugs['inheritsTransform'].set_value(False)
        this.curve = curve
        return this
