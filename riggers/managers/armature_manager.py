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

import Snowman3.riggers.utilities.container_utils as container_utils
importlib.reload(container_utils)
SceneContainerManager = container_utils.SceneContainerManager

import Snowman3.riggers.utilities.part_utils as part_utils
importlib.reload(part_utils)
ScenePartManager = part_utils.ScenePartManager

import Snowman3.riggers.containers.rig_container_utils as rig_container_utils
importlib.reload(rig_container_utils)
ContainerCreator = rig_container_utils.ContainerCreator
ContainerData = rig_container_utils.ContainerData
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
        for container in self.blueprint_manager.blueprint.containers.values():
            self.add_container(container)


    def add_container(self, container):
        container_manager = SceneContainerManager(container)
        return container_manager.create_scene_container()


    def remove_container(self, container):
        pm.delete(pm.PyNode(container.scene_name))


    def add_part(self, part, parent_container):
        scene_container = pm.PyNode(self.blueprint_manager.blueprint.containers[parent_container.data_name].scene_name)
        part_manager = ScenePartManager(part)
        return part_manager.create_scene_part(scene_container)


    def remove_part(self, part, parent_container):
        parent_scene_container = pm.PyNode(parent_container.scene_name)
        possible_scene_parts = pm.ls(part.scene_name)
        for scene_part in possible_scene_parts:
            if scene_part.getParent() == parent_scene_container:
                pm.delete(scene_part)
                break


    def mirror_container(self, container_key):
        for part_key in self.blueprint_manager.blueprint.containers[container_key].parts.keys():
            self.mirror_part(part_key, container_key)


    def mirror_part(self, part_key, container_key):
        self.mirror_part_handle(part_key, container_key)
        self.mirror_part_placer_positions(part_key, container_key)


    def mirror_part_handle(self, part_key, container_key):
        scene_part_handle = pm.PyNode(
            self.blueprint_manager.blueprint.containers[container_key].parts[part_key].scene_name)
        opposite_scene_part_handle = gen.get_opposite_side_obj(scene_part_handle)
        if not opposite_scene_part_handle:
            return False
        scene_part_handle_position = scene_part_handle.translate.get()
        opposite_scene_part_handle.translate.set(scene_part_handle_position)


    def mirror_part_placer_positions(self, part_key, container_key):
        part_placers = self.blueprint_manager.blueprint.containers[container_key].parts[part_key].placers
        [self.mirror_placer_position(key, part_key, container_key) for key in part_placers.keys()]


    def mirror_placer_position(self, placer_key, part_key, container_key):
        placer = self.blueprint_manager.blueprint.containers[container_key].parts[part_key].placers[placer_key]
        scene_placer = pm.PyNode(placer.scene_name)
        opposite_scene_placer = gen.get_opposite_side_obj(scene_placer)
        if not opposite_scene_placer:
            return False
        scene_placer_local_position = scene_placer.translate.get()
        opposite_scene_placer.translate.set(tuple(scene_placer_local_position))
