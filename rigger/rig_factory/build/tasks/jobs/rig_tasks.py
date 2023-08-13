# python modules
import os
import json
import logging
import functools
import traceback
# Snowman modules
import Snowman3.rigger.rig_factory.system_signals as sig
import Snowman3.rigger.rig_factory.utilities.handle_utilities as handle_utils
import Snowman3.rigger.rig_factory.utilities.geometry_utilities as geo_utils
import Snowman3.rigger.rig_factory.build.utilities.part_utilities as part_utils
import Snowman3.rigger.rig_factory.utilities.environment_utilities as env_utils
import Snowman3.rigger.rig_factory.build.tasks.jobs.cheek_driver_tasks as cheek_drv_utils
import Snowman3.rigger.rig_factory.build.utilities.visibility_utilities as vis_utils
import Snowman3.rigger.rig_factory.build.utilities.controller_utilities as ctrl_utils
import Snowman3.rigger.rig_factory.build.tasks.jobs.projection_eye_tasks as projection_eye_tasks
import Snowman3.rigger.rig_factory.build.tasks.task_utilities.task_utilities as task_utils
import Snowman3.rigger.rig_factory.build.tasks.task_utilities.face_task_utilities as face_task_utils
from Snowman3.rigger.rig_factory.build.tasks.task_objects import BuildTask


# ----------------------------------------------------------------------------------------------------------------------
def missing_blueprint_warning(file_path):
    return dict(
        status='warning',
        warning=f'unable to locate blueprint: {file_path}'
    )


# ----------------------------------------------------------------------------------------------------------------------
def apply_missing_blueprint_warning(root_task, build):
    return BuildTask(
        parent=root_task,
        build=build,
        name='Blueprint Warning',
        function=functools.partial(
            missing_blueprint_warning,
            '%s/%s' % (build.build_directory, build.rig_blueprint_file_name)
        )
    )


# ----------------------------------------------------------------------------------------------------------------------
def verify_entity_builds(entity_builds, root_task):
    for build in entity_builds:
        if build.rig_blueprint and 'guide_blueprint' not in build.rig_blueprint:
            raise Exception('Blueprint must be in RIG state: %s' % build.rig_blueprint)
        if not build.rig_blueprint:
            root_task = apply_missing_blueprint_warning(root_task, build)
    return root_task


# ----------------------------------------------------------------------------------------------------------------------
def flatten_blueprint(blueprint, include_self=True):
    blueprint_list = []
    if include_self:
        blueprint_list.append( blueprint )
    part_blueprints = blueprint.get('part_members', [])
    for part_blueprint in part_blueprints:
        blueprint_list.extend( flatten_blueprint( part_blueprint ) )
    return blueprint_list


