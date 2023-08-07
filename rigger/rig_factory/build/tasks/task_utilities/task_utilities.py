import os
import copy
import glob
import json
import functools
import logging
import traceback
import subprocess
import Snowman3.rigger.rig_api.parts as prtls
import Snowman3.rigger.rig_factory.objects as obs
import Snowman3.rigger.rig_api.part_hierarchy as pth
import Snowman3.utilities.version as irv
import Snowman3.rigger.rig_factory.environment as env
import Snowman3.rigger.rig_factory.system_signals as sig
import Snowman3.rigger.rig_factory.utilities.file_utilities as fut
import Snowman3.rigger.rig_factory.utilities.geometry_utilities as gtl
from Snowman3.rigger.rig_factory.objects.node_objects.joint import Joint
import Snowman3.rigger.rig_factory.utilities.dynamic_file_utilities as dfu
from Snowman3.rigger.rig_factory.build.tasks.task_objects import BuildTask
import Snowman3.rigger.rig_factory.build.utilities.general_utilities as gut
import Snowman3.rigger.rig_factory.build.utilities.set_utilities as stu
#import Snowman3.rigger.rig_factory.build.utilities.bifrost_utilities as bfu
import Snowman3.rigger.rig_factory.build.utilities.viewport_utilities as vpu
import Snowman3.rigger.rig_factory.utilities.space_switcher_utilities as spcu
import Snowman3.rigger.rig_factory.utilities.deformation_rig_utilities as dru
import Snowman3.rigger.rig_factory.build.utilities.controller_utilities as cut
import Snowman3.rigger.rig_factory.build.utilities.export_data_utilities as edu
#import Snowman3.utilities.shotgun_utilities.shotgun_utils as sgutls
import Snowman3.rigger.rig_factory.build.utilities.deformation_layer_utilities as dlu
import Snowman3.rigger.rig_factory.objects.deformation_stack_objects.deformation_stack as stk
#import maya_tools.deformer_utilities.Deformer_Data_Input_Check as ddic

def create_container(container_kwargs, skip_existing=False):
    controller = cut.get_controller()
    if controller.root and skip_existing:
        return dict(
            info='Skipping Container creating because the controller already had a root: "%s".' % controller.root.name
        )
    prtls.create_root(
        container_kwargs.pop('klass'),
        **container_kwargs
    )


def configure_container(skip_existing=False):
    controller = cut.get_controller()
    if not controller.root:
        raise Exception('Rig not found.')
    if skip_existing and controller.root.plugs.exists('irigCodeVersion'):
        return dict(
            info='Container already configured.'
        )
    controller.root.create_plug(
        'irigCodeVersion',
        dt='string',
        keyable=True
    )
    irig_version = irv.get_irig_version()
    if irig_version:
        controller.root.plugs['irigCodeVersion'].set_value(irig_version)
    else:
        controller.root.plugs['irigCodeVersion'].set_value('DEV')

    geometry_paths = controller.root.geometry_paths
    geometry_path_plug = controller.root.create_plug('geometry_path', dt='string')
    if geometry_paths:
        geometry_path_plug.set_value(str(geometry_paths[0]))
    geometry_path_plug.set_channel_box(True)
    geometry_path_plug.set_locked(True)

    # add version info that the current build is pulling from on container
    build_directory_path = env.local_build_directory
    build_directory_plug = controller.root.create_plug('build_directory', dt='string')
    build_directory_plug.set_value(str(build_directory_path))
    build_directory_plug.set_channel_box(True)
    build_directory_plug.set_locked(True)

    #  add parent rig path on container
    entity = os.environ['TT_ENTNAME']
    project = os.environ['TT_PROJCODE']

    parent_rig_path_plug = controller.root.create_plug(
        'parent_rig_path',
        dt='string'
    )

    parent_entity_name_list = sgutls.get_parent_asset_names(project, entity)
    if parent_entity_name_list:
        for parent_entity in parent_entity_name_list:
            parent_build_directory = '%s/rig' % dfu.get_products_directory(project, parent_entity)

            list_of_files = glob.glob('%s/*.ma' % parent_build_directory)

            if list_of_files:
                latest_path = sorted(list_of_files, key=os.path.getmtime)[-1]
                # check if there are any back slash in the directory, then change it to forward slash
                if latest_path and "\\" in latest_path:
                    latest_path = latest_path.replace('\\', '/')

                    parent_rig_path_plug.set_value(str(latest_path))

    else:
        parent_rig_path_plug.set_value('N/A')
    controller.root.parts_by_uuid[controller.root.part_uuid] = controller.root
    parent_rig_path_plug.set_channel_box(True)
    parent_rig_path_plug.set_locked(True)


def append_entity_data(entity_name, rig_blueprint, useful_rig_blueprint_keys=None):
    """ Store each entity/parent blueprint by entity name on the container in memory, to reference for overrides etc """
    controller = cut.get_controller()

    # Only keep certain data that is used elsewhere, to avoid saving huge skin weight dicts etc
    rig_blueprint_data = {}
    if useful_rig_blueprint_keys is None:
        useful_rig_blueprint_keys = ('delete_geometry_names', 'delete_on_finalize_data')
    for key in useful_rig_blueprint_keys:
        if key in rig_blueprint:
            rig_blueprint_data[key] = rig_blueprint[key]

    controller.root.entities_data[entity_name] = dict(
        rig_blueprint=rig_blueprint_data
    )


def create_container_tasks(entity_builds, root_task, skip_existing=False):
    blueprint = entity_builds[0].rig_blueprint
    if not blueprint:
        raise Exception(
            'Blueprint not found: %s/%s' % (
                entity_builds[0].build_directory,
                entity_builds[0].rig_blueprint_file_name
            )
        )

    container_kwargs = copy.deepcopy(blueprint)
    container_kwargs.pop('part_members', None)

    create_container_root = BuildTask(
        parent=root_task,
        name='Container'
    )

    for build in entity_builds:
        BuildTask(
            build=build,
            parent=create_container_root,
            name='Build.before_create_container()',
            function=build.create_callback('before_create_container'),
        )
    BuildTask(
        parent=create_container_root,
        name='Create Container',
        function=functools.partial(
            create_container,
            container_kwargs,
            skip_existing=skip_existing
        ),
        layer=os.environ['TT_ENTNAME']
    )
    BuildTask(
        parent=create_container_root,
        name='Configure Container',
        function=functools.partial(
            configure_container,
            skip_existing=skip_existing
        ),
        layer=os.environ['TT_ENTNAME'],
    )

    root = BuildTask(
        parent=root_task,
        name='Store Source Blueprints'
    )
    for build in entity_builds:
        BuildTask(
            build=build,
            parent=root,
            name='Append %s blueprint' % build.entity,
            function=functools.partial(
                append_entity_data,
                build.entity,
                build.rig_blueprint
            ),
        )

    for build in entity_builds:
        BuildTask(
            build=build,
            name='Build.after_create_container()',
            function=build.create_callback('after_create_container'),
            parent=create_container_root,
        )


def initialize_build_directory(source_directory, temp_directory):
    if not source_directory or not os.path.exists(source_directory):
        raise Exception('Source Directory Doesnt exist: %s' % source_directory)

    copy_directory(
        source_directory,
        temp_directory
    )
    sig.set_build_directory(temp_directory)
    if not env.local_build_directory == temp_directory:
        raise Exception('Failed to set build_directory to: %s' % temp_directory)


def copy_directory(source_directory, target_directory):
    """
    Copies contents of source_directory to latest realtime_build product
    """
    realtime_directory = os.path.dirname(target_directory)
    logger = logging.getLogger('rig_build')
    if not os.path.exists(realtime_directory):
        os.makedirs(realtime_directory)
    if os.path.exists(target_directory):
        proc = subprocess.Popen(
            'rmdir /s/q "%s"' % target_directory,
            shell=True
        )
        logger.info('Attempting to remove existing directory: %s' % target_directory)
        proc.wait()
    logger.info('Attempting to copy latest build to: %s' % target_directory)
    proc = subprocess.Popen(
        'robocopy %s %s /E /S' % (
            source_directory,
            target_directory,
        ),
        shell=True
    )
    proc.wait()
    if not os.path.exists(target_directory):
        raise Exception('Target Directory Does not exist')


def import_low_geometry(entity_builds, root_task):
    for build in entity_builds:
        for property_name in ['low_geometry']:
            paths_property_name = '%s_paths' % property_name
            if paths_property_name in build.rig_blueprint:
                BuildTask(
                    parent=root_task,
                    build=build,
                    namespace=None,
                    name='Import %s' % property_name.title(),
                    function=functools.partial(
                        import_geometry_paths,
                        build.entity,
                        property_name,
                        build.rig_blueprint[paths_property_name]
                    )
                )


def import_geometry_paths(*args, **kwargs):
    new_geometry = gtl.import_geometry_paths(*args, **kwargs)


def import_placements(entity_builds, root_task):
    import_placements_task = BuildTask(
        name='Import Placements',
        parent=root_task
    )
    for build in entity_builds:
        BuildTask(
            build=build,
            name='Before Placement Utilities',
            parent=import_placements_task,
            function=build.create_callback('before_placements')
        )
    for build in entity_builds:
        placements_path = build.rig_blueprint['product_paths']['placements']
        BuildTask(
            build=build,
            parent=import_placements_task,
            name='Import Placement Nodes',
            function=functools.partial(
                stu.import_placement_nodes,
                placements_path,
                create_plug=build.entity == os.environ['TT_ENTNAME']
            )
        )

    for build in entity_builds:
        BuildTask(
            build=build,
            name='After Placement Utilities',
            parent=import_placements_task,
            function=build.create_callback('after_placements')
        )


