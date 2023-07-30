from Snowman3.rigger.rig_factory.objects.node_objects.depend_node import DependNode
from Snowman3.rigger.rig_factory.utilities.decorators import flatten_args
import logging
logger = logging.getLogger(__name__)


class Deformer(DependNode):

    suffix = 'Def'


    def __init__(self, **kwargs):
        super(Deformer, self).__init__(**kwargs)


    @flatten_args
    def add_geometry(self, *geometry):
        geometry = map(str, geometry)
        clashing_members = [g for g in geometry if g in self.get_members().keys()]
        if clashing_members:
            raise Exception('Specified geometry "%s" were already members of : %s ' % (clashing_members, self.name))
        self.controller.scene.add_deformer_geometry(
            self.name,
            geometry
        )


    @flatten_args
    def remove_geometry(self, *geometry):
        geometry = map(str, geometry)
        members = self.get_members()
        missing_members = [x for x in geometry if x not in members.keys()]
        if missing_members:
            raise Exception(
                '%s did not have the following members.\n\n%s' % (
                    self.name,
                    '\n'.join(missing_members))
                )
        self.controller.scene.remove_deformer_geometry(
            self.name,
            geometry
        )
        logger.info('Removed Geometry:\n%s' % geometry)


    def get_weights(self, precision=None):
        return self.controller.scene.get_deformer_weights(
            self.m_object, precision=precision, skip_if_default_weights=True)


    def set_mesh_weights(self, mesh, weights):
        self.controller.scene.set_deformer_mesh_weights(self.m_object, mesh, weights)


    def get_mesh_weights(self, mesh):
        if mesh not in self.get_members():
            raise Exception('"%s" is not a member of %s' % (mesh, self.name))
        return self.controller.scene.get_deformer_mesh_weights(self.m_object, mesh)


    def set_weights(self, weights):
        self.controller.scene.set_deformer_weights(self.m_object, weights)


    def get_members(self, object_if_all_points=True):
        return self.controller.scene.get_deformer_members(self.m_object, object_if_all_points=object_if_all_points)


    def set_members(self, members):
        self.controller.scene.set_deformer_members(self.m_object, members)


    def add_members(self, members):
        geometry_names = [str(x) for x in self.get_members().keys()]
        for key in members:
            if key in geometry_names:
                raise Exception('%s is already deformed by %s' % (key, self))
            if key not in self.controller.named_objects:
                raise Exception('Unable to find mesh object "%s"' % key)
        self.controller.scene.add_deformer_members(self.m_object, members)