# ----------------------------------------------------------------------------------------------------------------------
def get_rig_tasks(entity_build, parent=None):
    root_task = BuildTask( parent=parent, build=entity_build, name='Rig' )
    # Listing from child to parent
    entity_builds = list(task_utils.flatten(entity_build))
    root_task = verify_entity_builds(entity_builds, root_task)

    # Create Container
    task_utils.create_container_tasks( entity_builds, root_task, )

    # Geometry
    geometry_task = BuildTask( parent=root_task, name='Geometry' )
    for build in entity_builds:
        BuildTask(
            parent=geometry_task,
            build=build,
            name='Build.before_import_geometry()',
            function=build.create_callback('before_import_geometry')
        )
    for build in list(task_utils.flatten(entity_build)):
        product_paths = build.rig_blueprint['product_paths']
        for product in ['abc', 'abc_anim']:
            if product_paths.get(product, None):
                BuildTask(
                    parent=geometry_task,
                    build=build,
                    name=f'Import Product ({product})',
                    function=functools.partial(
                        geo_utils.import_abc_product,
                        product,
                        product_paths[product],
                        store_path=build.entity == os.environ['ENTITY_NAME']
                    )
                )
    # Import Utility Geometry
    for build in entity_builds:
        if 'utility_geometry_paths' in build.rig_blueprint:
            BuildTask(
                parent=geometry_task,
                build=build,
                name='Import Utility geometry paths',
                function=functools.partial(
                    geo_utils.import_geometry_paths,
                    build.entity,
                    'utility_geometry',
                    list(set(build.rig_blueprint['utility_geometry_paths']))
                )
            )
        if 'low_geometry_paths' in build.rig_blueprint:
            BuildTask(
                parent=geometry_task,
                build=build,
                name='Import Low geometry paths',
                function=functools.partial(
                    geo_utils.import_geometry_paths,
                    build.entity,
                    'low_geometry',
                    list(set(build.rig_blueprint['low_geometry_paths']))
                )
            )
        if 'geometry_paths' in build.rig_blueprint:
            BuildTask(
                parent=geometry_task,
                build=build,
                name='Import geometry paths',
                function=functools.partial(
                    geo_utils.import_geometry_paths,
                    build.entity,
                    'geometry',
                    list(set(build.rig_blueprint['geometry_paths']))
                )
            )
    for build in entity_builds:
        BuildTask(
            parent=geometry_task,
            build=build,
            name='Build.after_import_geometry()',
            function=build.create_callback('after_import_geometry')
        )

    # Import Placements
    task_utils.import_placements(
        entity_builds,
        root_task
    )
    # Import Bifrost
    task_utils.import_bifrost(
        entity_builds,
        root_task
    )
    # Set Camera clipping planes
    task_utils.set_camera_clipping_plane(
        entity_builds,
        root_task
    )
    # Import Pre-vis Lights
    task_utils.import_previs_lights(
        entity_builds,
        root_task
    )

    # Cleanup Maya state after imports, BEFORE any Python garbage collection
    BuildTask(
        parent=root_task,
        name='Cleanup After Maya Imports',
        function=task_utils.cleanup_maya_after_imports
    )

    # Load Export Data
    task_utils.load_export_data(
        entity_builds,
        root_task
    )

    # Create Origin Geometry
    task_utils.create_origin_geometry(
        entity_builds,
        root_task
    )

    # Begin construction of the deformation layer stack
    task_utils.initialise_deformation_stack(
        entity_builds,
        root_task
    )

    # Create Parts
    task_utils.get_create_parts_tasks(
        entity_builds,
        root_task
    )


    # Projection Eyes

    projection_eye_tasks.get_projection_eye_tasks(entity_builds, root_task)

    # Post Create Parts
    task_utils.get_post_create_tasks(
        entity_builds,
        root_task
    )

    BuildTask(
        name='Set Snapping',
        parent=root_task,
        function=functools.partial(
            env_utils.set_snapping,
            default=0
        )
    )

    # Joint Count Tasks
    guide_part_joint_count_data = entity_build.rig_blueprint.get('guide_part_joint_count_data')
    if guide_part_joint_count_data:
        check_joint_count_task = BuildTask(
            name='Joint Count Check',
            parent=parent,
            function=functools.partial(
                task_utils.assert_guide_part_joint_count_data,
                guide_part_joint_count_data
            )
        )
        for part_name, joint_count in guide_part_joint_count_data.items():
            BuildTask(
                build=entity_build,
                name=part_name,
                parent=check_joint_count_task,
                function=functools.partial(
                    task_utils.check_joint_count,
                    part_name,
                    joint_count
                )
            )
    # Set Owners
    task_utils.get_hierarchy_tasks(
        entity_builds,
        root_task
    )
    cheek_drv_utils.get_cheek_driver_tasks(
        entity_build,
        parent=root_task
    )
    # Other Post-creation part automation
    BuildTask(
        name='Auto Eye',
        parent=root_task,
        function=face_task_utils.setup_auto_eye
    )

    # Deformation Rig
    deformation_rig_root = BuildTask(
        name='Deformation Rig',
        parent=root_task
    )
    for build in entity_builds:
        BuildTask(
            build=build,
            name='Before Deformation Rig',
            parent=deformation_rig_root,
            function=build.create_callback('before_create_deformation_rig')
        )

    group_position_root = BuildTask(
        name='Joint Group Position',
        parent=deformation_rig_root
    )
    for build in entity_builds:
        entity_task = BuildTask(
            build=build,
            name=build.entity,
            parent=group_position_root
        )
        task_utils.generate_group_position_tasks(
            entity_task,
            build.rig_blueprint['part_members']
        )
    deform_joints_task = BuildTask(
        build=entity_build,
        name='Create Deform Joints',
        parent=deformation_rig_root,
    )
    for build in entity_builds:
        entity_task = BuildTask(
            build=build,
            name=build.entity,
            parent=deform_joints_task,
        )
        task_utils.get_part_deformation_joint_tasks(
            entity_task,
            build.rig_blueprint.get('part_members', [])
        )

    parent_deform_joints_task = BuildTask(
        build=entity_build,
        name='Parent Deform Joints',
        parent=deformation_rig_root
    )
    for build in entity_builds:
        entity_task = BuildTask(
            build=build,
            name=build.entity,
            parent=parent_deform_joints_task,
        )
        task_utils.get_part_deformation_joint_parent_tasks(
            entity_task,
            build.rig_blueprint['part_members']
        )

    for build in entity_builds:
        BuildTask(
            build=build,
            name='After Deformation Rig',
            parent=deformation_rig_root,
            function=build.create_callback('after_create_deformation_rig')
        )

    # Joint Count Check
    BuildTask(
        parent=root_task,
        name='Check Joint Count',
        function=task_utils.perform_deformation_joint_count_check
    )

    # Label Joints
    BuildTask(
        parent=root_task,
        name='Label Joints',
        function=task_utils.label_joints
    )

    task_utils.import_skin_clusters(
        entity_builds,
        root_task
    )
    # Proxy Shaders
    if not os.environ.get('DO_NOT_LOAD_ARNOLD', False):
        task_utils.create_proxy_shaders(
            list(reversed(entity_builds)),
            root_task
        )

    task_utils.import_origin_bs_weight(
        entity_builds,
        root_task
    )

    # Bifrost Attributes
    BuildTask(
        parent=root_task,
        name='Set Bifrost Attributes',
        function=task_utils.set_bifrost_attributes
    )

    for build in entity_builds:
        for x in flatten_blueprint(build.rig_blueprint):
            if 'rig_data' not in x:
                raise Exception('rig_data not found in: %s' % x.keys())

    # Non-Linear Deformers
    task_utils.create_rig_data_tasks(
        entity_builds,
        root_task
    )

    # Visibility Plugs
    BuildTask(
        parent=root_task,
        name='Setup Visibility Plugs',
        function=vis_utils.setup_visibility_plugs
    )

    # Delta Mushs
    task_utils.import_delta_mushs(
        entity_builds,
        root_task
    )

    # Wraps
    task_utils.set_wraps(
        entity_builds,
        root_task
    )

    # cvWraps
    task_utils.set_cvwraps(
        entity_builds,
        root_task
    )

    # Connect the Deformation Layers
    task_utils.connect_deformation_layers_stack(
        entity_builds,
        root_task
    )

    # Deformer Stack
    task_utils.set_deformer_stack_data(
        entity_builds,
        root_task
    )

    # Space Switcher
    task_utils.get_space_switcher_tasks(
        list(reversed(entity_builds)),
        root_task
    )

    # Automated SDK-replacements
    BuildTask(
        name='Setup auto lip drivers',
        parent=root_task,
        function=face_task_utils.setup_auto_lips
    )

    # Custom Plugs
    task_utils.create_custom_plugs(
        entity_builds,
        root_task
    )

    # Custom Constraints
    task_utils.create_custom_constraints(
        entity_builds,
        root_task
    )

    # Finish Create Parts
    task_utils.finish_create_parts(
        entity_builds,
        root_task
    )

    # Finish Create Parts
    task_utils.get_handle_limits_tasks(
        entity_builds,
        root_task
    )

    # Set Handle Rotate Order
    BuildTask(
        parent=root_task,
        name='Set Handle Rotate Order',
        function=task_utils.set_handle_rotate_order
    )

    # Setup Settings Handle
    BuildTask(
        parent=root_task,
        name='Setup Settings Handle',
        function=part_utils.setup_settings_handle
    )

    # Handle Shapes
    handle_shapes_task = BuildTask(
        parent=root_task,
        name='Handle Shapes',
    )

    # Handle Colors
    handle_color_task = BuildTask(
        parent=root_task,
        name='Set Handle Colors'
    )
    for build in entity_builds:
        handle_data = build.rig_blueprint['rig_data'].get('handle_colors', dict())
        BuildTask(
            build=build,
            parent=handle_color_task,
            name='Set handle_colors (%s)' % build.entity,
            function=functools.partial(
                set_handle_colors,
                handle_data
            )
        )

    all_handle_shapes = []  # This gets filled farther down
    if entity_build.rig_blueprint.get('pre_delete_handle_shapes', False):
        BuildTask(
            parent=handle_shapes_task,
            name='Delete Handle_shapes (Makes it fast)',
            function=functools.partial(
                delete_handle_shapes,
                all_handle_shapes
            )
        )

    # Check if new folder structure is being used
    paths_to_check = []
    if os.path.exists(entity_build.build_directory):
        paths_to_check.append('%s/user_data/handle_shapes.json' % entity_build.build_directory) # new folder
        paths_to_check.append('%s/handle_shapes.json' % entity_build.build_directory) # old folder location
    local_shapes_path = None
    for path in paths_to_check:
        if os.path.exists(path):
            local_shapes_path = path
            break

    if local_shapes_path and os.path.exists(local_shapes_path):
        for build in entity_builds:
            BuildTask(
                build=build,
                parent=handle_shapes_task,
                name='Before Handle Shapes',
                function=build.create_callback('before_handle_shapes')
            )
        if not entity_build.rig_blueprint.get('custom_handles', True):
            handle_shapes_task.info = 'Custom Handle shapes is OFF, Ignoring: %s' % local_shapes_path
        else:
            try:
                with open(local_shapes_path, mode='r') as f:
                    local_handle_shapes = json.load(f)
            except Exception as e:
                logging.getLogger('rig_build').error(traceback.format_exc())
                handle_shapes_task.warning = 'Failed to parse local handle shapes from json file: %s' % local_shapes_path
                handle_shapes_task.status = 'warning'
            if local_handle_shapes:
                local_shapes_task = BuildTask(
                    parent=handle_shapes_task,
                    name='Set Handle Shapes (Local)',
                    function=functools.partial(
                        sig.gui_signals['warning_notification'].emit,
                        text="Local handle_shapes.json are overriding the rig_blueprint from this path: %s" % os.path.relpath(local_shapes_path, entity_build.build_directory),
                        timeout=13000
                        )
                    )
                all_handle_shapes.extend(local_handle_shapes.keys())
                for handle_name in local_handle_shapes:
                    if '_Gimbal_' not in handle_name:
                        local_task = BuildTask(
                            parent=local_shapes_task,
                            name=handle_name,
                            function=functools.partial(
                                set_handle_shape,
                                handle_name,
                                local_handle_shapes[handle_name]
                            )
                        )
                        if ':' in handle_name:
                            local_task.namespace = handle_name.split(':')[0]
                vis_connections_task = BuildTask(
                    parent=local_shapes_task,
                    name='Restore Visibility Connections'
                )
                for handle_name in local_handle_shapes:
                    if '_Gimbal_' not in handle_name:  # Gimbals already have curve vis connected
                        local_task = BuildTask(
                            parent=vis_connections_task,
                            name=handle_name,
                            function=functools.partial(
                                restore_handle_visibility_connections,
                                handle_name
                            )
                        )
                        if ':' in handle_name:
                            local_task.namespace = handle_name.split(':')[0]

        for build in entity_builds:
            BuildTask(
                build=build,
                parent=handle_shapes_task,
                name='After Handle Shapes',
                function=build.create_callback('after_handle_shapes')
            )
    else:
        for build in entity_builds:
            entity_task = BuildTask(
                build=build,
                parent=handle_shapes_task,
                name=build.entity,
            )
            BuildTask(
                build=build,
                parent=entity_task,
                name='Before Handle Shapes',
                function=build.create_callback('before_handle_shapes')
            )
            if not build.rig_blueprint.get('custom_handles'):
                handle_shapes_task.info = 'Custom Handle shapes is OFF Ignoring handle shapes data'
            else:
                if build.rig_blueprint.get('use_external_rig_data'):
                    # external handle shapes
                    if build.rig_blueprint.get('use_manual_rig_data'):
                        handle_shapes_task.info = 'Skipping Handle shapes. use_manual_rig_data = True'
                    else:
                        external_shapes_task = BuildTask(
                            parent=entity_task,
                            name='Set Handle Shapes (External)'
                        )
                        path = '%s/rig_data/handle_shapes.json' % build.build_directory
                        if not os.path.exists(path):
                            external_shapes_task.warning = 'Unable to locate file: %s' % path
                            external_shapes_task.status = 'warning'
                        else:
                            try:
                                with open(path, mode='r') as f:
                                    handle_shapes = json.load(f)
                            except Exception as e:
                                logging.getLogger('rig_build').error(traceback.format_exc())
                                external_shapes_task.warning = 'Failed to parse external handle shapes from json file: %s' % path
                                external_shapes_task.status = 'warning'

                            if not handle_shapes:
                                external_shapes_task.warning = 'No Handle shapes found in file: %s' % path
                                external_shapes_task.status = 'warning'

                            all_handle_shapes.extend(handle_shapes.keys())

                            for handle_name in handle_shapes:
                                if '_Gimbal_' not in handle_name:
                                    BuildTask(
                                        parent=external_shapes_task,
                                        name=handle_name,
                                        function=functools.partial(
                                            set_handle_shape,
                                            handle_name,
                                            handle_shapes[handle_name],
                                            namespace=build.namespace
                                        )
                                    )
                            vis_connections_task = BuildTask(
                                parent=external_shapes_task,
                                name='Restore Visibility Connections'
                            )
                            for handle_name in handle_shapes:
                                if '_Gimbal_' not in handle_name:  # Gimbals already have curve vis connected
                                    BuildTask(
                                        parent=vis_connections_task,
                                        name=handle_name,
                                        function=functools.partial(
                                            restore_handle_visibility_connections,
                                            handle_name,
                                            namespace=build.namespace
                                        )
                                    )
                else:
                    # Blueprint handle shapes
                    rig_data = build.rig_blueprint.get('rig_data', None)
                    if rig_data is None:
                        handle_shapes_task.warning = 'Unable to locate "rig_data" in blueprint'
                        handle_shapes_task.status = 'warning'

                        return
                    handle_shapes = rig_data.get('handle_shapes', None)
                    if handle_shapes is None:
                        handle_shapes_task.warning = 'Unable to locate "handle_shapes" in blueprint["rig_data"]'
                        handle_shapes_task.status = 'warning'
                        return

                    blueprint_handle_shapes_task = BuildTask(
                        parent=entity_task,
                        name='Set Handle Shapes (From Blueprint)'
                    )
                    if not handle_shapes:
                        blueprint_handle_shapes_task.info = 'No custom handle shapes found in rig_blueprint'

                    for handle_name in handle_shapes:
                        if '_Gimbal_' not in handle_name:
                            BuildTask(
                                parent=blueprint_handle_shapes_task,
                                name=handle_name,
                                function=functools.partial(
                                    set_handle_shape,
                                    handle_name,
                                    handle_shapes[handle_name],
                                    namespace=build.namespace
                                )
                            )
                    vis_connections_task = BuildTask(
                        parent=entity_task,
                        name='Restore Visibility Connections'
                    )
                    for handle_name in handle_shapes:
                        if '_Gimbal_' not in handle_name:  # Gimbals already have curve vis connected
                            BuildTask(
                                parent=vis_connections_task,
                                name=handle_name,
                                function=functools.partial(
                                    restore_handle_visibility_connections,
                                    handle_name,
                                    namespace=build.namespace
                                )
                            )
                    all_handle_shapes.extend(handle_shapes.keys())

                if build.layer == os.environ['ENTITY_NAME']:
                    BuildTask(
                        build=build,
                        parent=entity_task,
                        name='Set custom_handles property',
                        function=functools.partial(
                            set_custom_handles_property,
                            build.rig_blueprint.get('custom_handles', False)
                        )
                    )
            BuildTask(
                build=build,
                parent=entity_task,
                name='After Handle Shapes',
                function=build.create_callback('after_handle_shapes')
            )

    #  Custom SDKs
    task_utils.import_sdk_data(
        entity_builds,
        root_task
    )

    #  Parent Build Callbacks
    task_utils.parent_build_callbacks(
        list(reversed(entity_builds)),
        root_task
    )

    post_build_task = BuildTask(
        parent=root_task,
        build=entity_build,
        name='RigBuild.post_build'
    )
    for build in list(reversed(entity_builds)):
        BuildTask(
            build=build,
            parent=post_build_task,
            name='RigBuild.post_build',
            function=build.create_callback('post_build')
        )

    BuildTask(
        parent=root_task,
        name='Set Auto Rigged Property',
        function=set_auto_rigged_property
    )

    # Raise Build Warnings
    BuildTask(
        parent=root_task,
        name='Raise Build Warnings',
        function=task_utils.raise_build_warnings
    )

    return root_task


