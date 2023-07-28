import logging
import Snowman3.utilities.common_modules as com
from Snowman3.utilities.objects.node_objects.transform import Transform
from Snowman3.utilities.objects.rig_objects.grouped_handle import GroupedHandle
from Snowman3.utilities.objects.base_objects.properties import DataProperty, ObjectProperty, ObjectListProperty, ObjectDictProperty


class BasePart(Transform):

    pretty_name =               DataProperty( name='pretty_name' )
    disconnected_joints =       DataProperty( name='disconnected_joints', default_value=False )
    color =                     DataProperty( name='color' )
    use_plugins =               DataProperty( name='use_plugins', default_value=False )
    allowed_modes =             DataProperty( name='allowed_modes', default_value=[] )
    part_uuid =                 DataProperty( name='part_uuid' )
    utility_group =             ObjectProperty( name='utility_group' )
    parent_capsule =            ObjectProperty( name='parent_capsule' )
    hierarchy_parent =          ObjectProperty( name='hierarchy_parent' )
    part_owner =                ObjectProperty( name='part_owner' )
    joints =                    ObjectListProperty( name='joints' )
    deform_joints =             ObjectListProperty( name='deform_joints' )
    base_deform_joints =        ObjectListProperty( name='base_deform_joints' )
    handles =                   ObjectListProperty( name='handles' )
    local_translate_out_plugs = ObjectDictProperty( name='local_translate_out_plugs' )
    local_translate_in_plugs =  ObjectDictProperty( name='local_translate_in_plugs' )
    local_matrix_out_plugs =    ObjectDictProperty( name='local_matrix_out_plugs' )
    local_matrix_in_plugs =     ObjectDictProperty( name='local_matrix_in_plugs' )

    suffix = None
    toggle_class = None


    def __init__(self, **kwargs):
        super().__init__(**kwargs)


    def teardown(self):
        com.part_hierarchy.remove_from_hierarchy(self)
        com.part_owners.remove_from_part_members(self)
        super(BasePart, self).teardown()


    def finalize(self):
        pass


    def prepare_for_toggle(self):
        pass


    def set_guide_mode(self, mode):
        pass


    def has_verts(self):
        verts = [handle for handle in self.handles if handle.vertices]
        if verts:
            return verts


    @classmethod
    def create(cls, **kwargs):
        part_owner = kwargs.pop('part_owner', None)
        hierarchy_parent = kwargs.pop('hierarchy_parent', None)
        if part_owner is None:
            raise Exception(f"you must provide an 'owner' keyword argument to create a {cls.__name__}")
        kwargs.setdefault('side', 'center')
        kwargs.setdefault('segment_name', 'Part')
        this = super().create(**kwargs)
        controller = this.controller
        this.layer = controller.current_layer  # layer is needed for part owner. It would be nice if this was set by now
        this.set_part_owner(part_owner)
        if hierarchy_parent:
            this.set_hierarchy_parent(hierarchy_parent)
        this.plugs['overrideEnabled'].set_value(True)
        if this.color is not None:
            this.plugs['overrideRGBColors'].set_value(True)
            this.plugs['overrideColorR'].set_value(this.color[0])
            this.plugs['overrideColorG'].set_value(this.color[1])
            this.plugs['overrideColorB'].set_value(this.color[2])
        return this


    def delete(self):
        name = self.name
        del self
        return com.part_tools.delete_parts(name)


    def set_part_owner(self, part_owner, member_index=None):
        com.part_owners.set_part_owner(self, part_owner, member_index=member_index)


    def set_hierarchy_parent(self, hierarchy_parent, child_index=None):
        com.part_hierarchy.set_hierarchy_parent(self, hierarchy_parent, child_index=child_index)


    def create_nonlinear_deformers(self, **kwargs):
        pass


    def get_handle_positions(self):
        return dict((x.name, x.plugs['translate'].get_value()) for x in self.get_handles())


    def get_index_handle_positions(self):
        return [self.controller.xform(x, q=True, t=True, ws=True) for x in self.get_handles()]


    def set_index_handle_positions(self, positions):
        if self.handles:
            handle_count = len(self.handles)
            for x in range(len(positions)):
                if x < handle_count:
                    self.controller.xform( self.handles[x].get_selection_string(), ws=True, t=positions[x] )


    def get_vertex_data(self):
        """
        Creates A Dictionary with an entry for each handle. Each key is the name of the handle, and each value is a list
        of Tuples two items long. Each tuple represents a vertex, the first item being the mesh name and the second
        item being the vertex index
        :return: dict
        """
        vert_data_dict = {}
        for h in self.handles:
            vert_data_dict[h.name] = [(x.mesh.get_selection_string(), x.index) for x in h.vertices]\
                                     + [h.maintain_offset]\
                                     + [h.offset_Vec]\
                                     + [h.scale_offset]
        return vert_data_dict


    def get_joint_positions(self):
        return dict((x.name, list(x.get_matrix())) for x in self.get_joints())


    def get_joints(self):
        return self.joints


    def get_deform_joints(self):
        return self.deform_joints


    def get_base_deform_joints(self):
        return self.base_deform_joints


    def get_handles(self, include_gimbal_handles=True):
        handles = []
        for h in self.handles:
            handles.append(h)
            if include_gimbal_handles and isinstance(h, GroupedHandle) and h.gimbal_handle:
                handles.append(h.gimbal_handle)
        return handles


    def set_handles(self, handles):
        for handle in handles:
            if handle.owner:
                handle.owner.handles.remove(handle)
            handle.owner = self
        self.handles = handles


    def add_handles(self, *handles):
        for handle in handles:
            if handle.owner:
                handle.owner.handles.remove(handle)
            handle.owner = self
            self.handles.append(handle)
            if isinstance(handle, GroupedHandle) and handle.gimbal_handle:
                handle.gimbal_handle.owner = self


    def set_handle_positions(self, positions):
        handles = self.get_handles()
        if not handles:
            logging.getLogger('rig_build').warning(f"The part '{self.name}' seems to not have any handles.")
        for handle in handles:
            if handle.name in positions:
                handle.plugs['translate'].set_value(positions[handle.name])
                logging.getLogger('rig_build').info(
                    f"Set handle position for {handle.name} to {positions[handle.name]}" )
            else:
                logging.getLogger('rig_build').info(
                    f"Handle name '{handle.name}' not found in : {positions.keys()}" % () )


    def snap_to_mesh(self, mesh):
        self.controller.snap_part_to_mesh(self, mesh)


    def snap_to_selected_mesh(self):
        self.controller.snap_part_to_selected_mesh(self)


    def create_handles(self, count, **kwargs):
        return self.controller.create_handles( self, count, **kwargs )


    def get_root(self):
        if self.part_owner:
            return self.part_owner.get_root()
        else:
            raise Exception(f"No owner. Unable to find root from '{self}'")


    def post_create(self, **kwargs):
        pass


    def finish_create(self, **kwargs):
        pass


    def mirror(self):
        self.controller.mirror_part(self)


    def set_vertex_data(self, vertex_data):
        """
        Snaps handles to vertices based on given vertex_data
        """
        root = self.get_root()
        handle_map = dict((handle.name, handle) for handle in self.get_handles())
        mo = [0]
        differ_vec = []
        scale = 0
        for handle_name in vertex_data:
            if handle_name not in handle_map:
                logging.getLogger('rig_build').warning(
                    'Handle "%s" did not exist. Unable to set vertex_data' % handle_name )
            else:
                vertices = []
                vert_data = vertex_data[handle_name]
                if vert_data:
                    if [1] in vert_data or [0] in vert_data:
                        mo = vert_data[-3]
                        differ_vec = vert_data[-2]
                        scale = vert_data[-1]
                        vert_data = vert_data[:-3]
                    for mesh_name, index in vert_data:
                        if mesh_name in root.geometry:
                            vertex = root.geometry[mesh_name].get_vertex(index)
                            vertices.append(vertex)
                    handle_map[handle_name].snap_to_vertices(vertices, mo=mo[0], differ_vec=differ_vec, scale=scale)


    @classmethod
    def pre_process_kwargs(cls, **kwargs):
        kwargs = super(BasePart, cls).pre_process_kwargs(**kwargs)
        kwargs.pop('name', None)  # Name gets generated procedurally
        kwargs['segment_name'] = 'Part'
        kwargs.pop('name', None)
        return kwargs
