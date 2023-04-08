# Title: class_PartConstructor.py
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

import Snowman3.riggers.utilities.control_utils as control_utils
importlib.reload(control_utils)
SceneControlManager = control_utils.SceneControlManager
###########################
###########################


###########################
######## Variables ########

###########################
###########################


class PartConstructor:
    def __init__(
        self,
        part_name: str,
        side: str = None
    ):
        self.part_name = part_name
        self.side = side
    

    def proportionalize_vector_handle_positions(self, positions, placer_size, scale_factor=4.0):
        new_positions = [[], []]
        for i, position in enumerate(positions):
            for j in range(3):
                new_positions[i].append(position[j] * (placer_size * scale_factor))
        return new_positions


    def create_placers(self):
        return []


    def create_controls(self):
        return []


    def get_connection_pairs(self):
        return ()


    def get_vector_handle_attachments(self):
        return {}


    def build_rig_part(self, part):
        return None


    def create_rig_part_grps(self, part):
        rig_part_container = pm.group(name=f'{gen.side_tag(part.side)}{part.name}_RIG', world=1, empty=1)
        connector_node = pm.group(name=f'Connector', empty=1, parent=rig_part_container)
        transform_grp = pm.group(name=f'Transform_GRP', empty=1, parent=connector_node)
        no_transform_grp = pm.group(name=f'NoTransform_GRP', empty=1, parent=connector_node)
        if self.side == 'R':
            [gen.flip_obj(grp) for grp in (transform_grp, no_transform_grp)]
        no_transform_grp.inheritsTransform.set(0, lock=1)
        return rig_part_container, connector_node, transform_grp, no_transform_grp


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
        scene_ctrls = {key: manager.create_scene_control() for (key, manager) in scene_ctrl_managers.items()}
        return scene_ctrls