# ----------------------------------------------------------------------------------------------------------------------
def set_custom_handles_property(value):
    controller = ctrl_utils.get_controller()
    controller.root.custom_handles = value


# ----------------------------------------------------------------------------------------------------------------------
def get_handle(handle_name, controller, namespace=None):
    full_handle_name = handle_name
    if namespace:
        full_handle_name = f'{namespace}:{full_handle_name}'
    if full_handle_name not in controller.named_objects:
        return None
    handle = controller.named_objects[full_handle_name]
    return handle


# ----------------------------------------------------------------------------------------------------------------------
def set_handle_shape(handle_name, handle_data, namespace=None):
    controller = ctrl_utils.get_controller()
    handle = get_handle(handle_name, controller, namespace)
    if handle is None:
        return dict(status='warning', warning=f'Unable to find node: {handle_name}')
    result = handle_utils.set_handle_shape(handle, handle_data)
    return result


# ----------------------------------------------------------------------------------------------------------------------
def set_handle_colors(handle_data):
    controller = ctrl_utils.get_controller()
    results = []
    if handle_data:
        for handle, color in handle_data.items():
            handle = controller.named_objects.get(handle, None)
            if color and handle:
                result = handle_utils.set_handle_color(handle, color, False)
                results.append(result)
    return results


