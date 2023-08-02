from Snowman3.rigger.rig_factory.objects.node_objects.depend_node import DependNode
from Snowman3.rigger.rig_factory.objects.node_objects.shading_group import ShadingGroup
from Snowman3.rigger.rig_factory.objects.base_objects.properties import ObjectProperty, ObjectListProperty
import Snowman3.rigger.rig_factory.common_modules as com


class Shader(DependNode):

    shading_group = ObjectProperty(
        name='shading_group'
    )

    geometries = ObjectListProperty(
        name='geometries'
    )
    suffix = 'Shd'

    @classmethod
    def create(cls, **kwargs):
        controller = com.controller_utils.get_controller()
        kwargs['m_object'] = controller.scene.create_shader(kwargs['node_type'])
        this = super(Shader, cls).create(**kwargs)
        shading_group = this.create_child(ShadingGroup)
        this.plugs['outColor'].connect_to(shading_group.plugs['surfaceShader'])
        this.shading_group = shading_group
        shading_group.shaders.append(this)
        return this

    def teardown(self):
        if len(self.shading_group.shaders) < 2:
            self.controller.schedule_objects_for_deletion(self.shading_group)
        super(Shader, self).teardown()

    def add_geometries(self, geometries):
        """
        Assigns self to the given list of geometries.
        :param geometries:
            Objects to assign self too.
        """

        unique_geometries = [x for x in geometries if x not in self.geometries]
        self.controller.scene.sets(
            *(x.get_selection_string() for x in unique_geometries),
            forceElement=self.shading_group.get_selection_string()
        )
        self.geometries.extend(unique_geometries)

    def remove_geometries(self, geometry_names):
        """
        Un-assigns self from given list of geometries.
        :param geometry_names:
            Objects to un-assign self too.
        """

        existing_geometry_names = [x.name for x in self.geometries]
        for geometry_name in geometry_names:
            if not isinstance(geometry_name, str):
                raise Exception(
                    'geometry muust be string, not: %s' % type(geometry_name)
                )
            if geometry_name not in existing_geometry_names:
                raise Exception(
                    'Geometry "%s" was not a member of shader "%s"' % (
                        geometry_name,
                        self.name
                    )
                )
            if geometry_name not in self.controller.named_objects:
                raise Exception(
                    'Geometry "%s" was not found in controller.named_objects for shader "%s"' % (
                        geometry_name,
                        self.name
                    )
                )
        self.controller.scene.sets(
            *geometry_names,
            remove=self.shading_group.get_selection_string()
        )
        for geometry_name in geometry_names:
            self.geometries.remove(self.controller.named_objects[geometry_name])
