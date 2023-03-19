# Title: armatureBuilder.py
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

import Snowman3.riggers.utilities.blueprint_utils as blueprint_utils
importlib.reload(blueprint_utils)
Blueprint = blueprint_utils.Blueprint

import Snowman3.riggers.managers.blueprint_manager as blueprint_manager
importlib.reload(blueprint_manager)
BlueprintManager = blueprint_manager.BlueprintManager

import Snowman3.riggers.utilities.armature as armature
importlib.reload(armature)
Armature = armature.Armature

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
test_path = r'C:\Users\61451\Desktop\sam_build'
###########################
###########################



########################################################################################################################
class ArmatureBuilder:
    def __init__(
        self,
        armature = None,
        blueprint_manager = None

    ):
        self.armature = armature
        self.blueprint_manager = blueprint_manager


    def build_armature_from_blueprint(self):
        blueprint_data = self.blueprint_manager.data_from_blueprint()
        modules_data = blueprint_data['modules']
        modules = {}
        for data in modules_data.values():
            modules[data['data_name']] = Module(**data)
        self.armature = Armature(modules=modules)
        self.populate_armature()


    def populate_armature(self):
        for module in self.armature.modules.values():
            module.create_scene_module()




    def add_module(self, name, prefab_key=None, side=None):
        module = self.armature.add_module(name=name, prefab_key=prefab_key, side=side)
        self.blueprint_manager.add_module(module)


    '''def remove_module(self, module):
        self.armature.remove_module(module)
        self.blueprint.remove_module(module)'''


    def add_part(self, name, parent_module, prefab_key=None, side=None):
        part = self.armature.add_part(name=name, prefab_key=prefab_key, side=side, module=parent_module)
        self.blueprint_manager.add_part(part, parent_module)


    def remove_part(self, part, module):
        self.armature.remove_part(part, module)
        self.blueprint_manager.remove_part(part, module)


    def add_placer(self, name, parent_module, parent_part, side=None):
        placer = self.armature.add_placer_to_part(name=name, side=side, module=parent_module, part=parent_part)
        self.blueprint_manager.add_placer_to_part(placer, parent_part)


    def remove_placer(self, placer, part, module):
        self.armature.remove_placer(placer, part, module)
        self.blueprint_manager.remove_placer(placer, part, module)
