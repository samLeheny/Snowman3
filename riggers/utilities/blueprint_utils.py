# Title: blueprint_utils.py
# Author: Sam Leheny
# Contact: samleheny@live.com

# Description:


###########################
##### Import Commands #####
import json
import importlib
import pymel.core as pm

import Snowman3.utilities.general_utils as gen
importlib.reload(gen)

import Snowman3.riggers.utilities.module_utils as module_utils
importlib.reload(module_utils)
Module = module_utils.Module

import Snowman3.riggers.utilities.part_utils as part_utils
importlib.reload(part_utils)
Part = part_utils.Part

import Snowman3.riggers.utilities.placer_utils as placer_utils
importlib.reload(placer_utils)
Placer = placer_utils.Placer
###########################
###########################

###########################
######## Variables ########
core_data_filename = 'core_data'
working_dir = 'working'
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



########################################################################################################################
def save_blueprint(dirpath, blueprint, filename=core_data_filename):
    blueprint_data = data_from_blueprint(blueprint)
    filepath = f'{dirpath}/{filename}.json'
    print(f'\nExporting blueprint data to dir: {filepath}...')
    with open(filepath, 'w') as fh:
        json.dump(blueprint_data, fh, indent=5)


########################################################################################################################
def data_from_blueprint(blueprint):
    data = {}
    for param, value in vars(blueprint).items():
        data[param] = value
    return data


########################################################################################################################
def data_from_file(dirpath):
    with open(f'{dirpath}/{core_data_filename}.json', 'r') as fh:
        data = json.load(fh)
    return data


########################################################################################################################
def blueprint_from_data(data):
    blueprint = Blueprint(**data)
    return blueprint


########################################################################################################################
def blueprint_from_file(dirpath):
    blueprint_data = data_from_file(dirpath)
    blueprint = blueprint_from_data(blueprint_data)
    return blueprint


########################################################################################################################
def update_blueprint_from_scene(blueprint):
    # ...Update modules
    blueprint_data = data_from_blueprint(blueprint)
    modules_data = blueprint_data['modules']
    modules = [module_utils.module_from_data(d) for d in modules_data.values()]
    for module in modules:
        module_utils.update_module_from_scene(module)
    # ...Re-export blueprint data
    blueprint = blueprint_from_data(blueprint_data)
    save_blueprint(dirpath=f"{blueprint_data['dirpath']}/{working_dir}", blueprint=blueprint)


########################################################################################################################
def add_module_to_blueprint(module, check_for_clashes=True):
    dirpath = r'C:\Users\61451\Desktop\test_build\working'
    working_blueprint = blueprint_from_file(dirpath)
    if check_for_clashes:
        if module_exists(module, working_blueprint):
            print(f"Cannot add module '{module.scene_name}' to blueprint - "
                  f"a module with this name already exists in blueprint.")
            return False
    working_blueprint.modules[module.data_name] = module_utils.data_from_module(module)
    # ...Update disk
    save_blueprint(dirpath=dirpath, blueprint=working_blueprint)


########################################################################################################################
def add_part_to_module(part, module, check_for_clashes=True):
    if check_for_clashes:
        if part_exists(part, module):
            print(f"Cannot add part '{part.scene_name}' to blueprint - "
                  f"a part with this name already exists in blueprint.")
            return False
    module.parts[part.data_name] = part_utils.data_from_part(part)
    update_module_in_blueprint(module)


########################################################################################################################
def add_placer_to_part(placer, part, module, check_for_clashes=True):
    if check_for_clashes:
        if placer_exists(placer, part):
            print(f"Cannot add placer '{placer.scene_name}' to blueprint - "
                  f"a placer with this name already exists in blueprint.")
            return False
    part.placers[placer.data_name] = placer_utils.data_from_placer(placer)
    update_part_in_blueprint(part, module)


########################################################################################################################
def module_exists(module, blueprint):
    if module.data_name in blueprint.modules.keys():
        return True
    return False


########################################################################################################################
def part_exists(part, module):
    if part.data_name in module.parts.keys():
        return True
    return False


