# Title: fk_chain.py
# Author: Sam Leheny
# Contact: samleheny@live.com

# Description:


###########################
##### Import Commands #####
import Snowman3.utilities.general_utils as gen

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
CTRL_SHAPE_SIZE = 1.0
###########################
###########################


class BespokePartConstructor(PartConstructor):

    def __init__(
        self,
        part_name: str,
        side: str = None,
        seg_count: int = 1
    ):
        super().__init__(part_name, side)
        self.seg_count = seg_count



    def create_placers(self):
        spacing = CTRL_SHAPE_SIZE * 4
        placers = []
        for i in range(self.seg_count):
            n = i + 1
            placer_creator = PlacerCreator(
                name=f'{self.part_name}{n}',
                side=self.side,
                part_name=self.part_name,
                position=[0, spacing*i, 0],
                size=CTRL_SHAPE_SIZE,
                vector_handle_positions=self.proportionalize_vector_handle_positions([[0, 1, 0], [0, 0, 1]], 1.0),
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
            ) for i in range(self.seg_count)
        ]
        return ctrls



    def create_part_nodes_list(self):
        return [f'{self.part_name}{str(i+1)}' for i in range(self.seg_count)]



    def bespoke_build_rig_part(self, part, rig_part_container, transform_grp, no_transform_grp, orienters, scene_ctrls):
        parent_obj = transform_grp
        for key, ctrl in scene_ctrls.items():
            ctrl_buffer = gen.buffer_obj(ctrl, parent_=parent_obj)
            gen.match_pos_ori(ctrl_buffer, orienters[key])
            self.part_nodes[key] = scene_ctrls[key]
            parent_obj = ctrl
        return rig_part_container
