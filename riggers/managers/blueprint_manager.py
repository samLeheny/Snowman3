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

import Snowman3.riggers.utilities.part_utils as part_utils
importlib.reload(part_utils)
PartManager = part_utils.PartManager
Part = part_utils.Part
###########################
###########################

###########################
######## Variables ########
temp_files_dir = 'working'
versions_dir = 'versions'
core_data_filename = 'core_data'
default_version_padding = 4
###########################
###########################


########################################################################################################################
class Blueprint:
    def __init__(
        self,
        asset_name,
        dirpath = None,
        parts = {}
    ):
        self.asset_name = asset_name
        self.dirpath = dirpath
        self.parts = parts


########################################################################################################################
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
        dir_string = 'Snowman3.riggers.prefab_blueprints.{}.parts'
        prefab_parts = importlib.import_module(dir_string.format(self.prefab_key))
        importlib.reload(prefab_parts)
        self.blueprint.parts = prefab_parts.parts
        self.save_blueprint_to_tempdisk()


    def create_new_blueprint(self):
        print(f"Creating new blueprint for asset '{self.asset_name}'...")
        self.blueprint = Blueprint(asset_name=self.asset_name, dirpath=self.tempdir)
        self.create_working_dir()
        self.create_versions_dir()
        self.save_blueprint_to_tempdisk()
        return self.blueprint


    def load_blueprint_from_numbered_version(self, number):
        version_dir = self.get_numbered_version_dir(number)
        version_blueprint_filepath = f'{version_dir}/{core_data_filename}.json'
        self.blueprint_from_file(version_blueprint_filepath)


    def get_numbered_version_dir(self, number, version_padding=default_version_padding):
        padded_num_string = str(number).rjust(version_padding, '0')
        subdir_names = self.get_all_numbered_subdir_names()
        version_dir_string = f'{self.asset_name}-v{padded_num_string}'
        if version_dir_string not in subdir_names:
            return False
        dir = f'{self.versions_dir}/{version_dir_string}'
        return dir


    def load_blueprint_from_latest_version(self):
        latest_version_dir = self.get_latest_numbered_directory()
        latest_version_blueprint_filepath = f'{latest_version_dir}/{core_data_filename}.json'
        self.blueprint_from_file(latest_version_blueprint_filepath)


    def get_latest_numbered_directory(self):
        subdir_names = self.get_all_numbered_subdir_names()
        nums = [name.split('-v')[1] for name in subdir_names]
        latest_dir_string = f'{self.asset_name}-v{nums[-1]}'
        latest_dir_filepath = f'{self.versions_dir}/{latest_dir_string}'
        return latest_dir_filepath


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
        self.blueprint = self.blueprint_from_file(f'{self.tempdir}/{core_data_filename}.json')
        return self.blueprint


    def update_blueprint_from_scene(self):
        for key, part in self.blueprint.parts.items():
            self.blueprint.parts[key] = self.update_part_from_scene(part)
        return self.blueprint


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


    def get_all_numbered_subdirs(self):
        version_dirs = [p[0] for p in os.walk(self.versions_dir)]
        version_subdirs = [version_dirs[i] for i in range(1, len(version_dirs))]
        return version_subdirs


    def get_all_numbered_subdir_names(self):
        version_subdirs = self.get_all_numbered_subdirs()
        subdir_names = [os.path.basename(os.path.normpath(p)) for p in version_subdirs]
        return subdir_names


    def create_new_numbered_directory(self, asset_name, version_padding=default_version_padding):
        version_subdirs = self.get_all_numbered_subdirs()
        subdir_names = self.get_all_numbered_subdir_names()
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
        parts_data_holder = self.blueprint.parts
        self.blueprint.parts = {}
        for key, data in parts_data_holder.items():
            new_part = Part(**data)
            part_manager = PartManager(new_part)
            part_manager.create_placers_from_data(new_part.placers)
            self.blueprint.parts[key] = part_manager.part
        return self.blueprint


    def data_from_blueprint(self):
        data = {}
        for key, value in vars(self.blueprint).items():
            data[key] = value
        data['parts'] = {}
        for key, part in self.blueprint.parts.items():
            part_manager = PartManager(part)
            data['parts'][key] = part_manager.data_from_part()
        return data


    def data_from_part(self, part):
        part_manager = PartManager(part)
        return part_manager.data_from_part()


    def save_blueprint(self, dirpath=None):
        if not dirpath:
            dirpath = self.dirpath
        blueprint_data = self.data_from_blueprint()
        filepath = f'{dirpath}/{core_data_filename}.json'
        with open(filepath, 'w') as fh:
            json.dump(blueprint_data, fh, indent=5)


    def add_part(self, part):
        self.blueprint = self.get_blueprint_from_working_dir()
        self.blueprint.parts[part.data_name] = part
        self.save_blueprint_to_tempdisk()


    def remove_part(self, part):
        self.blueprint = self.get_blueprint_from_working_dir()
        self.blueprint.parts.pop(part.data_name)
        self.save_blueprint_to_tempdisk()


    def get_part(self, part_key):
        return self.blueprint.parts[part_key]
