import os
import copy
import functools
import Snowman3.rigger.rig_factory.utilities.geometry_utilities as gut
from Snowman3.rigger.rig_factory.build.tasks.task_objects import BuildTask
import Snowman3.rigger.rig_factory.build.utilities.controller_utilities as cut
import Snowman3.rigger.rig_factory.build.tasks.task_utilities.task_utilities as tut
import Snowman3.rigger.rig_factory.build.tasks.task_utilities.guide_utilities as gtu


# ----------------------------------------------------------------------------------------------------------------------
def get_guide_tasks(entity_build, parent=None):
    root_task = BuildTask(
        parent=parent,
        build=entity_build,
        name='Guide'
    )
    entity_builds = list(tut.flatten(entity_build))
    tut.create_container_tasks(
        entity_builds,
        root_task,
        skip_existing=True
    )
    geometry_task = BuildTask(
        parent=root_task,
        name='Import Geometry'
    )
    for build in entity_builds:
        BuildTask(
            parent=geometry_task,
            build=build,
            name='Build.before_import_geometry()',
            function=build.create_callback('before_import_geometry')
        )
    for build in entity_builds:
        product_paths = build.rig_blueprint['product_paths']
        for product in ['abc', 'abc_anim']:
            if product_paths.get(product, None):
                BuildTask(
                    parent=geometry_task,
                    build=build,
                    name='Import Product (%s)' % product,
                    function=functools.partial(
                        gut.import_abc_product,
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
                    gut.import_geometry_paths,
                    build.entity,
                    'utility_geometry',
                    build.rig_blueprint['utility_geometry_paths']
                )
            )
        if 'low_geometry_paths' in build.rig_blueprint:
            BuildTask(
                parent=geometry_task,
                build=build,
                name='Import Low geometry paths',
                function=functools.partial(
                    gut.import_geometry_paths,
                    build.entity,
                    'low_geometry',
                    build.rig_blueprint['low_geometry_paths']
                )
            )
        if 'geometry_paths' in build.rig_blueprint:
            BuildTask(
                parent=geometry_task,
                build=build,
                name='Import geometry paths',
                function=functools.partial(
                    gut.import_geometry_paths,
                    build.entity,
                    'geometry',
                    build.rig_blueprint['geometry_paths']
                )
            )
    for build in entity_builds:
        BuildTask(
            parent=geometry_task,
            build=build,
            name='Build.after_import_geometry()',
            function=build.create_callback('after_import_geometry')
        )

    #  Create Origin Geometry
    tut.create_origin_geometry(
        entity_builds,
        root_task
    )
    tut.get_create_parts_tasks(
        entity_builds,
        root_task
    )

    gtu.get_parts_positions_tasks(
        entity_builds,
        root_task
    )
    gtu.get_parts_vertices_tasks(
        entity_builds,
        root_task
    )
    # Post Create Parts
    tut.get_post_create_tasks(
        entity_builds,
        root_task
    )
    # Set Parent Joints
    tut.get_hierarchy_tasks(
        entity_builds,
        root_task
    )
    # Finish Create Parts
    tut.finish_create_parts(
        entity_builds,
        root_task
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
        function=tut.raise_build_warnings
    )
    return root_task


# ----------------------------------------------------------------------------------------------------------------------
def set_auto_rigged_property():
    cut.get_controller().root.auto_rigged = False


# ----------------------------------------------------------------------------------------------------------------------
def get_merge_tasks_root(entity_build):
    entity_build.children = []  # we don't want to execute parent entities
    root_task = get_guide_tasks(entity_build)
    blueprint = entity_build.rig_blueprint
    container_kwargs = dict((x, copy.deepcopy(blueprint[x])) for x in blueprint if x != 'part_members')
    BuildTask(
        parent=root_task,
        name='Merge Container Data',
        function=functools.partial(
            tut.merge_container_data,
            container_kwargs
        )
    )
    return root_task