def import_bifrost(entity_builds, root_task):
    bifrost_task = BuildTask(
        name='Import Bifrost',
        parent=root_task
    )
    for build in entity_builds:
        bifrost_path = build.rig_blueprint['product_paths']['bifrost']
        if bifrost_path:
            BuildTask(
                build=build,
                parent=bifrost_task,
                name='Import Bifrost',
                function=functools.partial(
                    bfu.import_bifrost_nodes,
                    build.rig_blueprint['product_paths']['bifrost'],
                    create_plug=build.entity == os.environ['TT_ENTNAME']
                )
            )


def cleanup_maya_after_imports(suspend_refresh_afterwards=True):
    """
    Fixes an unstable Maya state when updating geo on an asset, specifically one with placements
    but likely other assets too.

    If Maya is not refreshed after the imports (primarily the placements ie. maya scene import,)
    then a glitch may be created in Maya, when the Python garbage collection is forced through
    'delete_scheduled_objects', at any point in the code before the reload.
    Possibly also because of the 'toggle state' as part of the geo update.

    The glitch manifests as either: (in sets with placements)
     - Wireframe rectangles left in the scene, hideable as 'plugin shapes' but not visible in the outliner etc
     - a maya crash on toggling to rig state (not investigated in detail)

    This glitch is only the case because of the maya refresh being disabled for most of the build.
    """
    controller = cut.get_controller()
    controller.scene.refresh(suspend=False)
    controller.scene.refresh()
    # There isn't a command to check whether refreshes were already suspended or not, so it has to be a parameter
    if suspend_refresh_afterwards:
        controller.scene.refresh(suspend=True)


def load_export_data(entity_builds, root_task):
    export_data_task = BuildTask(
        name='Load Export Data',
        parent=root_task
    )
    for build in entity_builds:
        BuildTask(
            build=build,
            name='Before Export Data',
            parent=export_data_task,
            function=build.create_callback('before_export_data')
        )
    for build in entity_builds:
        BuildTask(
            build=build,
            parent=export_data_task,
            name='Load Export Data',
            function=functools.partial(
                edu.load_export_data,
                build.namespace,
                build.rig_blueprint['product_paths']['export_data'],
                build.rig_blueprint['product_paths']['fin_export_data'],
                build.rig_blueprint['product_paths']['set_snap_locators'],
                create_plugs=build.entity == os.environ['TT_ENTNAME']
            )
        )

    for build in entity_builds:
        BuildTask(
            build=build,
            name='After Export Data',
            parent=export_data_task,
            function=build.create_callback('after_export_data')
        )


def import_previs_lights(entity_builds, root_task):
    previs_lights_task = BuildTask(
        name='Import Previs Lights',
        parent=root_task
    )

    for build in entity_builds:
        BuildTask(
            build=build,
            parent=previs_lights_task,
            name='Import Previs Lights',
            function=functools.partial(
                stu.import_previs_lights,
                os.environ['TT_PROJCODE'],
                build.entity
            )
        )


def set_camera_clipping_plane(entity_builds, root_task):
    set_camera_clipping_plane_task = BuildTask(
        name='Set Camera Planes',
        parent=root_task
    )

    for build in entity_builds:
        BuildTask(
            build=build,
            parent=set_camera_clipping_plane_task,
            name='Set Camera Planes',
            function=functools.partial(
                vpu.set_camera_clipping_planes,
            )
        )


def create_origin_geometry(entity_builds, root_task):
    origin_geometry_task = BuildTask(
        parent=root_task,
        name='Origin Geometry'
    )
    for build in entity_builds:
        BuildTask(
            parent=origin_geometry_task,
            build=build,
            name='Before Create Origin Geometry',
            function=build.create_callback('before_create_origin_geometry')
        )
    for build in entity_builds:
        BuildTask(
            parent=origin_geometry_task,
            build=build,
            name='Create Origin Geometry',
            function=functools.partial(
                gtl.create_origin_geometry,
                build.rig_blueprint.get('origin_geometry_data', [])
            )
        )
    for build in entity_builds:
        BuildTask(
            parent=origin_geometry_task,
            build=build,
            name='After Create Origin Geometry',
            function=build.create_callback('after_create_origin_geometry')
        )


def get_create_parts_tasks(entity_builds, root_task):

    create_parts_task = BuildTask(
        name='Parts',
        parent=root_task
    )

    for build in entity_builds:
        entity_task = BuildTask(
            build=build,
            parent=create_parts_task,
            name='%s (Accessory)' % build.entity if build.namespace else build.entity
        )
        BuildTask(
            parent=entity_task,
            name='Before Create parts',
            function=build.create_callback('before_create_parts')
        )
        get_part_creation_tasks(
            entity_task,
            build,
            copy.deepcopy(build.rig_blueprint['part_members']),
            None
        )
        BuildTask(
            build=build,
            name='After Create parts',
            parent=entity_task,
            function=build.create_callback('after_create_parts')
        )


def initialise_deformation_stack(entity_builds, root_task):
    """Defines build steps where the deformation stack is starting to get created. Namely adjusting maya's evaluation
    settings and building the deformation layers."""

    setup_deformation_stack_task = BuildTask(
        parent=root_task,
        name='Setup Deformation Stack'
    )

    # Switch to dg evaluation and turn off GPU override
    BuildTask(
        parent=setup_deformation_stack_task,
        name="Prepare Evaluation Settings",
        function=dlu.set_evaluation_settings
    )

    # Build the stack elements without connecting them
    for build, deformation_layers_data in _filter_deformation_stack_data(entity_builds):
        BuildTask(
            parent=setup_deformation_stack_task,
            name="Build Stack Layers",
            build=build,
            function=functools.partial(
                stk.create_deformation_layers,
                deformation_layers_data,
                build.entity)
        )


def _filter_deformation_stack_data(entity_builds):
    """
    Remove child deformation stack geos from parent stacks, for deformation stack creation, to resolve clashes

    From deformation_layers_widget.LayerModel.get_deform_layers_data_in_property_format:
    layer_data[layer_item.name] = [[x.name for x in layer_item.children], layer_row]
    """
    logger = logging.getLogger('rig_build')

    geos_already_listed = []
    for i, build in enumerate(entity_builds):
        # Get deformation later data if found for entity (child first before parents)
        deformation_layers_data = build.rig_blueprint.get('deformation_layers', None)
        if not deformation_layers_data:
            continue

        # Remove geo from data if a child entity already mentioned the geo name, otherwise save geo name for checking
        deformation_layers_data_filtered = {}
        this_stack_geos = set()
        for layer_name, (layer_geos, layer_row) in deformation_layers_data.iteritems():
            filtered_layer_geos = []
            for mesh_transform_name in layer_geos:
                if mesh_transform_name not in geos_already_listed:
                    this_stack_geos.add(mesh_transform_name)
                    filtered_layer_geos.append(mesh_transform_name)
                else:
                    logger.warning("Excluding clashing geo '{}' from asset {}'s '{}' deformation layer data".format(
                        mesh_transform_name, build.entity, layer_name))
            if i and filtered_layer_geos:  # Omit parent layer data altogether if it has no unique geos left
                deformation_layers_data_filtered[layer_name] = [filtered_layer_geos, layer_row]

        if this_stack_geos:
            geos_already_listed.extend(sorted(this_stack_geos))

        if not i:
            # Don't change data of the current asset, as it will override the parent anyway,
            # and otherwise empty layers may be lost
            yield build, deformation_layers_data
        else:
            # Return the data for the current entity, with only valid geo names (in terms of clashing entities)
            yield build, deformation_layers_data_filtered


def connect_deformation_layers_stack(entity_builds, root_task):
    """Updates the information of the stack with the loaded deformers after these have been imported into the scene.
    Then it connects the layers in the order specified inside the widget."""

    connect_deformation_stack_task = BuildTask(
        parent=root_task,
        name="Connect Deformation Stack"
    )

    for build in entity_builds:
        BuildTask(
            parent=connect_deformation_stack_task,
            build=build,
            name="Connect Layers",
            function=functools.partial(
                dlu.connect_stack_layers,
                build.entity)
        )


def assert_guide_part_joint_count_data(value):
    if not bool(value):
        return dict(
            status='warning',
            warning='Unable to find a record of guide-state joint-count data'
        )


def check_joint_count(part_name, joint_count):
    controller = cut.get_controller()
    if part_name not in controller.named_objects:
        return dict(
            status='warning',
            warning='Unable to find part "%s"' % part_name
        )
    part = controller.named_objects[part_name]
    if len(part.joints) != joint_count:
        raise Exception(
            'The part <%s name="%s"> had %s joints while its guide state had %s' % (
                part.__class__.__name__,
                part_name,
                len(part.joints),
                joint_count)
        )


def get_part_creation_tasks(
        parent_task,
        build,
        part_blueprints,
        part_owner_name
):
    for part_blueprint in part_blueprints:
        create_part_task = BuildTask(
            build=build,
            parent=parent_task,
            name='%s.create()' % part_blueprint.get('name', part_blueprint['klass']),
            function=functools.partial(
                create_part,
                part_blueprint,
                part_owner_name
            ),
        )
        get_part_creation_tasks(
            create_part_task,
            build,
            part_blueprint.pop('part_members', []),
            obs.__dict__[part_blueprint['klass']].get_predicted_name(
                **part_blueprint
            )
        )


