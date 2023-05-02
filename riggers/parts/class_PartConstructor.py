# Title: class_PartConstructor.py
# Author: Sam Leheny
# Contact: samleheny@live.com

# Description:


###########################
##### Import Commands #####
import importlib
import ast
import pymel.core as pm

import Snowman3.utilities.general_utils as gen
importlib.reload(gen)

import Snowman3.utilities.attribute_utils as attr_utils
importlib.reload(attr_utils)

import Snowman3.riggers.utilities.placer_utils as placer_utils
importlib.reload(placer_utils)
OrienterManager = placer_utils.OrienterManager

import Snowman3.riggers.utilities.control_utils as control_utils
importlib.reload(control_utils)
ControlCreator = control_utils.ControlCreator
SceneControlManager = control_utils.SceneControlManager

import Snowman3.dictionaries.colorCode as color_code
importlib.reload(color_code)
###########################
###########################


###########################
######## Variables ########
color_code = color_code.sided_ctrl_color
###########################
###########################


class PartConstructor:
    def __init__(
        self,
        part_name: str,
        side: str = None,
        part_nodes: dict = {}
    ):
        self.part_name = part_name
        self.side = side
        self.colors = self.get_colors()
        self.scene_ctrls = None
        self.part_nodes = part_nodes


    def get_colors(self):
        side_key = self.side if self.side else 'M'
        return [color_code[side_key]] + [color_code[f'{side_key}{i}'] for i in range(2, 5)]
    

    def proportionalize_vector_handle_positions(self, positions, placer_size, scale_factor=4.0):
        new_positions = [[], []]
        for i, position in enumerate(positions):
            for j in range(3):
                new_positions[i].append(position[j] * (placer_size * scale_factor))
        return new_positions


    def create_part_nodes_list(self):
        return []


    def create_placers(self):
        return []


    def create_controls(self):
        return []


    def get_connection_pairs(self):
        return ()


    def get_vector_handle_attachments(self):
        return {}


    def bespoke_build_rig_part(self, part, rig_part_container, transform_grp, no_transform_grp, orienters,
                               scene_ctrls):
        return None


    def check_construction_inputs_integrity(self, construction_inputs):
        return construction_inputs


    def build_rig_part(self, part):
        rig_part_container, transform_grp, no_transform_grp = self.create_rig_part_grps(part)
        orienters, scene_ctrls = self.get_scene_armature_nodes(part)
        rig_part_container = self.bespoke_build_rig_part(part, rig_part_container, transform_grp, no_transform_grp,
                                                         orienters, scene_ctrls)
        self.apply_all_control_transform_locks()
        pm.select(clear=1)
        return rig_part_container


    def create_rig_part_grps(self, part):
        rig_part_container = pm.group(name=f'{gen.side_tag(part.side)}{part.name}_RIG', world=1, empty=1)
        transform_grp = pm.group(name=f'{gen.side_tag(part.side)}{part.name}_Transform_GRP', empty=1,
                                 parent=rig_part_container)
        no_transform_grp = pm.group(name=f'{gen.side_tag(part.side)}{part.name}_NoTransform_GRP', empty=1,
                                    parent=rig_part_container)
        if self.side == 'R':
            [gen.flip_obj(grp) for grp in (transform_grp, no_transform_grp)]
        no_transform_grp.inheritsTransform.set(0, lock=1)
        return rig_part_container, transform_grp, no_transform_grp


    def get_scene_armature_nodes(self, part):
        orienters = self.get_scene_orienters(part)
        ctrls = self.create_scene_ctrls(part)
        return orienters, ctrls


    def get_scene_orienters(self, part):
        orienter_managers = {key: OrienterManager(placer) for (key, placer) in part.placers.items()}
        scene_orienters = {key: manager.get_orienter() for (key, manager) in orienter_managers.items()}
        return scene_orienters


    def create_scene_ctrls(self, part):
        scene_ctrl_managers = {ctrl.name: SceneControlManager(ctrl) for ctrl in part.controls.values()}
        '''for manager in scene_ctrl_managers.values():
            for shape in manager.control.shape:
                for i, cv in enumerate(shape['cvs']):
                    shape['cvs'][i] = [cv[i] * part.part_scale for i in range(3)]'''
        self.scene_ctrls = {key: manager.create_scene_control() for (key, manager) in scene_ctrl_managers.items()}
        return self.scene_ctrls


    def apply_all_control_transform_locks(self):
        for scene_ctrl in self.scene_ctrls.values():
            self.apply_control_transform_locks(scene_ctrl)


    def apply_control_transform_locks(self, scene_ctrl):
        transform_axis_letters = ('x', 'y', 'z')
        for letter in ('t', 'r', 's'):
            attr_name = f'LockAttrData{letter.upper()}'
            if not pm.attributeQuery(attr_name, node=scene_ctrl, exists=1):
                continue
            if pm.getAttr(f'{scene_ctrl}.{attr_name}') in ('None', 'none', None):
                continue
            values = ast.literal_eval(pm.getAttr(f'{scene_ctrl}.{attr_name}'))
            for i, value in enumerate(values):
                pm.setAttr(f'{scene_ctrl}.{letter}{transform_axis_letters[i]}', keyable=0, lock=1) if value else None
        vis_attr_name = f'LockAttrData{"V"}'
        if not pm.attributeQuery(vis_attr_name, node=scene_ctrl, exists=1):
            return
        pm.setAttr(f'{scene_ctrl}.visibility', keyable=0, lock=1) \
            if pm.getAttr(f'{scene_ctrl}.{vis_attr_name}') else None
        self.remove_transform_lock_attributes(scene_ctrl)


    def remove_transform_lock_attributes(self, scene_ctrl):
        pm.deleteAttr(f'{scene_ctrl}.{"LockAttrData"}')


    def migrate_lock_data(self, scene_ctrl, new_node):
        if pm.attributeQuery('LockAttrData', node=scene_ctrl, exists=1):
            attr_utils.migrate_attr(scene_ctrl, new_node, 'LockAttrData', remove_original=False)


    def migrate_control_to_new_node(self, scene_ctrl, new_ctrl):
        scene_ctrl_name = gen.get_clean_name(str(scene_ctrl))
        pm.rename(scene_ctrl, f'{scene_ctrl_name}_TEMP')
        pm.rename(new_ctrl, scene_ctrl_name)
        scene_ctrl.setParent(new_ctrl.getParent())
        gen.zero_out(scene_ctrl)
        pm.matchTransform(scene_ctrl, new_ctrl)
        self.migrate_lock_data(scene_ctrl, new_ctrl)
        gen.copy_shapes(source_obj=scene_ctrl, destination_obj=new_ctrl, delete_existing_shapes=True)
        return new_ctrl
