import copy
import Snowman3.rigger.rig_factory as rig_factory
from Snowman3.rigger.rig_math.matrix import Matrix
from collections import OrderedDict
from Snowman3.rigger.rig_factory.objects.node_objects.transform import Transform
from Snowman3.rigger.rig_factory.objects.node_objects.mesh import Mesh
from Snowman3.rigger.rig_factory.objects.part_objects.base_part import BasePart
from Snowman3.rigger.rig_factory.objects.base_objects.properties import DataProperty, ObjectListProperty, ObjectProperty

blueprint_dict_type = dict  # blueprint_dict_type = JsonDict if os.getenv('PIPE_DEV_MODE') else dict


class PartGuide(BasePart):

    rig_data = DataProperty( name='rig_data' )
    default_settings = dict( root_name='Part' )
    base_handles = ObjectListProperty( name='base_handles' )


    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.toggle_class = Part.__name__


    def after_first_create(self):
        """implement in sub class"""
        return None


    @classmethod
    def pre_process_kwargs(cls, **kwargs):
        kwargs = super().pre_process_kwargs(**kwargs)
        for x in cls.default_settings:
            kwargs.setdefault(x, cls.default_settings[x])
        return kwargs


    @classmethod
    def create(cls, **kwargs):
        this = super().create(**kwargs)
        size = this.size
        size_plug = this.create_plug( 'size', at='double', k=True, dv=size )
        size_plug.set_value(size)
        utility_group = this.create_child( 'Transform', segment_name='Utility' )
        utility_group.plugs['visibility'].set_value(False)
        this.utility_group = utility_group
        return this


    def create_handle(self, **kwargs):
        return self.controller.create_guide_handle(self, **kwargs)


    def get_blueprint(self):
        """
        Compose a dictionary containing blueprint data of part
        """
        blueprint = blueprint_dict_type(
            klass = self.__class__.__name__,
            module = self.__module__,
            root_name = self.root_name,
            side = self.side,
            size = self.size,
            name = self.name,
            base_type = PartGuide.__name__,  # needed by blueprint view
            handle_positions = self.get_handle_positions(),
            handle_vertices = self.get_vertex_data(),
            index_handle_positions = self.get_index_handle_positions()
        )
        data_properties = DataProperty.map.get(self, dict())
        for d in data_properties:
            blueprint[d.name] = data_properties[d]
        blueprint['size'] = self.plugs['size'].get_value(1.0)
        if not blueprint.get('matrices', None):
            blueprint['matrices'] = [list(jnt.get_matrix()) for jnt in self.joints]
        return blueprint


    def get_toggle_blueprint(self):
        blueprint = blueprint_dict_type(
            klass=self.toggle_class,
            module=self.__module__,
        )
        if self.rig_data:
            blueprint['rig_data'] = self.rig_data
        blueprint['guide_blueprint'] = self.get_blueprint()
        blueprint['matrices'] = [list(jnt.get_matrix()) for jnt in self.joints]
        data_properties = DataProperty.map.get(self, dict())
        for d in data_properties:
            blueprint[d.name] = data_properties[d]
        blueprint['size'] = self.plugs['size'].get_value(1.0)
        blueprint['opposing_state_joint_count'] = len(self.joints)
        blueprint['base_type'] = Part.__name__
        return blueprint


    def get_mirror_blueprint(self):
        sides = dict(right='L', left='R')
        if self.side not in sides:
            raise Exception(f'Cannot mirror "{self}" invalid side "{self.side}"')
        blueprint = self.get_blueprint()
        blueprint['side'] = sides[blueprint['side']]
        blueprint.pop('name', None)
        blueprint.pop('pretty_name', None)
        blueprint['disconnected_joints'] = self.disconnected_joints
        mirrored_vertices = dict()
        vertex_data = self.get_vertex_data()
        search_prefix = self.side
        replace_prefix = self.side
        for handle_name in vertex_data:
            mirror_handle_name = handle_name.replace(search_prefix, replace_prefix)
            vertex_pairs = vertex_data[handle_name]
            mirrored_vertex_pairs = []
            if [1] in vertex_pairs or [0] in vertex_pairs:
                vertex_pairs = vertex_pairs[:-3]
            for pair in vertex_pairs:
                mesh_name, index = pair
                if mesh_name in self.controller.named_objects:
                    mesh = self.controller.named_objects[mesh_name]
                    if isinstance(mesh, Mesh):
                        position = self.controller.scene.xform( f'{mesh_name}.vtx[{index}]', q=True, ws=True, t=True )
                        position[0] *= -1.0
                        mirror_index = mesh.get_closest_vertex_index(position)
                        mirrored_vertex_pairs.append((mesh_name, mirror_index))
            mirrored_vertices[mirror_handle_name] = mirrored_vertex_pairs
        blueprint['index_handle_positions'] = [[x[0]*-1.0, x[1], x[2]] for x in self.get_index_handle_positions()]
        blueprint['handle_vertices'] = mirrored_vertices
        return blueprint



