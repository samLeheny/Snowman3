import logging
import copy
import traceback
from collections import OrderedDict
import Snowman3.rigger.rig_factory.common_modules as com
import Snowman3.rigger.rig_factory.utilities.decorators as dec
from Snowman3.rigger.rig_factory.objects.base_objects.properties import *
from Snowman3.rigger.rig_factory.objects.base_objects.weak_list import WeakList
from Snowman3.rigger.rig_factory.objects.node_objects.transform import Transform
from Snowman3.rigger.rig_factory.objects.rig_objects.grouped_handle import GroupedHandle


class BaseContainer(Transform):

    rig_lod =                          DataProperty( name='rig_lod', default_value='rig' )
    top_deform_joints =                ObjectListProperty( name='top_deform_joints' )
    shaders =                          ObjectDictProperty( name='shaders' )
    joints =                           ObjectListProperty( name='joints' )
    deform_joints =                    ObjectListProperty( name='deform_joints' )
    base_deform_joints =               ObjectListProperty( name='base_deform_joints' )
    handles =                          ObjectListProperty( name='handles' )
    color =                            DataProperty( name='color' )
    toggle_class =                     DataProperty( name='toggle_class' )
    geometry_group =                   ObjectProperty( name='geometry_group' )
    root_geometry_group =              ObjectProperty( name='root_geometry_group' )
    low_geometry_group =               ObjectProperty( name='low_geometry_group' )
    utility_geometry_group =           ObjectProperty( name='utility_geometry_group' )
    export_data_group =                ObjectProperty( name='export_data_group' )
    placement_group =                  ObjectProperty( name='placement_group' )
    bifrost_group =                    ObjectProperty( name='bifrost_group' )
    utility_geometry_paths =           DataProperty( name='utility_geometry_paths', default_value=[] )
    low_geometry_paths =               DataProperty( name='low_geometry_paths', default_value=[] )
    geometry_paths =                   DataProperty( name='geometry_paths', default_value=[] )
    import_placement_path =            DataProperty( name='import_placement_path', default_value=True )
    import_bifrost_path =              DataProperty( name='import_bifrost_path', default_value=True )
    anim_textures_date =               DataProperty( name='anim_textures_date' )
    standin_group =                    DataProperty( name='standin_group', default_value=[] )
    geometry =                         ObjectDictProperty( name='geometry' )
    origin_geometry =                  ObjectDictProperty( name='origin_geometry' )
    low_geometry =                     ObjectDictProperty( name='low_geometry' )
    utility_geometry =                 ObjectDictProperty( name='utility_geometry' )
    deformers =                        ObjectListProperty( name='deformers' )  # Is this being used?  Delete if not...
    disconnected_joints =              DataProperty( name='disconnected_joints', default_value=False )
    expanded_handles =                 ObjectListProperty( name='expanded_handles' )
    visible_plugs =                    ObjectListProperty( name='visible_plugs' )
    unlocked_plugs =                   ObjectListProperty( name='unlocked_plugs' )
    keyable_plugs =                    ObjectListProperty( name='keyable_plugs' )
    control_group =                    ObjectProperty( name='control_group' )
    joint_group =                      ObjectProperty( name='joint_group' )
    origin_geometry_group =            ObjectProperty( name='origin_geometry_group' )
    origin_geometry_data =             DataProperty( name='origin_geometry_data', default_value=dict() )
    # Delete on any publish (may later be replaced by delete_on_finalize_data)
    delete_geometry_names =            DataProperty( name='delete_geometry_names', default_value=[] )
    # Delete only for specified publish types. Doesn't have to be geometry.
    delete_on_finalize_data =          DataProperty( name='delete_on_finalize_data' )
    realtime_geometry_names =          DataProperty( name='realtime_geometry_names', default_value=[] )
    poly_reduce_data =                 DataProperty( name='poly_reduce_data', default_value=dict() )
    metadata =                         DataProperty( name='metadata', default_value=dict() )
    custom_plugs =                     ObjectListProperty( name='custom_plugs' )
    smooth_mesh_normals =              DataProperty( name='smooth_mesh_normals', default_value=False )
    deform_group =                     ObjectProperty( name='deform_group' )
    origin_deform_group =              ObjectProperty( name='origin_deform_group' )
    deleted_parent_entity_part_names = DataProperty( name='deleted_parent_entity_part_names', default_value=[] )
    local_translate_out_plugs =        ObjectDictProperty( name='local_translate_out_plugs' )
    local_translate_in_plugs =         ObjectDictProperty( name='local_translate_in_plugs' )
    local_matrix_out_plugs =           ObjectDictProperty( name='local_matrix_out_plugs' )
    local_matrix_in_plugs =            ObjectDictProperty( name='local_matrix_in_plugs' )
    product_paths =                    DataProperty( name='product_paths', default_value={} )
    use_external_rig_data =            DataProperty( name='use_external_rig_data', default_value=False )
    use_manual_rig_data =              DataProperty( name='use_manual_rig_data', default_value=False )
    auto_rigged =                      DataProperty( name='auto_rigged', default_value=False )
    disable_shard_baking =             DataProperty( name='disable_shard_baking', default_value=False )
    hierarchy_parent =                 ObjectProperty( name='hierarchy_parent' )  # OwnerView Parent
    # OwnerView children
    hierarchy_children =               ObjectListProperty( name='hierarchy_children', default_value=[] )
    part_owner =                       ObjectProperty( name='part_owner' )  # PartView parent
    part_members =                     ObjectListProperty( name='part_members', default_value=[] )  # PartView children
    pre_delete_handle_shapes =         DataProperty( name='pre_delete_handle_shapes', default_value=True )
    deformation_layers =               DataProperty( name='deformation_layers', default_value={} )
    deformation_stacks =               ObjectDictProperty( name='deformation_stack' )
    part_uuid =                        DataProperty( name='part_uuid' )
    default_settings = dict( parent_namespace=False )
    suffix = None
    unlockable_node_types = ['nucleus', 'hairSystem', 'nCloth', 'nRigid', 'follicle']
    entities_data = None  # Allows for initialisation in init. Stores blueprints of parent entities for reference


    def __init__(self, **kwargs):
        self.entities_data = OrderedDict()
        self.delete_on_finalize_data = dict()  # Ensures no reuse of the same dict across multiple instances
        super(BaseContainer, self).__init__(**kwargs)


    def set_guide_mode(self, mode):
        for part in self.get_parts():
            part.set_guide_mode(mode)


    @dec.flatten_args
    def add_plugs(self, *plugs, **kwargs):
        """
        by default all attributes get locked and hidden in framework at publish time.
        we need to let framework know we about the attributes we want unlocked and visible.
        to do so we use add_plugs(). eg: root.add_plugs(some_plug_object)

        :param plugs: framework object plugs we want to be visibile and/or unlocked
        :type plugs: list of framework plugs
        :param kwargs: we can set state of plugs using keyable, unlocked or visible arguments
        :return: N/A
        """
        keyable = kwargs.get('keyable', True)
        unlocked = kwargs.get('unlocked', True)
        visible = kwargs.get('visible', True)
        for plug in plugs:
            if isinstance(plug, str):
                if '.' not in plug:
                    raise Exception('Invalid plug : %s' % plug)
                node_name, plug_name = plug.split('.')
                if not self.controller.scene.objExists(node_name):
                    raise Exception('The node "%s" dones not exist' % node_name)
                if node_name not in self.controller.named_objects:
                    raise Exception('Node not found: %s' % node_name)
                node = self.controller.named_objects[node_name]
                if not node:
                    raise Exception('The node is not registered with the rig controller : %s' % node_name)
                plug = node.plugs[plug_name]

            if keyable:
                self.keyable_plugs.append(plug)
            if unlocked:
                self.unlocked_plugs.append(plug)
            if visible:
                self.visible_plugs.append(plug)
            node = plug.get_node()
            if isinstance(node, GroupedHandle) and node.groups:

                # unlock Cns Transform
                if self.controller.scene.objExists('%s.%s' % (node.groups[-1].name, plug.root_name)):
                    cns_plug = node.groups[-1].plugs[plug.root_name]
                    if keyable:
                        self.keyable_plugs.append(cns_plug)
                    if unlocked:
                        self.unlocked_plugs.append(cns_plug)
                    if visible:
                        self.visible_plugs.append(cns_plug)

                # unlock Cfx Transform
                if node.cfx:
                    if self.controller.scene.objExists('%s.%s' % (node.cfx, plug.root_name)):
                        cfx_plug = node.cfx.plugs[plug.root_name]
                        if keyable:
                            self.keyable_plugs.append(cfx_plug)
                        if unlocked:
                            self.unlocked_plugs.append(cfx_plug)
                        if visible:
                            self.visible_plugs.append(cfx_plug)

                # unlock gimbal controls
                if node.gimbal_handle:
                    if self.controller.scene.objExists('%s.%s' % (node.gimbal_handle.name, plug.root_name)):
                        gimbal_plug = node.gimbal_handle.plugs[plug.root_name]
                        if keyable:
                            self.keyable_plugs.append(gimbal_plug)
                        if unlocked:
                            self.unlocked_plugs.append(gimbal_plug)
                        if visible:
                            self.visible_plugs.append(gimbal_plug)


    def teardown(self):
        if self != self.get_root():
            com.part_hierarchy.remove_from_hierarchy(self)
            com.part_owners.remove_from_part_members(self)
        if self.shaders:
            self.controller.schedule_objects_for_deletion(self.shaders.values())
        super(BaseContainer, self).teardown()


    @classmethod
    def create(cls, **kwargs):
        part_owner = kwargs.pop('part_owner', None)
        hierarchy_parent = kwargs.pop('hierarchy_parent', None)
        this = super(BaseContainer, cls).create(**kwargs)

        controller = this.controller
        this.layer = controller.current_layer  # layer is needed for part owner. It would be nice if thi was set by now
        if part_owner:
            this.set_part_owner(part_owner)
        if hierarchy_parent:
            this.set_hierarchy_parent(hierarchy_parent)
        this.deform_group = this
        this.plugs['overrideEnabled'].set_value(False)
        uuid_plug = this.create_plug(
            'serializationId',
            dt='string',
            keyable=False
        )
        uuid_plug.set_channel_box(True)
        uuid_plug.set_locked(True)
        return this


    def set_part_owner(self, part_owner, member_index=None):
        com.part_owners.set_part_owner(
            self,
            part_owner,
            member_index=member_index
        )


    def set_hierarchy_parent(self, hierarchy_parent, child_index=None):
        com.part_hierarchy.set_hierarchy_parent(
            self,
            hierarchy_parent,
            child_index=child_index
        )


    def finalize(self):
        if self.geometry_group:
            for plug_name in self.product_paths:
                path = self.product_paths[plug_name]
                if not self.geometry_group.plugs.exists(plug_name):
                    self.geometry_group.create_plug(plug_name, dt='string')
                if path:
                    self.geometry_group.plugs[plug_name].set_value(path)

            path_dict = {
                'geometry_paths': self.geometry_paths,
                'utility_geometry_path': self.utility_geometry_paths,
                'low_geometry_path': self.low_geometry_paths
            }
            for plug_name in path_dict:
                path_list = path_dict[plug_name]
                if not self.geometry_group.plugs.exists(plug_name):
                    self.geometry_group.create_plug(plug_name, dt='string')
                if path_list:
                    self.geometry_group.plugs[plug_name].set_value(str(path_list))


    def create_part(self, klass, **kwargs):
        return com.part_tools.create_part(self, klass, **kwargs)


    def get_origin_geo_data(self):
        ogd = self.origin_geometry_data
        return dict((x, ogd[x]) for x in ogd if x in self.geometry and self.geometry[x].layer is None)


    def post_create(self, **kwargs):
        pass


    def create_groups(self):
        pass


    ## Commented out as assumed Obsolete - but could be used externally somewhere?
    # def get_deformer_data(self, precision=None):
    #     return self.controller.get_deformer_data(self, precision=precision)

    def create_shaders(self):
        self.controller.create_rig_shaders(self)


    def get_joints(self):
        joints = WeakList(self.joints)
        for part in self.get_parts():
            joints.extend(part.joints)
        return joints


    def get_deform_joints(self):
        deform_joints = WeakList(self.deform_joints)
        for part in self.get_parts():
            deform_joints.extend(part.deform_joints)
        return deform_joints


    def get_base_deform_joints(self):
        deform_joints = WeakList(self.base_deform_joints)
        for part in self.get_parts():
            deform_joints.extend(part.base_deform_joints)
        return deform_joints


    def snap_to_selected_mesh(self):
        self.controller.snap_part_to_selected_mesh(self)


    def get_handles(self, include_gimbal_handles=True):
        handles = []
        for h in self.handles:
            handles.append(h)
            if include_gimbal_handles and isinstance(h, GroupedHandle) and h.gimbal_handle:
                handles.append(h.gimbal_handle)
        for sub_part in self.get_parts(recursive=False):
            handles.extend(sub_part.get_handles(include_gimbal_handles=include_gimbal_handles))
        return handles


    def get_joint_positions(self):
        return dict((x.name, list(x.get_matrix())) for x in self.get_joints())


    def get_handle_positions(self):
        return dict((x.name, list(x.plugs['translate'].get_value())) for x in self.get_handles())


    def set_handle_positions(self, positions, skip_handles_with_vertices=False):
        handle_map = dict((handle.name, handle) for handle in self.get_handles())
        for handle_name in positions:
            if handle_name in handle_map:
                position = positions[handle_name]
                handle = handle_map[handle_name]
                if skip_handles_with_vertices and handle.vertices:
                    logging.getLogger('rig_build').info(
                        'The handle "%s" had a vertex association. skipping set position.' % handle
                    )
                else:
                    # self.controller.scene.xform(handle_name, ws=True, t=position)
                    handle.plugs['translate'].set_value(position)


    def get_handle_mesh_positions(self):
        return self.controller.get_handle_mesh_positions(self)


    def set_handle_mesh_positions(self, positions):
        self.controller.set_handle_mesh_positions(self, positions)


    def snap_handles_to_mesh_positons(self):
        self.controller.snap_handles_to_mesh_positons(self)


    def get_parts(
            self,
            include_self=False,
            recursive=True
    ):
        parts = []
        if include_self:
            parts.append(self)
        for child_part in self.part_members:
            parts.append(child_part)
            if recursive:
                if isinstance(child_part, BaseContainer):
                    parts.extend(child_part.get_parts())
        return parts


    def find_first_part(self, *types, **kwargs):
        side = kwargs.get('side', 'any')
        root_name = kwargs.get('root_name', 'any')
        differentiation_name = kwargs.get('differentiation_name', 'any')
        layer = kwargs.get('layer', 'any')
        for part in self.get_parts():
            if not types or isinstance(part, types):
                if side == 'any' or part.side == side:
                    if str(root_name) == 'any' or str(part.root_name) == root_name:
                        if str(differentiation_name) == 'any' or str(part.differentiation_name) == differentiation_name:
                            if str(layer) == 'any' or part.layer == str(layer):
                                return part


    def find_parts(self, *types, **kwargs):
        side = kwargs.get('side', 'any')
        root_name = kwargs.get('root_name', 'any')
        differentiation_name = kwargs.get('differentiation_name', 'any')
        layer = kwargs.get('layer', 'any')
        parts = []
        for part in self.get_parts():
            if not types or isinstance(part, types):
                if side == 'any' or part.side == side:
                    if root_name == 'any' or part.root_name == root_name:
                        if differentiation_name == 'any' or part.differentiation_name == differentiation_name:
                            if layer == 'any' or part.layer == layer:
                                parts.append(part)

        if kwargs.get('sorted', False):
            return sorted(list(set(parts)), key=lambda x: x.name)

        return list(set(parts))


    def get_root(self):
        if self.part_owner:
            return self.part_owner.get_root()
        return self


    def lock_nodes(self):
        self.controller.lock_node(*self.get_descendants(), lock=True, ic=True)


    def unlock_nodes(self):
        self.controller.lock_node(*self.get_descendants(), lock=False)


    def bind_geometry(self, geometry):
        return self.controller.bind_rig_geometry(self, geometry)


    def get_skin_cluster_data(self):
        return self.controller.get_skin_cluster_data(self)


    def get_deformer_stack_data(self):
        return self.controller.get_deformer_stack_data(self)


    def set_skin_cluster_data(self, data):
        return self.controller.set_skin_cluster_data(self, data)


    def set_deformer_stack_data(self, data):
        return self.controller.set_deformer_stack_data(self, data)


    def set_delta_mush_data(self, data):
        if data:
            self.controller.set_delta_mush_data(self, data)


    def get_delta_mush_data(self, precision=None):
        return self.controller.get_delta_mush_data(self, precision=precision)


    def build_delta_mush(self, data):
        logger = logging.getLogger('rig_build')
        if data:
            try:
                self.set_delta_mush_data(data)
            except Exception as e:
                logger.error(traceback.format_exc())


    def get_wrap_data(self):
        return self.controller.get_wrap_data(self)


    def set_wrap_data(self, data):
        if data:
            self.controller.set_wrap_data(self, data)


    def get_cvwrap_data(self):
        return self.controller.get_cvwrap_data(self)


    def set_cvwrap_data(self, data):
        if data:
            self.controller.set_cvwrap_data(self, data)


    def set_transform_axis_visibility(self, value):
        for item in self.get_descendants():
            if isinstance(item, Transform):
                item.plugs['displayLocalAxis'].set_value(value)


    def create_nonlinear_deformers(self, **kwargs):
        pass


    def prepare_for_toggle(self):
        for part in self.get_parts(recursive=False):
            part.prepare_for_toggle()


    def finish_create(self, **kwargs):
        pass


    def get_delete_geometry_names(self, name=None, include_parent_entities=False):
        """
        Gets data on whether geo should be deleted or not on finalize, based only on legacy-type (overall) delete tags
        """
        delete_geometry_names = set(self.delete_geometry_names)
        if include_parent_entities:
            if self.entities_data:
                parent_blueprints = [entity_data['rig_blueprint'] for entity_data in self.entities_data.values()[1:]]
                for entity_blueprint in parent_blueprints:
                    entity_delete_data = entity_blueprint.get('delete_geometry_names', {})
                    delete_geometry_names.update(entity_delete_data)

        if name:
            return name in delete_geometry_names or None
        return delete_geometry_names


    def geo_will_delete_by_default(self, transform_name):
        """
        Convenience check, for consistency and later extension
        Currently, this is only if the geo contains the string '_Util_',
        but could also eg. delete anim geo for non-anim rigs, if a publish_type arg was added

        Shouldn't delete groups.

        returns True/False
        """
        return transform_name.endswith('_Geo') and '_Util_' in transform_name


    def get_delete_on_finalize_data(self, name=None, publish_type=None, default_data=False, parent_data=False):
        """
        Gets data on whether geo should be deleted or not on finalize, according to the requested data type
        (default value, parent asset overrides, or current asset overrides)
        Leaves merging these sources up to the UI or finalise function, to allow for displaying the difference.

        If name is not specified, all data is returned, for the given publish type;
        If publish_type is not specified, all data is returned;

        Returns, per geo if name not given:
            None if no override is set (geo not deleted if no source saying otherwise)
            False if overridden to be kept
            True if overridden to be deleted

        Parent data overrides default;
        Current asset data overrides parent.
        """
        if default_data:
            # Return whether the given geo would be deleted by default, if no parent or current asset overrides
            # Currently, this is only if the geo contains the string '_Util_'
            if name:
                return self.geo_will_delete_by_default(name) or None

            delete_names = []
            for geo_name, geo in self.controller.root.geometry.iteritems():
                name = geo.parent.name  # geo is shape, but geometry view uses transforms
                if self.geo_will_delete_by_default(name):
                    delete_names.append(name)

            # Currently no publish_type specific auto-delete logic, so return as if publish_type was given,
            # ie. a list rather than a dict of default_delete_data[name][each_publish_type] = True
            return delete_names

        if parent_data:
            if not self.entities_data:
                return None

            parent_blueprints = [entity_data['rig_blueprint'] for entity_data in self.entities_data.values()[1:]]
            if not parent_blueprints:
                return None

            parent_delete_data = {}
            for entity_blueprint in reversed(parent_blueprints):
                # From grandparent down,
                entity_delete_data = entity_blueprint.get('delete_on_finalize_data', {})
                if not parent_delete_data:
                    parent_delete_data = copy.deepcopy(entity_delete_data)
                else:
                    # Replace grandparent values with parent values where not None values
                    # (Could probably be optimised)
                    for each_name, data in entity_delete_data.iteritems():
                        if each_name in parent_delete_data:
                            for each_publish_type, new_value in data.iteritems():
                                if new_value is not None:
                                    parent_delete_data[each_name][each_publish_type] = new_value
                        else:
                            parent_delete_data[each_name] = copy.copy(data)
            delete_data = parent_delete_data
        else:
            delete_data = self.delete_on_finalize_data or {}

        if name:
            if name in delete_data:
                if publish_type:
                    # Return whether this object has the given delete tag type
                    return delete_data[name].get(publish_type, None)
                else:
                    # Return the dict of delete tags for the object
                    return delete_data[name]
            # Object has no delete tags
            return None

        if publish_type:
            # Return list of all names tagged for the given deletion type
            return [each_name for each_name, data in delete_data.iteritems() if data.get(publish_type, None)]

        return delete_data


    def set_delete_on_finalize_data(self, names, publish_type, value):
        # Cleanup existing list (removing non-existent names, initialise from None)
        delete_data = self.get_delete_on_finalize_data()

        for name in names:
            if value is None:  # Ie. revert to default - which is visible or parent value  ## optimise
                # Remove value from data, for given type
                data = delete_data.get(name, {})
                if data and publish_type in data:
                    if len(data) == 1:
                        # This type was the only tag; remove the name altogether
                        del delete_data[name]
                    else:
                        # Remove tag for given type
                        del delete_data[name][publish_type]
            else:
                # Add or Edit value
                if name in delete_data:
                    delete_data[name][publish_type] = value  # Merging with existing data for other types
                else:
                    delete_data[name] = {publish_type: value}

        self.delete_on_finalize_data = delete_data


def get_parts_from_joint(joints):
    child_parts = WeakList()
    for joint in joints:
        child_parts.extend(joint.child_parts)
        for child_part in joint.child_parts:
            if isinstance(child_part, BaseContainer):
                child_parts.extend(child_part.get_parts())
            child_parts.extend(get_parts_from_joint(child_part.joints))
    return child_parts
