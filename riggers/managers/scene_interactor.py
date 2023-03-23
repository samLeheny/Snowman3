# Title: scene_interactor.py
# Author: Sam Leheny
# Contact: samleheny@live.com

# Description:


###########################
##### Import Commands #####
import importlib

import Snowman3.utilities.general_utils as gen
importlib.reload(gen)

import Snowman3.riggers.managers.blueprint_manager as blueprint_manager_util
importlib.reload(blueprint_manager_util)
BlueprintManager = blueprint_manager_util.BlueprintManager

import Snowman3.riggers.managers.armature_manager as armature_manager_util
importlib.reload(armature_manager_util)
ArmatureManager = armature_manager_util.ArmatureManager

import Snowman3.riggers.utilities.container_utils as container_utils
importlib.reload(container_utils)
ContainerCreator = container_utils.ContainerCreator
ContainerData = container_utils.ContainerData

import Snowman3.riggers.utilities.part_utils as part_utils
importlib.reload(part_utils)
PartCreator = part_utils.PartCreator
###########################
###########################

###########################
######## Variables ########

###########################
###########################



class SceneInteractor:
    def __init__(
        self,
        blueprint_manager=None,
        armature_manager=None
    ):
        self.blueprint_manager = blueprint_manager
        self.armature_manager = armature_manager


    def create_managers(self, asset_name, dirpath, prefab_key=None):
        self.blueprint_manager = BlueprintManager(asset_name=asset_name, dirpath=dirpath, prefab_key=prefab_key)
        self.armature_manager = ArmatureManager(blueprint_manager=self.blueprint_manager)


    def build_armature_from_prefab(self):
        self.blueprint_manager.create_blueprint_from_prefab()
        self.armature_manager.build_armature_from_blueprint()


    def update_blueprint_from_scene(self):
        self.blueprint_manager.update_blueprint_from_scene()


    def build_armature_from_latest_version(self):
        self.blueprint_manager.load_blueprint_from_latest_version()
        self.armature_manager.build_armature_from_blueprint()


    def build_armature_from_version_number(self, number):
        self.blueprint_manager.load_blueprint_from_numbered_version(number)
        self.armature_manager.build_armature_from_blueprint()


    def mirror_armature(self, driver_side):
        for key, container in self.blueprint_manager.blueprint.containers.items():
            if container.side == driver_side:
                self.armature_manager.mirror_container(key)


    def create_container(self, name, side=None, prefab_key=None, parts_prefix=None):
        container_creator = ContainerCreator(ContainerData(
            name=name,
            prefab_key=prefab_key,
            side=side,
            part_offset=(0, 0, 0),
            parts_prefix=parts_prefix
        ))
        return container_creator.create_container()


    def add_container(self, name, side=None, prefab_key=None, parts_prefix=None):
        container = self.create_container(name=name, side=side, prefab_key=prefab_key, parts_prefix=parts_prefix)
        self.blueprint_manager.add_container(container)
        self.armature_manager.add_container(container)


    def remove_container(self, container_key):
        container = self.blueprint_manager.get_container(container_key)
        self.armature_manager.remove_container(container)
        self.blueprint_manager.remove_container(container)


    def create_part(self, name, prefab_key, parent_container_key, side=None):
        parent_container = self.blueprint_manager.get_container(parent_container_key)
        parent_container_parts_prefix = parent_container.parts_prefix
        part_creator = PartCreator(name=f'{parent_container_parts_prefix}{name}', prefab_key=prefab_key, side=side)
        return part_creator.create_part()


    def add_part(self, name, prefab_key, parent_container_key, side=None):
        parent_container = self.blueprint_manager.get_container(parent_container_key)
        part = self.create_part(name, prefab_key, parent_container_key, side)
        self.blueprint_manager.add_part(part, parent_container)
        self.armature_manager.add_part(part, parent_container)


    def remove_part(self, part_key, parent_container_key):
        parent_container = self.blueprint_manager.get_container(parent_container_key)
        part = parent_container.parts[part_key]
        self.armature_manager.remove_part(part, parent_container)
        self.blueprint_manager.remove_part(part, parent_container)


    def save_work(self):
        self.blueprint_manager.save_work()


    def create_mirrored_part(self, existing_part_key, existing_container_key):
        existing_part = self.blueprint_manager.get_part(existing_part_key, existing_container_key)
        opposite_container = self.blueprint_manager.get_opposite_container(existing_container_key)
        opposite_part_data = self.blueprint_manager.data_from_part(existing_part)
        opposite_part_data['side'] = gen.opposite_side(existing_part.side)

        new_opposing_part = self.create_part(
            name=f"{opposite_container.parts_prefix}{opposite_part_data['name']}", side=opposite_part_data['side'],
            prefab_key=opposite_part_data['prefab_key'], parent_container_key=opposite_container.data_name)
        return new_opposing_part


    def create_mirrored_container(self, existing_container_key):
        existing_container = self.blueprint_manager.get_container(existing_container_key)
        if self.blueprint_manager.get_opposite_container(existing_container_key):
            return False
        opposite_container_data = self.blueprint_manager.data_from_container(existing_container)
        opposite_container_data['side'] = gen.opposite_side(existing_container.side)
        new_opposing_container = self.create_container(
            opposite_container_data['name'], opposite_container_data['side'], opposite_container_data['prefab_key'],
            existing_container.parts_prefix)
        return new_opposing_container


    def add_mirrored_part(self, existing_part_key, existing_container_key):
        opposite_container = self.blueprint_manager.get_opposite_container(existing_container_key)
        new_opposite_part = self.create_mirrored_part(existing_part_key, existing_container_key)
        self.blueprint_manager.add_part(new_opposite_part, opposite_container)
        self.armature_manager.add_part(new_opposite_part, opposite_container)
        self.armature_manager.mirror_part(new_opposite_part.data_name, existing_container_key)
        self.blueprint_manager.update_blueprint_from_scene()
        self.blueprint_manager.save_blueprint_to_tempdisk()


    def add_mirrored_container(self, existing_container_key):
        existing_container = self.blueprint_manager.get_container(existing_container_key)
        new_opposing_container = self.create_mirrored_container(existing_container_key)
        self.blueprint_manager.add_container(new_opposing_container)
        self.armature_manager.add_container(new_opposing_container)
        self.armature_manager.mirror_container(existing_container.data_name)
        self.blueprint_manager.update_blueprint_from_scene()
        self.blueprint_manager.save_blueprint_to_tempdisk()