def create_part(part_blueprint, part_owner_name):
    controller = cut.get_controller()
    namespace_part_owner = '%s:%s' % (controller.namespace, part_owner_name)
    if part_owner_name is None:
        if controller.root is None:
            raise Exception('Rig not found')
        part_owner = controller.root
        parent = part_owner.control_group
    elif namespace_part_owner in controller.named_objects:  # parented to name-spaced (accessory) parts
        part_owner = controller.named_objects[namespace_part_owner]
        parent = part_owner
    elif part_owner_name in controller.named_objects:  # Local parts re-parented to name-spaced parts
        part_owner = controller.named_objects[part_owner_name]
        parent = part_owner
    else:
        raise Exception('Unable to find part_owner "%s"' % part_owner_name)
    logging.getLogger('rig_build').info('Creating part %s under %s' % (part_blueprint['klass'], part_owner_name))
    opposing_state_joint_count = part_blueprint.pop('opposing_state_joint_count', None)
    predicted_name = obs.__dict__[part_blueprint['klass']].get_predicted_name(
        **part_blueprint
    )
    part = controller.create_object(
        part_blueprint['klass'],
        part_owner=part_owner,
        hierarchy_parent=part_owner,
        parent=parent,
        **copy.deepcopy(part_blueprint)  # Part.create functions tend to edit kwargs, so its best we do a deep copy
    )
    part.get_root().parts_by_uuid[part.part_uuid] = part
    if opposing_state_joint_count is not None and opposing_state_joint_count != len(part.joints):
        if isinstance(part, (obs.ContainerGuide, obs.PartGuide)):
            logging.getLogger('rig_build').warning(
                'Joint count mismatch on %s between states. RIG:%s GUIDE:%s' % (
                        part_blueprint['klass'],
                        opposing_state_joint_count,
                        len(part.joints)
                    )
                )
        else:
            raise Exception(
                'Joint count mismatch on %s between states. Guide:%s RIG:%s' % (
                        part_blueprint['klass'],
                        opposing_state_joint_count,
                        len(part.joints)
                    )
                )

    if part.name != predicted_name:
        raise Exception(
            'The created part name "%s" did not match the predicted name: "%s"' % (part.name, predicted_name)
        )
    if isinstance(
            part, (obs.Main, obs.MainGuide)):
        return dict(
            status='warning',
            warning='Legacy part type: %s' % part.__class__.__name__
        )
    return dict(
        info='Created Part "%s" uuid=%s type=%s layer=%s namespace=%s' % (
            part.name,
            part.part_uuid,
            part.__class__.__name__,
            part.layer,
            part.namespace
        )
    )


def get_part_post_creation_tasks(parent_task, build, part_blueprints):
    for part_blueprint in part_blueprints:
        part_blueprint = copy.deepcopy(part_blueprint)
        post_create_part_task = BuildTask(
            build=build,
            parent=parent_task,
            name='%s.post_create()' % part_blueprint.get('name', part_blueprint['klass']),
            function=functools.partial(
                post_create_part,
                copy.deepcopy(part_blueprint)
            ),
        )
        get_part_post_creation_tasks(
            post_create_part_task,
            build,
            part_blueprint.pop('part_members', [])
        )


def get_post_create_tasks(entity_builds, root_task):
    main_blueprint = entity_builds[0].rig_blueprint
    container_kwargs = copy.deepcopy(main_blueprint)
    container_kwargs.pop('part_members', None)
    post_create_task = BuildTask(
        name='Post Create Parts',
        parent=root_task
    )
    for build in entity_builds:
        BuildTask(
            build=build,
            name='Before Post Create Parts',
            parent=post_create_task,
            function=build.create_callback('before_post_create')
        )
    for build in entity_builds:
        entity_task = BuildTask(
            build=build,
            parent=post_create_task,
            name='%s (Accessory)' % build.entity if build.namespace else build.entity
        )
        get_part_post_creation_tasks(
            entity_task,
            build,
            build.rig_blueprint['part_members']
        )
    BuildTask(
        parent=post_create_task,
        name='Post Create Container',
        function=functools.partial(
            post_create_container,
            container_kwargs
        )
    )

    for build in entity_builds:
        BuildTask(
            build=build,
            name='After Post Create',
            parent=post_create_task,
            function=build.create_callback('after_post_create')
        )


def get_hierarchy_tasks(entity_builds, root_task):
    hierarchy_task = BuildTask(
        name='Hierarchy',
        parent=root_task
    )
    part_joints_task = BuildTask(
        parent=hierarchy_task,
        name='Update joint parents',
    )
    for build in entity_builds:
        entity_task = BuildTask(
            build=build,
            name=build.entity,
            parent=part_joints_task,
        )
        get_joint_hierarchy_parent_tasks(
            copy.deepcopy(build.rig_blueprint['part_members']),
            entity_task
        )
    set_parents_task = BuildTask(
        parent=hierarchy_task,
        name='Set hierarchy parents',
    )
    for build in entity_builds:
        entity_task = BuildTask(
            build=build,
            name=build.entity,
            parent=set_parents_task,
        )
        hierarchy_data = build.rig_blueprint['hierarchy_data']
        if not isinstance(hierarchy_data, list):
            raise Exception(
                'Invalid hierarchy_data type: %s. Please re-save blueprint for: %s ' % (
                    type(hierarchy_data),
                    build.entity)
            )
        for h in build.rig_blueprint['hierarchy_data']:
            if not h.get('part_uuid', None):
                entity_task.status = 'warning'
                entity_task.warning = 'Legacy Hierarchy data detected. Please re-save blueprint for: %s ' % build.entity
                break
        BuildTask(
            build=build,
            name='Before Set Parent Joints (Legacy)',
            parent=entity_task,
            function=build.create_callback('before_set_parent_joints')
        )
        get_part_hierarchy_tasks(
            entity_task,
            build.rig_blueprint['hierarchy_data']
        )
        BuildTask(
            build=build,
            name='After Set Parent Joints (Legacy)',
            parent=entity_task,
            function=build.create_callback('after_set_parent_joints')
        )
    BuildTask(
        name='Check Hierarchy',
        parent=hierarchy_task,
        create_children_function=generate_hierarchy_check_tasks
    )


def generate_hierarchy_check_tasks():
    """Check that parts are not parented to ancestors etc"""
    tasks = []
    controller = cut.get_controller()
    for part in controller.root.get_parts():
        new_task = BuildTask(
            name=part.name,
            function=functools.partial(
                check_part_hierarchy_parent,
                part.name
            )
        )
        tasks.append(new_task)
    return tasks


def check_part_hierarchy_parent(part_name):
    controller = cut.get_controller()
    part = controller.named_objects[part_name]
    if part.hierarchy_parent in pth.get_descendants(part):
        raise Exception(
            '%s is parented to its own descendant: %s' % (
                part_name,
                part.hierarchy_parent.name
            )
        )


def set_joints_hierarchy_parent(part_name):
    controller = cut.get_controller()
    if controller.namespace:
        part_name = '%s:%s' % (controller.namespace, part_name)
    part = controller.named_objects[part_name]
    for joint in part.joints:
        joint.hierarchy_parent = part


def get_joint_hierarchy_parent_tasks(part_blueprints, parent_task):
    for part_blueprint in part_blueprints:
        part_name = obs.__dict__[part_blueprint['klass']].get_predicted_name(
            **part_blueprint
        )
        new_task = BuildTask(
            parent=parent_task,
            name=part_name,
            function=functools.partial(
                set_joints_hierarchy_parent,
                part_name
            )
        )
        part_members = part_blueprint.get('part_members', None)
        if part_members:
            get_joint_hierarchy_parent_tasks(
                part_members,
                new_task
            )


def get_part_hierarchy_tasks(parent_task, hierarchy_data):
    for i in range(len(hierarchy_data)):
        if 'parent_part_name' not in hierarchy_data[i]:
            lines = [
                'This blueprint was saved with a broken version of OwnerMember branch.',
                'Please revert to a blueprint built before 12/14/2022'
            ]
            raise Exception(' '.join(lines))
        part_name = hierarchy_data[i]['part_name']
        part_uuid = hierarchy_data[i]['part_uuid']
        parent_name = hierarchy_data[i]['parent_name']
        parent_part_uuid = hierarchy_data[i]['parent_part_uuid']
        parent_part_name = hierarchy_data[i]['parent_part_name']
        parent_joint_index = hierarchy_data[i]['parent_joint_index']
        legacy_parent_name = hierarchy_data[i].get('legacy_parent_name')
        legacy_joint_index = hierarchy_data[i].get('legacy_joint_index')
        legacy_data = hierarchy_data[i].get('legacy_data')

        if not legacy_data:
            BuildTask(
                parent=parent_task,
                name='%s' % part_name,
                function=functools.partial(
                    pth.set_hierarchy_parent_with_data,
                    part_uuid,
                    parent_part_uuid,
                    parent_part_name,
                    parent_joint_index,
                    part_name,
                    parent_name
                )
            )
        else:
            BuildTask(
                parent=parent_task,
                name='%s (Legacy)' % part_name,
                function=functools.partial(
                    pth.set_legacy_hierarchy_parent,
                    part_name,
                    parent_name,
                    legacy_parent_name=legacy_parent_name,
                    legacy_joint_index=legacy_joint_index
                )
            )


