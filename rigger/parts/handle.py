# Title: handle.py
# Author: Sam Leheny
# Contact: samleheny@live.com

# Description:


###########################
##### Import Commands #####

import Snowman3.utilities.general_utils as gen
import Snowman3.utilities.rig_utils as rig

import Snowman3.utilities.node_utils as nodes

import Snowman3.rigger.utilities.placer_utils as placer_utils
Placer = placer_utils.Placer
PlacerCreator = placer_utils.PlacerCreator

import Snowman3.rigger.parts.class_PartConstructor as class_PartConstructor
PartConstructor = class_PartConstructor.PartConstructor

import Snowman3.dictionaries.colorCode as color_code
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
        placer_creator = PlacerCreator(
            name=self.part_name,
            side=self.side,
            part_name=self.part_name,
            position=[0, 0, 0],
            size=1.0,
            vector_handle_positions=self.proportionalize_vector_handle_positions([[0, 1, 0], [0, 0, 1]], 1.0),
            orientation=[[0, 1, 0], [0, 0, 1]],
            match_orienter=None,
            has_vector_handles=True
        )
        placers = [placer_creator.create_placer()]
        return placers



    def create_controls(self):
        ctrls = [
            self.initialize_ctrl(
                name=self.part_name,
                shape='cube',
                color=self.colors[0],
                size=[1, 1, 1],
                up_direction = [1, 0, 0],
                forward_direction = [0, 0, 1],
                side=self.side
            ),
        ]
        return ctrls



    def create_part_nodes_list(self):
        part_nodes = [self.part_name]
        return part_nodes



    def bespoke_build_rig_part(self, part, rig_part_container, transform_grp, no_transform_grp, orienters, scene_ctrls):
        handle_ctrl_buffers = rig.BufferHierarchy.create(scene_ctrls[self.part_name], parent=transform_grp)
        gen.match_pos_ori(handle_ctrl_buffers.list()[-1], orienters[self.part_name])
        self.part_nodes[self.part_name] = scene_ctrls[self.part_name]
        return rig_part_container
