import os
import glob


def get_server_base():
    server_base = os.environ.get('SERVER_BASE')
    if not os.path.exists(server_base):
        raise Exception('SERVER_BASE not found.')
    return server_base.replace('\\','/')

def get_base_directory(project):
    return '%s%s' % (
        get_server_base(),
        project
    )


def get_gen_elems_directory(project):
    return '%s/assets/gen_elems' % (
        get_base_directory(project)
    )


def get_products_directory(project, entity):
    print('MISSING SHOTGUN FUNCTIONALITY')
    '''
    asset_data = SG.find(
        "Asset",
        [["code", "is", entity], ["project.Project.sg_code", "is", project]],
        ["code", "sg_asset_type"]
    )
    if asset_data:
        return '%s/assets/type/%s/%s/products' % (
            get_base_directory(project),
            asset_data[0]['sg_asset_type'],
            entity
        )'''


def get_pipeline_directory(project, entity):
    print('MISSING SHOTGUN FUNCTIONALITY')
    '''asset_data = SG.find(
        "Asset",
        [["code", "is", entity], ["project.Project.sg_code", "is", project]],
        ["code", "sg_asset_type"]
    )
    if not asset_data:
        raise Exception('Unable to find asset with signature: Project=%s Entity=%s' % (project, entity))
    return '%s/assets/type/%s/%s/pipeline' % (
        get_base_directory(project),
        asset_data[0]['sg_asset_type'],
        entity
    )'''


def get_latest_product_directory(project, entity, product='rig_build'):
    # Gets the latest published rig build folder, avoiding any in-progress ('~' prefix) or broken folders
    rig_build_directory = '%s/%s' % (
        get_products_directory(
            project,
            entity
        ),
        product
    )
    list_of_directories = glob.glob(
        '%s/%s_v*' % (
            rig_build_directory,
            product
        )
    )
    if list_of_directories:
        return sorted(
            [x.replace('\\', '/') for x in list_of_directories],
            key=lambda x: os.path.basename(x)
        )[-1]


def get_latest_rig_product(project, entity):
    rig_products_directory = '%s/rig' % get_products_directory(project, entity)
    if os.path.exists(rig_products_directory):
        list_of_files = glob.glob('%s/*.ma' % rig_products_directory)
        if list_of_files:
            latest_file = max(list_of_files, key=os.path.getctime)
            return latest_file.replace('\\', '/')


def get_logs_directory(project, entity):
    return '%s/logs' % get_pipeline_directory(project, entity)


def get_all_users_work_directories(project, entity):
    work_rig_directory = '%s/rig/Maya' % get_work_directory(project, entity)
    user_work_dirs = []
    for user in os.listdir(work_rig_directory):
        item_path = '%s/%s' % (work_rig_directory, user)
        if os.path.isdir(item_path):
            user_work_dirs.append(item_path)
    return user_work_dirs


def get_all_users_work_scenes(project, entity):
    """
    Get all users work files (.ma)
    """
    work_scenes = []
    for work_dir in get_all_users_work_directories(project, entity):
        user_scenes = [x.replace('\\', '/') for x in glob.glob(
            '%s/%s_rig_v*.ma' % (
                work_dir,
                entity
            )
        )]
        if user_scenes:
            work_scenes.extend(user_scenes)
    return sorted(work_scenes, key=lambda x: os.path.basename(x).split('_rig_v')[-1].split())

def get_current_work_versions(project, entity):
    """
    get the current major and minor version strings based on ALL user work files
    """
    work_scenes = get_all_users_work_scenes(project, entity)
    if not work_scenes:
        return ['0000', '0000']
    latest_work_scene = work_scenes[-1]
    major_verson = os.path.basename(latest_work_scene).split('rig_v')[-1].split('.')[0]
    minor_version = os.path.basename(latest_work_scene).split('rig_v')[-1].split('.')[1]
    return [major_verson, minor_version]