def set_joint_group_position(part_name, namespace=None):
    controller = cut.get_controller()
    if namespace:
        part_name = '%s:%s' % (controller.namespace, part_name)
    if part_name not in controller.named_objects:
        raise Exception('part not found: %s' % part_name)
    part = controller.named_objects[part_name]
    if part.disconnected_joints:
        return dict(
            info='Did not set group position. %s.disconnected_joints=True' % part.name
        )
    if not part.joint_group:
        return dict(
            info='Did not set group position. Unable to find joint_group for %s ' % part
        )
    joint_ancestors = [x for x in pth.get_ancestors(part) if isinstance(x, Joint)]
    if not joint_ancestors:
        return dict(
            info='Did not set group position. Unable to find any joints in ancestors of %s ' % part
        )
    if not part.joints:
        return dict(
            info='Did not set group position. Part had no joints: %s ' % part
        )
    last_joint_ancestor = joint_ancestors[-1]
    joint_matrix = last_joint_ancestor.get_matrix()
    part.joint_group.set_matrix(joint_matrix)
    logging.getLogger('rig_build').info(
        'Snapped joint group for "%s" to joint ancestor: "%s"' % (
            part,
            last_joint_ancestor.name
        )
    )
    return dict(
        info='Snapped joint group for "%s" to joint ancestor: "%s"' % (
            part,
            last_joint_ancestor.name
        )
    )


def get_part_deformation_joint_tasks(parent_task, part_blueprints):
    for part_blueprint in part_blueprints:
        part_name = obs.__dict__[part_blueprint['klass']].get_predicted_name(
            **part_blueprint
        )
        if parent_task.namespace:
            part_name = '%s:%s' % (parent_task.namespace, part_name)
        task_name = part_name
        if part_blueprint.get('disconnected_joints', False):
            task_name = '%s (Disconnected)' % part_name
        part_task = BuildTask(
            parent=parent_task,
            name=task_name,
            create_children_function=functools.partial(
                generate_deform_joint_tasks,
                part_blueprint
            )
        )
        get_part_deformation_joint_tasks(
            part_task,
            part_blueprint.get('part_members', [])
        )


def generate_group_position_tasks(parent_task, part_blueprints):
    for part_blueprint in part_blueprints:
        part_name = obs.__dict__[part_blueprint['klass']].get_predicted_name(
            **part_blueprint
        )
        if parent_task.namespace:
            part_name = '%s:%s' % (parent_task.namespace, part_name)
        task_name = part_name
        if part_blueprint.get('disconnected_joints'):
            task_name = '%s ( Disconnected )' % task_name
        part_task = BuildTask(
            parent=parent_task,
            name=task_name,
            function=functools.partial(
                set_joint_group_position,
                part_name
            )
        )
        generate_group_position_tasks(
            part_task,
            part_blueprint.get('part_members', [])
        )


def generate_deform_joint_tasks(part_blueprint):
    """
    recursive function iterates through the blueprint tree and generates tasks that create deformation joints
    """
    new_tasks = []
    controller = cut.get_controller()
    part_name = obs.__dict__[part_blueprint['klass']].get_predicted_name(
        **part_blueprint
    )
    if part_name not in controller.named_objects:
        raise Exception('part not found: %s' % part_name)
    part = controller.named_objects[part_name]
    if hasattr(part, 'create_deformation_rig'):
        legacy_task = BuildTask(
            name='LEGACY deformation rig (%s %s)' % (part.name, part.__class__.__name__),
            function=functools.partial(
                legacy_create_deformation_rig,
                part.name,
                part.__class__.__name__
            )
        )
        new_tasks.append(legacy_task)
    else:
        for joint in part.joints:
            joint_task = BuildTask(
                name=joint.name,
                function=functools.partial(
                    create_deformation_joint,
                    part.name,
                    joint.name
                )
            )
            assert not joint_task.layer
            new_tasks.append(joint_task)
    return new_tasks


def get_part_deformation_joint_parent_tasks(parent_task, part_blueprints):
    """
    recursive function iterates through the blueprint tree and generates tasks that parent the deformation joints
    """
    for part_blueprint in part_blueprints:
        predicted_part_name = obs.__dict__[part_blueprint['klass']].get_predicted_name(
            **part_blueprint
        )
        if parent_task.namespace:
            predicted_part_name = '%s:%s' % (
                parent_task.namespace,
                predicted_part_name
            )
        part_task = BuildTask(
            parent=parent_task,
            name=predicted_part_name,
            create_children_function=functools.partial(
                generate_parent_deformation_joint_tasks,
                predicted_part_name
            )
        )
        member_blueprints = part_blueprint.get('part_members')
        if member_blueprints:
            get_part_deformation_joint_parent_tasks(
                part_task,
                member_blueprints
            )


def generate_parent_deformation_joint_tasks(part_name):
    """
    resolves parent hierarchy for deformation joints of one part.
    """
    tasks = []
    controller = cut.get_controller()
    if part_name not in controller.named_objects:
        raise Exception('part not found: %s' % part_name)
    part = controller.named_objects[part_name]
    for joint in part.joints:
        joint_task = BuildTask(
            name=joint.name,
            function=functools.partial(
                parent_deformation_joint,
                joint.name,
                disconnected=part.disconnected_joints
            )
        )
        tasks.append(joint_task)
    return tasks


def get_handle_limits_tasks(entity_builds, root_task):
    create_handle_limits_task = BuildTask(
        name='Handle Transform Limits',
        parent=root_task
    )
    for build in entity_builds:
        limits_task = BuildTask(
            build=build,
            parent=create_handle_limits_task,
            name='%s (Accessory)' % build.entity if build.namespace else build.entity,
        )

        part_blueprints = gut.flatten_blueprint(
            build.rig_blueprint,
            include_self=False
        )
        for part_blueprint in part_blueprints:
            handle_limits = part_blueprint.get('handle_limits')
            if handle_limits:
                BuildTask(
                    build=build,
                    parent=limits_task,
                    name='Handle Limits (%s)' % part_blueprint['klass'],
                    function=functools.partial(
                        set_handle_limits,
                        handle_limits,
                        namespace=build.namespace
                    )
                )


def set_handle_rotate_order():
    """
    finds rotate orders in show_config.json and sets them on specified handles for all parts of the same class
    """
    controller = cut.get_controller()
    asset_type = controller.root.__class__.__name__  # type of asset: biped, character, quadruped, environment, prop...
    rot_orders = ['xyz', 'yzx', 'zxy', 'xzy', 'yxz', 'zyx']

    show_config_dict = fut.get_show_config_data()
    asset_rotate_order = show_config_dict.get('{}_rotate_order'.format(asset_type.lower()))

    # if we find rotate order data, check all parts and see if we find the klass type on the dictionary
    if asset_rotate_order:
        for part in controller.root.get_parts():
            partclass = part.__class__.__name__  # klass of the part: BipedArm, FkChain, Handle...
            if partclass in asset_rotate_order:
                # if the part klass is found, set the rotate orders for the specified handles
                for hndl, ro in asset_rotate_order[partclass].items():
                    hndlname = hndl  # set handle name to entry, works for Root klass that have None as side
                    if partclass != "Root" and partclass != "Main":
                        side = part.side.upper()[0]  # returns L, R or C
                        rootname = part.root_name
                        hndlname = '{}_{}_{}'.format(side, rootname, hndl)  # constructing the handle name
                    if controller.scene.objExists(hndlname):  # if the handle exists, set the rotate order
                        handle = controller.named_objects[hndlname]
                        handle.plugs['rotateOrder'].set_value(rot_orders.index(ro))


def set_handle_limits(handle_limits, namespace):
    controller = cut.get_controller()
    missing_handles = []
    for handle_name in handle_limits:
        long_name = handle_name
        if namespace:
            long_name = '%s:%s' % (namespace, handle_name)
        if long_name in controller.named_objects:
            controller.named_objects[long_name].set_transform_limits(handle_limits[handle_name])
        else:
            missing_handles.append(long_name)
    if missing_handles:
        return dict(
            status='warning',
            warning='Unable to apply transform limits due to mising nodes:\n\n%s' % '\n'.join(missing_handles)
        )


def finish_create_parts(entity_builds, root_task):
    main_blueprint = entity_builds[0].rig_blueprint
    container_kwargs = copy.deepcopy(main_blueprint)
    container_kwargs.pop('part_members', None)

    finish_task = BuildTask(
        name='Finish Create',
        parent=root_task
    )

    for build in reversed(entity_builds):
        BuildTask(
            build=build,
            parent=finish_task,
            name='Before Finish Create Parts',
            function=build.create_callback('before_finish_create')
        )
    for build in entity_builds:
        finish_entity_task = BuildTask(
            build=build,
            parent=finish_task,
            name='%s (Accessory)' % build.entity if build.namespace else build.entity
        )

        part_blueprints = gut.flatten_blueprint(
            build.rig_blueprint,
            include_self=False
        )
        for part_blueprint in part_blueprints:
            BuildTask(
                build=build,
                parent=finish_entity_task,
                name='%s.finish_create()' % part_blueprint['klass'],
                function=functools.partial(
                    finish_create_part,
                    part_blueprint
                )
            )

    BuildTask(
        parent=finish_task,
        name='Finish Create Container',
        function=functools.partial(
            finish_create_container,
            container_kwargs
        )
    )

    for build in reversed(entity_builds):
        BuildTask(
            build=build,
            name='After Finish Create',
            parent=finish_task,
            function=build.create_callback('after_finish_create')
        )


def post_create_part(kwargs):
    kwargs.pop('name', None)
    current_controller = cut.get_controller()
    predicted_name = obs.__dict__[kwargs['klass']].get_predicted_name(
        **kwargs
    )
    if predicted_name not in current_controller.named_objects:
        raise Exception('part not found: %s' % predicted_name)
    return current_controller.named_objects[predicted_name].post_create(**kwargs)


