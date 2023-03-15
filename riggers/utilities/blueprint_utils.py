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
###########################
###########################



########################################################################################################################
class Blueprint:
    def __init__(
        self,
        asset_name,
        dirpath = None,
        modules = None,

    ):
        self.asset_name = asset_name
        self.dirpath = dirpath
        self.modules = modules if modules else {}


    def add_module(self, module):
        if module.prefab_key:
            self.add_prefab_module(module)
        else:
            self.add_empty_module(module)


    def add_empty_module(self, module):
        self.modules[module.data_name] = module.data_from_module()


    def add_prefab_module(self, module):
        module.populate_prefab()
        self.modules[module.data_name] = module.data_from_module()


    def remove_module(self, module):
        working_blueprint = self.blueprint_from_file()
        working_blueprint.modules.pop(module.data_name)


    def add_part(self, part, module):
        working_blueprint = self.blueprint_from_file()
        working_blueprint.modules[module.data_name].parts[part.data_name] = part.data_from_part()


    def remove_part(self, part, module):
        working_blueprint = self.blueprint_from_file()
        working_blueprint.modules[module.data_name]['parts'].pop(part.data_name)


    def add_placer(self, placer, part, module):
        working_blueprint = self.blueprint_from_file()
        working_blueprint.modules[module.data_name].parts[part.data_name].placers[placer.data_name] =\
            placer.data_from_placer()


    def remove_placer(self, placer, part, module):
        working_blueprint = self.blueprint_from_file()
        working_blueprint.modules[module.data_name]['parts'][part.data_name]['placers'].pop(part.data_name)


    def blueprint_from_file(self):
        blueprint_data = self.data_from_file()
        for key, value in blueprint_data.items():
            setattr(self, key, value)



    def data_from_file(self):
        with open(f'{self.dirpath}/{core_data_filename}.json', 'r') as fh:
            data = json.load(fh)
        return data


    def data_from_blueprint(self):
        data = {}
        for param, value in vars(self).items():
            data[param] = value
        return data


    def blueprint_from_data(self, data):
        blueprint = Blueprint(**data)
        return blueprint


    def save_blueprint(self, dirpath=None, filename=core_data_filename):
        if not dirpath:
            dirpath = self.dirpath
        blueprint_data = self.data_from_blueprint()
        filepath = f'{dirpath}/{filename}.json'
        with open(filepath, 'w') as fh:
            json.dump(blueprint_data, fh, indent=5)






########################################################################################################################
'''def update_blueprint_from_scene(blueprint):
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
def update_module_in_blueprint(module):
    add_module_to_blueprint(module, check_for_clashes=False)


########################################################################################################################
def update_part_in_blueprint(part, module):
    add_part_to_module(part, module, check_for_clashes=False)


########################################################################################################################
def update_placer_in_blueprint(placer, part, module):
    add_placer_to_part(placer, part, module, check_for_clashes=False)


########################################################################################################################
def populate_prefab_module(module):
    dir_string = 'Snowman3.riggers.modules.{}.data.parts'
    prefab_parts = importlib.import_module(dir_string.format(module.prefab_key))
    importlib.reload(prefab_parts)
    for part in prefab_parts.parts.values():
        create_part(part, module)'''