# ----------------------------------------------------------------------------------------------------------------------
def restore_handle_visibility_connections(handle_name, namespace=None):
    controller = ctrl_utils.get_controller()
    handle = get_handle(handle_name, controller, namespace)
    if handle is None:
        return dict(status='warning', warning=f'Unable to find node: {handle_name}')
    failed_curves = []
    connected_plugs = []
    if handle.cached_curve_visibility_connections:
        for curve in handle.curves:
            curve_name = curve.get_selection_string()  # this is to support legacy Main part
            plug_name = handle.cached_curve_visibility_connections.get(curve_name)
            if plug_name:
                try:
                    visibility_plug = f'{curve.get_selection_string()}.visibility'
                    controller.scene.connectAttr( plug_name, visibility_plug )
                    connected_plugs.append((plug_name, visibility_plug))
                except Exception as e:
                    logging.getLogger('rig_build').error(traceback.format_exc())
                    failed_curves.append(curve.name)
    handle.cached_curve_visibility_connections = dict()
    if failed_curves:
        return dict(
            status='warning',
            warning=f'Unable to connect to visibility on curves: {", ".join(failed_curves)}'
        )
    if connected_plugs:
        return dict(
            info='Connected plugs:\n\n{}'.format(
                '\n'.join(
                    [ '{} ----> {}'.format(x[0], x[1]) for x in connected_plugs ]
                )
            )
        )


