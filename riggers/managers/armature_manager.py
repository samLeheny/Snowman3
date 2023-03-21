# Title: armature_manager.py
# Author: Sam Leheny
# Contact: samleheny@live.com

# Description:


###########################
##### Import Commands #####
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
        blueprint_manager = None
    ):
        self.blueprint_manager = blueprint_manager


    def build_armature_from_blueprint(self):
        print("Building armature in scene from blueprint...")
        for module in self.blueprint_manager.blueprint.modules.values():
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


    def add_part(self, part, parent_module):
        scene_module = pm.PyNode(self.blueprint_manager.blueprint.modules[parent_module.data_name].scene_name)
        scene_part = part.create_scene_part(scene_module)
        self.zero_out_part_rotation(part)
        return scene_part


    def zero_out_part_rotation(self, part):
        pm.PyNode(part.scene_name).rotate.set(0, 0, 0)


    def remove_part(self, part, parent_module):
        parent_scene_module = pm.PyNode(parent_module.scene_name)
        possible_scene_parts = pm.ls(part.scene_name)
        for scene_part in possible_scene_parts:
            if scene_part.getParent() == parent_scene_module:
                pm.delete(scene_part)
                break


    def mirror_module(self, module_key):
        for part_key in self.blueprint_manager.blueprint.modules[module_key].parts.keys():
            self.mirror_part(part_key, module_key)


    def mirror_part(self, part_key, module_key):
        self.mirror_part_handle(part_key, module_key)
        self.mirror_part_placer_positions(part_key, module_key)


    def mirror_part_handle(self, part_key, module_key):
        scene_part_handle = pm.PyNode(self.blueprint_manager.blueprint.modules[module_key].parts[part_key].scene_name)
        opposite_scene_part_handle = gen.get_opposite_side_obj(scene_part_handle)
        if not opposite_scene_part_handle:
            return False
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