def legacy_create_deformation_rig(part_name, klass):
    raise Exception('%s has legacy deformation rig (%s)' % (klass, part_name))


def create_deformation_joint(part_name, joint_name):
    controller = cut.get_controller()
    if joint_name not in controller.named_objects:
        raise Exception('joint not found: %s' % joint_name)
    if part_name not in controller.named_objects:
        raise Exception('part not found: %s' % part_name)
    joint = controller.named_objects[joint_name]
    part = controller.named_objects[part_name]
    deform_joint = dru.create_deform_joint(
        joint,
        part.get_root().deform_group
    )
    part.deform_joints.append(deform_joint)
    part.base_deform_joints.append(deform_joint)


def parent_deformation_joint(
        control_joint_name,
        disconnected=False
):
    controller = cut.get_controller()
    if control_joint_name not in controller.named_objects:
        raise Exception('joint not found: %s' % control_joint_name)
    control_joint = controller.named_objects[control_joint_name]
    deform_joint = control_joint.relationships.get('deform_joint')
    if not deform_joint:
        return dict(
            status='warning',
            warning='Unable to locate deform joint for %s' % control_joint
        )
    part = control_joint.hierarchy_parent
    if part is None:
        raise Exception('%s.hierarchy_parent is None' % control_joint.name)
    if control_joint.parent is None:
        raise Exception('%s.parent is None' % control_joint.name)

    if control_joint.parent in part.joints:  # Internal parenting
        deform_joint_ancestor = control_joint.parent.relationships.get('deform_joint')
        if not deform_joint_ancestor:
            raise Exception('Unable to locate deform joint for control_join.parent:%s' % control_joint.parent)
        deform_joint.set_parent(deform_joint_ancestor)
        return dict(
            info='Parented %s to %s' % (
                deform_joint.name,
                deform_joint_ancestor.name
            )
        )

    if disconnected or control_joint.disconnected_joint:
        deform_joint.set_parent(controller.root.origin_deform_group)
        if disconnected:
            return dict(
                info='%s uses disconnected joints. Parented joint to "OriginDeform" group' % part.name
            )
        return dict(
            info='%s is set as a disconnected_joint; Parented joint to "OriginDeform" group' % deform_joint.name
        )

    joint_ancestor = pth.find_first_joint_ancestor(control_joint)

    if isinstance(joint_ancestor, Joint):  # External parenting
        parent_deform_joint = joint_ancestor.relationships.get('deform_joint')
        if not parent_deform_joint:
            raise Exception('Unable to locate deform joint for joint ancestor: %s' % joint_ancestor.name)
        deform_joint.set_parent(parent_deform_joint)
        return dict(
            info='Parented %s to %s' % (
                deform_joint.name,
                parent_deform_joint.name
            )
        )

    return dict(
        info='Parent not set for %s' % deform_joint.name
    )


def finish_create_part(kwargs):
    """
    cut.get_controller allows this to be called safely in sub-processes/threads
    """
    kwargs.pop('name', None)
    current_controller = cut.get_controller()
    predicted_name = obs.__dict__[kwargs['klass']].get_predicted_name(
        **kwargs
    )
    if predicted_name not in current_controller.named_objects:
        raise Exception('part not found: %s' % predicted_name)
    current_controller.named_objects[predicted_name].finish_create(**kwargs)


def label_joints():
    controller = cut.get_controller()
    controller.scene.label_joints()


def perform_deformation_joint_count_check():
    controller = cut.get_controller()
    container = controller.root
    all_joints = container.get_joints()
    all_deform_joints = container.get_base_deform_joints()
    if len(all_joints) != len(all_deform_joints):
        report_mismatched_joints(container)
        raise Exception(
            'Deform joint mismatch. %s joints and %s deform joints' % (
                len(all_joints),
                len(all_deform_joints)
            )
        )


def report_mismatched_joints(container):
    messages = []
    for part in container.get_parts(include_self=True):
        if len(part.joints) != len(part.base_deform_joints):
            message = '%s mismatched joints: %s had %s joints and %s base deform joints' % (
                part.__class__.__name__,
                part.name,
                len(part.joints),
                len(part.base_deform_joints)
            )
            messages.append(message)
    if messages:
        raise Exception('\n'.join(messages))


def import_origin_bs_weight(entity_builds, root_task):
    root_bs_task = BuildTask(
        name='Import BlendShape weight',
        parent=root_task
    )
    for build in entity_builds:
        if build.rig_blueprint.get('use_external_rig_data'):
            if not build.rig_blueprint.get('use_manual_rig_data'):
                BuildTask(
                    build=build,
                    parent=root_bs_task,
                    name='Import BS_Weight: %s' % build.namespace,
                    function=functools.partial(
                        import_external_container_rig_data,
                        '%s/rig_data/origin_bs_weights.json' % build.build_directory
                    )
                )
        else:
            origin_data = build.rig_blueprint['rig_data'].get('origin_bs_weights', dict())
            if origin_data:
                BuildTask(
                    parent=root_bs_task,
                    build=build,
                    name='Import origin_bs_weights (%s)' % build.entity,
                    function=functools.partial(
                        import_bs_weights,
                        origin_data
                    )
                )


def import_skin_clusters(entity_builds, root_task):
    root_skin_task = BuildTask(
        name='Skin Clusters',
        parent=root_task
    )
    for build in entity_builds:
        BuildTask(
            build=build,
            parent=root_skin_task,
            name='Before Import Skin Clusters',
            function=build.create_callback('before_skin_clusters')
        )
        if build.rig_blueprint.get('use_external_rig_data'):
            if not build.rig_blueprint.get('use_manual_rig_data'):
                BuildTask(
                    parent=root_skin_task,
                    build=build,
                    name='Import skin_clusters (%s)' % build.entity,
                    create_children_function=functools.partial(
                        generate_external_import_skin_tasks,
                        '%s/rig_data/skin_clusters' % build.build_directory,
                        build.namespace
                    )
                )
                BuildTask(
                    parent=root_skin_task,
                    build=build,
                    name='Import shard_skin_cluster_data (%s)' % build.entity,
                    create_children_function=functools.partial(
                        generate_external_import_skin_tasks,
                        '%s/rig_data/shard_skin_cluster_data' % build.build_directory,
                        build.namespace
                    )
                )
        else:
            for data in build.rig_blueprint['rig_data'].get('skin_clusters', []):
                if build.namespace:
                    data['geometry'] = '%s:%s' % (build.namespace, data['geometry'])
                    data['joints'] = ['%s:%s' % (build.namespace, x) for x in data['joints']]
                BuildTask(
                    build=build,
                    parent=root_skin_task,
                    name='Import Skin: %s' % data['geometry'],
                    function=functools.partial(
                        import_skin,
                        data
                    )
                )
            for data in build.rig_blueprint['rig_data'].get('shard_skin_cluster_data', []):
                if build.namespace:
                    data['geometry'] = '%s:%s' % (build.namespace, data['geometry'])
                    data['joints'] = ['%s:%s' % (build.namespace, x) for x in data['joints']]
                BuildTask(
                    build=build,
                    parent=root_skin_task,
                    name='Import shard skin: %s' % data['geometry'],
                    function=functools.partial(
                        import_skin,
                        data
                    )
                )
        BuildTask(
            build=build,
            parent=root_skin_task,
            name='After Import Skin Clusters',
            function=build.create_callback('after_skin_clusters')
        )


def generate_external_skin_tasks(directory):
    controller = cut.get_controller()
    rig = controller.root
    layer = controller.current_layer
    skin_tasks = []
    for geometry_name in [x for x in rig.geometry if rig.geometry[x].layer == layer]:
        json_path = '%s/%s.json' % (directory, geometry_name)
        if os.path.exists(json_path):
            skin_task = BuildTask(
                name='Import External Skin: %s' % geometry_name,
                function=functools.partial(
                    import_skin_from_json,
                    json_path
                )
            )
            skin_tasks.append(skin_task)
    return skin_tasks


def import_skin_from_json(json_path):
    try:
        with open(json_path, mode='r') as f:
            skin_data = json.load(f)
    except Exception as e:
        logging.getLogger('rig_build').error(traceback.format_exc())
        return dict(
            status='warning',
            warning='Failed to parse skin data from json path: %s' % json_path
        )
    import_skin(skin_data)


def import_skin(skin_data):
    controller = cut.get_controller()
    skin_data['joints'] = update_joints(skin_data['joints'])
    geometry = skin_data['geometry']
    missing_joints = []
    duplicate_joints = []
    for joint in skin_data['joints']:
        if not controller.scene.objExists(joint):
            missing_joints.append(joint)
        listed_joints = controller.scene.ls(joint)
        if listed_joints and len(listed_joints) > 1:
            duplicate_joints.append(joint)

    if not controller.scene.objExists(geometry):
        return dict(
            status='warning',
            warning='Unable to create skin cluster due to missing geometry: %s' % geometry
        )

    if missing_joints:
        return dict(
            status='warning',
            warning='Unable to create skin cluster due to missing joints:\n\n%s' % '\n'.join(missing_joints)
        )
    if duplicate_joints:
        return dict(
            status='warning',
            warning='Unable to create skin cluster due to duplicate joints:\n\n%s' % '\n'.join(duplicate_joints)
        )
    controller.scene.create_from_skin_data(skin_data)


