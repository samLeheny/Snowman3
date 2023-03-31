# Title: rig_manager.py
# Author: Sam Leheny
# Contact: samleheny@live.com

# Description:


###########################
##### Import Commands #####
import importlib
import pymel.core as pm

import Snowman3.utilities.general_utils as gen
importlib.reload(gen)

import Snowman3.riggers.utilities.placer_utils as placer_utils
importlib.reload(placer_utils)
OrienterManager = placer_utils.OrienterManager
###########################
###########################

###########################
######## Variables ########

###########################
###########################



########################################################################################################################
class Rig:
    def __init__(
        self,
        name: str,
        scene_rig_container = None
    ):
        self.name = name
        self.scene_rig_container = scene_rig_container



########################################################################################################################
class RigManager:
    def __init__(
        self,
        blueprint_manager = None,
        rig = None
    ):
        self.blueprint_manager = blueprint_manager
        self.rig = rig


    def build_rig_from_armature(self):
        self.rig = Rig(name=self.blueprint_manager.blueprint.asset_name)
        self.build_rig_root_structure()
        self.build_rig_parts()
        self.make_custom_constraints()


    def build_rig_root_structure(self):
        self.rig.scene_rig_container = pm.shadingNode('transform', name=self.rig.name, au=1)


    def build_rig_parts(self):
        rig_parts_parent = self.rig.scene_rig_container
        parts = self.blueprint_manager.blueprint.parts
        for key, part in parts.items():
            self.build_rig_part(part, parent=rig_parts_parent)


    def build_rig_part(self, part, parent):
        dir_string = f"Snowman3.riggers.parts.{part.prefab_key}"
        getter = importlib.import_module(dir_string)
        importlib.reload(getter)
        BespokePartConstructor = getter.BespokePartConstructor
        part_manager = BespokePartConstructor(part_name = part.name, side = part.side)
        rig_part_container = part_manager.build_rig_part(part)
        if rig_part_container:
            rig_part_container.setParent(self.rig.scene_rig_container)


    def make_custom_constraints(self):
        constraint_pairs = self.blueprint_manager.blueprint.custom_constraints
        for pair in constraint_pairs:
            self.make_custom_constraint(pair)


    def make_custom_constraint(self, constraint_pair):
        source_part_key, source_ctrl_key = constraint_pair[0]
        target_part_key = constraint_pair[1]
        source_ctrl = self.blueprint_manager.blueprint.parts[source_part_key].controls[source_ctrl_key]
        target_part = self.blueprint_manager.blueprint.parts[target_part_key]
        if not all((pm.objExists(source_ctrl.scene_name), pm.objExists(self.get_rig_part_scene_name(target_part)))):
            return False
        scene_source_ctrl = pm.PyNode(source_ctrl.scene_name)
        scene_target_part = pm.PyNode(self.get_rig_part_scene_name(target_part))
        pm.parentConstraint(scene_source_ctrl, scene_target_part, mo=1)
        pm.scaleConstraint(scene_source_ctrl, scene_target_part, mo=1)


    def get_rig_part_scene_name(self, part):
        part_scene_name = part.scene_name
        return part_scene_name.replace('PART', 'RIG')
