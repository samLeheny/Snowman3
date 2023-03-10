# Title: blueprint_utils.py
# Author: Sam Leheny
# Contact: samleheny@live.com

# Description:


###########################
##### Import Commands #####
import json
import importlib
import pymel.core as pm

import Snowman3.riggers.utilities.module_utils as module_utils
importlib.reload(module_utils)
Module = module_utils.Module

import Snowman3.riggers.utilities.part_utils as part_utils
importlib.reload(part_utils)
Part = part_utils.Part
###########################
###########################

###########################
######## Variables ########
core_data_filename = 'core_data'
###########################
###########################



########################################################################################################################
class Blueprint:
    def __init__(
        self,
        asset_name,
        dirpath = None,
        loose_parts = None,
        modules = None

    ):
        self.asset_name = asset_name
        self.dirpath = dirpath
        self.loose_parts = loose_parts if loose_parts else {}
        self.modules = modules if modules else {}



####################################################################################################################
def save(dirpath, blueprint):
    blueprint_data = data_from_blueprint(blueprint)
    filepath = f'{dirpath}/{core_data_filename}.json'
    print(f'\nExporting blueprint data to dir: {filepath}...')
    with open(filepath, 'w') as fh:
        json.dump(blueprint_data, fh, indent=5)


####################################################################################################################
def data_from_blueprint(blueprint):
    data = {
        'asset_name': blueprint.asset_name,
        'dirpath': blueprint.dirpath,
        'modules': blueprint.modules,
        'loose_parts': blueprint.loose_parts
    }
    return data


####################################################################################################################
def load(dirpath):
    blueprint_data = data_from_file(dirpath)
    blueprint = blueprint_from_data(blueprint_data)
    return blueprint


####################################################################################################################
def data_from_file(dirpath):
    with open(f'{dirpath}/{core_data_filename}.json', 'r') as fh:
        data = json.load(fh)
    return data


####################################################################################################################
def blueprint_from_data(data):
    blueprint = Blueprint(
        asset_name = data['asset_name'],
        dirpath = data['dirpath'],
        modules = data['modules'],
        loose_parts = data['loose_parts']
    )
    return blueprint


####################################################################################################################
def blueprint_from_file(dirpath):
    blueprint_data = data_from_file(dirpath)
    blueprint = blueprint_from_data(blueprint_data)
    return blueprint


####################################################################################################################
def update_blueprint_from_scene(blueprint):
    # ...Update modules
    blueprint_data = data_from_blueprint(blueprint)
    modules_data = blueprint_data['modules']
    modules = [module_utils.module_from_data(d) for d in modules_data.values()]
    for module in modules:
        module_utils.update_module_from_scene(module)
    # ...Re-export blueprint data
    blueprint = blueprint_from_data(blueprint_data)
    save(dirpath=f"{blueprint_data['dirpath']}/working", blueprint=blueprint)


####################################################################################################################
def mirror_module(blueprint, module_key, driver_side='L', driven_side='R'):
    module = blueprint.modules[module_key]
    module_utils.mirror_module(module, driver_side=driver_side, driven_side=driven_side)


####################################################################################################################
def add_part_to_module(part, module):
    part.name = f'{module.side_tag}{module.name}_{part.name}'
    scene_part = part_utils.create_scene_part(part, parent=module_utils.get_scene_module(module))
    module.parts[f'{part.side_tag}{part.name}'] = part_utils.data_from_part(part)
    update_module_in_blueprint(module)
    return scene_part


####################################################################################################################
def remove_module_from_blueprint(module):
    dirpath = r'C:\Users\61451\Desktop\test_build\working'
    working_blueprint = blueprint_from_file(dirpath)
    working_blueprint.modules.pop(f'{module.side_tag}{module.name}')
    # ...Update disk
    save(dirpath=dirpath, blueprint=working_blueprint)


####################################################################################################################
def remove_scene_module(module):
    module_name = module_utils.get_module_name(module)
    if not pm.objExists(module_name):
        print(f"Cannot delete part {''} - part not found in scene.")
        return False
    pm.delete(pm.PyNode(module_name))
    remove_module_from_blueprint(module)
    return True


####################################################################################################################
def add_module_to_blueprint(module, check_for_clashes=True):
    dirpath = r'C:\Users\61451\Desktop\test_build\working'
    working_blueprint = blueprint_from_file(dirpath)
    module_key = f'{module.side_tag}{module.name}'
    if check_for_clashes:
        if module_key in working_blueprint.modules.keys():
            print(f"Cannot add module '{module_key}' to blueprint - "
                  f"a module with this name already exists in blueprint.")
            return False
    working_blueprint.modules[module_key] = module_utils.data_from_module(module)
    # ...Update disk
    save(dirpath=dirpath, blueprint=working_blueprint)


####################################################################################################################
def update_module_in_blueprint(module):
    add_module_to_blueprint(module, check_for_clashes=False)


####################################################################################################################
def add_part_to_blueprint(part, check_for_clashes=True):
    dirpath = r'C:\Users\61451\Desktop\test_build\working'
    working_blueprint = blueprint_from_file(dirpath)
    part_key = f'{part.side_tag}{part.name}'
    if check_for_clashes:
        if part_key in working_blueprint.loose_parts:
            print(f"Cannot add part '{part_key}' to blueprint - a part with this name already exists in blueprint.")
            return False
    working_blueprint.loose_parts[part_key] = part_utils.data_from_part(part)
    # ...Update disk
    save(dirpath=dirpath, blueprint=working_blueprint)


####################################################################################################################
def remove_part_from_blueprint(part):
    dirpath = r'C:\Users\61451\Desktop\test_build\working'
    working_blueprint = blueprint_from_file(dirpath)
    working_blueprint.loose_parts.pop(f'{part.side_tag}{part.name}')
    # ...Update disk
    save(dirpath=dirpath, blueprint=working_blueprint)


####################################################################################################################
def remove_scene_part(part):
    part_name = part_utils.get_part_name(part)
    if not pm.objExists(part_name):
        print(f"Cannot delete part {''} - part not found in scene.")
        return False
    pm.delete(pm.PyNode(part_name))
    remove_part_from_blueprint(part)
    return True


####################################################################################################################
def create_loose_scene_part(part, parent=None):
    scene_part = part_utils.create_scene_part(part, parent=parent)
    add_part_to_blueprint(part)
    return scene_part