def import_bs_weights(origin_data):
    controller = cut.get_controller()
    if controller.scene.mock:
        return
    try:  # This code is not safe. we need to use try except until it is fixed
        for key in origin_data:
            if 'weights' in origin_data[key]:
                if origin_data[key]['weights'] != None:
                    bls = '{}'.format(key) + '_Origin_Bs'
                    controller.scene.set_blendshape_weights(
                        bls,
                        data=origin_data[key]['weights']
                    )
    except Exception as e:
        logging.getLogger('rig_build').error(traceback.format_exc())
        return dict(
            status='warning',
            warning='Failed to set bs weights. See log for details'
        )


def update_joints(joints):
    """
    This is being used to swap out control joints for bind joints in the SurfaceSpline and SplitBrow parts
    Delete this once all rigs have been built with current > iRig_2.1579.0
    """
    controller = cut.get_controller()
    joint_map = dict()
    remapped_joints = []
    remap_parts = controller.root.find_parts(
        obs.SurfaceSpline,
        obs.DoubleSurfaceSpline,
        obs.DoubleSurfaceSplineUpvectors,
        obs.SplitBrow
    )
    all_bind_joints = []
    for part in remap_parts:
        for i in range(len(part.joints)):
            joint_map[part.joints[i].name] = part.deform_joints[i].name
            all_bind_joints.append(part.deform_joints[i].name)
    for i in range(len(joints)):
        if joints[i] in joint_map:
            remapped_joints.append(joint_map[joints[i]])
        else:
            remapped_joints.append(joints[i])
    if len(list(set(remapped_joints))) != len(remapped_joints):
        logging.getLogger('rig_build').warning('Duplicate joint names found after search replace. (Unable to remap)')
        return joints
    return remapped_joints


def import_delta_mushs(entity_builds, root_task):
    delta_mush_task = BuildTask(
        name='Import Delta Mushs',
        parent=root_task
    )
    for build in entity_builds:
        BuildTask(
            build=build,
            parent=delta_mush_task,
            name='Before Delta Mushs',
            function=build.create_callback('before_delta_mush')
        )
        if build.rig_blueprint.get('use_external_rig_data'):
            if not build.rig_blueprint.get('use_manual_rig_data'):
                BuildTask(
                    build=build,
                    parent=delta_mush_task,
                    name='Import delta_mush',
                    function=functools.partial(
                        import_external_container_rig_data,
                        '%s/rig_data/delta_mush.json' % build.build_directory
                    )
                )
        else:
            BuildTask(
                build=build,
                parent=delta_mush_task,
                name='Import Delta Mushs',
                function=functools.partial(
                    set_delta_mush_data,
                    build.rig_blueprint['rig_data'].get('delta_mush', None)
                )
            )
        BuildTask(
            build=build,
            parent=delta_mush_task,
            name='After Delta Mushs',
            function=build.create_callback('after_delta_mush')
        )


def set_wraps(entity_builds, root_task):
    wrap_task = BuildTask(
        name='Set Wrap Data',
        parent=root_task
    )
    for build in entity_builds:
        entity_task = BuildTask(
            build=build,
            parent=wrap_task,
            name=build.entity
        )
        BuildTask(
            build=build,
            parent=entity_task,
            name='Before Wraps',
            function=build.create_callback('before_wrap')
        )
        if build.rig_blueprint.get('use_external_rig_data'):
            if not build.rig_blueprint.get('use_manual_rig_data'):
                BuildTask(
                    build=build,
                    parent=entity_task,
                    name='Import wrap',
                    function=functools.partial(
                        import_external_container_rig_data,
                        '%s/rig_data/wrap.json' % build.build_directory
                    )
                )
        else:
            for wrap_data in build.rig_blueprint['rig_data'].get('wrap', []):
                BuildTask(
                    build=build,
                    parent=entity_task,
                    name=wrap_data['target_geometry'],
                    function=functools.partial(
                        create_wrap_from_data,
                        wrap_data
                    )
                )
        BuildTask(
            build=build,
            parent=entity_task,
            name='After Wraps',
            function=build.create_callback('after_wrap')
        )


def set_cvwraps(entity_builds, root_task):
    cvwrap_task = BuildTask(
        name='Set cvWrap Data',
        parent=root_task
    )
    for build in entity_builds:
        entity_task = BuildTask(
            build=build,
            parent=cvwrap_task,
            name=build.entity
        )
        BuildTask(
            build=build,
            parent=entity_task,
            name='Before cvWraps',
            function=build.create_callback('before_cvwrap')
        )
        if build.rig_blueprint.get('use_external_rig_data'):
            if not build.rig_blueprint.get('use_manual_rig_data'):
                BuildTask(
                    build=build,
                    parent=entity_task,
                    name='Import cvWrap',
                    function=functools.partial(
                        import_external_container_rig_data,
                        '%s/rig_data/cvwrap.json' % build.build_directory
                    )
                )
        else:
            for cvwrap_data in build.rig_blueprint['rig_data'].get('cvwrap', []):
                BuildTask(
                    build=build,
                    parent=entity_task,
                    name=cvwrap_data['driver_mesh'],
                    function=functools.partial(
                        create_cvwrap_from_data,
                        cvwrap_data
                    )
                )
        BuildTask(
            build=build,
            parent=entity_task,
            name='After cvWraps',
            function=build.create_callback('after_cvwrap')
        )


def create_wrap_from_data(wrap_data):
    controller = cut.get_controller()
    wrap = controller.scene.find_deformer_node(
        wrap_data['target_geometry'],
        'wrap'
    )
    if wrap:
        return dict(
            status='warning',
            warning='The geometry "%s" already had a wrap. unable to create more than one wrap' % wrap_data[
                'target_geometry']
        )
    controller.scene.create_wrap(
        wrap_data,
        namespace=controller.namespace
    )


def create_cvwrap_from_data(cvwrap_data):
    controller = cut.get_controller()
    controller.scene.create_cvwrap(
        cvwrap_data,
        namespace=controller.namespace
    )


def set_deformer_stack_data(entity_builds, root_task):
    stack_task = BuildTask(
        name='Set Deformer Stack',
        parent=root_task
    )

    for build in entity_builds:
        BuildTask(
            build=build,
            parent=stack_task,
            name='Before Deformer Stack',
            function=build.create_callback('before_deformer_stack')
        )
        if build.rig_blueprint.get('use_external_rig_data'):
            if not build.rig_blueprint.get('use_manual_rig_data'):
                BuildTask(
                    build=build,
                    parent=stack_task,
                    name='Import deformer_stack_data',
                    function=functools.partial(
                        import_external_container_rig_data,
                        '%s/rig_data/deformer_stack_data.json' % build.build_directory
                    )
                )
        else:
            BuildTask(
                build=build,
                parent=stack_task,
                name='Import Deformer Stack',
                function=functools.partial(
                    set_deformer_stacks,
                    build.rig_blueprint['rig_data'].get('deformer_stack_data', None)
                )
            )
        BuildTask(
            build=build,
            parent=stack_task,
            name='After Deformer Stack',
            function=build.create_callback('after_deformer_stack')
        )


def get_space_switcher_tasks(entity_builds, root_task):
    stack_task = BuildTask(
        name='Handle Spaces',
        parent=root_task
    )
    for build in entity_builds:
        entity_task = BuildTask(
            build=build,
            parent=stack_task,
            name=build.entity
        )
        BuildTask(
            build=build,
            parent=entity_task,
            name='Before Space Switchers',
            function=build.create_callback('before_space_switchers')
        )
        if build.rig_blueprint.get('use_external_rig_data'):
            if not build.rig_blueprint.get('use_manual_rig_data'):
                BuildTask(
                    build=build,
                    parent=entity_task,
                    name='Import space_switchers (External)',
                    function=functools.partial(
                        import_external_container_rig_data,
                        '%s/rig_data/space_switchers.json ' % build.build_directory
                    )
                )
        else:
            handle_data = build.rig_blueprint['rig_data'].get('space_switchers', dict())
            for handle_name in handle_data:
                BuildTask(
                    build=build,
                    parent=entity_task,
                    name=handle_name,
                    function=functools.partial(
                        spcu.create_space_switcher_from_data,
                        handle_name,
                        handle_data[handle_name]
                    )
                )
        BuildTask(
            build=build,
            parent=entity_task,
            name='After Space Switchers',
            function=build.create_callback('after_space_switchers')
        )


def create_part_nonlinear_deformers(kwargs):
    """
    cut.get_controller allows this to be called safely in sub-processes/threads
    """
    current_controller = cut.get_controller()
    predicted_name = obs.__dict__[kwargs['klass']].get_predicted_name(
        **kwargs
    )
    if predicted_name not in current_controller.named_objects:
        raise Exception('part not found: %s' % predicted_name)
    current_controller.named_objects[predicted_name].create_rig_data_tasks(**kwargs)


