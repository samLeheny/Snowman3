from Snowman3.rigger.rig_factory.objects.deformer_objects.deformer import Deformer
from Snowman3.rigger.rig_factory.objects.base_objects.properties import ObjectProperty


class Wire(Deformer):

    base_wire = ObjectProperty( name='wire' )
    base_wire_shape = ObjectProperty( name='wire_shape' )
    suffix = 'Wire'

    def __init__(self, **kwargs):
        super(Wire, self).__init__(**kwargs)
        self.node_type = 'wire'

    def get_weights(self, precision=None):
        return self.controller.get_deformer_weights(
            self, precision=precision, skip_if_default_weights=True)

    def set_weights(self, weights):
        self.controller.set_deformer_weights(self, weights)

    def add_geometry(self, geometry):
        self.deformer_set.members.extend(geometry)
        self.controller.add_deformer_geometry(self, geometry)
