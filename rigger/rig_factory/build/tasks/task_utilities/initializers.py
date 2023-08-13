import os
#import Snowman3.utilities.shotgun_utilities.shotgun_utils as sgu
import Snowman3.rigger.rig_factory.utilities.dynamic_file_utilities as dfu
import Snowman3.rigger.rig_factory.build.tasks.jobs.rig_tasks as rtsk
import Snowman3.rigger.rig_factory.build.tasks.jobs.guide_tasks as gtsk
import Snowman3.rigger.rig_factory.build.tasks.task_objects as tob
from Snowman3.rigger.rig_factory.build.tasks.task_objects import BuildTask
import Snowman3.rigger.rig_factory.utilities.build_directory_utilities as build_dir_utils


def yield_builds(
        project,
        entity,
        controller,
        build_directory,
        rig_blueprint=None,
        face_blueprint=None,
        guide=None,
        parent=None,
        namespace=None,
        product='rig_build',  # Needed to resolve child/accessory build_directories
        blueprint_file_name='rig_blueprint.json',
        face_blueprint_file_name='face_blueprint.json',
        children_about_to_be_inserted_callback=None,
        children_inserted_callback=None,
        task_callback=None,
        retrieve_data=False

):
    if build_directory and not os.path.exists(build_directory):
        raise Exception(f'Build directory does not exist: {build_directory}')
    build_dir_utils.setup_build_directory(build_directory)
    if rig_blueprint and guide is None:
        guide = 'guide_blueprint' not in rig_blueprint
    build = tob.EntityBuild(
        project,
        entity,
        controller,
        build_directory=build_directory,
        namespace=namespace,
        parent=parent,
        guide=guide,
        rig_blueprint_file_name=blueprint_file_name,
        face_blueprint_file_name=face_blueprint_file_name,
        rig_blueprint=rig_blueprint,
        face_blueprint=face_blueprint,
        retrieve_data=retrieve_data,
        children_about_to_be_inserted_callback=children_about_to_be_inserted_callback,
        children_inserted_callback=children_inserted_callback,
        task_callback=task_callback
    )
    yield build
    '''for parent_entity in sgu.get_parent_asset_names(project, entity):
        for build in yield_builds(
            project,
            parent_entity,
            controller,
            dfu.get_latest_product_directory(
                project,
                parent_entity,
                product=product
            ),
            product=product,
            guide=guide,
            parent=build,
            blueprint_file_name=blueprint_file_name,
            face_blueprint_file_name=face_blueprint_file_name,
            retrieve_data=retrieve_data,
            children_about_to_be_inserted_callback=children_about_to_be_inserted_callback,
            children_inserted_callback=children_inserted_callback,
            task_callback=task_callback
        ):
            yield build
    

    for accessory_entity in sgu.get_accessory_names(project, entity):

        for build in yield_builds(
            project,
            accessory_entity,
            controller,
            dfu.get_latest_product_directory(
                project,
                accessory_entity,
                product=product
            ),
            product=product,
            guide=guide,
            parent=build,
            namespace=accessory_entity,
            blueprint_file_name=blueprint_file_name,
            face_blueprint_file_name=face_blueprint_file_name,
            retrieve_data=retrieve_data,
            children_about_to_be_inserted_callback=children_about_to_be_inserted_callback,
            children_inserted_callback=children_inserted_callback,
            task_callback=task_callback
        ):

            yield build
    '''


def get_root_build(
        project,
        entity,
        controller,
        build_directory,
        rig_blueprint=None,
        face_blueprint=None,
        guide=None,
        parent=None,
        namespace=None,
        product='rig_build',
        blueprint_file_name='rig_blueprint.json',
        face_blueprint_file_name='face_blueprint.json',
        retrieve_data=False,
        children_about_to_be_inserted_callback=None,
        children_inserted_callback=None,
        task_callback=None

):

    builds = list(
        yield_builds(
            project,
            entity,
            controller,
            build_directory,
            rig_blueprint=rig_blueprint,
            face_blueprint=face_blueprint,
            guide=guide,
            parent=parent,
            namespace=namespace,
            product=product,
            blueprint_file_name=blueprint_file_name,
            face_blueprint_file_name=face_blueprint_file_name,
            retrieve_data=retrieve_data,
            children_about_to_be_inserted_callback=children_about_to_be_inserted_callback,
            children_inserted_callback=children_inserted_callback,
            task_callback=task_callback
        )
    )

    return builds[0]


def get_root_task(root_build, parent=None):
    if not root_build.rig_blueprint:
        return BuildTask(
            parent=parent,
            build=root_build,
            name='No Toggle Needed'
        )

    guide_mode = 'guide_blueprint' not in root_build.rig_blueprint
    if guide_mode:
        return gtsk.get_guide_tasks(root_build, parent=parent)
    else:
        return rtsk.get_rig_tasks(root_build, parent=parent)