def create_rig_data_tasks(entity_builds, root_task):
    """
    Parts rig data needs to happen inside this function because of the old build order
    Eventually, we should separate these
    """
    controller = cut.get_controller()

    part_rig_data_root = BuildTask(
        name='Part rig_data',
        parent=root_task
    )

    for build in entity_builds:
        BuildTask(
            build=build,
            name='Before Non-Linear Deformers',
            parent=part_rig_data_root,
            function=build.create_callback('before_nonlinears')
        )

    for build in entity_builds:
        use_external_rig_data = build.rig_blueprint.get('use_external_rig_data', False)
        if use_external_rig_data:
            BuildTask(
                parent=part_rig_data_root,
                build=build,
                name='%s (External)' % build.entity,
                create_children_function=functools.partial(
                    generate_external_part_data_tasks,
                    build.build_directory
                )
            )
        else:
            entity_task = BuildTask(
                build=build,
                parent=part_rig_data_root,
                name='%s (Blueprint)' % build.entity,
            )

            part_blueprints = gut.flatten_blueprint(
                build.rig_blueprint,
                include_self=False
            )
            for part_blueprint in part_blueprints:
                name_kwargs = copy.deepcopy(part_blueprint)
                predicted_name = obs.__dict__[part_blueprint['klass']].get_predicted_name(
                    namespace=build.namespace,
                    **name_kwargs
                )
                part_task = BuildTask(
                    parent=entity_task,
                    build=build,
                    name=predicted_name
                )
                part_data_keys = []
                rig_data = part_blueprint.get('rig_data', dict())
                if rig_data is None:
                    raise Exception('rig_data = None for part: %s' % predicted_name)
                for key in rig_data.keys():
                    if key in ['weights']:
                        part_data_keys.append(key)
                    else:
                        part_data_keys.insert(0, key)
                for key in part_data_keys:
                    BuildTask(
                        build=build,
                        parent=part_task,
                        name=key,
                        function=functools.partial(
                            set_part_rig_data,
                            predicted_name,
                            key,
                            part_blueprint['rig_data'][key]
                        )
                    )

    for build in entity_builds:
        BuildTask(
            build=build,
            name='After Non-Linear Deformers',
            parent=part_rig_data_root,
            function=build.create_callback('after_nonlinears')
        )


def set_part_rig_data(part_name, key, value):
    controller = cut.get_controller()
    part = controller.named_objects[part_name]
    if key not in part.data_setters:
        return dict(
            status='warning',
            warning='Unable to find data `setter for %s.%s existing setters: %s' % (
                part_name, key, part.data_setters.keys()
            )
        )
    if value is None:
        return dict(
            status='warning',
            warning='Setter value for %s.%s was "None". Aborting rig data task.' % (part.name, key)
        )
    part.data_setters[key](value)


def import_part_data(part_name, json_path):
    controller = cut.get_controller()
    part = controller.named_objects[part_name]
    key = os.path.basename(json_path).split('.')[0]
    try:
        with open(json_path, mode='r') as f:
            data = json.load(f)
    except Exception as e:
        logging.getLogger('rig_build').error(traceback.format_exc())
        return dict(
            status='warning',
            warning='Failed to parse json data from path: %s -s See script editor for details' % json_path
        )
    if key not in part.data_setters:
        return dict(
            status='warning',
            warning='Unable to find data setter for %s.%s' % (part_name, key)
        )
    part.data_setters[key](data)


def generate_external_part_data_tasks(directory):
    controller = cut.get_controller()

    container = controller.root
    tasks = []
    parts_directory = '%s/rig_data/parts' % directory
    if not os.path.exists(parts_directory):
        logging.getLogger('rig_build').warning('Directory not found: %s' % parts_directory)
        return dict(
            status='warning',
            warning='Directory not found: %s' % parts_directory
        )
    parts = [x for x in container.get_parts() if x.layer == controller.current_layer]
    if not parts:
        logging.getLogger('rig_build').warning('Unable to find any parts with the layer: %s' % controller.current_layer)
        return dict(
            status='warning',
            warning='Unable to find any parts with the layer: %s' % controller.current_layer
        )
    for part in parts:
        part_task = BuildTask(
            name=part.name
        )
        tasks.append(part_task)
        for key in part.data_setters:
            directory = '%s/rig_data/parts/%s' % (env.local_build_directory, part.name)
            if not os.path.exists(directory):
                os.makedirs(directory)
            json_path = '%s/%s.json' % (directory, key)
            if os.path.exists(json_path):
                BuildTask(
                    parent=part_task,
                    name='%s.json' % key,
                    function=functools.partial(
                        import_part_data,
                        part.name,
                        json_path
                    )
                )
    return tasks


def set_local_handles(handles_json_path):
    try:
        with open(handles_json_path, mode='r') as f:
            local_handles_data = json.load(f)
    except Exception as e:
        logging.getLogger('rig_build').error(traceback.format_exc())
        return dict(
            status='warning',
            warning='Unable to parse json file: %s' % handles_json_path)
    set_handle_shape_data(local_handles_data)


def create_custom_plugs(entity_builds, root_task):
    plugs_task = BuildTask(
        name='Custom Plugs',
        parent=root_task
    )

    for build in entity_builds:
        BuildTask(
            build=build,
            parent=plugs_task,
            name='Before Custom Plugs',
            function=build.create_callback('before_custom_plugs')
        )

        if build.rig_blueprint.get('use_external_rig_data'):
            if not build.rig_blueprint.get('use_manual_rig_data'):
                BuildTask(
                    build=build,
                    parent=plugs_task,
                    name='Import custom_plug_data',
                    function=functools.partial(
                        import_external_container_rig_data,
                        '%s/rig_data/custom_plug_data.json' % build.build_directory
                    )
                )
        else:
            BuildTask(
                build=build,
                parent=plugs_task,
                name='Create Custom Plugs',
                function=functools.partial(
                    set_custom_plug_data,
                    build.rig_blueprint['rig_data'].get('custom_plug_data', [])
                ),
            )
        BuildTask(
            build=build,
            parent=plugs_task,
            name='After Custom Plugs',
            function=build.create_callback('after_custom_plugs')
        )


def create_custom_constraints(entity_builds, root_task):
    constraint_task = BuildTask(
        name='Custom Constraints',
        parent=root_task
    )
    for build in entity_builds:
        BuildTask(
            build=build,
            parent=constraint_task,
            name='Before Custom Constraints',
            function=build.create_callback('before_constraints')
        )
        if build.rig_blueprint.get('use_external_rig_data'):
            if not build.rig_blueprint.get('use_manual_rig_data'):
                BuildTask(
                    build=build,
                    parent=constraint_task,
                    name='Import custom_constraint_data',
                    function=functools.partial(
                        import_external_container_rig_data,
                        '%s/rig_data/custom_constraint_data.json' % build.build_directory
                    )
                )
        else:
            BuildTask(
                build=build,
                parent=constraint_task,
                name='Create Custom Constraints',
                function=functools.partial(
                    set_custom_constraints_data,
                    build.rig_blueprint['rig_data'].get('custom_constraint_data', [])
                )
            )
        BuildTask(
            build=build,
            parent=constraint_task,
            name='After Custom Constraints',
            function=build.create_callback('after_constraints')
        )


def create_proxy_shaders(entity_builds, root_task):
    proxy_shader_task = BuildTask(
        name='Proxy Shaders',
        parent=root_task
    )

    for build in entity_builds:
        BuildTask(
            build=build,
            parent=proxy_shader_task,
            name='Before Proxy Shaders',
            function=build.create_callback('before_proxy_shaders')
        )

    for build in entity_builds:
        BuildTask(
            build=build,
            parent=proxy_shader_task,
            name='Create Proxy Shaders',
            function=functools.partial(
                set_proxy_shaders,
                build.build_directory,
                build.entity,
                build.namespace
            )
        )
    for build in entity_builds:
        BuildTask(
            build=build,
            parent=proxy_shader_task,
            name='After Proxy Shaders',
            function=build.create_callback('after_proxy_shaders')
        )


def import_sdk_data(entity_builds, root_task):
    sdk_task = BuildTask(
        name='Import SDKs',
        parent=root_task
    )

    for build in entity_builds:
        BuildTask(
            build=build,
            parent=sdk_task,
            name='Before Import SDks',
            function=build.create_callback('before_sdks')
        )
    for build in entity_builds:
        if build.rig_blueprint.get('use_external_rig_data'):
            if not build.rig_blueprint.get('use_manual_rig_data'):
                BuildTask(
                    build=build,
                    parent=sdk_task,
                    name='Import sdk_data',
                    function=functools.partial(
                        import_external_container_rig_data,
                        '%s/rig_data/sdks.json' % build.build_directory
                    )
                )
        else:
            BuildTask(
                build=build,
                parent=sdk_task,
                name='Import SDks',
                function=functools.partial(
                    set_sdk_data,
                    build.rig_blueprint['rig_data'].get('sdks', [])
                )
            )
    for build in entity_builds:
        BuildTask(
            build=build,
            parent=sdk_task,
            name='After Import SDks',
            function=build.create_callback('after_sdks')
        )


def parent_build_callbacks(entity_builds, root_task):
    parent_rig_task = BuildTask(
        name='Parent Build Callbacks',
        parent=root_task
    )

    for build in entity_builds:
        BuildTask(
            build=build,
            parent=parent_rig_task,
            name='Before Parent Build',
            function=build.create_callback('before_finish_parent_build')
        )

    for build in entity_builds:
        BuildTask(
            build=build,
            parent=parent_rig_task,
            name='After Parent Build',
            function=build.create_callback('after_finish_parent_build')
        )


def set_sdk_data(sdk_data):
    cut.get_controller().root.set_sdk_data(sdk_data)


def set_proxy_shaders(build_directory, entity, namespace):
    current_controller = cut.get_controller()
    if not current_controller.scene.mock:
        import rig_factory.build.utilities.proxy_shaders as psh  # This is not ideal
        return psh.exec_assign_proxy_shaders(
            os.environ['TT_PROJCODE'],
            entity,
            current_controller,
            build_directory,
            namespace
        )


def set_custom_constraints_data(constraint_data):
    cut.get_controller().root.set_custom_constraints_data(constraint_data)


