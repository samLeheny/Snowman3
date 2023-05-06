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

import Snowman3.utilities.attribute_utils as attr_utils
importlib.reload(attr_utils)

import Snowman3.riggers.utilities.placer_utils as placer_utils
importlib.reload(placer_utils)
OrienterManager = placer_utils.OrienterManager

import Snowman3.riggers.utilities.constraint_utils as constraint_utils
importlib.reload(constraint_utils)
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
        rig = None
    ):
        self.rig = rig
        self.scene_root = None
        self.part_constructors = {}


    def build_rig_from_armature(self, blueprint):
        self.rig = Rig(name=blueprint.asset_name)
        self.get_scene_root(blueprint.asset_name)
        self.build_rig_root_structure()
        self.build_rig_parts(blueprint.parts)
        self.perform_attribute_handoffs(blueprint.attribute_handoffs)
        self.make_custom_constraints(blueprint.custom_constraints)
        self.kill_unwanted_controls(blueprint.kill_ctrls)
        self.arrange_hierarchy(blueprint.parts)


    def get_scene_root(self, scene_root_name):
        if not pm.objExists(scene_root_name):
            pm.error(f"Scene root: '{scene_root_name}' not found")
        self.scene_root = pm.PyNode(scene_root_name)


    def build_rig_root_structure(self):
        self.rig.scene_rig_container = pm.group(name='Rig', em=1, p=self.scene_root)


    def build_rig_parts(self, parts):
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
        self.part_constructors[f'{gen.side_tag(part.side)}{part.name}'] = part_manager


    def make_custom_constraints(self, constraint_data):
        for package in constraint_data:
            self.make_custom_constraint(package)
        pm.select(clear=1)


    def make_custom_constraint(self, data):
        if type(data) == dict:
            data = constraint_utils.create_constraint_data_from_dict(data)
        constraint_utils.enact_constraint(data)


    def arrange_hierarchy(self, parts):
        for part in parts.values():
            if not part.parent:
                continue
            parent_part_key, parent_node_key = part.parent
            part_root_node = self.get_part_root_node(part)
            parent_node_string = self.part_constructors[parent_part_key].part_nodes[parent_node_key]
            if not pm.objExists(parent_node_string):
                continue
            parent_node = pm.PyNode(parent_node_string)
            part_root_node.setParent(parent_node)
        pm.select(clear=1)


    def kill_unwanted_controls(self, kill_ctrls):
        [self.kill_unwanted_control(package) for package in kill_ctrls]


    def kill_unwanted_control(self, data):
        part = pm.PyNode(f'{data["part_name"]}_RIG')
        ctrl = None
        for child in part.getChildren(allDescendents=1):
            if gen.get_clean_name(str(child)) == data['ctrl_node_name']:
                ctrl = child
                break
        if not ctrl:
            return False
        if data['hide']:
            for shape in ctrl.getShapes():
                shape.visibility.set(0, lock=1)
        if data['lock']:
            for attr in ('translate', 'tx', 'ty', 'tz', 'rotate', 'rx', 'ry', 'rz', 'scale', 'sx', 'sy', 'sz',
                         'visibility'):
                pm.setAttr(f'{ctrl}.{attr}', lock=1)
        if data['rename']:
            current_name = gen.get_clean_name(str(ctrl))
            new_name = current_name.replace('CTRL', 'DeadCTRL')
            pm.rename(ctrl, new_name)


    def get_rig_part_scene_name(self, part):
        part_suffix, rig_suffix = 'PART', 'RIG'
        part_scene_name = part.scene_name
        return part_scene_name.replace(part_suffix, rig_suffix)


    def get_rig_connector(self, part):
        rig_part_connector_name = f'{gen.side_tag(part.side)}{part.name}_CONNECTOR'
        if not pm.objExists(rig_part_connector_name):
            return None
        return pm.PyNode(rig_part_connector_name)


    def get_part_root_node(self, part):
        root_node_name = f'{gen.side_tag(part.side)}{part.name}_RIG'
        if not pm.objExists(root_node_name):
            return None
        return pm.PyNode(root_node_name)


    def perform_attribute_handoffs(self, attr_handoffs):
        [self.perform_attr_handoff(package) for package in attr_handoffs]


    def perform_attr_handoff(self, handoff_data):
        attr_exceptions = ("LockAttrData", "LockAttrDataT", "LockAttrDataR", "LockAttrDataS", "LockAttrDataV")
        old_node = pm.PyNode(handoff_data['old_attr_node'])
        new_node = pm.PyNode(handoff_data['new_attr_node'])
        attrs = pm.listAttr(old_node, userDefined=1)
        [attrs.remove(a) if a in attrs else None for a in attr_exceptions]
        [attr_utils.migrate_attr(old_node, new_node, a) for a in attrs]
        if handoff_data['delete_old_node']:
            pm.delete(old_node)


    def get_root_part(self, parts):
        root_part = None
        for part in parts.values():
            if part.prefab_key == 'root':
                root_part = part
                break
        return root_part


    def get_non_root_parts(self, parts):
        non_root_parts = parts.copy()
        for key in parts:
            if parts[key].prefab_key == 'root':
                non_root_parts.pop(key)
                break
        return non_root_parts.values()


    def make_rig_scalable(self, blueprint):
        root_part = self.get_root_part(blueprint.parts)
        if not root_part:
            pm.error('No Root part found in scene')
        non_root_parts = self.get_non_root_parts(blueprint.parts)
        part_scale_driver_node = pm.PyNode(root_part.controls['SubRoot'].scene_name)
        for part in non_root_parts:
            driven_part = pm.PyNode(f'{part.data_name}_RIG')
            part_connector_node = self.get_rig_connector(part)
            pm.scaleConstraint(part_scale_driver_node, part_connector_node, mo=1)
