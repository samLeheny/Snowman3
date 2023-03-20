# Title: armature_manager.py
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

import Snowman3.riggers.managers.blueprint_manager as blueprint_manager
importlib.reload(blueprint_manager)
BlueprintManager = blueprint_manager.BlueprintManager

import Snowman3.riggers.utilities.armature as armature
importlib.reload(armature)
Armature = armature.Armature
###########################
###########################

###########################
######## Variables ########

###########################
###########################



########################################################################################################################
class ArmatureManager:
    def __init__(
        self,
        armature = None,
        blueprint_manager = None

    ):
        self.armature = armature
        self.blueprint_manager = blueprint_manager


    def build_armature_from_blueprint(self):
        print("Building armature in scene from blueprint...")
        self.armature = Armature(modules=self.blueprint_manager.blueprint.modules)
        self.populate_armature()


    def populate_armature(self):
        for module in self.armature.modules.values():
            self.add_module(module)


    def add_module(self, module):
        scene_module = pm.shadingNode('transform', name=module.scene_name, au=1)
        module.add_module_metadata(scene_module)
        module.populate_scene_module(parts_parent=scene_module)
        if module.side == 'R':
            gen.flip(scene_module)
        return scene_module


    def remove_module(self, module):
        pm.delete(pm.PyNode(module.scene_name))


    def mirror_part(self, part_key, module_key):
        self.mirror_part_handle(part_key, module_key)
        self.mirror_part_placer_positions(part_key, module_key)


    def mirror_part_handle(self, part_key, module_key):
        scene_part_handle = pm.PyNode(self.blueprint_manager.blueprint.modules[module_key].parts[part_key].scene_name)
        opposite_scene_part_handle = gen.get_opposite_side_obj(scene_part_handle)
        scene_part_handle_position = scene_part_handle.translate.get()
        opposite_scene_part_handle.translate.set(scene_part_handle_position)


    def mirror_part_placer_positions(self, part_key, module_key):
        part_placers = self.blueprint_manager.blueprint.modules[module_key].parts[part_key].placers
        [self.mirror_placer_position(key, part_key, module_key) for key in part_placers.keys()]


    def mirror_placer_position(self, placer_key, part_key, module_key):
        placer = self.blueprint_manager.blueprint.modules[module_key].parts[part_key].placers[placer_key]
        scene_placer = pm.PyNode(placer.scene_name)
        opposite_scene_placer = gen.get_opposite_side_obj(scene_placer)
        if not opposite_scene_placer:
            return False
        scene_placer_local_position = scene_placer.translate.get()
        opposite_scene_placer.translate.set(tuple(scene_placer_local_position))
