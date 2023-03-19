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
    ):
        self.blueprint_manager = blueprint_manager
        self.blueprint = blueprint_manager.get_blueprint_from_working_dir()


    def mirror_placer_position(self, placer_key, part_key, module_key):
        part_data = self.get_blueprint_part(part_key, module_key)
        placer = part_data['placers'][placer_key]
        scene_placer = pm.PyNode(placer['scene_name'])
        opposite_scene_placer = gen.get_opposite_side_obj(scene_placer)
        if not opposite_scene_placer:
            return False
        scene_placer_local_position = scene_placer.translate.get()
        opposite_scene_placer.translate.set(tuple(scene_placer_local_position))


    def mirror_part(self, part_key, module_key):
        self.mirror_part_handle(part_key, module_key)
        self.mirror_part_placer_positions(part_key, module_key)


    def mirror_part_handle(self, part_key, module_key):
        part_data = self.get_blueprint_part(part_key, module_key)
        scene_part_handle = pm.PyNode(part_data['scene_name'])
        opposite_scene_part_handle = gen.get_opposite_side_obj(scene_part_handle)
        scene_part_handle_position = scene_part_handle.translate.get()
        opposite_scene_part_handle.translate.set(scene_part_handle_position)


    def mirror_part_placer_positions(self, part_key, module_key):
        part_data = self.get_blueprint_part(part_key, module_key)
        part_placers = part_data['placers']
        [self.mirror_placer_position(key, part_key, module_key) for key in part_placers.keys()]


    def get_blueprint_part(self, part_key, module_key):
        module_data = self.get_blueprint_module(module_key)
        return module_data['parts'][part_key]


    def get_blueprint_module(self, module_key):
        blueprint_modules = self.get_all_modules_data()
        return blueprint_modules[module_key]


    def mirror_module_placer_positions(self, module_key):
        module_data = self.get_blueprint_module(module_key)
        for part_key in module_data['parts'].keys():
            self.mirror_part(part_key, module_key)


    def get_all_modules_data(self):
        modules_data = self.blueprint.modules
        return modules_data


    def mirror_armature(self, driver_side):
        modules_data = self.get_all_modules_data()
        for key, module_data in modules_data.items():
            if module_data['side'] == driver_side:
                self.mirror_module_placer_positions(key)


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
        module.create_scene_module()
