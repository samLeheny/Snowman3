# Title: scene_interactor.py
# Author: Sam Leheny
# Contact: samleheny@live.com

# Description:


###########################
##### Import Commands #####
import os
import importlib

import pymel.core as pm

import Snowman3.utilities.general_utils as gen
importlib.reload(gen)

import Snowman3.riggers.managers.blueprint_manager as blueprint_manager_util
importlib.reload(blueprint_manager_util)
BlueprintManager = blueprint_manager_util.BlueprintManager

import Snowman3.riggers.modules.rig_module_utils as rig_module_utils
importlib.reload(rig_module_utils)
ModuleCreator = rig_module_utils.ModuleCreator
ModuleData = rig_module_utils.ModuleData

import Snowman3.riggers.utilities.module_utils as module_utils
importlib.reload(module_utils)
Module = module_utils.Module
###########################
###########################

###########################
######## Variables ########

###########################
###########################



class SceneInteractor:
    def __init__(
        self,
        blueprint_manager,
        armature_manager
    ):
        self.blueprint_manager = blueprint_manager
        self.armature_manager = armature_manager


    def mirror_armature(self, driver_side):
        for key, module in self.blueprint_manager.blueprint.modules.items():
            if module.side == driver_side:
                self.armature_manager.mirror_module(key)


    def add_module(self, name, side=None, prefab_key=None, parts_prefix=None):
        module_creator = ModuleCreator(ModuleData(
            name=name,
            prefab_key=prefab_key,
            side=side,
            part_offset=(0, 0, 0),
            parts_prefix=parts_prefix
        ))
        module = module_creator.create_module()
        self.blueprint_manager.add_module(module)
        self.blueprint_manager.save_blueprint_to_tempdisk()
        self.armature_manager.add_module(module)


    def remove_module(self, module_key):
        module = self.blueprint_manager.blueprint.modules[module_key]
        self.armature_manager.remove_module(module)
        self.blueprint_manager.remove_module(module)


    def add_part(self, name, prefab_key, parent_module_key, side=None):
        parent_module = self.blueprint_manager.blueprint.modules[parent_module_key]
        part = self.create_part(name, prefab_key, parent_module_key, side)
        self.blueprint_manager.add_part(part, parent_module)
        self.armature_manager.add_part(part, parent_module)
        return part


    def create_part(self, name, prefab_key, parent_module_key, side=None):
        parent_module = self.blueprint_manager.blueprint.modules[parent_module_key]
        parent_module_parts_prefix = parent_module.parts_prefix
        dir_string = f'Snowman3.riggers.parts.{prefab_key}'
        part_data = importlib.import_module(dir_string)
        importlib.reload(part_data)
        part = part_data.create_part(f'{parent_module_parts_prefix}{name}', side)
        return part


    def remove_part(self, part_key, parent_module_key):
        parent_module = self.blueprint_manager.blueprint.modules[parent_module_key]
        part = parent_module.parts[part_key]
        self.armature_manager.remove_part(part, parent_module)
        self.blueprint_manager.remove_part(part, parent_module)


    def save_work(self):
        self.blueprint_manager.save_work()


    def create_mirrored_part(self, existing_part_key, existing_module_key):
        existing_module = self.blueprint_manager.blueprint.modules[existing_module_key]
        existing_part = self.blueprint_manager.blueprint.modules[existing_module_key].parts[existing_part_key]
        opposite_module = self.blueprint_manager.get_opposite_module(existing_module)
        opposite_part_data = existing_part.data_from_part()
        opposite_part_data['side'] = gen.opposite_side(existing_part.side)

        dir_string = f"Snowman3.riggers.parts.{opposite_part_data['prefab_key']}"
        part_data = importlib.import_module(dir_string)
        importlib.reload(part_data)
        new_opposing_part = part_data.create_part(f"{opposite_module.parts_prefix}{opposite_part_data['name']}",
                                                  opposite_part_data['side'])
        return new_opposing_part


    def create_mirrored_module(self, existing_module_key):
        existing_module = self.blueprint_manager.blueprint.modules[existing_module_key]
        if self.blueprint_manager.get_opposite_module(existing_module):
            return False
        opposite_module_data = existing_module.data_from_module()
        opposite_module_data['side'] = gen.opposite_side(existing_module.side)
        new_opposing_module_creator = ModuleCreator(
            ModuleData(
                name=opposite_module_data['name'],
                prefab_key=opposite_module_data['prefab_key'],
                side=opposite_module_data['side'],
                part_offset=(0, 0, 0),
                parts_prefix=existing_module.parts_prefix
            )
        )
        new_opposing_module = new_opposing_module_creator.create_module()
        return new_opposing_module


    def add_mirrored_part(self, existing_part_key, existing_module_key):
        existing_module = self.blueprint_manager.blueprint.modules[existing_module_key]
        opposite_module = self.blueprint_manager.get_opposite_module(existing_module)
        new_opposite_part = self.create_mirrored_part(existing_part_key, existing_module_key)
        self.blueprint_manager.add_part(new_opposite_part, opposite_module)
        self.armature_manager.add_part(new_opposite_part, opposite_module)
        self.armature_manager.mirror_part(new_opposite_part.data_name, existing_module.data_name)
        self.blueprint_manager.update_blueprint_from_scene()
        self.blueprint_manager.save_blueprint_to_tempdisk()


    def add_mirrored_module(self, existing_module_key):
        existing_module = self.blueprint_manager.blueprint.modules[existing_module_key]
        new_opposing_module = self.create_mirrored_module(existing_module_key)
        self.blueprint_manager.add_module(new_opposing_module)
        self.armature_manager.add_module(new_opposing_module)
        self.armature_manager.mirror_module(existing_module.data_name)
        self.blueprint_manager.update_blueprint_from_scene()
        self.blueprint_manager.save_blueprint_to_tempdisk()
