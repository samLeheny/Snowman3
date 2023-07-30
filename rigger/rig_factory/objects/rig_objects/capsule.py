from Snowman3.rigger.rig_factory.objects.node_objects.transform import Transform
from Snowman3.rigger.rig_factory.objects.base_objects.properties import ObjectProperty
import Snowman3.rigger.rig_factory.environment as env



class Capsule(Transform):

    mesh = ObjectProperty( name='mesh' )
    multiply_node = ObjectProperty( name='multiply_node' )
    poly_cylinder = ObjectProperty( name='poly_cylinder' )

    suffix = 'Caps'


    @classmethod
    def create(cls, **kwargs):
        round_cap = kwargs.pop('round_cap', True)
        subdivs_caps = kwargs.pop('subdivs_caps', 3)
        subdivs_axis = kwargs.pop('subdivs_axis', 8)
        length_plug = kwargs.pop('length_plug', None)

        this = super().create(**kwargs)

        size = this.size
        size_plug = this.create_plug( 'size', at='double', k=True, dv=size )
        size_plug.set_value(size)

        mesh = this.create_child('Mesh')
        mesh.plugs['overrideEnabled'].set_value(True)
        mesh.plugs['overrideDisplayType'].set_value(2)

        poly_cylinder = this.create_child( 'DependNode', node_type='polyCylinder', )
        multiply = this.create_child( 'DependNode', node_type='multiplyDivide', )
        poly_cylinder.plugs['roundCap'].set_value(round_cap)
        poly_cylinder.plugs['subdivisionsCaps'].set_value(subdivs_caps)
        poly_cylinder.plugs['subdivisionsAxis'].set_value(subdivs_axis)
        poly_cylinder.plugs['axis'].set_value(env.aim_vector)
        poly_cylinder.plugs['output'].connect_to(mesh.plugs['inMesh'])

        size_plug.connect_to(multiply.plugs['input1X'])
        multiply.plugs['input2X'].set_value(0.45)
        multiply.plugs['outputX'].connect_to(poly_cylinder.plugs['radius'])

        if length_plug is None:
            # Standard 'capsule' attributes for linking two objects
            position_1_plug = this.create_plug( 'position1', dt='double3', k=True )
            position_2_plug = this.create_plug( 'position2', dt='double3', k=True )
            distance_node = this.create_child( 'DependNode', node_type='distanceBetween' )
            position_1_plug.connect_to(distance_node.plugs['point1'])
            position_2_plug.connect_to(distance_node.plugs['point2'])
            distance_node.plugs['distance'].connect_to(poly_cylinder.plugs['height'])
        else:
            # Option for using a cylinder without linking objects
            length_plug.connect_to(poly_cylinder.plugs['height'])

        this.mesh = mesh
        this.multiply_node = multiply
        this.poly_cylinder = poly_cylinder
        return this
