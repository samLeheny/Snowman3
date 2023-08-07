import os
import json
import shutil
import logging
import functools
import traceback
import subprocess
import Snowman3.rigger.rig_factory.utilities.file_utilities as fut
from Snowman3.rigger.rig_factory.build.tasks.task_objects import BuildTask
import Snowman3.rigger.rig_factory.build.utilities.controller_utilities as cut
import Snowman3.rigger.rig_factory.build.tasks.task_utilities.task_utilities as tut


def get_export_rig_data_tasks(
        entity_build,
        parent=None,
        clear_old_data=False
):
    root_task = BuildTask(
        parent=parent,
        build=entity_build,
        name='Export rig_data'
    )

    if clear_old_data:
        BuildTask(
            parent=root_task,
            build=entity_build,
            name='Create empty rig_data folder',
            function=functools.partial(
                create_empty_folder,
                '%s/rig_data' % fut.get_user_build_directory()
            )
        )
    entity_builds = list(tut.flatten(entity_build))
    BuildTask(
        parent=root_task,
        build=entity_build,
        name='Export: skin_clusters',
        create_children_function=functools.partial(
            generate_skin_tasks,
            'skin_clusters'
        )
    )
    for key in [
        'handle_shapes',
        'handle_colors',
        'handle_default_colors',
        'deformer_stack_data',
        'delta_mush',
        'wrap',
        'cvwrap',
        'space_switchers',
        'sdks',
        'custom_plug_data',
        'custom_constraint_data',
        'origin_bs_weights'
    ]:
        BuildTask(
            parent=root_task,
            build=entity_build,
            name='Export: %s' % key,
            function=functools.partial(
                export_container_data,
                key
            )
        )
    get_export_parts_rig_data_tasks(
        entity_build,
        parent=root_task
    )
    return root_task


def get_export_skin_clusters_tasks(build, parent=None):
    root_task = BuildTask(
        parent=parent,
        build=build,
        name='Export Skin Clusters'
    )
    BuildTask(
        parent=root_task,
        build=build,
        name='Skin Clusters',
        create_children_function=functools.partial(
            generate_skin_tasks,
            'skin_clusters'
        )
    )
    return root_task


def get_export_parts_rig_data_tasks(
        entity_build,
        parent=None,
        clear_old_data=False
):
    controller = cut.get_controller()
    container = controller.root
    root_task = BuildTask(
        parent=parent,
        build=entity_build,
        name='Export Parts rig_data'
    )
    parts_directory = '%s/rig_data/parts' % fut.get_user_build_directory()
    if clear_old_data:
        BuildTask(
            parent=root_task,
            build=entity_build,
            name='Create empty rig_data/parts folder',
            function=functools.partial(
                create_empty_folder,
                parts_directory
            )
        )
    if not os.path.exists(parts_directory):
        os.makedirs(parts_directory)

    for part in container.get_parts():
        if part.layer is None:
            part_directory = '%s/%s' % (parts_directory, part.name)
            if not os.path.exists(part_directory):
                os.makedirs(part_directory)
            BuildTask(
                parent=root_task,
                build=entity_build,
                name='Export Rig Data: %s' % part.name,
                function=functools.partial(
                    export_part_data,
                    part.name
                )
            )
    return root_task


def generate_skin_tasks(key):
    controller = cut.get_controller()
    container = controller.root
    function = container.data_getters[key]
    all_skins_data = function()
    if container.use_external_rig_data:
        subfolder = 'rig_data'
    else:
        subfolder = 'user_data'

    skins_directory = '%s/%s/skin_clusters' % (fut.get_user_build_directory(), subfolder)
    if not os.path.exists(skins_directory):
        os.makedirs(skins_directory)
    skin_tasks = []
    if all_skins_data:
        for skin_data in all_skins_data:
            skin_task = BuildTask(
                name='Export Skin: %s' % skin_data['geometry'],
                function=functools.partial(
                    export_json_data,
                    skin_data,
                    '%s/%s.json' % (
                        skins_directory,
                        skin_data['geometry']
                    )
                )
            )
            skin_tasks.append(skin_task)
    return skin_tasks


def export_json_data(data, json_path):
    try:
        with open(json_path, mode='w') as f:
            json.dump(
                data,
                f,
                sort_keys=True,
                indent=4,
                separators=(',', ': ')
            )
    except Exception as e:
        logging.getLogger('rig_build').error(traceback.format_exc())
        return dict(
            status='warning',
            warning='Failed to export to: %s' % json_path
        )


def export_container_data(key):
    controller = cut.get_controller()
    container = controller.root
    function = container.data_getters[key]
    data = function()
    if not data:
        logging.getLogger('rig_build').info('%s\'s not found. skipping export' % key)
        return
    rig_data_directory = '%s/rig_data' % fut.get_user_build_directory()
    if not os.path.exists(rig_data_directory):
        os.makedirs(rig_data_directory)
    try:
        with open('%s/%s.json' % (rig_data_directory, key), mode='w') as f:
            json.dump(
                data,
                f,
                sort_keys=True,
                indent=4,
                separators=(',', ': ')
            )

    except Exception as e:
        logging.getLogger('rig_build').error(traceback.format_exc())
        return dict(
            status='warning',
            warning='Failed to export %s. See log for details' % key
        )

def export_part_data(part_name):
    controller = cut.get_controller()
    part = controller.named_objects[part_name]
    part_rig_data = part.get_rig_data()
    directory = '%s/rig_data/parts/%s' % (fut.get_user_build_directory(), part_name)
    if not os.path.exists(directory):
        os.makedirs(directory)
    for key in part_rig_data:
        with open('%s/%s.json' % (directory, key), mode='w') as f:
            json.dump(
                part_rig_data[key],
                f,
                sort_keys=True,
                indent=4,
                separators=(',', ': ')
            )


def delete_folder(path):
    if not os.path.exists(path):
        shutil.rmtree(path)


def create_empty_folder(path):
    if os.path.exists(path):
        proc = subprocess.Popen(
            'rmdir /s/q "%s"' % path,
            shell=True
        )
        proc.wait()
    os.makedirs(path)
