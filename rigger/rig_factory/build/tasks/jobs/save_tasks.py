import os
import json
import logging
import functools
import subprocess
from datetime import datetime
import Snowman3.rigger.rig_api.parts as pts
import Snowman3.rigger.rig_factory.objects as obs
import Snowman3.rigger.rig_factory.environment as env
import Snowman3.rigger.rig_factory.system_signals as ssg
import Snowman3.rigger.rig_factory.utilities.file_utilities as fut
import Snowman3.rigger.rig_factory.utilities.blueprint_utilities as blueprint_utils
from Snowman3.rigger.rig_factory.build.tasks.task_objects import BuildTask
#import Snowman3.utilities.shotgun_utilities.task_utilities as stu
import Snowman3.rigger.rig_factory.build.utilities.controller_utilities as cut
from Snowman3.rigger.rig_factory.objects.part_objects.container import Container
import Snowman3.rigger.rig_factory.build.tasks.jobs.export_rig_data_tasks as erdt
#import Snowman3.rigger.rig_factory.utilities.face_utilities.face_utilities as fcu
import Snowman3.rigger.rig_factory.build.tasks.task_utilities.task_utilities as tut


def get_save_tasks(entity_build, comment=None, major_version_up=False, parent=None, version_from_env=False):

    controller = cut.get_controller()
    if not controller.root:
        raise Exception('No rig found.')

    entity_builds = tut.flatten(entity_build)

    root_task = BuildTask(
        build=entity_build,
        parent=parent,
        name='Save Work'
    )
    BuildTask(
        build=entity_build,
        parent=root_task,
        name='Check Folder Size',
        function=check_folder_size
    )
    if controller.scene.mock:
        return root_task

    callbacks_task = BuildTask(
        name='Pre Save Callbacks',
        parent=root_task
    )
    for build in entity_builds:
        BuildTask(
            build=build,
            name='Build.execute_pre_save()',
            parent=callbacks_task,
            function=build.create_callback('execute_pre_save'),
        )
        BuildTask(
            build=build,
            name='Build.before_save()',
            parent=callbacks_task,
            function=build.create_callback('before_save'),
        )
        BuildTask(
            build=build,
            name='toggle_parts_orientation_mode',
            parent=callbacks_task,
            function=pts.toggle_parts_orientation_mode,
        )

    BuildTask(
        name='Rename Work Scene',
        function=functools.partial(
            rename_scene_file,
            major_version_up=major_version_up,
            version_from_env=version_from_env
        ),
        parent=root_task,

    )
    BuildTask(
        name='Remove Vaccine',
        function=remove_vaccine,
        parent=root_task,
    )

    BuildTask(
        name='Save Scene File',
        function=save_scene_file,
        parent=root_task,
    )

    BuildTask(
        name='Save build_directory',
        function=save_user_directory,
        parent=root_task
    )

    if controller.root:
        BuildTask(
            name='Export rig blueprint',
            function=export_rig_blueprint,
            parent=root_task,
        )
        if isinstance(controller.root, Container):
            if controller.root.use_external_rig_data:
                if not controller.root.use_manual_rig_data:
                    erdt.get_export_rig_data_tasks(
                        entity_build,
                        parent=root_task
                    )
    if controller.face_network:
        BuildTask(
            name='Export face blueprint',
            function=export_face_blueprint,
            parent=root_task
        )

    BuildTask(
        name='Setup build folders',
        function=setup_build_folders,
        parent=root_task
    )

    BuildTask(
        name='Version-up build-directory',
        function=version_up_build_directory,
        parent=root_task,
    )

    BuildTask(
        name='Add Comment',
        function=functools.partial(
            tut.add_comment,
            comment
        ),
        parent=root_task,
    )
    BuildTask(
        name='Update shot-grid versions',
        function=update_shotgrid_task_versions,
        parent=root_task,
    )

    return root_task