########################################################################################################################
def placer_exists(placer, part):
    if placer.data_name in part.placers.keys():
        return True
    return False


########################################################################################################################
def create_placer(placer, part, module):
    if not placer.scene_name:
        placer.scene_name = f'{gen.side_tag(placer.side)}{module.name}_{part.name}_{placer.name}'
    scene_placer = placer_utils.create_scene_placer(placer, parent=part_utils.get_scene_part(part))
    add_placer_to_part(placer, part, module)
    return scene_placer


########################################################################################################################
def remove_module(module):
    remove_module_from_blueprint(module)
    remove_module_from_scene(module)


########################################################################################################################
def remove_module_from_blueprint(module):
    dirpath = r'C:\Users\61451\Desktop\test_build\working'
    working_blueprint = blueprint_from_file(dirpath)
    working_blueprint.modules.pop(f'{module.side_tag}{module.name}')
    save_blueprint(dirpath=dirpath, blueprint=working_blueprint)


########################################################################################################################
def remove_module_from_scene(module):
    if not pm.objExists(module.scene_name):
        print(f"Cannot delete part {module.scene_name} - part not found in scene.")
        return False
    pm.delete(pm.PyNode(module.scene_name))
    return True


########################################################################################################################
def remove_part_from_module(part, module):
    remove_part_from_blueprint(part, module)
    remove_part_from_scene(part, module)


########################################################################################################################
def remove_part_from_blueprint(part, module):
    dirpath = r'C:\Users\61451\Desktop\test_build\working'
    working_blueprint = blueprint_from_file(dirpath)
    working_blueprint.modules[module.data_name]['parts'].pop(part.data_name)
    save_blueprint(dirpath=dirpath, blueprint=working_blueprint)


########################################################################################################################
def remove_part_from_scene(part, module):
    if not pm.objExists(part.scene_name):
        print(f"Cannot delete part {part.scene_name} - part not found in scene.")
        return False
    pm.delete(pm.PyNode(part.scene_name))
    return True


########################################################################################################################
def remove_placer_from_part(placer, part, module):
    remove_part_from_blueprint(placer, part)
    remove_part_from_scene(placer, part)


########################################################################################################################
def remove_placer_from_blueprint(placer, part, module):
    dirpath = r'C:\Users\61451\Desktop\test_build\working'
    working_blueprint = blueprint_from_file(dirpath)
    working_blueprint.modules[module.data_name]['parts'][part.data_name]['placers'].pop(placer.data_name)
    save_blueprint(dirpath=dirpath, blueprint=working_blueprint)


########################################################################################################################
def remove_placer_from_scene(placer, part, module):
    if not pm.objExists(placer.scene_name):
        print(f"Cannot delete placer {placer.scene_name} - placer not found in scene.")
        return False
    pm.delete(pm.PyNode(placer.scene_name))
    return True


########################################################################################################################
def create_part(part, module):
    if not part.scene_name:
        part.scene_name = f'{gen.side_tag(part.side)}{module.name}_{part.name}_PART'
    scene_part = part_utils.create_scene_part(part, parent=module_utils.get_scene_module(module))
    module.parts[part.data_name] = part_utils.data_from_part(part)
    update_module_in_blueprint(module)
    return scene_part


########################################################################################################################
def create_scene_module(module, parent=None):
    scene_module = module_utils.create_scene_module(module, parent)
    add_module_to_blueprint(module)
    return scene_module


########################################################################################################################
def update_module_in_blueprint(module):
    add_module_to_blueprint(module, check_for_clashes=False)


########################################################################################################################
def update_part_in_blueprint(part, module):
    add_part_to_module(part, module, check_for_clashes=False)


########################################################################################################################
def update_placer_in_blueprint(placer, part, module):
    add_placer_to_part(placer, part, module, check_for_clashes=False)


########################################################################################################################
def mirror_blueprint(blueprint, driver_side='L'):
    modules = blueprint.modules
    for module in modules.values():
        module_utils.mirror_module(module, driver_side=driver_side)

