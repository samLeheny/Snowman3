# python modules
import os
import json
import logging
import glob

# iRig modules
import Snowman3.rigger.rig_factory as rig_factory
import Snowman3.rigger.rig_factory.utilities.dynamic_file_utilities as dfu



def get_current_realtime_directory():
    """
    Gets a realtime directory with version that matches latest product version
    (weather it exists yet or not)
    """
    major_version, minor_version = get_current_work_versions()
    realtime_directory = '%s/rig_build_realtime' % get_products_directory()
    return '%s/rig_build_realtime_v%s' % (
        realtime_directory,
        major_version
    )


def get_standard_build_script_path():
    return '%s/build/build.py' % os.path.dirname(rig_factory.__file__.replace('\\', '/'))


def get_all_users_work_scenes():
    """
    Get all users work files (.ma)
    """
    work_scenes = []
    for work_dir in get_all_users_work_directories():
        user_scenes = [x.replace('\\', '/') for x in glob.glob(
            '%s/%s_rig_v*.ma' % (
                work_dir,
                os.environ['ENTITY_NAME']
            )
        )]
        if user_scenes:
            work_scenes.extend(user_scenes)
    return sorted(work_scenes, key=lambda x: os.path.basename(x).split('_rig_v')[-1].split())


def get_next_versions(major_version_up=False):
    """
    get the next major and minor version strings based on ALL user work files
    """
    major_version, minor_version = get_current_work_versions()
    product_version = get_latest_product_version()
    if int(product_version) > int(major_version):
        major_version = product_version
        minor_version = '0001'

    if major_version_up:
        major_version = str(int(major_version) + 1).zfill(4)
        minor_version = '0001'
    else:
        minor_version = str(int(minor_version) + 1).zfill(4)

    return [major_version, minor_version]


def get_current_work_versions():
    """
    get the current major and minor version strings based on ALL user work files
    """
    work_scenes = get_all_users_work_scenes()
    if not work_scenes:
        return ['0000', '0000']
    latest_work_scene = work_scenes[-1]
    major_verson = os.path.basename(latest_work_scene).split('rig_v')[-1].split('.')[0]
    minor_version = os.path.basename(latest_work_scene).split('rig_v')[-1].split('.')[1]
    return [major_verson, minor_version]

"""
Switch to this version after we are sure all rigs have been saved with current source code 3/1/2022
"""


# def get_next_versions(major_version_up=False):
#     major, minor = stu.get_shotgrid_versions()
#     if major_version_up:
#         major += 1
#     minor += 1
#     return major, minor
#
#
# def get_current_work_versions():
#     return stu.get_shotgrid_versions()


def get_latest_product_version():
    latest_project_build_dir = dfu.get_latest_product_directory(
        os.environ['PROJECT_CODE'],
        os.environ['ENTITY_NAME'],
        product='rig_build')
    if not latest_project_build_dir:
        return '0000'
    return os.path.basename(latest_project_build_dir).split('rig_build_v')[-1]


def get_pipeline_directory():
    return '%s/assets/type/%s/%s/pipeline' % (
        get_base_directory(),
        os.environ['TT_ASSTYPE'],
        os.environ['ENTITY_NAME']
    )


def get_logs_directory():
    return '%s/logs' % get_pipeline_directory()


def get_work_directory():
    work_directory = '%s/assets/type/%s/%s/work' % (
        get_base_directory(),
        os.environ['TT_ASSTYPE'],
        os.environ['ENTITY_NAME']
    )
    return work_directory


def get_all_users_work_directories():
    work_rig_directory = '%s/rig/Maya' % get_work_directory()
    user_work_dirs = []
    for user in os.listdir(work_rig_directory):
        item_path = '%s/%s' % (work_rig_directory, user)
        if os.path.isdir(item_path):
            user_work_dirs.append(item_path)
    return user_work_dirs


def get_user_work_directory():
    return '%s/rig/Maya/%s' % (
        get_work_directory(),
        os.environ['USERNAME']
    )


def get_user_name():
    return os.environ['USERNAME']


def get_user_build_directory():
    return '%s/build' % (
        get_user_work_directory()
    )


def get_userdata_build_directory():
    return '%s/build/user_data' % (
        get_user_work_directory()
    )


def get_rigdata_build_directory():
    return '%s/build/rig_data' % (
        get_user_work_directory()
    )


def get_scene_cache_directory():
    return '%s/scene_cache' % get_elems_directory()


def get_elems_directory():
    return '%s/elems' % (
        get_work_directory()
    )


def get_gen_elems_directory():
    return '%s/assets/gen_elems' % (
        get_base_directory()
    )


def get_abc_directory():
    return dfu.get_abc_directory(
        os.environ['PROJECT_CODE'],
        os.environ['ENTITY_NAME']
    )


def get_abc_anim_directory():
    return dfu.get_abc_anim_directory(
        os.environ['PROJECT_CODE'],
        os.environ['ENTITY_NAME']
    )


def get_placements_directory():
    return dfu.get_placements_directory(
        os.environ['PROJECT_CODE'],
        os.environ['ENTITY_NAME']
    )


def get_bifrost_directory():
    return dfu.get_bifrost_directory(
        os.environ['PROJECT_CODE'],
        os.environ['ENTITY_NAME']
    )