def setup_build_folders():
    for folder_name in ['ignore', 'user_data', 'rig_data']:
        directory = '%s/%s' % (env.local_build_directory, folder_name)
        if not os.path.exists(directory):
            logging.getLogger('rig_build').info('Creating directory: %s' % directory)
            os.makedirs(directory)



def make_skins_directory():
    skins_directory = '%s/skin_clusters' % fut.get_user_build_directory()
    if not os.path.exists(skins_directory):
        os.makedirs(skins_directory)



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



def update_shotgrid_task_versions():
    major_version, minor_version = fut.get_current_work_versions()
    stu.update_task_data(
        sg_publish_version=int(major_version),
        sg_wip_version=int(minor_version)
    )



def rename_scene_file(major_version_up=False, version_from_env=False):
    controller = cut.get_controller()
    logger = logging.getLogger('rig_build')
    wip_directory = fut.get_user_work_directory()

    if not os.path.exists(wip_directory):
        os.makedirs(str(wip_directory))
    ext = '.mb' if os.environ.get('TT_MAYAFILETYPE') == 'mayaBinary' else '.ma'

    if version_from_env:
        # Use dynamic version resolved by publish process
        major_version = os.environ.get('FW_RIG_PUBLISH_VERSION', None)
        if not major_version:
            raise StandardError(
                "Env var 'FW_RIG_PUBLISH_VERSION' is invalid! version_from_env is only for publish process.")
        minor_version = '0001'
    else:
        major_version, minor_version = fut.get_next_versions(
            major_version_up=major_version_up
        )

    file_name = os.environ['ENTITY_NAME'] + '_rig_v' + major_version + '.' + minor_version + ext
    wip_file = '%s/%s' % (wip_directory, file_name)
    if os.path.exists(wip_file):
        controller.raise_warning('Wip file "%s" already existed. Overwriting file.' % file_name)
    logger.info('Saving Work scene: : %s' % wip_file)
    controller.scene.file(rn=wip_file)



def remove_vaccine():
    controller = cut.get_controller()
    if not controller.scene.mock:
        import Snowman3.rigger.rig_factory.build.utilities.virus_utilities as vut
        vut.remove_vaccine()



def save_scene_file():
    controller = cut.get_controller()
    if controller.scene.mock:
        return dict(
            status='warning',
            warning='WARNING: Mock mode active. Task aborted'
        )
    controller.scene.file(
        save=True,
        force=True,
        type='mayaAscii'
    )



def save_user_directory():
    user_build_directory = fut.get_user_build_directory()
    if env.local_build_directory == user_build_directory:
        return dict(
            info='No need to save work directory. Current build_directory was already set to users work %s' % user_build_directory
        )

    deleted_old_directory = False
    if os.path.exists(user_build_directory):
        proc = subprocess.Popen(
            'rmdir /s/q "%s"' % user_build_directory,
            shell=True
        )
        proc.wait()
        deleted_old_directory = True
    logging.getLogger('rig_build').info(
        'Copying current build directory "%s" to: %s' % (
            env.local_build_directory,
            user_build_directory
        )
    )
    proc = subprocess.Popen(
        'robocopy %s %s /E /S' % (
            env.local_build_directory,
            user_build_directory,
        ),
        shell=True
    )
    proc.wait()
    ssg.set_build_directory(user_build_directory)
    if deleted_old_directory:
        return dict(
            status='warning',
            warning='Deleted old build directory: %s' % user_build_directory
        )



def export_rig_blueprint(build_directory=None):
    controller = cut.get_controller()
    if not controller.root:
        raise Exception('Rig not found')
    if not build_directory:
        build_directory = fut.get_user_build_directory()
    if not os.path.exists(build_directory):
        os.makedirs(build_directory)
    rig_blueprint_path = f'{build_directory}/rig_blueprint.json'
    logging.getLogger('rig_build').info('Saving rig blueprint: {rig_blueprint_path}')
    with open(rig_blueprint_path, mode='w') as f:
        json.dump(
            blueprint_utils.get_blueprint(),
            f,
            sort_keys=True,
            indent=4,
            separators=(',', ': ')
        )



