# Title: biped_arm.py
# Author: Sam Leheny
# Contact: samleheny@live.com

# Description:


###########################
##### Import Commands #####
import importlib
import pymel.core as pm

import Snowman3.utilities.general_utils as gen
importlib.reload(gen)

import Snowman3.utilities.node_utils as nodes
importlib.reload(nodes)

import Snowman3.riggers.utilities.placer_utils as placer_utils
importlib.reload(placer_utils)
Placer = placer_utils.Placer
PlacerCreator = placer_utils.PlacerCreator

import Snowman3.riggers.parts.class_PartConstructor as class_PartConstructor
importlib.reload(class_PartConstructor)
PartConstructor = class_PartConstructor.PartConstructor

import Snowman3.riggers.utilities.control_utils as control_utils
importlib.reload(control_utils)
ControlCreator = control_utils.ControlCreator
SceneControlManager = control_utils.SceneControlManager

import Snowman3.dictionaries.colorCode as color_code
importlib.reload(color_code)

import Snowman3.riggers.utilities.class_LimbRig as class_LimbRig
importlib.reload(class_LimbRig)
LimbRig = class_LimbRig.LimbRig
###########################
###########################


###########################
######## Variables ########
color_code = color_code.sided_ctrl_color
###########################
###########################


class BespokePartConstructor(PartConstructor):

    def __init__(
        self,
        part_name: str,
        side: str = None,
    ):
        super().__init__(part_name, side)



    def create_placers(self):
        data_packs = [
            [self.part_name, (0, 0, 0), [[0, 1, 0], [0, 0, 1]], [[0, 1, 0], [0, 0, 1]], 1.0, True, None],
        ]
        placers = []
        for p in data_packs:
            placer_creator = PlacerCreator(
                name=p[0],
                side=self.side,
                parent_part_name=self.part_name,
                position=p[1],
                size=p[4],
                vector_handle_positions=self.proportionalize_vector_handle_positions(p[2], p[4]),
                orientation=p[3],
                match_orienter=p[6],
                has_vector_handles=p[5]
            )
            placers.append(placer_creator.create_placer())
        return placers



    def create_controls(self):
        ctrl_creators = [
            ControlCreator(
                name=self.part_name,
                shape='cube',
                color=self.colors[0],
                size=[1, 1, 1],
                up_direction = [1, 0, 0],
                forward_direction = [0, 0, 1],
                side=self.side
            ),
        ]
        controls = [creator.create_control() for creator in ctrl_creators]
        return controls



    def create_part_nodes_list(self):
        part_nodes = [self.part_name]
        return part_nodes



    def bespoke_build_rig_part(self, part, rig_part_container, transform_grp, no_transform_grp, orienters, scene_ctrls):
        handle_ctrl_buffer = gen.buffer_obj(scene_ctrls[self.part_name], parent=transform_grp)
        gen.match_pos_ori(handle_ctrl_buffer, orienters[self.part_name])
        self.part_nodes[self.part_name] = scene_ctrls[self.part_name]
        return rig_part_container
