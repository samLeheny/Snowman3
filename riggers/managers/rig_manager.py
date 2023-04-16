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
        parts = self.blueprint_manager.blueprint.parts
        for key, part in parts.items():
            self.build_rig_part(part)


    def build_rig_part(self, part):
        dir_string = f"Snowman3.riggers.parts.{part.prefab_key}"
        getter = importlib.import_module(dir_string)
        importlib.reload(getter)
        BespokePartConstructor = getter.BespokePartConstructor
        part_manager = BespokePartConstructor(part_name=part.name, side=part.side)
        rig_part_container = part_manager.build_rig_part(part)
        if rig_part_container:
            rig_part_container.setParent(self.rig.scene_rig_container)


    def make_custom_constraints(self):
        constraint_pairs = self.blueprint_manager.blueprint.custom_constraints
        for package in constraint_pairs:
            self.make_custom_constraint(package)
        pm.select(clear=1)


    def make_custom_constraint(self, data):
        driver_part = pm.PyNode(f'{data["driver_part_name"]}_RIG')
        driven_part = pm.PyNode(f'{data["driven_part_name"]}_RIG')
        driver_node, driven_node = None, None
        for child in driver_part.getChildren(allDescendents=1):
            if gen.get_clean_name(str(child)) == data['driver_node_name']:
                driver_node = child
                break
        for child in driven_part.getChildren(allDescendents=1):
            if gen.get_clean_name(str(child)) == data['driven_node_name']:
                driven_node = child
                break
        if not all((driver_node, driven_node)):
            return False
        if data['match_transform']:
            children = driven_node.getChildren()
            for child in children:
                child.setParent(world=1)
            pm.matchTransform(driven_node, driver_node)
            for child in children:
                child.setParent(driven_node)
        if data['constraint_type'] == 'parent':
            pm.parentConstraint(driver_node, driven_node, mo=1)
        elif data['constraint_type'] == 'point':
            pm.pointConstraint(driver_node, driven_node, mo=1)


    def get_rig_part_scene_name(self, part):
        part_suffix, rig_suffix = 'PART', 'RIG'
        part_scene_name = part.scene_name
        return part_scene_name.replace(part_suffix, rig_suffix)


    def get_rig_connector(self, rig_scene_part):
        rig_part_connector_name = 'Connector'
        return_node = None
        for child in rig_scene_part.getChildren():
            if gen.get_clean_name(str(child)) == rig_part_connector_name:
                return_node = child
        return return_node
