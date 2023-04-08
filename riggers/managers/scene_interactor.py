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

import Snowman3.riggers.utilities.part_utils as part_utils
importlib.reload(part_utils)
PartCreator = part_utils.PartCreator

import Snowman3.riggers.managers.rig_manager as rig_manager_util
importlib.reload(rig_manager_util)
RigManager = rig_manager_util.RigManager
###########################
###########################

###########################
######## Variables ########

###########################
###########################



class SceneInteractor:
    def __init__(
        self,
        blueprint_manager: BlueprintManager = None,
        armature_manager: ArmatureManager = None,
        rig_manager: RigManager = None
    ):
        self.blueprint_manager = blueprint_manager
        self.armature_manager = armature_manager
        self.rig_manager = rig_manager


    def create_managers(self, asset_name, dirpath, prefab_key=None):
        self.blueprint_manager = BlueprintManager(asset_name=asset_name, dirpath=dirpath, prefab_key=prefab_key)
        self.armature_manager = ArmatureManager(blueprint_manager=self.blueprint_manager)
        self.rig_manager = RigManager(blueprint_manager=self.blueprint_manager)


    def build_armature_from_prefab(self):
        self.blueprint_manager.create_blueprint_from_prefab()
        self.blueprint_manager.run_prefab_post_actions()
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
        for key, part in self.blueprint_manager.blueprint.parts.items():
            if part.side == driver_side:
                self.armature_manager.mirror_part(key)


    def create_part(self, name, prefab_key, side=None):
        part_creator = PartCreator(name=name, prefab_key=prefab_key, side=side)
        return part_creator.create_part()


    def add_part(self, name, prefab_key, side=None):
        part = self.create_part(name, prefab_key, side)
        self.blueprint_manager.add_part(part)
        self.armature_manager.add_part(part, parent=self.armature_manager.scene_root)


    def remove_part(self, part_key):
        part = self.blueprint_manager.get_part(part_key)
        self.armature_manager.remove_part(part)
        self.blueprint_manager.remove_part(part)


    def save_work(self):
        self.blueprint_manager.save_work()


    def create_mirrored_part(self, existing_part_key):
        existing_part = self.blueprint_manager.get_part(existing_part_key)
        opposite_part_data = self.blueprint_manager.data_from_part(existing_part)
        opposite_part_data['side'] = gen.opposite_side(existing_part.side)

        new_opposing_part = self.create_part(
            name=f"{opposite_part_data['name']}", side=opposite_part_data['side'],
            prefab_key=opposite_part_data['prefab_key'])
        return new_opposing_part


    def add_mirrored_part(self, existing_part_key):
        new_opposite_part = self.create_mirrored_part(existing_part_key)
        self.blueprint_manager.add_part(new_opposite_part)
        self.armature_manager.add_part(new_opposite_part)
        self.armature_manager.mirror_part(existing_part_key)
        self.blueprint_manager.update_blueprint_from_scene()
        self.blueprint_manager.save_blueprint_to_tempdisk()


    def build_rig(self):
        self.rig_manager.build_rig_from_armature()