def export_face_blueprint():
    controller = cut.get_controller()
    if not controller.face_network:
        raise Exception('Face Network not found')
    user_build_directory = fut.get_user_build_directory()
    if not os.path.exists(user_build_directory):
        os.makedirs(user_build_directory)
    face_blueprint_path = '%s/face_blueprint.json' % user_build_directory
    logging.getLogger('rig_build').info('Saving face blueprint: %s' % face_blueprint_path)
    fcu.export_face_blueprint(file_name=face_blueprint_path)



def version_up_build_directory():
    controller = cut.get_controller()
    if controller.scene.mock:
        return dict(
            status='warning',
            warning='WARNING: Mock mode active. Task aborted'
        )
    evaluation_mode = str(controller.scene.evaluationManager(q=True, mode=True)[0])
    controller.scene.evaluationManager(mode="off")
    if controller.currently_saving:
        raise Exception('A save is already in progress')
    if isinstance(controller.root, obs.Container) and controller.root.has_been_finalized:
        raise Exception('The rig has been finalized.\nA blueprint cannot be saved.')
    if isinstance(controller.face_network, obs.FaceNetwork) and controller.face_network.has_been_finalized:
        raise Exception('The face has been finalized.\nA bluprint cannot be saved.')
    controller.currently_saving = True
    scene_name = controller.scene.file(q=True, sn=True)
    if not os.path.exists(scene_name):
        raise Exception('Save Failed. Check script editor for details')
    versioned_directory_name_base_name = os.path.basename(scene_name).replace('.ma', '').replace('.mb', '')
    user_build_directory = fut.get_user_build_directory()
    if not os.path.exists(user_build_directory):
        raise Exception('Directory not found: %s' % user_build_directory)
    version_directory = '%s_versions/%s' % (
        user_build_directory,
        versioned_directory_name_base_name
    )
    removed_version_directory = False
    if os.path.isdir(version_directory):
        logging.getLogger('rig_build').info(
            'removing directory: %s' % version_directory
        )
        proc = subprocess.Popen(
            'rmdir /s/q "%s"' % version_directory,
            shell=True
        )
        proc.wait()
        removed_version_directory = True

    logging.getLogger('rig_build').info(
        'Copying directory from "%s" to --> "%s"' % (
            user_build_directory,
            version_directory
        )
    )
    proc = subprocess.Popen(
        'robocopy %s %s /E /S' % (
            user_build_directory,
            version_directory
        ),
        shell=True
    )
    proc.wait()
    temp_text_file_directory = '%s/TEMP_FILE_FOR_FOLDER_DATE_TIME.txt' % version_directory
    with open(temp_text_file_directory, mode='w') as f:
        f.write('This is a test')
    os.remove(temp_text_file_directory)
    controller.currently_saving = False
    controller.scene.evaluationManager(mode=evaluation_mode)

    # Get current time in a readable format and pass into signal to send back to rig_widget
    current_time = datetime.now()
    current_time_formatted = current_time.strftime('%H:%M:%S')
    ssg.gui_signals['saved_time_signal'].emit(current_time_formatted)
    if removed_version_directory:
        return dict(
            status='warning',
            warning='Removed pre-existing version directory: %s' % version_directory
        )
    return dict(
        info='Copied directory from "%s" to --> "%s"' % (
            user_build_directory,
            version_directory
        )
    )



def check_folder_size(max_bytes=1000000000):
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(env.local_build_directory):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            if not os.path.islink(fp):
                total_size += os.path.getsize(fp)

    if total_size > max_bytes:
        return dict(
            status='warning',
            warning='Folder size is larger than %s gigs: %s' % (
                1000000000.0 / max_bytes,
                env.local_build_directory
            )

        )
