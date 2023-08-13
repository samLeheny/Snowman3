import os
import logging
from shutil import copyfile



# ----------------------------------------------------------------------------------------------------------------------
def setup_build_directory(build_directory):
    ensure_build_directory_exists(build_directory)
    ensure_build_script_path_exists(build_directory)


# ----------------------------------------------------------------------------------------------------------------------
def ensure_build_directory_exists(build_directory):
    if not os.path.exists(build_directory):
        create_build_directory(build_directory)


# ----------------------------------------------------------------------------------------------------------------------
def create_build_directory(build_directory):
    logging.getLogger('rig_build').info(f'Creating directory: {build_directory}')
    os.makedirs(build_directory)


# ----------------------------------------------------------------------------------------------------------------------
def ensure_build_script_path_exists(build_directory):
    build_script_path = f'{build_directory}/build.py'
    if not os.path.exists(build_script_path):
        create_build_script_path(build_directory)


# ----------------------------------------------------------------------------------------------------------------------
def create_build_script_path(build_directory):
    build_script_path = f'{build_directory}/build.py'
    project_build_path = 'C:/Users/61451/Documents/Projects/{}/Scripts/build.py'.format(
        os.environ['PROJECT_CODE']
    )
    if not os.path.exists(project_build_path):
        raise Exception(
            'Unable to find {} build module: {}'.format(
                os.getenv('PROJECT_CODE'),
                project_build_path
            )
        )
    copyfile( project_build_path, build_script_path )
