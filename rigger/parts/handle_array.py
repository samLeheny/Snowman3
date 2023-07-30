# Title: handle_array.py
# Author: Sam Leheny
# Contact: samleheny@live.com

# Description:


###########################
##### Import Commands #####
import importlib

import Snowman3.utilities.general_utils as gen
importlib.reload(gen)
import Snowman3.utilities.rig_utils as rig
importlib.reload(rig)

import Snowman3.rigger.utilities.placer_utils as placer_utils
importlib.reload(placer_utils)
Placer = placer_utils.Placer
PlacerCreator = placer_utils.PlacerCreator

import Snowman3.rigger.parts.class_PartConstructor as class_PartConstructor
importlib.reload(class_PartConstructor)
PartConstructor = class_PartConstructor.PartConstructor

import Snowman3.dictionaries.colorCode as color_code
importlib.reload(color_code)
###########################
###########################


###########################
######## Variables ########
color_code = color_code.sided_ctrl_color
CTRL_SHAPE_SIZE = 1.0
###########################
###########################


class BespokePartConstructor(PartConstructor):

    def __init__(
        self,
        part_name: str,
        side: str = None,
        handle_count: int = 1
    ):
        super().__init__(part_name, side)
        self.handle_count = handle_count



    def create_placers(self):
        spacing = CTRL_SHAPE_SIZE * 4
        placers = []
        for i in range(self.handle_count):
            n = i + 1
            placer_creator = PlacerCreator(
                name=f'{self.part_name}{str(n)}',
                side=self.side,
                part_name=self.part_name,
                position=[0, spacing * i, 0],
                size=CTRL_SHAPE_SIZE,
                vector_handle_positions=self.proportionalize_vector_handle_positions([[0, 1, 0], [0, 0, 1]], True),
                orientation=[[0, 1, 0], [0, 0, 1]],
                match_orienter=None,
                has_vector_handles=True
            )
            placers.append(placer_creator.create_placer())
        return placers



    def create_controls(self):
        ctrls = [
            self.initialize_ctrl(
                name=f'{self.part_name}{str(i+1)}',
                shape='cube',
                color=self.colors[0],
                size=CTRL_SHAPE_SIZE,
                up_direction = [0, 1, 0],
                forward_direction = [0, 0, 1],
                side=self.side
            ) for i in range(self.handle_count)
        ]
        return ctrls



    def create_part_nodes_list(self):
        return [f'{self.part_name}{str(i+1)}' for i in range(self.handle_count)]



    def bespoke_build_rig_part(self, part, rig_part_container, transform_grp, no_transform_grp, orienters, scene_ctrls):
        for key, ctrl in scene_ctrls.items():
            ctrl_buffers = rig.BufferHierarchy.create(ctrl, parent=transform_grp)
            gen.match_pos_ori(ctrl_buffers.list()[-1], orienters[key])
            self.part_nodes[key] = scene_ctrls[key]
        return rig_part_container
