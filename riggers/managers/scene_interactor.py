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
        armature_builder
    ):
        self.blueprint_manager = blueprint_manager
        self.armature_builder = armature_builder


    def mirror_module(self, module_key):
        for part_key in self.blueprint_manager.blueprint.modules[module_key].parts.keys():
            self.armature_builder.mirror_part(part_key, module_key)


    def mirror_armature(self, driver_side):
        for key, module in self.blueprint_manager.blueprint.modules.items():
            if module.side == driver_side:
                self.mirror_module(key)


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
        self.armature_builder.add_module(module)


    def remove_module(self, module_key):
        module = self.blueprint_manager.blueprint.modules[module_key]
        self.armature_builder.remove_module(module)
        self.blueprint_manager.remove_module(module)
        self.blueprint_manager.save_blueprint_to_tempdisk()