def set_handle_shape_data(handle_shapes):
    cut.get_controller().root.set_handle_shapes(handle_shapes)


def set_custom_plug_data(plug_data):
    cut.get_controller().root.set_custom_plug_data(plug_data)

def set_deformer_stacks(stack_data):
    cut.get_controller().root.set_deformer_stack_data(stack_data)


def set_delta_mush_data(delta_mush_data):
    cut.get_controller().root.set_delta_mush_data(delta_mush_data)


def set_skin_cluster_data(skin_data):
    cut.get_controller().root.set_skin_cluster_data(skin_data)


def finish_create_container(container_kwargs):
    cut.get_controller().root.finish_create(**container_kwargs)


def post_create_container(container_kwargs):
    cut.get_controller().root.post_create(**container_kwargs)


def get_part_from_indices(indices):
    controller = cut.get_controller()
    if controller.root:
        owner = controller.root
        for index in indices:
            owner = owner.part_members[index]
        return owner


def get_kwarg_location_pairs_from_builds(entity_builds):
    controller = cut.get_controller()
    owner_index_pairs = dict()
    for build in entity_builds:
        index_kwarg_pairs = list(
            get_kwarg_location_pairs(controller, copy.deepcopy(build.rig_blueprint.get('part_members', [])), []))
        owner_index_pairs[build.entity] = index_kwarg_pairs
    return owner_index_pairs


def get_kwarg_location_pairs(controller, part_blueprints, parent_indices):
    """
    Special data for setting the owners of parts during a build
    Flattens hierarchical blueprint data into a flat list of tuples
    the first item is the indices of the owner
    the second item is the part blueprint
    Uses "breadth first" traversal
    If a rig is already loaded, the index of the existing part is added
    """
    for i in range(len(part_blueprints)):
        part_blueprint = part_blueprints[i]
        child_indices = copy.deepcopy(parent_indices)
        if controller.root and not parent_indices:

            members = [x for x in controller.root.part_members if x.layer == controller.current_layer]
            child_indices.append(len(members) + i)  # Bump by existing member count (for merging)
        else:
            child_indices.append(i)
        yield child_indices, part_blueprint
        child_blueprints = part_blueprint.pop('part_members', [])
        for pair in get_kwarg_location_pairs(
                controller,
                child_blueprints,
                child_indices
        ):
            yield pair


def raise_build_warnings():
    controller = cut.get_controller()
    if controller.build_warnings:
        build_warnings = controller.build_warnings
        shortened_build_warnings = [build_warnings[i] for i in range(len(build_warnings)) if i < 10]
        if len(shortened_build_warnings) < len(build_warnings):
            shortened_build_warnings.append('+ %s more' % (len(build_warnings) - len(shortened_build_warnings)))
        controller.raise_warning(
            'BuildWarnings:\n\n%s' % '\n\n'.join(shortened_build_warnings)
        )
        controller.build_warnings = []


def set_bifrost_attributes():
    controller = cut.get_controller()
    bifrost_targets = ['Bifrost_Transform_Grp']
    driver = None

    # Constrain Bifrost_Transform_Grp if it exists
    for bifrost_target in bifrost_targets:
        if controller.scene.objExists(bifrost_target):

            if not driver:
                if controller.scene.objExists('C_Main_Cog_Jnt'):
                    driver = 'C_Main_Cog_Jnt'
                elif controller.scene.objExists('Cog_Jnt'):
                    driver = 'Cog_Jnt'
                else:
                    raise Exception(
                        'Could not find Cog_Jnt to add the Bifrost constraint'
                    )

            controller.scene.parentConstraint(driver, bifrost_target, mo=True)
            controller.scene.scaleConstraint(driver, bifrost_target, mo=True)
            break

    if controller.scene.ls('Bifrost_Deform_Grp'):
        return dict(
            status='warning',
            warning='Assets has included the Bifrost_Deform_Grp in this rig. You will be able to apply deformers to '
                    'the geometry in this group.'
        )


def add_comment(comment):
    if comment:
        major_version, minor_version = fut.get_current_work_versions()
        comments_directory = '%s/comments' % fut.get_logs_directory()
        comments_json = '%s/%s_rig_comments.json' % (comments_directory, os.environ['TT_ENTNAME'])
        comments_data = dict()
        if os.path.exists(comments_json):
            with open(comments_json, mode='r') as f:
                comments_data = json.load(f)
        comments_data['v%s.%s' % (major_version, minor_version)] = comment
        with open(comments_json, mode='w') as f:
            json.dump(comments_data, f, sort_keys=True, indent=4, separators=(',', ': '))


def merge_container_data(blueprint):
    controller = cut.get_controller()
    container = controller.root
    missing_keys = []
    if not container:
        raise Exception('Container not found.')
    for key in blueprint['rig_data']:
        key = str(key)
        merging_value = blueprint['rig_data'][key]
        if key not in container.rig_data:
            missing_keys.append(key)
        container_value = container.rig_data.get(key, None)
        if isinstance(container_value, list) and isinstance(merging_value, list):
            merging_value.extend(container_value)
            if all(isinstance(x, (str, int, float)) for x in merging_value):
                merging_value = list(set(merging_value))
            logging.getLogger('rig_build').info('Merging rig_data: "%s"' % key)
            container.rig_data[key] = merging_value
        elif isinstance(container_value, dict) and isinstance(merging_value, dict):
            container_value.update(merging_value)
            logging.getLogger('rig_build').info('Merging rig_data: "%s"' % key)
            container.rig_data[key] = container_value
        elif not container_value:
            logging.getLogger('rig_build').info('Setting rig_data: "%s"' % key)
            container.rig_data[key] = merging_value
        else:
            logging.getLogger('rig_build').warning('Unable to merge rig data: %s' % key)
    if missing_keys:
        return dict(
            status='warning',
            warning='Missing data in guide state rig_data: %s' % missing_keys
        )


def execute_data_setter(part_name, key, value):
    controller = cut.get_controller()
    setter = controller.named_objects[part_name].data_settegrs.get(key)
    if not setter:
        return dict(
            status='warning',
            warning='unable to find setter for %s %s ' % (part_name, key)
        )
    setter(value)


def flatten(root):
    yield root
    for x in root.children:
        for child in flatten(x):
            yield child


def check_deformer_input_order(root_task, entity_build):

    use_external_rig_data = entity_build.rig_blueprint.get('use_external_rig_data', False)

    controller = cut.get_controller()
    geo_deformer_checker = ddic.deformer_order_checker
    checker = geo_deformer_checker(controller,use_external_rig_data)

    deformer_order_checker = BuildTask(parent=root_task,
                                       name="Deformer Order Checker"
    )

    if use_external_rig_data == True:
        deformer_order_checker.info = 'The asset is using external rig data'

    else:
        if checker.external_rig_data == False:
            deformer_order_checker.info = 'Checking Geos & Deformer Order'

            def get_geo_info():
                if checker.inputOrderCheck() != None:
                    return dict(info=checker.inputOrderCheck())


                return dict(status= 'warning',
                            warning = 'No published build to compare with'
                )

            def deformer_info():
                get_deformer_info = checker.inputOrderCheck(deformer_order_info= True)

                if get_deformer_info != None:
                    return dict(status='warning',
                                warning= get_deformer_info)

                else:
                    return dict(status='warning',
                                warning= 'No matching Geo')


            BuildTask(
                      parent=deformer_order_checker,
                      name="Deformer Geo Info",
                      function=functools.partial(get_geo_info)
            )

            BuildTask(
                parent=deformer_order_checker,
                name="Deformation Order Info",
                function=functools.partial(deformer_info)
            )


def import_external_container_rig_data(file_path):
    controller = cut.get_controller()
    key = file_path.split('/')[-1].split('.')[0]
    if not file_path or not os.path.exists(file_path):
        return dict(
            status='warning',
            warning='Unable to locate file: %s' % file_path
        )
    if key not in controller.root.data_setters:
        return dict(
            status='warning',
            warning='Unable to find data setter for %s' % key
        )
    try:
        with open(file_path, mode='r') as f:
            data = json.load(f)
    except Exception as e:
        logging.getLogger('rig_build').error(traceback.format_exc())
        return dict(
            status='warning',
            warning='Unable to parse json: %s' % file_path
        )
    if not data:
        return dict(
            status='warning',
            warning='Data not found : %s' % key
        )
    controller.root.data_setters[key](data)


def return_warning(warning):
    return dict(
        status='warning',
        warning=warning
    )


def generate_external_import_skin_tasks(skins_directory, namespace=None):
    tasks = []
    for skin_path in glob.glob('%s/*.json' % skins_directory):
        try:
            with open(skin_path, mode='r') as f:
                skin_data = json.load(f)
        except Exception as e:
            logging.getLogger('rig_build').error(traceback.format_exc())
            new_task = BuildTask(
                name='Import skin: %s' % os.path.basename(skin_path),
                function=functools.partial(
                    return_warning,
                    'Unable to parse skin weights json: %s' % skin_path
                )
            )
        else:
            if namespace:
                skin_data['geometry'] = '%s:%s' % (
                    namespace,
                    skin_data['geometry']
                )
                skin_data['joints'] = ['%s:%s' % (namespace, x) for x in skin_data['joints']]
            new_task = BuildTask(
                name='Import skin: %s' % os.path.basename(skin_path),
                function=functools.partial(
                    import_skin,
                    skin_data
                )
            )
        tasks.append(new_task)
    return tasks


def missing_blueprint_warning(file_path):
    return dict(
        status='warning',
        warning='unable to locate blueprint: %s/%s' % file_path
    )