def get_anim_textures_date(project, entity):
    anim_texture_path = '%s/anim_textures' % get_products_directory(project, entity)

    if os.path.exists(anim_texture_path):
        shader_json = '%s/bake_anim_shaders.json' % anim_texture_path
        if not os.path.lexists(shader_json):
            return None
        else:
            json_date = os.path.getmtime(shader_json)
            return float(json_date)


def get_elems_directory(project, entity):
    return '%s/elems' % (
        get_work_directory(project, entity)
    )


def get_work_directory(project, entity):
    print('MISSING SHOTGUN FUNCTIONALITY')
    '''
    asset_data = SG.find(
        "Asset",
        [["code", "is", entity], ["project.Project.sg_code", "is", project]],
        ["code", "sg_asset_type"]
    )

    return '%s/assets/type/%s/%s/work' % (
        get_base_directory(project),
        asset_data[0]['sg_asset_type'],
        entity
    )
    '''


def get_user_build_directory(project, entity):
    return '%s/rig/Maya/%s/build' % (
        get_work_directory(project, entity),
        os.environ['USERNAME']
    )


def get_abc_directory(project, entity):
    return '%s/abc' % get_products_directory(project, entity)


def get_abc_anim_directory(project, entity):
    return '%s/abc_anim' % get_products_directory(project, entity)


def get_placements_directory(project, entity):
    return '%s/placements' % get_products_directory(project, entity)


def get_bifrost_directory(project, entity):
    return '%s/bifrost' % get_products_directory(project, entity)


def get_export_data_directory(project, entity):
    return '%s/export_data' % get_pipeline_directory(project, entity)


def get_fin_export_data_directory(project, entity):
    return '%s/fin_export_data' % get_pipeline_directory(project, entity)


def get_set_snap_locators_directory(project, entity):
    return '%s/set_snap_locators' % get_pipeline_directory(project, entity)


def get_anim_textures_directory(project, entity):
    return '%s/anim_textures/Backup' % get_products_directory(project, entity)


def get_bifrost_files(project, entity):
    return get_list_of_files(get_bifrost_directory(project, entity), 'ma')


def get_abc_files(project, entity):
    return get_list_of_files(get_abc_directory(project, entity), 'abc')


def get_abc_anim_files(project, entity):
    return get_list_of_files(get_abc_anim_directory(project, entity), 'abc')


def get_placement_files(project, entity):
    return get_list_of_files(get_placements_directory(project, entity), 'ma')


def get_export_data_files(project, entity):
    return get_list_of_files(get_export_data_directory(project, entity), 'json')


def get_fin_export_data_files(project, entity):
    return get_list_of_files(get_fin_export_data_directory(project, entity), 'json')


def get_set_snap_locator_files(project, entity):
    return get_list_of_files(get_set_snap_locators_directory(project, entity), 'json')


def get_anim_textures_files(project, entity):
    # return get_list_of_files(get_anim_textures_directory(project, entity), 'zip')
    return []


def get_list_of_files(directory, extension):
    if os.path.exists(directory):
        list_of_files = [x.replace('\\', '/') for x in glob.glob('%s/*.%s' % (directory, extension))]
        if list_of_files:
            return sorted(
                list_of_files,
                key=lambda x: os.path.getctime(x)
            )
    return []


def get_product_files(project, entity):
    return dict(
        abc=get_abc_files(project, entity),
        abc_anim=get_abc_anim_files(project, entity),
        placements=get_placement_files(project, entity),
        bifrost=get_bifrost_files(project, entity),
        export_data=get_export_data_files(project, entity),
        fin_export_data=get_fin_export_data_files(project, entity),
        set_snap_locators=get_set_snap_locator_files(project, entity),
        anim_textures=get_anim_textures_files(project, entity)
    )


def get_product_directories(project, entity):
    return dict(
        abc=get_abc_directory(project, entity),
        abc_anim=get_abc_anim_directory(project, entity),
        placements=get_placements_directory(project, entity),
        bifrost=get_bifrost_directory(project, entity),
        export_data=get_export_data_directory(project, entity),
        fin_export_data=get_fin_export_data_directory(project, entity),
        set_snap_locators=get_set_snap_locators_directory(project, entity),
        anim_textures=get_anim_textures_directory(project, entity)
    )