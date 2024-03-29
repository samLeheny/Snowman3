# Title: class_PartConstructor.py
# Author: Sam Leheny
# Contact: samleheny@live.com

# Description:


###########################
##### Import Commands #####
import ast
import copy
import pymel.core as pm

import Snowman3.utilities.general_utils as gen

import Snowman3.utilities.attribute_utils as attr_utils

import Snowman3.rigger.utilities.placer_utils as placer_utils
OrienterManager = placer_utils.OrienterManager

import Snowman3.rigger.utilities.control_utils as control_utils
Control = control_utils.Control
SceneControlManager = control_utils.SceneControlManager
CurveShape = control_utils.CurveShape

import Snowman3.dictionaries.colorCode as color_code

import Snowman3.dictionaries.nurbsCurvePrefabs as prefab_curve_shapes
###########################
###########################


###########################
######## Variables ########
COLOR_CODE = color_code.sided_ctrl_color
PREFAB_CTRL_SHAPES = prefab_curve_shapes.create_dict()
PART_SUFFIX = 'Part'
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
        return [COLOR_CODE[side_key]] + [COLOR_CODE[f'{side_key}{i}'] for i in range(2, 5)]


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
        rig_part_container = pm.group(name=f'{gen.side_tag(part.side)}{part.name}_{PART_SUFFIX}', world=1, empty=1)
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


    def create_scene_ctrls(self, part):
        scene_ctrl_managers = {ctrl.name: SceneControlManager(ctrl) for ctrl in part.controls.values()}
        self.scene_ctrls = {}
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


    def initialize_ctrl(self, name, shape, color, locks=None, data_name=None, position=None, size=1.0,
                        forward_direction=None, up_direction=None, shape_offset=None, match_position=None, side=None,
                        scene_name=None):
        curve_shape = crv_utils.compose_curve_construct_cvs(
            curve_data=copy.deepcopy(PREFAB_CTRL_SHAPES[shape]),
            scale=size,
            shape_offset=shape_offset,
            up_direction=up_direction,
            forward_direction=forward_direction
        )
        ctrl_data = { 'name': name, 'color': color, 'locks': locks, 'data_name': data_name, 'position': position,
                      'match_position': match_position, 'side': side, 'scene_name': scene_name,
                      'part_name': self.part_name, 'shape': curve_shape }
        return Control.create_from_data(**ctrl_data)


    @staticmethod
    def proportionalize_vector_handle_positions(positions, placer_size, scale_factor=4.0):
        new_positions = [[], []]
        for i, position in enumerate(positions):
            for j in range(3):
                new_positions[i].append(position[j] * (placer_size * scale_factor))
        return new_positions


    @staticmethod
    def remove_transform_lock_attributes(scene_ctrl):
        pm.deleteAttr(f'{scene_ctrl}.{"LockAttrData"}')


    @staticmethod
    def migrate_lock_data(scene_ctrl, new_node):
        if pm.attributeQuery('LockAttrData', node=scene_ctrl, exists=1):
            attr_utils.migrate_attr(scene_ctrl, new_node, 'LockAttrData', remove_original=False)


    @staticmethod
    def get_scene_orienters(part):
        orienter_managers = {key: OrienterManager(placer) for (key, placer) in part.placers.items()}
        scene_orienters = {key: manager.get_orienter() for (key, manager) in orienter_managers.items()}
        return scene_orienters