class Part(BasePart):

    guide_blueprint = DataProperty( name='guide_blueprint' )
    secondary_handles = ObjectListProperty( name='secondary_handles' )
    joint_group = ObjectProperty( name='joint_group' )
    top_group = ObjectProperty( name='top_group' )  # Get rid of this once all parts are converted to sup part method
    top_deform_joints = ObjectListProperty( name='top_deform_joints' )
    scale_multiply_transform = ObjectProperty( name='scale_multiply_transform' )

    matrices = []
    data_getters = OrderedDict()
    data_setters = OrderedDict()


    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.data_getters = OrderedDict( handle_limits=self.get_handle_limits )
        self.data_setters = OrderedDict( handle_limits=self.set_handle_limits )


    def create_child(self, object_type, *args, **kwargs):
        kwargs.setdefault('parent', self.top_group)  # Get rid of this once all parts are converted to sup part method
        return super().create_child(object_type, *args, **kwargs)


    @classmethod
    def create(cls, **kwargs):
        matrices = copy.deepcopy(kwargs.pop('matrices', []))
        this = super().create(**kwargs)
        this.create_groups(**kwargs)
        this.matrices = [Matrix(*x) for x in matrices]
        this.top_group = this  # Get rid of this once all parts are converted to sup part method
        return this


    def post_create(self, **kwargs):
        super().post_create(**kwargs)
        self.set_vertex_data( kwargs.get( 'handle_vertices', dict() ) )


    def create_groups(self, **kwargs):
        utility_group = self.create_child( Transform, segment_name='Utility' )
        if isinstance(self.hierarchy_parent, Part):  # If this is a sub part, use the parents joint group
            joint_group = self.hierarchy_parent.joint_group
        else:
            joint_group = self.create_child( Transform, segment_name='Joints' )
        scale_multiply_transform = self.create_child( Transform, segment_name='ScaleMultiply' )
        self.controller.create_scale_constraint(self, scale_multiply_transform)
        scale_multiply_transform.plugs['inheritsTransform'].set_value(False)
        utility_group.plugs['visibility'].set_value(False)
        self.utility_group = utility_group
        self.joint_group = joint_group
        self.scale_multiply_transform = scale_multiply_transform


    def create_handle(self, **kwargs):
        return self.controller.create_standard_handle(self, **kwargs)


    def get_handle_positions(self):
        return dict((x.name, list(x.get_matrix())) for x in self.get_handles())


    def set_handle_positions(self, positions):
        handle_map = dict((handle.name, handle) for handle in self.get_handles())
        for handle_name in positions:
            if handle_name in handle_map:
                handle_map[handle_name].set_matrix(Matrix(*positions[handle_name]))
            else:
                raise Exception(f"Handle '{handle_name}' did not exist. Unable to set position")


    def get_blueprint(self):
        blueprint = blueprint_dict_type(
            klass=self.__class__.__name__,
            module=self.__module__,
            root_name=self.root_name,
            side=self.side,
            size=self.size,
            matrices=[list(x) for x in self.matrices],
            guide_blueprint=self.guide_blueprint,
            base_type=Part.__name__,  # needed by blueprint view
        )
        data_properties = DataProperty.map.get(self, dict())
        for x in data_properties:
            blueprint[x.name] = data_properties[x]
        if not self.get_root().use_external_rig_data:
            blueprint['rig_data'] = self.get_rig_data()
        return blueprint


    def get_rig_data(self):
        return dict((x, self.data_getters[x]()) for x in self.data_getters)


    def get_toggle_blueprint(self):
        blueprint = self.guide_blueprint
        if not blueprint:
            raise Exception('No Guide Blueprint found!')
        if not self.get_root().use_external_rig_data:
            blueprint['rig_data'] = self.get_rig_data()
        blueprint['opposing_state_joint_count'] = len(self.joints)
        blueprint['base_type'] = Part.__name__
        return blueprint


    def get_handle_limits(self):
        return dict((x.name, x.get_transform_limits()) for x in self.handles)


    def set_handle_limits(self, handle_limits):
        for handle_name in handle_limits:
            if handle_name in self.controller.named_objects:
                self.controller.named_objects[handle_name].set_transform_limits(handle_limits[handle_name])


    def reset_handle_limits(self):
        for handle in self.handles:
            handle.reset_transform_limits()
