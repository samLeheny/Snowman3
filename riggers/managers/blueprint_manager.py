# Title: blueprint_manager.py
# Author: Sam Leheny
# Contact: samleheny@live.com

# Description:


###########################
##### Import Commands #####
import os
import importlib
import pymel.core as pm
import json

import Snowman3.utilities.general_utils as gen
importlib.reload(gen)

import Snowman3.riggers.utilities.blueprint_utils as blueprint_utils
importlib.reload(blueprint_utils)
Blueprint = blueprint_utils.Blueprint

import Snowman3.riggers.utilities.module_utils as module_utils
importlib.reload(module_utils)
Module = module_utils.Module

import Snowman3.riggers.utilities.placer_utils as placer_utils
importlib.reload(placer_utils)
Placer = placer_utils.Placer
###########################
###########################

###########################
######## Variables ########
temp_files_dir = 'working'
versions_dir = 'versions'
core_data_filename = 'core_data'
version_padding = 4
###########################
###########################



class BlueprintManager:
    def __init__(
        self,
        asset_name: str = None,
        prefab_key: str = None,
        dirpath: str = None,
        blueprint = None
    ):
        self.asset_name = asset_name
        self.prefab_key = prefab_key
        self.dirpath = f'{dirpath}'
        self.tempdir = f'{self.dirpath}/{temp_files_dir}'
        self.versions_dir = f'{self.dirpath}/{versions_dir}'
        self.blueprint = blueprint



    def create_blueprint_from_prefab(self):
        print(f"Creating blueprint from prefab: '{self.prefab_key}'...")
        self.blueprint = self.create_new_blueprint()
        self.populate_prefab_blueprint()
        return self.blueprint


    def populate_prefab_blueprint(self):
        dir_string = 'Snowman3.riggers.prefab_blueprints.{}.modules'
        prefab_modules = importlib.import_module(dir_string.format(self.prefab_key))
        importlib.reload(prefab_modules)
        self.blueprint.modules = prefab_modules.modules
        self.save_blueprint_to_tempdisk()


    def create_new_blueprint(self):
        print(f"Creating new blueprint for asset '{self.asset_name}'...")
        self.blueprint = Blueprint(asset_name=self.asset_name, dirpath=self.tempdir)
        self.create_working_dir()
        self.create_versions_dir()
        self.save_blueprint_to_tempdisk()
        return self.blueprint


    def save_blueprint_to_tempdisk(self):
        self.save_blueprint(self.tempdir)


    def create_working_dir(self):
        if not os.path.exists(self.tempdir):
            print("Asset 'working' directory created.")
            os.mkdir(self.tempdir)


    def create_versions_dir(self):
        if not os.path.exists(self.versions_dir):
            print("Asset 'versions' directory created.")
            os.mkdir(self.versions_dir)


    def save_work(self):
        print('Saving work...')
        self.blueprint = self.get_blueprint_from_working_dir()
        self.update_blueprint_from_scene()
        self.save_blueprint_to_disk()
        self.save_blueprint_to_tempdisk()


    def get_blueprint_from_working_dir(self):
        print("Fetching current working blueprint...")
        self.blueprint = self.blueprint_from_file(f'{self.tempdir}/{core_data_filename}.json')
        return self.blueprint


    def update_blueprint_from_scene(self):
        print("Updating working blueprint with scene data...")
        for key, module in self.blueprint.modules.items():
            self.blueprint.modules[key] = self.update_module_from_scene(module)
        return self.blueprint


    def update_module_from_scene(self, module):
        for key, part in module.parts.items():
            module.parts[key] = self.update_part_from_scene(part)
        return module


    def update_part_from_scene(self, part):
        scene_handle = pm.PyNode(part.scene_name)
        part.position = tuple(scene_handle.translate.get())
        for key, placer in part.placers.items():
            part.placers[key] = self.update_placer_from_scene(placer)
        return part


    def update_placer_from_scene(self, placer):
        scene_placer = pm.PyNode(placer.scene_name)
        placer.position = tuple(scene_placer.translate.get())
        return placer


    def save_blueprint_to_disk(self):
        print("Saving work to disk...")
        asset_name = self.blueprint.asset_name
        new_save_dir = self.create_new_numbered_directory(asset_name)
        self.save_blueprint(dirpath=new_save_dir)


    def create_new_numbered_directory(self, asset_name, version_padding=version_padding):
        version_dirs = [p[0] for p in os.walk(self.versions_dir)]
        version_subdirs = [version_dirs[i] for i in range(1, len(version_dirs))]
        subdir_names = [os.path.basename(os.path.normpath(p)) for p in version_subdirs]
        if not version_subdirs:
            bulked_num = str(1).rjust(version_padding, '0')
            new_dir_string = f'{asset_name}-v{bulked_num}'
        else:
            nums = [name.split('-v')[1] for name in subdir_names]
            next_num = int(max(nums)) + 1
            bulked_num = str(next_num).rjust(version_padding, '0')
            new_dir_string = f'{asset_name}-v{bulked_num}'
        new_dir = f'{self.versions_dir}/{new_dir_string}'
        os.mkdir(new_dir)
        return new_dir


    def blueprint_from_file(self, filepath):
        blueprint_data = self.data_from_file(filepath)
        self.blueprint = self.blueprint_from_data(blueprint_data)
        return self.blueprint


    def data_from_file(self, filepath):
        with open(filepath, 'r') as fh:
            data = json.load(fh)
        return data


    def blueprint_from_data(self, data):
        self.blueprint = Blueprint(**data)
        modules_data_holder = self.blueprint.modules
        self.blueprint.modules = {}
        for key, data in modules_data_holder.items():
            new_module = Module(**data)
            self.blueprint.modules[key] = new_module
        return self.blueprint


    def data_from_blueprint(self):
        data = {}
        for param, value in vars(self.blueprint).items():
            data[param] = value

        data['modules'] = {}
        for key, module in self.blueprint.modules.items():
            data['modules'][key] = module.data_from_module()

        return data


    def save_blueprint(self, dirpath=None):
        if not dirpath:
            dirpath = self.dirpath
        blueprint_data = self.data_from_blueprint()
        filepath = f'{dirpath}/{core_data_filename}.json'
        with open(filepath, 'w') as fh:
            json.dump(blueprint_data, fh, indent=5)


    def add_module(self, module):
        if module.prefab_key:
            self.add_prefab_module(module)
        else:
            self.add_empty_module(module)


    def add_empty_module(self, module):
        self.blueprint.modules[module.data_name] = module


    def add_prefab_module(self, module):
        self.blueprint.modules[module.data_name] = module


    def remove_module(self, module):
        self.blueprint = self.get_blueprint_from_working_dir()
        self.blueprint.modules.pop(module.data_name)


    def add_part(self, part, module, filepath):
        working_blueprint = self.blueprint_from_file(filepath)
        self.blueprint.modules[module.data_name].parts[part.data_name] = part.data_from_part()


    def remove_part(self, part, module):
        working_blueprint = self.blueprint_from_file()
        self.blueprint.modules[module.data_name]['parts'].pop(part.data_name)


    def add_placer(self, placer, part, module):
        working_blueprint = self.blueprint_from_file()
        self.blueprint.modules[module.data_name].parts[part.data_name].placers[placer.data_name] =\
            placer.data_from_placer()


    def remove_placer(self, placer, part, module):
        working_blueprint = self.blueprint_from_file()
        self.blueprint.modules[module.data_name]['parts'][part.data_name]['placers'].pop(part.data_name)
