from Snowman3.rigger.rig_factory.objects.node_objects.transform import Transform
from Snowman3.rigger.rig_factory.objects.node_objects.dag_node import DagNode
from Snowman3.rigger.rig_factory.objects.node_objects.depend_node import DependNode
from Snowman3.rigger.rig_factory.objects.node_objects.mesh import Mesh
from Snowman3.rigger.rig_factory.objects.base_objects.properties import ObjectProperty, DataProperty
from Snowman3.rigger.rig_factory.objects.node_objects.nurbs_surface import NurbsSurface


class SurfacePoint(Transform):

    surface = ObjectProperty( name='surface' )
    follicle = ObjectProperty( name='follicle' )
    use_plugin = DataProperty( name='use_plugin', default_value=False )
    local = DataProperty( name='local', default_value=False )
    suffix = 'Spt'

    def __init__(self, **kwargs):
        super(SurfacePoint, self).__init__(**kwargs)

    @classmethod
    def create(cls, **kwargs):
        this = super(SurfacePoint, cls).create(**kwargs)
        use_plugin = this.use_plugin
        surface = this.surface
        if surface is not None:
            if not isinstance(surface, (NurbsSurface, Mesh)):
                raise Exception('Expected a NurbsSurface or Mesh. Got : {0}'.format(type(surface)))

        if not use_plugin:
            follicle = this.create_child(
                DagNode,
                node_type='follicle'
            )
            if surface:
                if isinstance(surface, NurbsSurface):
                    surface.plugs['local'].connect_to(follicle.plugs['inputSurface'])
                elif isinstance(surface, Mesh):
                    surface.plugs['outMesh'].connect_to(follicle.plugs['inputMesh'])
                if not this.local:
                    surface.plugs['worldMatrix'].element(0).connect_to(follicle.plugs['inputWorldMatrix'])
            follicle.plugs['outRotate'].connect_to(this.plugs['rotate'])
            follicle.plugs['outTranslate'].connect_to(this.plugs['translate'])
            follicle.plugs['visibility'].set_value(False)
            if not this.local:
                this.plugs['inheritsTransform'].set_value(False)
        else:
            follicle = this.create_child(
                DependNode,
                node_type='rigFollicle'
            )
            if surface:
                surface.plugs['worldSpace'].element(0).connect_to(follicle.plugs['inSurface'])
            follicle.plugs['outTranslate'].connect_to(this.plugs['translate'])
            follicle.plugs['outRotate'].connect_to(this.plugs['rotate'])

        this.follicle = follicle
        return this
