# Title: cog.py
# Author: Sam Leheny
# Contact: samleheny@live.com

# Description:


###########################
##### Import Commands #####
import pymel.core as pm

import Snowman3.utilities.general_utils as gen

import Snowman3.rigger.utilities.placer_utils as placer_utils
Placer = placer_utils.Placer
PlacerCreator = placer_utils.PlacerCreator
OrienterManager = placer_utils.OrienterManager

import Snowman3.rigger.utilities.control_utils as control_utils
SceneControlManager = control_utils.SceneControlManager

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
        placers = []
        size = 1.75
        placer_creator = PlacerCreator(
            name='Cog',
            side=self.side,
            part_name=self.part_name,
            position=[0, 0, 0],
            size=size,
            vector_handle_positions=self.proportionalize_vector_handle_positions([[0, 0, 1], [0, 1, 0]], size),
            orientation=[[0, 0, 1], [0, 1, 0]],
            has_vector_handles=False
        )
        placers.append(placer_creator.create_placer())
        return placers


    def create_controls(self):
        ctrls = [
            self.initialize_ctrl(
                name = 'Cog',
                shape = 'COG',
                color = color_code['major'],
                locks = {"s": [1, 1, 1], "v": 1},
                size = 20,
                match_position = None
            )
        ]
        return ctrls


    def create_part_nodes_list(self):
        part_nodes = []
        for name in ('Cog',):
            part_nodes.append(name)
        return part_nodes



    def bespoke_build_rig_part(self, part, rig_part_container, transform_grp, no_transform_grp, orienters, scene_ctrls):

        scene_ctrls['Cog'].setParent(transform_grp)
        orienter_manager = OrienterManager(part.placers['Cog'])
        cog_orienter = orienter_manager.get_orienter()
        gen.match_pos_ori(scene_ctrls['Cog'], cog_orienter)
        buffer = gen.buffer_obj(scene_ctrls['Cog'])

        for key in ('Cog',):
            self.part_nodes[key] = scene_ctrls[key].nodeName()

        return rig_part_container
