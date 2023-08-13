import os
import json
import functools
import Snowman3.rigger.rig_api.parts as pts
import Snowman3.rigger.rig_factory.utilities.file_utilities as fut
import Snowman3.rigger.rig_factory.build.tasks.jobs.rig_tasks as rtsk
import Snowman3.rigger.rig_factory.build.tasks.jobs.guide_tasks as gtsk
from Snowman3.rigger.rig_factory.build.tasks.task_objects import BuildTask
import Snowman3.rigger.rig_factory.build.utilities.controller_utilities as cut


# ----------------------------------------------------------------------------------------------------------------------
def get_toggle_tasks(entity_build, parent=None, remove_vertices=False):
    root_task = BuildTask(
        parent=parent,
        build=entity_build,
        name='Toggle State'
    )

    BuildTask(
        parent=root_task,
        name='Toggle State',
        create_children_function=functools.partial(
            generate_toggle_tasks,
            entity_build,
            remove_vertices
        )
    )
    return root_task


# ----------------------------------------------------------------------------------------------------------------------
def generate_toggle_tasks(source_build, remove_vertices):
    toggle_build = source_build.get_toggle_build()
    toggle_orientation_task = BuildTask(
        build=toggle_build,
        name='Toggle Orientation Mode',
        function=pts.toggle_parts_orientation_mode
    )
    prepare_task = BuildTask(
        build=toggle_build,
        name='Prepare for toggle',
        function=prepare_for_toggle
    )
    delete_root_task = BuildTask(
        build=toggle_build,
        name='Delete Container',
        function=pts.delete_container
    )
    remove_vert_task = BuildTask(
        build=toggle_build,
        name='Remove Vert',
        function=pts.delete_vert(toggle_build, remove_vertices)
    )
    if toggle_build.guide:
        root_task = gtsk.get_guide_tasks(toggle_build)
    else:
        root_task = rtsk.get_rig_tasks(toggle_build)
    root_task.children[0].always_expand = True  # makes the build expand in BuildView
    return [toggle_orientation_task, prepare_task, delete_root_task, remove_vert_task, root_task]


# ----------------------------------------------------------------------------------------------------------------------
def prepare_for_toggle():
    controller = cut.get_controller()
    controller.root.prepare_for_toggle()
    controller.reset()


# ----------------------------------------------------------------------------------------------------------------------
def make_skins_directory():
    skins_directory = '%s/skin_clusters' % fut.get_user_build_directory()
    if not os.path.exists(skins_directory):
        os.makedirs(skins_directory)


# ----------------------------------------------------------------------------------------------------------------------
def get_local_skinned_geometry():
    """
    Get all geometry that has a skin that belongs to the root build layer (None)
    """
    controller = cut.get_controller()
    rig = controller.root
    valid_geometry_names = []
    for key in rig.geometry:
        geometry = rig.geometry[key]
        geometry_name = geometry.name
        skin_cluster = controller.find_skin_clusters(geometry)
        if skin_cluster:
            named_obs = controller.named_objects
            joints = [named_obs[x] for x in controller.scene.skinCluster(key, q=True, influence=True) if
                      x in named_obs]
            if geometry.layer is None  or any([joint.layer is None for joint in joints]):
                valid_geometry_names.append(geometry_name)
    return valid_geometry_names


# ----------------------------------------------------------------------------------------------------------------------
def export_skin_cluster_data_file(geometry_name, json_path):
    controller = cut.get_controller()
    if geometry_name not in controller.named_objects:
        return dict(
            status='warning',
            warning='Unable to find geometry "%s" in controller' % geometry_name
        )
    skin_clusters = controller.find_skin_clusters(controller.named_objects[geometry_name])
    if not skin_clusters:
        return dict(
            status='warning',
            warning='Unable to find skin cluster on : %s' % geometry_name
        )
    invalid_skins = []
    if len(skin_clusters) > 1:
        invalid_skins = skin_clusters[1:]

    skin_data = controller.scene.get_skin_data(skin_clusters[0])

    with open(json_path, mode='w') as f:
        json.dump(
            skin_data,
            f,
            sort_keys=True,
            indent=4,
            separators=(',', ': ')
        )
    if invalid_skins:
        return dict(
            status='warning',
            warning='More than one skin was found. The following were skipped : %s' % invalid_skins
        )
