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

import Snowman3.riggers.utilities.part_utils as part_utils
importlib.reload(part_utils)
PartManager = part_utils.PartManager
ScenePartManager = part_utils.ScenePartManager
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
        for part in self.blueprint_manager.blueprint.parts.values():
            self.add_part(part)


    def add_part(self, part):
        scene_part_manager = ScenePartManager(part)
        return scene_part_manager.create_scene_part()


    def remove_part(self, part):
        pm.delete(pm.PyNode(part.scene_name))


    def mirror_part(self, part_key):
        self.mirror_part_handle(part_key)
        self.mirror_part_placer_positions(part_key)


    def mirror_part_handle(self, part_key):
        scene_part_handle = pm.PyNode(
            self.blueprint_manager.blueprint.parts[part_key].scene_name)
        opposite_scene_part_handle = gen.get_opposite_side_obj(scene_part_handle)
        if not opposite_scene_part_handle:
            return False
        scene_part_handle_position = scene_part_handle.translate.get()
        scene_part_handle_position[0] = -scene_part_handle_position[0]
        opposite_scene_part_handle.translate.set(scene_part_handle_position)


    def mirror_part_placer_positions(self, part_key):
        part_placers = self.blueprint_manager.blueprint.parts[part_key].placers
        [self.mirror_placer_position(key, part_key) for key in part_placers.keys()]


    def mirror_placer_position(self, placer_key, part_key):
        placer = self.blueprint_manager.blueprint.parts[part_key].placers[placer_key]
        scene_placer = pm.PyNode(placer.scene_name)
        opposite_scene_placer = gen.get_opposite_side_obj(scene_placer)
        if not opposite_scene_placer:
            return False
        scene_placer_local_position = list(scene_placer.translate.get())
        scene_placer_local_position[0] = -scene_placer_local_position[0]
        opposite_scene_placer.translate.set(tuple(scene_placer_local_position))
