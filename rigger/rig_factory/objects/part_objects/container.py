import os
import copy
import functools
import logging
import traceback
import Snowman3.rigger.rig_factory.environment as env
import Snowman3.rigger.rig_factory.common_modules as cmt
import Snowman3.rigger.rig_factory.utilities.deformer_utilities as dtl
import Snowman3.rigger.rig_factory.utilities.space_switcher_utilities as spu
from Snowman3.rigger.rig_factory.objects.base_objects.json_dict import JsonDict
from Snowman3.rigger.rig_factory.objects.base_objects.weak_list import WeakList
from Snowman3.rigger.rig_factory.objects.node_objects.transform import Transform
from Snowman3.rigger.rig_factory.objects.sdk_objects.sdk_network import SDKNetwork
from Snowman3.rigger.rig_factory.objects.base_objects.properties import ObjectProperty
from Snowman3.rigger.rig_factory.objects.rig_objects.grouped_handle import GroupedHandle
from Snowman3.rigger.rig_factory.objects.part_objects.base_container import BaseContainer
import Snowman3.rigger.rig_factory.utilities.sdk_utilities.sdk_blueprint_utilities as sbl
#import Snowman3.rigger.rig_factory.build.tasks.task_utilities.legacy_blueprint_utilities as lbu
from Snowman3.rigger.rig_factory.objects.base_objects.properties import DataProperty, ObjectListProperty,\
    ObjectDictProperty

dev_mode = os.getenv('PIPE_DEV_MODE') == 'TRUE'
blueprint_dict_type = JsonDict if dev_mode else dict



