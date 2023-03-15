# Title: armature.py
# Author: Sam Leheny
# Contact: samleheny@live.com

# Description:


###########################
##### Import Commands #####
import importlib
import pymel.core as pm

import Snowman3.riggers.utilities.module_utils as module_utils
importlib.reload(module_utils)
Module = module_utils.Module

import Snowman3.riggers.utilities.part_utils as part_utils
importlib.reload(part_utils)
Part = part_utils.Part
###########################
###########################

###########################
######## Variables ########

###########################
###########################



########################################################################################################################
class Armature:
    def __init__(
        self,
        modules = None,

    ):
        self.modules = modules if modules else {}



    def add_module(self, name, prefab_key=None, side=None):
        if prefab_key:
            module = self.add_prefab_module(name=name, prefab_key=prefab_key, side=side)
        else:
            module = self.add_empty_module(name=name, side=side)
        self.modules[module.data_name] = module
        module.create_scene_module(parent=None)
        return module


    def add_empty_module(self, name, side=None):
        module = Module(name=name, side=side)
        return module


    def add_prefab_module(self, name, prefab_key, side=None):
        module = Module(name=name, prefab_key=prefab_key, side=side)
        return module


    def remove_module(self, module):
        pm.delete(module.get_scene_module())
        self.modules.pop(module.data_name)


    def add_part(self, name, module, prefab_key=None, side=None):
        part = module.add_part(name, prefab_key, side)
        return part


    def remove_part(self, part, module):
        module.remove_part(part)


    def add_placer(self, name, module, part, side=None):
        placer = module.add_placer_to_part(name=name, side=side, part=part)
        return placer


    def remove_placer(self, placer, part, module):
        module.remove_placer(placer, part)