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

import Snowman3.riggers.utilities.container_utils as container_utils
importlib.reload(container_utils)
Container = container_utils.Container
ContainerManager = container_utils.ContainerManager
ContainerCreator = container_utils.ContainerCreator
ContainerData = container_utils.ContainerData

import Snowman3.riggers.utilities.part_utils as part_utils
importlib.reload(part_utils)
PartManager = part_utils.PartManager
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
        containers = {}
    ):
        self.asset_name = asset_name
        self.dirpath = dirpath
        self.containers = containers


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
        dir_string = 'Snowman3.riggers.prefab_blueprints.{}.containers'
        prefab_containers = importlib.import_module(dir_string.format(self.prefab_key))
        importlib.reload(prefab_containers)
        self.blueprint.containers = prefab_containers.containers
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
        self.blueprint = self.blueprint_from_file(f'{self.tempdir}/{core_data_filename}.json')
        return self.blueprint


    def update_blueprint_from_scene(self):
        for key, container in self.blueprint.containers.items():
            self.blueprint.containers[key] = self.update_container_from_scene(container)
        return self.blueprint


    def update_container_from_scene(self, container):
        for key, part in container.parts.items():
            container.parts[key] = self.update_part_from_scene(part)
        return container


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


    def create_new_numbered_directory(self, asset_name, version_padding=default_version_padding):
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
        containers_data_holder = self.blueprint.containers
        self.blueprint.containers = {}
        for key, data in containers_data_holder.items():
            new_container = Container(**data)
            container_manager = ContainerManager(new_container)
            container_manager.create_parts_from_data(new_container.parts)
            self.blueprint.containers[key] = container_manager.container
        return self.blueprint


    def data_from_blueprint(self):
        data = {}
        for key, value in vars(self.blueprint).items():
            data[key] = value
        data['containers'] = {}
        for key, container in self.blueprint.containers.items():
            container_manager = ContainerManager(container)
            data['containers'][key] = container_manager.data_from_container()
        return data


    def data_from_container(self, container):
        container_manager = ContainerManager(container)
        return container_manager.data_from_container()


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


    def add_container(self, container):
        self.blueprint.containers[container.data_name] = container
        self.save_blueprint_to_tempdisk()


    def remove_container(self, container):
        self.blueprint = self.get_blueprint_from_working_dir()
        self.blueprint.containers.pop(container.data_name)
        self.save_blueprint_to_tempdisk()


    def add_part(self, part, container):
        self.blueprint = self.get_blueprint_from_working_dir()
        self.blueprint.containers[container.data_name].parts[part.data_name] = part
        self.save_blueprint_to_tempdisk()


    def remove_part(self, part, parent_container):
        self.blueprint = self.get_blueprint_from_working_dir()
        self.blueprint.containers[parent_container.data_name].parts.pop(part.data_name)
        self.save_blueprint_to_tempdisk()


    def get_opposite_container(self, container_key):
        container = self.get_container(container_key)
        container_manager = ContainerManager(container)
        opposite_container_key = container_manager.opposite_container_data_name()
        if opposite_container_key not in self.blueprint.containers:
            return None
        opposite_container = self.blueprint.containers[opposite_container_key]
        return opposite_container


    def get_container(self, container_key):
        return self.blueprint.containers[container_key]


    def get_part(self, part_key, container_key):
        container = self.get_container(container_key)
        return container.parts[part_key]