class ContainerGuide(BaseContainer):

    # Rig state data (such as skin clusters etc.) gets stored here while in guide state
    rig_data = DataProperty( name='rig_data', default_value=dict() )
    utilities_group = ObjectProperty( name='utilities_group' )
    # This MAY no longer be used.. Need to run tests and check
    base_handles = ObjectListProperty( name='base_handles' )
    # Must be None to retain backwards compatibility
    custom_handles = DataProperty( name='custom_handles', default_value=None )
    # Rigs/Blueprints can specify versions of parts to be used here.
    module_versions = DataProperty( name='module_versions', default_value=dict() )
    dynamics_group = ObjectProperty( name='dynamics_group' )
    parts_by_uuid = ObjectDictProperty( name='parts_by_uuid' )

    toggle_class = None


    def __init__(self, **kwargs):
        super(ContainerGuide, self).__init__(**kwargs)
        self.toggle_class = Container.__name__


    @classmethod
    def create(cls, **kwargs):
        this = super(ContainerGuide, cls).create(**kwargs)
        this.plugs['inheritsTransform'].set_value(False)
        this.create_shaders()

        this.control_group = this.create_child( Transform, segment_name="Control" )
        this.joint_group = this.create_child( Transform, segment_name="Joint" )
        this.root_geometry_group = this.create_child( Transform, segment_name="RootGeometry" )
        this.utilities_group = this.create_child( Transform, segment_name='Utilities' )
        this.geometry_group = this.root_geometry_group.create_child( Transform, segment_name="Geometry" )
        this.utility_geometry_group = this.root_geometry_group.create_child( Transform, segment_name="UtilityGeometry" )
        this.low_geometry_group = this.root_geometry_group.create_child( Transform, segment_name='LowGeometry' )
        this.origin_geometry_group = this.utility_geometry_group.create_child( Transform,
                                                                               segment_name="OriginGeometry" )
        this.dynamics_group = this.create_child( Transform, segment_name="Dynamics" )

        this.plugs['overrideEnabled'].set_value(True)
        this.plugs['overrideRGBColors'].set_value(1)
        this.plugs['overrideColorRGB'].set_value([0.2, 0.2, 0.2])
        this.plugs['translate'].set_locked(True)
        this.plugs['rotate'].set_locked(True)
        this.plugs['scale'].set_locked(True)
        if this.part_uuid:
            root = this.get_root()
            if this.part_uuid in root.parts_by_uuid:
                raise Exception('The part uuid was already used.')
            root.parts_by_uuid[this.part_uuid] = this
        return this


    def create_handle(self, **kwargs):
        return self.controller.create_guide_handle(self, **kwargs)


    def get_blueprint(self):
        blueprint = blueprint_dict_type(
            base_type='Container',  # needed by blueprint view,
            klass=self.__class__.__name__,
            module=self.__module__,
            root_name=self.root_name,
            side=self.side,
            size=self.size,
            rig_data=self.rig_data,
            geometry_paths=process_paths(env.local_build_directory, self.geometry_paths),
            utility_geometry_paths=process_paths(env.local_build_directory, self.utility_geometry_paths),
            low_geometry_paths=process_paths(env.local_build_directory, self.low_geometry_paths),
            anim_textures_date=self.anim_textures_date,
            hierarchy_data=cmt.part_hierarchy.get_hierarchy_data(),
            origin_geometry_data=self.get_origin_geo_data(),
            delete_geometry_names=self.delete_geometry_names,
            custom_handles=self.custom_handles,
            use_external_rig_data=self.use_external_rig_data,
            disable_shard_baking=self.disable_shard_baking,
            pre_delete_handle_shapes=self.pre_delete_handle_shapes
        )

        data_properties = DataProperty.map.get(self, dict())
        for x in data_properties:
            blueprint[x.name] = data_properties[x]
        return blueprint


    def get_toggle_blueprint(self):
        guide_blueprint = self.get_blueprint()
        guide_blueprint.pop('rig_data', None)
        blueprint = blueprint_dict_type(
            base_type='ContainerGuide',
            klass=self.toggle_class,
            module=self.__module__,
            root_name=self.root_name,
            side=self.side,
            size=self.size,
            smooth_mesh_normals=self.smooth_mesh_normals,
            geometry_paths=process_paths(env.local_build_directory, self.geometry_paths),
            utility_geometry_paths=process_paths(env.local_build_directory, self.utility_geometry_paths),
            low_geometry_paths=process_paths(env.local_build_directory, self.low_geometry_paths),
            anim_textures_date=self.anim_textures_date,
            hierarchy_data=cmt.part_hierarchy.get_hierarchy_data(),
            guide_blueprint=guide_blueprint,
            origin_geometry_data=self.get_origin_geo_data(),
            delete_geometry_names=self.delete_geometry_names,
            realtime_geometry_names=self.realtime_geometry_names,
            use_external_rig_data=self.use_external_rig_data,
            guide_part_joint_count_data=dict((x.name, len(x.joints)) for x in self.get_parts())
        )

        blueprint['base_type'] = Container.__name__
        if self.custom_handles is not None:
            blueprint['custom_handles'] = self.custom_handles
        data_properties = DataProperty.map.get(self, dict())
        for x in data_properties:
            blueprint[x.name] = data_properties[x]
        if self.rig_data and not self.use_external_rig_data:
            blueprint['rig_data'] = copy.deepcopy(self.rig_data)
        return blueprint


    def get_mirror_blueprint(self):
        return self.get_blueprint()


    def post_create(self, **kwargs):
        for plug in self.visible_plugs:
            plug.set_channel_box(True)
        for plug in self.unlocked_plugs:
            plug.set_locked(False)
        for plug in self.keyable_plugs:
            plug.set_keyable(True)


    def get_base_handles(self):
        base_handles = WeakList(self.base_handles)
        for sub_part in self.get_parts(recursive=False):
            if isinstance(sub_part, ContainerGuide):
                base_handles.extend(sub_part.get_base_handles())
            else:
                base_handles.extend(sub_part.base_handles)
        return base_handles


    @classmethod
    def pre_process_kwargs(cls, **kwargs):
        kwargs = super(BaseContainer, cls).pre_process_kwargs(**kwargs)
        kwargs['segment_name'] = 'Container'
        kwargs['root_name'] = None
        kwargs.pop('name', None)
        return kwargs