def get_export_data_directory():
    return dfu.get_export_data_directory(
        os.environ['PROJECT_CODE'],
        os.environ['ENTITY_NAME']
    )


def get_anim_textures_directory():
    return dfu.get_anim_textures_directory(
        os.environ['PROJECT_CODE'],
        os.environ['ENTITY_NAME']
    )


def get_bifrost_files():
    return dfu.get_bifrost_files(
        os.environ['PROJECT_CODE'],
        os.environ['ENTITY_NAME']
    )


def get_abc_files():
    return dfu.get_abc_files(
        os.environ['PROJECT_CODE'],
        os.environ['ENTITY_NAME']
    )


def get_abc_anim_files():
    return dfu.get_abc_anim_files(
        os.environ['PROJECT_CODE'],
        os.environ['ENTITY_NAME']
    )


def get_placement_files():
    return dfu.get_placement_files(
        os.environ['PROJECT_CODE'],
        os.environ['ENTITY_NAME']
    )


def get_export_data_files():
    return dfu.get_export_data_files(
        os.environ['PROJECT_CODE'],
        os.environ['ENTITY_NAME']
    )


def get_anim_textures_files():
    return dfu.get_anim_textures_files(
        os.environ['PROJECT_CODE'],
        os.environ['ENTITY_NAME']
    )


def get_latest_abc():
    list_of_files = get_abc_files()
    if list_of_files:
        return list_of_files[-1]


def get_latest_rig_product():
    rig_products_directory = '%s/rig' % get_products_directory()
    if os.path.exists(rig_products_directory):
        list_of_files = glob.glob('%s/*.ma' % rig_products_directory)
        if list_of_files:
            latest_file = list_of_files[-1]
            return latest_file.replace('\\', '/')


def get_product_files():
    return dfu.get_product_files(
        os.environ['PROJECT_CODE'],
        os.environ['ENTITY_NAME']
    )


def get_product_directories():
    return dfu.get_product_directories(
        os.environ['PROJECT_CODE'],
        os.environ['ENTITY_NAME']
    )


def get_base_directory():
    return dfu.get_base_directory(
        os.environ['PROJECT_CODE']
    )


def get_products_directory():
    return '%s/assets/type/%s/%s/products' % (
        get_base_directory(),
        os.environ['TT_ASSTYPE'],
        os.environ['ENTITY_NAME']
    )


def get_latest_product_directory(product='rig_build'):
    rig_build_directory = '%s/%s' % (get_products_directory(), product)
    list_of_directories = [x.replace('\\', '/') for x in glob.glob(
        '%s/%s_v*' % (
            rig_build_directory,
            product
        )
    )]
    if list_of_directories:
        return sorted(list_of_directories, key=lambda x: os.path.basename(x))[-1]


def get_latest_realtime_product_directory():
    rig_build_directory = '%s/rig_build_realtime' % get_products_directory()
    list_of_directories = [x.replace('\\', '/') for x in glob.glob(
        '%s/rig_build_realtime_v*' % (
            rig_build_directory
        )
    )]
    if list_of_directories:
        return sorted(list_of_directories, key=lambda x: os.path.basename(x))[-1]


def get_project_config_path():
    if os.getenv('SHOW_DEV_MODE') == "True":
        dev_show_path = 'Snowman3.ProjectCode/{}/show_config.json'.format(
            os.getenv('PROJECT_CODE')
        )
        if os.path.exists(dev_show_path):
            return dev_show_path
        else:
            raise 'Unable to find show_config_json'


def to_relative_path(path, build_dir=None):
    """ If the path contains the build dir, trim the path to be relative to that """
    if build_dir is None:
        build_dir = get_user_build_directory()

    # Remove user_data from build_dir
    if build_dir.endswith('user_data'):
        build_dir = build_dir[:-10]

    # Remove rig_data from build_dir
    if build_dir.endswith('rig_data'):
        build_dir = build_dir[:-9]

    if path.startswith(build_dir):
        return path.split(build_dir, 1)[-1]
    return path


def from_relative_path(path, build_dir=None, check_exists=True):
    """ If the path is in relative form, prepend the build dir """
    if path.startswith('/'):
        if build_dir is None:
            build_dir = get_user_build_directory()
        path = build_dir + path
    if check_exists and not os.path.exists(path):
        raise Exception('File does not exist: %s ' % path)
    return path


def get_show_config_data():
    config_path = get_project_config_path()
    with open(config_path, mode='r') as f:
        config_data = json.load(f)
    return config_data


def get_proxy_shader_data_path(build_directory):
    if build_directory is None:
        logging.getLogger('rig_build').warning(
            'The directory you are sourcing from is set to None. Please load the asset through the correct means '
            'in order to get a proper root directory'
        )
        return
    else:
        build_userdata_directory = os.path.join(build_directory, 'user_data')

        paths_to_check = []
        if os.path.exists(build_directory):
            paths_to_check.append('%s/custom_proxy_data.json' % build_userdata_directory)  # build/user_data
            paths_to_check.append('%s/custom_proxy_data.json' % build_directory)  # the old /build location

        for path in paths_to_check:
            if os.path.exists(path):
                return path
            else:
                logging.getLogger('rig_build').warning(
                    'Custom Proxy Shader Data was not found here: {}'.format(path)
                )