# ----------------------------------------------------------------------------------------------------------------------
def set_auto_rigged_property():
    ctrl_utils.get_controller().root.auto_rigged = False


# ----------------------------------------------------------------------------------------------------------------------
def delete_handle_shapes(handle_names, namespace=None):
    missing_handles = []
    controller = ctrl_utils.get_controller()
    for handle_name in handle_names:
        full_handle_name = handle_name
        if namespace:
            full_handle_name = f'{namespace}:{full_handle_name}'
        if full_handle_name not in controller.named_objects:
            missing_handles.append(full_handle_name)
            continue

        handle = controller.named_objects[full_handle_name]
        handle.shape = None
        if handle.curves:
            for curve in handle.curves:
                curve_name = curve.get_selection_string()  # support for legacy Main Part
                visibility_connections = controller.scene.listConnections(
                    f'{curve_name}.visibility', s=True, d=False, plugs=True
                )
                if visibility_connections:
                    handle.cached_curve_visibility_connections[curve_name] = visibility_connections[0]
            del curve
            controller.schedule_objects_for_deletion(handle.curves)
        if handle.base_curves:
            controller.schedule_objects_for_deletion(handle.base_curves)
    controller.delete_scheduled_objects()
    if missing_handles:
        return dict(
            status='warning',
            warning='Unable to find handles: %s' % missing_handles
        )