class Container(BaseContainer):

    guide_blueprint = DataProperty( name='guide_blueprint' )
    utilities_group = ObjectProperty( name='utilities_group' )
    expanded_handles_group = ObjectProperty( name='expanded_handles_group' )
    deform_joints = ObjectListProperty( name='deform_joints' )
    control_group = ObjectProperty( name='control_group' )
    custom_handles = DataProperty( name='custom_handles', default_value=False )
    sdk_networks = ObjectListProperty( name='sdk_networks' )
    settings_handle = ObjectProperty( name='settings_handle' )
    __custom_constraint_data__ = DataProperty( name='__custom_constraint_data__', default_value=[] )
    dynamics_group = ObjectProperty( name='dynamics_group' )
    module_versions = DataProperty( name='module_versions', default_value=dict() )
    use_anim_textures = DataProperty( name='use_anim_textures' )
    geometry_layers = DataProperty( name='geometry_layers', default_value=[] )
    parts_by_uuid = ObjectDictProperty( name='parts_by_uuid' )

    has_been_finalized = False
    data_getters = dict()
    data_setters = dict()


    def __init__(self, **kwargs):
        super(Container, self).__init__(**kwargs)
        self.data_getters = dict(
            handle_shapes=functools.partial(
                self.get_handle_shapes,
                local=True
            ),
            handle_colors=self.get_handle_colors,
            handle_default_colors=self.get_handle_default_colors,
            skin_clusters=self.get_skin_cluster_data,
            deformer_stack_data=self.get_deformer_stack_data,
            delta_mush=self.get_delta_mush_data,
            shard_skin_cluster_data=self.get_shard_skin_cluster_data,
            wrap=self.get_wrap_data,
            cvwrap=self.get_cvwrap_data,
            space_switchers=self.get_space_switcher_data,
            sdks=self.get_sdk_data,
            custom_plug_data=self.get_custom_plug_data,
            custom_constraint_data=self.get_custom_constraints_data,
            origin_bs_weights=self.get_origin_bs_weights
        )
        self.data_setters = dict(
            handle_shapes=self.set_handle_shapes,
            skin_clusters=self.set_skin_cluster_data,
            deformer_stack_data=self.set_deformer_stack_data,
            delta_mush=self.set_delta_mush_data,
            shard_skin_cluster_data=self.set_shard_skin_cluster_data,
            wrap=self.set_wrap_data,
            cvwrap=self.set_cvwrap_data,
            space_switchers=spu.set_space_switcher_data,
            sdks=self.set_sdk_data,
            custom_plug_data=self.set_custom_plug_data,
            custom_constraint_data=self.set_custom_constraints_data,
            origin_bs_weights=self.set_origin_bs_weights
        )


    @classmethod
    def create(cls, **kwargs):
        for x in cls.default_settings:
            kwargs.setdefault(x, cls.default_settings[x])
        this = super(Container, cls).create(**kwargs)
        this.create_shaders()
        settings_handle = this.create_handle(
            segment_name='Settings',
            shape='figure',
            axis='z',
            line_width=2,
            create_gimbal=False
        )

        this.deform_group = this.create_child( Transform, segment_name='Deform' )
        this.origin_deform_group = this.deform_group.create_child( Transform, segment_name='OriginDeform' )
        this.control_group = this.create_child( Transform, segment_name='Control' )
        this.root_geometry_group = this.create_child( Transform, segment_name='RootGeometry' )
        this.geometry_group = this.root_geometry_group.create_child( Transform, segment_name='Geometry' )
        this.utilities_group = this.create_child( Transform, segment_name='Utilities' )
        this.export_data_group = this.utilities_group.create_child( Transform, segment_name='ExportDataGroup' )
        this.utility_geometry_group = this.root_geometry_group.create_child( Transform, segment_name='UtilityGeometry' )
        this.low_geometry_group = this.root_geometry_group.create_child( Transform, segment_name='LowGeometry' )
        this.placement_group = this.root_geometry_group.create_child( Transform, segment_name='Placements' )
        this.origin_geometry_group = this.utility_geometry_group.create_child( Transform,
                                                                               segment_name='OriginGeometry' )
        this.dynamics_group = this.create_child( Transform, segment_name="Dynamics" )
        this.controller.scene.rename( this.export_data_group, 'ExportData' )

        geometry_display_plug = settings_handle.create_plug(
            'geometryDisplay', k=True, at='enum', en="Selectable:Template:Locked", dv=2
        )
        geometry_visibility_plug = settings_handle.create_plug(
            'geometryVis', k=True, at='long', min=0, max=1, dv=1
        )
        utility_geometry_visibility_plug = settings_handle.create_plug(
            'utilityGeometryVis', k=True, at='long', min=0, max=1, dv=0
        )
        origin_geometry_visibility_plug = settings_handle.create_plug(
            'originGeometryVis', k=True, at='long', min=0, max=1, dv=1
        )
        low_geometry_visibility_plug = settings_handle.create_plug(
            'lowGeometryVis', k=True, at='long', min=0, max=1, dv=0
        )
        utilities_plug = settings_handle.create_plug(
            'utilitiesVis', k=True, at='long', min=0, max=1, dv=1
        )
        dynamics_plug = settings_handle.create_plug(
            'dynamicsVis', k=True, at='long', min=0, max=1, dv=1
        )
        realtime_visualization_display_plug = settings_handle.create_plug(  # This belongs in realtime_rig
            'realtimeIndicatorDisplay', k=True, at='enum', en="Selectable:Template:Locked", dv=2
        )
        joint_vis_plug = settings_handle.create_plug(
            'jointVis', k=True, at='long', min=0, max=1, dv=1
        )
        control_vis_plug = settings_handle.create_plug(
            'controlVis', k=True, at='long', min=0, max=1, dv=1
        )
        playback_plug = settings_handle.create_plug(
            'ControlVisPlayback', k=True, at='long', min=0, max=1, dv=0
        )
        root_vis_plug = settings_handle.create_plug(
            'RootCtrlVis', k=True, at='long', min=0, max=1, dv=1
        )

        geometry_display_plug.set_value(0)
        joint_vis_plug.connect_to(this.deform_group.plugs['visibility'])
        control_vis_plug.connect_to(this.control_group.plugs['visibility'])
        playback_plug.connect_to(this.control_group.plugs['hideOnPlayback'])
        this.root_geometry_group.plugs['overrideEnabled'].set_value(True)
        geometry_display_plug.connect_to(this.root_geometry_group.plugs['overrideDisplayType'])
        utility_geometry_visibility_plug.connect_to(this.utility_geometry_group.plugs['visibility'])
        origin_geometry_visibility_plug.connect_to(this.origin_geometry_group.plugs['visibility'])
        low_geometry_visibility_plug.connect_to(this.low_geometry_group.plugs['visibility'])
        utilities_plug.connect_to(this.utilities_group.plugs['visibility'])

        # List of plugs that CANNOT be keyed by Animation
        this.add_plugs(
            joint_vis_plug,
            control_vis_plug,
            playback_plug,
            root_vis_plug,
            geometry_display_plug,
            geometry_visibility_plug,
            utility_geometry_visibility_plug,
            low_geometry_visibility_plug,
            utilities_plug,
            dynamics_plug,
            realtime_visualization_display_plug,
            keyable=False
        )
        # List of plugs that CAN be keyed by Animation
        this.add_plugs(
            geometry_visibility_plug,
            keyable=True
        )

        this.settings_handle = settings_handle
        return this


    def create_handle(self, **kwargs):
        return self.controller.create_standard_handle(self, **kwargs)


    def create_sdk_network(self, **kwargs):
        return self.create_child(
            SDKNetwork,
            container=self,
            **kwargs.copy()
        )


    def get_sdk_data(self):
        data = []
        for x in self.sdk_networks:
            if x.layer == self.controller.current_layer:
                sdk_data = sbl.get_blueprint(x)
                data.append(sdk_data)
        return data


    def set_sdk_data(self, data):
        for x in data:
            x = x.copy()
            x['parent'] = self
            x['container'] = self
            try:
                sbl.build_blueprint(self.controller, x)
            except Exception as e:
                logging.getLogger('rig_builder').error(traceback.format_exc())
                self.controller.raise_warning(
                    'Warning: Failed to create sdk network\n"%s"' % e.message
                )


    def get_blueprint(self):
        blueprint = dict(
            base_type='Container',  # needed by blueprint view
            klass=self.__class__.__name__,
            module=self.__module__,
            root_name=self.root_name,
            side=self.side,
            size=self.size,
            hierarchy_data=cmt.part_hierarchy.get_hierarchy_data(),
            guide_blueprint=self.guide_blueprint,
            geometry_paths=process_paths(env.local_build_directory, self.geometry_paths),
            utility_geometry_paths=process_paths(env.local_build_directory, self.utility_geometry_paths),
            low_geometry_paths=process_paths(env.local_build_directory, self.low_geometry_paths),
            anim_textures_date=self.anim_textures_date,
            use_external_rig_data=self.use_external_rig_data,
            use_manual_rig_data=self.use_manual_rig_data,
            custom_handles=self.custom_handles,
            disable_shard_baking=self.disable_shard_baking,
            pre_delete_handle_shapes=self.pre_delete_handle_shapes
        )
        if not self.use_external_rig_data:
            blueprint['rig_data'] = self.get_rig_data()

        data_properties = DataProperty.map.get(self, dict())
        for x in data_properties:
            blueprint[x.name] = data_properties[x]
        blueprint.pop('__custom_constraint_data__', None)  # get rid of duplicate constraints
        return blueprint


    def get_rig_data(self):
        return dict((x, self.data_getters[x]()) for x in self.data_getters)


    def get_toggle_blueprint(self):

        blueprint = self.guide_blueprint
        blueprint['custom_handles'] = self.custom_handles
        blueprint['deleted_parent_entity_part_names'] = self.deleted_parent_entity_part_names
        blueprint['anim_textures_date'] = self.anim_textures_date
        blueprint['use_external_rig_data'] = self.use_external_rig_data
        blueprint['use_manual_rig_data'] = self.use_manual_rig_data
        blueprint['base_type'] = Container.__name__
        blueprint['disable_shard_baking'] = self.disable_shard_baking

        if not blueprint:
            raise Exception('No Guide Blueprint found!')
        if not self.use_external_rig_data:
            blueprint['rig_data'] = self.get_rig_data()
        blueprint['product_paths'] = copy.deepcopy(self.product_paths)

        return blueprint


    def clear_spaces(self):
        for handle in self.get_handles():
            if isinstance(handle, GroupedHandle) and handle.space_switcher:
                if handle.space_switcher:
                    if handle.plugs.exists('parentSpace'):
                        self.controller.scene.deleteAttr(handle.name, at='parentSpace')
                        self.controller.schedule_objects_for_deletion(handle.plugs['parentSpace'])
                    self.controller.schedule_objects_for_deletion(handle.space_switcher)
                    self.controller.delete_scheduled_objects()


    def get_space_switcher_data(self):
        space_switcher_data = dict()
        for handle in self.get_handles():
            if isinstance(handle, GroupedHandle):
                if handle.space_switcher:
                    if handle.space_switcher.layer == self.controller.current_layer:
                        space_switcher = handle.space_switcher
                        switcher_type = handle.space_switcher.__class__.__name__
                        plug_data = dict(
                            translate=space_switcher.translate,
                            rotate=space_switcher.rotate,
                            scale=space_switcher.scale,
                            dv=space_switcher.dv
                        )
                        target_data = [(x.name, x.pretty_name) for x in handle.space_switcher.targets]
                        space_switcher_data[handle.name] = (switcher_type, plug_data, target_data)
        return space_switcher_data


    def get_custom_plug_data(self):
        data = []
        for plug in self.custom_plugs:
            if plug.layer == self.controller.current_layer:
                plug_data = plug.get_data()
                plug_data['in_connections'] = self.controller.scene.listConnections(
                    plug.name,
                    s=True,
                    d=False,
                    p=True,
                    scn=True
                )
                plug_data['out_connections'] = self.controller.scene.listConnections(
                    plug.name,
                    s=False,
                    d=True,
                    p=True,
                    scn=True
                )
                data.append(plug_data)
        return data


    def get_custom_constraints_data(self):
        data = []
        constraint_names = set()
        for constraint in self.__custom_constraint_data__:
            constraint_name = constraint['name']
            if constraint_name in constraint_names:
                continue  # Skip duplicates
            constraint_names.add(constraint_name)

            if self.controller.scene.objExists(constraint_name):
                constraint_data = self.controller.scene.get_constraint_data(constraint_name)
                data.append(constraint_data)
        return data


    def set_custom_constraints_data(self, data):
        new_data = []
        constraint_names = set()
        for constraint_data in data:
            constraint_name = constraint_data.get('name')
            if constraint_name in constraint_names:
                continue  # Skip duplicates
            constraint_names.add(constraint_name)

            kwargs = copy.deepcopy(constraint_data)
            constraint_type = kwargs.pop('constraint_type')
            target_list = kwargs.pop('target_list')
            target_list.append(kwargs.pop('constrained_node'))
            kwargs.pop('parent', None)
            if self.controller.namespace:
                for i in range(len(target_list)):
                    target_list[i] = '%s:%s' % (self.controller.namespace, target_list[i])
                if 'worldUpObject' in kwargs:
                    kwargs['worldUpObject'] = '%s:%s' % (self.controller.namespace, kwargs['worldUpObject'])
                if 'interpType' in kwargs:
                    kwargs['interpType'] = '%s:%s' % (self.controller.namespace, kwargs['interpType'])
            missing_nodes = []
            for x in target_list:
                if not self.controller.scene.objExists(x):
                    missing_nodes.append(x)
            if missing_nodes:
                self.controller.raise_warning(
                    'transforms not found.  Skipping constraint creation: %s' % missing_nodes
                )
            else:
                try:
                    self.controller.scene.create_constraint(
                        constraint_type,
                        *target_list,
                        **kwargs
                    )
                    new_data.append(constraint_data)
                except Exception as e:
                    logging.getLogger('rig_build').error(traceback.format_exc())
                    self.controller.raise_warning(
                        'WARNING: Failed to create %s on : %s\nSee script editor for details.' % (
                            constraint_type,
                            target_list
                        )
                    )
        if self.controller.current_layer is None:
            self.__custom_constraint_data__ = new_data


    def add_custom_constraint(self, constraint_string, data):
        if not isinstance(constraint_string, basestring):
            raise Exception('Invalid type "%s" use String' % constraint_string)

        if self.controller.current_layer is None:
            if constraint_string in (x['name'] for x in self.__custom_constraint_data__):
                logging.getLogger('rig_builder').warning(
                    'The constraint "%s" already been added to the controller.' % constraint_string
                )
                return
            self.__custom_constraint_data__.append(data)


    def set_origin_bs_weights(self, origin_data):
        controller = self.controller
        if controller.scene.mock:
            return
        for key in origin_data:
            if 'weights' in origin_data[key]:
                if origin_data[key]['weights'] != None:
                    bls = '{}'.format(key) + '_Origin_Bs'
                    controller.scene.set_blendshape_weights(
                        bls,
                        data=origin_data[key]['weights']
                    )


    def get_origin_bs_weights(self):
        dtl.get_origin_weight_data(
            self.controller,
            self.origin_geometry_data
        )


    def set_custom_plug_data(self, data):

        """
        This function is a mess. we need to try and do it without resorting to try-except
        """
        failed_in = []
        failed_out = []

        for x in list(data):
            node_name = x['node']
            long_name = x['long_name']
            if self.controller.namespace:
                node_name = '%s:%s' % (self.controller.namespace, node_name)

            if node_name in self.controller.named_objects:
                node = self.controller.named_objects[node_name]
                if self.controller.scene.attributeQuery(long_name, n=node_name, exists=True):
                    plug = node.plugs[long_name]
                else:
                    attribute_type = x['type']
                    plug_kwargs = dict(
                        at=attribute_type,
                        keyable=x['keyable']
                    )
                    if 'min' in x:
                        plug_kwargs['min'] = x['min']
                    if 'max' in x:
                        plug_kwargs['max'] = x['max']
                    if x.get('dv', None) is not None:
                        plug_kwargs['dv'] = x['dv']
                    if attribute_type == 'enum' and 'listEnum' in x:
                        plug_kwargs['en'] = x['listEnum']
                    plug = node.create_plug(
                        long_name,
                        **plug_kwargs
                    )
                if x.get('current_value', None) is not None:
                    try:
                        plug.set_value(x['current_value'])
                    except Exception as e:
                        print(e.message)
                in_connections = x.get('in_connections', None)
                if in_connections is not None:
                    for in_plug in x['in_connections']:
                        if self.controller.namespace:
                            in_plug = '%s:%s' % (self.controller.namespace, in_plug)
                        try:
                            self.controller.scene.connectAttr(in_plug, plug.name)
                        except Exception as e:
                            logging.getLogger('rig_builder').error(traceback.format_exc())
                            failed_in.append((in_plug, plug))
                if x.get('locked', None) is not None:
                    plug.set_locked(x['locked'])
                if x.get('channelbox', None) is not None:
                    plug.set_channel_box(x['channelbox'])
                out_connections = x.get('out_connections', None)
                if out_connections is not None:
                    for out_plug in out_connections:
                        if self.controller.namespace:
                            out_plug = '%s:%s' % (self.controller.namespace, out_plug)
                        if not self.controller.scene.objExists(out_plug):
                            logging.getLogger('rig_build').warning(
                                'CustomPlugs: out_plug "%s" didnt exist/ skipping.' % out_plug
                            )
                        else:
                            connections = self.controller.scene.listConnections(
                                plug.name,
                                d=True,
                                s=False,
                                scn=True,
                                plugs=True
                            ) or []
                            if out_plug in connections:
                                logging.getLogger('rig_build').warning(
                                    'CustomPlugs: The plug %s was already connected to %s skipping' % (plug, out_plug)
                                )
                            else:
                                try:
                                    self.controller.scene.connectAttr(plug.name, out_plug)
                                except RuntimeError as e:
                                    logging.getLogger('rig_builder').error(traceback.format_exc())
                                    failed_out.append((plug, out_plug))
                if not self.controller.namespace and plug not in self.custom_plugs:
                    self.custom_plugs.append(plug)
            else:
                print('Warning: The node "%s" was not found in the controller' % node_name)
        if failed_in:
            m = [failed_in[x] for x in range(len(failed_in)) if x < 10]
            message = 'Custom plug INPUT connections failed:\n\n%s' % '\n\n'.join(
                    ['%s ----> %s' % (x[0], x[1]) for x in m]
                )
            print(message)
            self.controller.raise_warning(message)
        if failed_out:
            m = [failed_out[x] for x in range(len(failed_out)) if x < 10]
            message = 'Custom plug OUTPUT connections failed:\n\n%s' % '\n\n'.join(
                    ['%s ----> %s' % (x[0], x[1]) for x in m]
                )
            self.controller.raise_warning(message)


    def add_custom_plug(self, plug_string):
        if not isinstance(plug_string, basestring):
            raise Exception('Invalid plug_string type "%s" use String' %  plug_string)
        node_name, attr_name = plug_string.split('.')
        if node_name not in self.controller.named_objects:
            raise Exception('The node "%s" was not found in the controller' % node_name)
        if not self.controller.scene.objExists(plug_string):
            raise Exception('The plug "%s" does not exist' % plug_string)
        node = self.controller.named_objects[node_name]
        plug = node.initialize_plug(attr_name)
        if plug not in self.custom_plugs:
            self.custom_plugs.append(plug)
        else:
            logging.getLogger('rig_build').info('Warning: The plug "%s" has already been added. Skipping...' % plug_string)


    def get_space_switchers(self):
        current_layer = self.controller.current_layer
        return [x.space_switcher for x in self.get_handles() if x.space_switcher and x.layer == current_layer]


    def expand_handle_shapes(self):
        self.controller.expand_handle_shapes(self)


    def collapse_handle_shapes(self):
        self.controller.collapse_handle_shapes(self)
        self.custom_handles = True


    def get_handle_shapes(self, local):
        return self.controller.get_handle_shapes(self, local)


    def set_handle_shapes(self, shapes):
        self.controller.set_handle_shapes(self, shapes)
        self.custom_handles = True


    def get_handle_colors(self):
        return self.controller.get_handle_colors(self)


    def get_handle_default_colors(self):
        return self.controller.get_handle_default_colors(self)


    def get_shard_skin_cluster_data(self):
        return self.controller.get_shard_skin_cluster_data(self)


    def set_shard_skin_cluster_data(self, data):
        return self.controller.set_shard_skin_cluster_data(data)


    def get_shards(self):
        return self.controller.get_shard_mesh_nodes()


    def finalize(self):
        super(Container, self).finalize()
        self.settings_handle.plugs['geometryDisplay'].set_value(2)
        self.settings_handle.plugs['geometryVis'].set_value(1)
        self.settings_handle.plugs['utilityGeometryVis'].set_value(0)
        self.settings_handle.plugs['lowGeometryVis'].set_value(0)
        if self.settings_handle.plugs.exists('placementsVis'):
            self.settings_handle.plugs['placementsVis'].set_value(1)
        self.settings_handle.plugs['utilitiesVis'].set_value(0)
        self.settings_handle.plugs['jointVis'].set_value(0)
        if self.settings_handle.plugs.exists('bendyVis'):
            self.settings_handle.plugs['bendyVis'].set_value(0)
        if self.settings_handle.plugs.exists('foot_placements'):
            self.settings_handle.plugs['foot_placements'].set_value(1)
        if self.settings_handle.plugs.exists('wheels_placements'):
            self.settings_handle.plugs['wheels_placements'].set_value(1)
        if self.settings_handle.plugs.exists('Face_Control_Vis'):
            self.settings_handle.plugs['Face_Control_Vis'].set_value(0)
        if self.settings_handle.plugs.exists('bifrostGeoVis'):
            self.settings_handle.plugs['bifrostGeoVis'].set_value(1)
        if self.settings_handle.plugs.exists('squashLatticeVis'):
            self.settings_handle.plugs['squashLatticeVis'].set_value(0)
        self.settings_handle.plugs['RootCtrlVis'].set_value(1)


    def finish_create(self, **kwargs):
        super(Container, self).finish_create(**kwargs)
        for handle in self.get_handles():
            handle.default_limits = handle.get_transform_limits()


    def teardown(self):
        self.controller.schedule_objects_for_deletion(self.sdk_networks)
        super(Container, self).teardown()


    def get_handle_limits(self):
        return dict((x.name, x.get_transform_limits()) for x in self.get_handles())


    def set_handle_limits(self, handle_limits):
        for handle_name in handle_limits:
            if handle_name in self.controller.named_objects:
                self.controller.named_objects[handle_name].set_transform_limits(handle_limits[handle_name])


    @classmethod
    def pre_process_kwargs(cls, **kwargs):
        kwargs = super(BaseContainer, cls).pre_process_kwargs(**kwargs)
        kwargs['segment_name'] = 'Container'
        kwargs['root_name'] = None
        kwargs.pop('name', None)
        return kwargs


def process_paths(build_directory, paths):
    return [x for x in list(set(paths)) if os.path.exists(x) or os.path.exists('%s%s' % (build_directory, x))]
