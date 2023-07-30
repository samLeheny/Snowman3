from Snowman3.rigger.rig_factory.objects.node_objects.transform import Transform
from Snowman3.rigger.rig_factory.objects.node_objects.depend_node import DependNode
from Snowman3.rigger.rig_math.matrix import Matrix
from Snowman3.rigger.rig_factory.objects.base_objects.properties import ObjectProperty
import Snowman3.rigger.rig_factory.environment as env



class Cone(Transform):

    mesh = ObjectProperty( name='mesh' )
    poly_cone = ObjectProperty( name='poly_cone' )


    @classmethod
    def create(cls, **kwargs):
        height = kwargs.pop('height', 1.0)
        axis = kwargs.pop('axis', env.up_vector)
        rounded = kwargs.pop('rounded', True)
        this = super().create(**kwargs)
        size = this.size

        size_plug = this.create_plug( 'size', at='double', k=True, dv=size )
        matrix_plug = this.create_plug( 'shapeMatrix', at='matrix' )
        cone_node = this.create_child( DependNode, node_type='polyCone' )
        mesh = this.create_child('Mesh')
        cone_node.plugs.set_values( subdivisionsAxis=10, axis=axis, roundCap=rounded, subdivisionsCap=3 )

        transform_geometry = this.create_child( DependNode, node_type='transformGeometry' )
        cone_node.plugs['height'].set_value(0.5)
        cone_node.plugs['radius'].set_value(0.1)
        cone_node.plugs['output'].connect_to(transform_geometry.plugs['inputGeometry'])
        transform_geometry.plugs['outputGeometry'].connect_to(mesh.plugs['inMesh'])
        matrix_plug.connect_to(transform_geometry.plugs['transform'])
        shape_matrix = Matrix()
        shape_matrix.set_translation([x*0.25 for x in axis])
        matrix_plug.set_value(list(shape_matrix))
        for x in ('X', 'Y', 'Z'):
            size_plug.connect_to(this.plugs[f'scale{x}'])
        this.plugs['overrideEnabled'].set_value(True)
        this.plugs['overrideRGBColors'].set_value(1)
        this.plugs['overrideColorRGB'].set_value(env.colors['highlight'])
        this.mesh = mesh
        this.poly_cone = cone_node
        return this
