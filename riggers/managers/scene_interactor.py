# Title: scene_interactor.py
# Author: Sam Leheny
# Contact: samleheny@live.com

# Description:


###########################
##### Import Commands #####
import importlib
import logging
import pymel.core as pm

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

import Snowman3.riggers.utilities.constraint_utils as constraint_utils
importlib.reload(constraint_utils)
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
        self.armature_manager = ArmatureManager()
        self.rig_manager = RigManager()


    def build_armature_from_blueprint(self):
        self.armature_manager.build_armature_from_blueprint(blueprint=self.blueprint_manager.blueprint)


    def build_blank_armature(self):
        self.blueprint_manager.create_new_blueprint()
        self.update_working_blueprint_file()
        self.build_armature_from_blueprint()


    def build_armature_from_prefab(self):
        self.blueprint_manager.create_blueprint_from_prefab()
        self.blueprint_manager.run_prefab_post_actions()
        self.update_working_blueprint_file()
        self.build_armature_from_blueprint()


    def update_blueprint_from_scene(self):
        self.blueprint_manager.update_blueprint_from_scene()
        self.update_working_blueprint_file()


    def build_armature_from_latest_version(self):
        self.blueprint_manager.load_blueprint_from_latest_version()
        self.build_armature_from_blueprint()


    def build_armature_from_version_number(self, number):
        self.blueprint_manager.load_blueprint_from_numbered_version(number)
        self.build_armature_from_blueprint()


    def mirror_armature(self, driver_side):
        for part in self.blueprint_manager.blueprint.parts.values():
            if part.side == driver_side:
                self.mirror_part(part)
        self.update_working_blueprint_file()


    @staticmethod
    def create_part(name, prefab_key, side=None, construction_inputs=None):
        part_creator = PartCreator(name=name, prefab_key=prefab_key, side=side, construction_inputs=construction_inputs)
        return part_creator.create_part()


    def add_part(self, name, prefab_key, side=None, construction_inputs=None):
        if self.check_for_part(name=name, side=side):
            logging.error(f"Part already exists.")
            return False
        part = self.create_part(name, prefab_key, side, construction_inputs)
        self.blueprint_manager.add_part(part)
        self.armature_manager.add_part(part)
        self.update_working_blueprint_file()
        return part


    def check_for_part(self, name=None, side=None, part_key=None):
        if self.blueprint_manager.check_for_part(name=name, side=side, part_key=part_key):
            return True
        return False


    def remove_part(self, part_key):
        if not self.check_for_part(part_key=part_key):
            return False
        part = self.blueprint_manager.get_part(part_key)
        self.armature_manager.remove_part(part)
        self.blueprint_manager.remove_part(part)
        self.update_working_blueprint_file()


    def save_work(self):
        self.update_blueprint_from_scene()
        self.blueprint_manager.save_work()


    def create_mirrored_part(self, existing_part_key):
        if not self.check_for_part(part_key=existing_part_key):
            return False
        existing_part = self.blueprint_manager.get_part(existing_part_key)
        opposite_part_data = self.blueprint_manager.data_from_part(existing_part)
        opposite_part_data['side'] = gen.opposite_side(existing_part.side)
        new_opposing_part = self.create_part(
            name=f"{opposite_part_data['name']}",
            side=opposite_part_data['side'],
            prefab_key=opposite_part_data['prefab_key']
        )
        return new_opposing_part


    def add_mirrored_part(self, existing_part_key):
        existing_part = self.blueprint_manager.get_part(existing_part_key)
        new_part = self.create_mirrored_part(existing_part_key)
        if not new_part:
            return False
        self.blueprint_manager.add_part(new_part)

        self.blueprint_manager.mirror_part(existing_part)
        self.armature_manager.add_part(new_part)
        #self.mirror_part(self.blueprint_manager.blueprint.parts[existing_part_key])
        # Mirror control shapes
        self.armature_manager.mirror_part(existing_part)
        self.blueprint_manager.update_blueprint_from_scene()
        self.update_working_blueprint_file()


    def mirror_part(self, part):
        self.armature_manager.mirror_part(part)
        self.blueprint_manager.mirror_part(part)


    def mirror_solo_part(self, part):
        self.mirror_part(part)
        self.update_working_blueprint_file()


    def build_rig(self):
        self.rig_manager.build_rig_from_armature(self.blueprint_manager.blueprint)
        self.armature_manager.hide_armature()


    def update_selected_control_shapes(self):
        sel = pm.ls(sl=1)
        if not sel:
            return False
        for obj in sel:
            if not self.check_obj_is_control(obj):
                continue
            self.update_control_shape(obj)
        self.update_working_blueprint_file()


    def update_all_control_shapes(self):
        possible_ctrls = pm.ls('*_CTRL', type='transform')
        for obj in possible_ctrls:
            if not self.check_obj_is_control(obj):
                continue
            self.update_control_shape(obj)
        self.update_working_blueprint_file()


    def mirror_selected_control_shapes(self):
        sel = pm.ls(sl=1)
        if not sel:
            return False
        for obj in sel:
            if not gen.get_obj_side(obj):
                continue
            if not self.check_obj_is_control(obj):
                continue
            self.mirror_control_shape(obj)
        self.update_working_blueprint_file()


    def mirror_all_control_shapes(self, side):
        side_tags = {'L': 'L_', 'R': 'R_'}
        possible_ctrls = pm.ls(f'{side_tags[side]}*_CTRL', type='transform')
        for obj in possible_ctrls:
            if not self.check_obj_is_control(obj):
                continue
            self.mirror_control_shape(obj)
        self.update_working_blueprint_file()


    @staticmethod
    def check_obj_is_control(obj):
        if not gen.get_clean_name(str(obj)).endswith('_CTRL'):
            return False
        if not obj.getShape():
            return False
        return True


    def update_control_shape(self, ctrl):
        blueprint_ctrl = self.find_scene_control_in_blueprint(ctrl)
        self.blueprint_manager.update_control_shape_from_scene(blueprint_ctrl)


    @staticmethod
    def mirror_control_shape(ctrl):
        transform_attrs = ('translate', 'tx', 'ty', 'tz', 'rotate', 'rx', 'ry', 'rz', 'scale', 'sx', 'sy', 'sz')
        if not gen.get_obj_side(ctrl) in ('L', 'R'):
            return False
        opposite_ctrl = gen.get_opposite_side_obj(ctrl)
        if not opposite_ctrl:
            return False
        opposite_ctrl_color = gen.get_color(opposite_ctrl)
        dup_ctrl = pm.duplicate(ctrl)[0]
        for child in dup_ctrl.getChildren():
            if not child.nodeType() == 'nurbsCurve':
                pm.delete(child)
        temp_offset = pm.group(name='TEMP_FLIP_GRP', world=1, empty=1)
        for attr in transform_attrs:
            pm.setAttr(f'{dup_ctrl}.{attr}', lock=0)
        dup_ctrl.setParent(temp_offset)
        gen.flip_obj(temp_offset)
        gen.copy_shapes(dup_ctrl, opposite_ctrl, delete_existing_shapes=True)
        gen.set_color(opposite_ctrl, opposite_ctrl_color)
        pm.delete(temp_offset)


    def find_scene_control_in_blueprint(self, ctrl):
        return_node = None
        blueprint_ctrls = []
        blueprint = self.blueprint_manager.blueprint
        for part in blueprint.parts.values():
            for control in part.controls.values():
                blueprint_ctrls.append(control)
        for control in blueprint_ctrls:
            if gen.get_clean_name(str(ctrl)) == control.scene_name:
                return_node = control
        return return_node


    def add_selected_constraints(self):
        constraint_types = ('pointConstraint', 'orientConstraint', 'parentConstraint', 'scaleConstraint',
                            'aimConstraint', 'geometryConstraint')
        selection = pm.ls(sl=1)
        for node in selection:
            if node.nodeType() not in constraint_types:
                continue
            self.add_custom_constraint(node)
        self.update_working_blueprint_file()


    def add_custom_constraint(self, constraint_node):
        custom_constraint_data = constraint_utils.create_constraint_data(constraint_node)
        self.blueprint_manager.add_custom_constraint(custom_constraint_data)


    def remove_selected_constraints(self, delete=True):
        constraint_types = ('pointConstraint', 'orientConstraint', 'parentConstraint', 'scaleConstraint',
                            'aimConstraint', 'geometryConstraint')
        selection = pm.ls(sl=1)
        for node in selection:
            if node.nodeType() not in constraint_types:
                continue
            self.remove_custom_constraint(node.nodeName())
            pm.delete(node) if delete else None
        self.update_working_blueprint_file()


    def remove_custom_constraint(self, constraint_name):
        custom_constraints_list = self.blueprint_manager.blueprint.custom_constraints.copy()
        constraint_utils.remove_constraint(constraint_name, custom_constraints_list)
        self.blueprint_manager.blueprint.custom_constraints = custom_constraints_list


    def update_working_blueprint_file(self):
        self.blueprint_manager.save_blueprint_to_tempdisk()


    def assign_part_parent(self, part_key, parent_part_key, parent_node_name):
        self.blueprint_manager.assign_part_parent(part_key, parent_part_key, parent_node_name)
        self.update_working_blueprint_file()
