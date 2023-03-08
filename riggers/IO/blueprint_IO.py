# Title: blueprint_IO.py
# Author: Sam Leheny
# Contact: samleheny@live.com

# Description:


###########################
##### Import Commands #####
import json
import importlib

import Snowman3.riggers.utilities.classes.class_Blueprint as class_Blueprint
importlib.reload(class_Blueprint)
Blueprint = class_Blueprint.Blueprint

import Snowman3.riggers.utilities.module_utils as module_utils
importlib.reload(module_utils)
Module = module_utils.Module
###########################
###########################

###########################
######## Variables ########
core_data_filename = 'core_data'
###########################
###########################



########################################################################################################################
class BlueprintIO:
    def __init__(
        self,
        blueprint = None,
        data = None,
        dirpath = None,
    ):
        self.blueprint = blueprint
        self.data = data
        self.dirpath = dirpath


    ####################################################################################################################
    def save(self, dirpath):
        self.data_from_blueprint()
        filepath = f'{dirpath}/{core_data_filename}.json'
        print(f'\nExporting blueprint data to dir: {filepath}...')
        with open(filepath, 'w') as fh:
            json.dump(self.data, fh, indent=5)


    ####################################################################################################################
    def data_from_blueprint(self):
        self.data = {
            'asset_name': self.blueprint.asset_name,
            'dirpath': self.blueprint.dirpath,
            'modules': self.blueprint.modules,
            'loose_parts': self.blueprint.loose_parts
        }


    ####################################################################################################################
    def load(self, dirpath):
        self.data_from_file(dirpath)
        self.blueprint_from_data(self.data)
        return self.blueprint


    ####################################################################################################################
    def data_from_file(self, dirpath):
        with open(f'{dirpath}/{core_data_filename}.json', 'r') as fh:
            self.data = json.load(fh)


    ####################################################################################################################
    def blueprint_from_data(self, data):
        self.blueprint = Blueprint(
            asset_name = data['asset_name'],
            dirpath = data['dirpath'],
            modules = data['modules'],
            loose_parts = data['loose_parts']
        )


    ####################################################################################################################
    def blueprint_from_file(self, dirpath):
        self.data_from_file(dirpath)
        self.blueprint_from_data(self.data)
        return self.blueprint


    ####################################################################################################################
    def update_blueprint_from_scene(self, blueprint):
        # ...Update modules
        self.data_from_blueprint()
        modules_data = self.data['modules']
        modules = [module_utils.module_from_data(d) for d in modules_data.values()]
        for module in modules:
            module_utils.update_module_from_scene(module)
        # ...Re-export blueprint data
        self.blueprint_from_data(self.data)
        self.save(self.dirpath)


    ####################################################################################################################
    def mirror_module(self, blueprint, module_key, driver_side='L', driven_side='R'):
        module = blueprint.modules[module_key]
        module_utils.mirror_module(module, driver_side=driver_side, driven_side=driven_side)
