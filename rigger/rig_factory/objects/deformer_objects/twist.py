from Snowman3.rigger.rig_factory.objects.deformer_objects.nonlinear import NonLinear


class Twist(NonLinear):

    plug_values = dict(
            startAngle=0.0,
            endAngle=0.0,
            lowBound=-1.0,
            highBound=1.0
    )

    handle_type = 'deformTwist'
    deformer_type = 'twist'
    suffix = 'Twist'

    def __init__(self, **kwargs):
        super(Twist, self).__init__(**kwargs)
