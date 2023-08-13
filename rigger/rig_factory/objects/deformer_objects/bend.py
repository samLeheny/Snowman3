from Snowman3.rigger.rig_factory.objects.deformer_objects.nonlinear import NonLinear


class Bend(NonLinear):

    plug_values = dict(
            curvature=0.0,
            highBound=1.0,
            lowBound=-1.0
        )

    handle_type = 'deformBend'
    deformer_type = 'bend'
    suffix = 'Bend'

    def __init__(self, **kwargs):
        super(Bend, self).__init__(**kwargs)
