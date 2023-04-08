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

import Snowman3.riggers.utilities.placer_utils as placer_utils
importlib.reload(placer_utils)
Placer = placer_utils.Placer
PlacerCreator = placer_utils.PlacerCreator

import Snowman3.riggers.parts.class_PartConstructor as class_PartConstructor
importlib.reload(class_PartConstructor)
PartConstructor = class_PartConstructor.PartConstructor
###########################
###########################


###########################
######## Variables ########

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
            ['Thigh', (0, 0, 0), [[0, -1, 0], [0, 0, 1]], [[1, 0, 0], [0, 0, 1]], 1.25, True, None],
            ['Calf', (0, -45, 4.57), [[0, -1, 0], [0, 0, 1]], [[1, 0, 0], [0, 0, 1]], 1.25, True, None],
            ['CalfEnd', (0, -91, 0), [[0, -1, 0], [0, 0, 1]], [[1, 0, 0], [0, 0, 1]], 1.25, True, None],
            ['AnkleEnd', (0, -101, 0), [[0, -1, 0], [0, 0, 1]], [[1, 0, 0], [0, 0, 1]], 0.7, False, 'CalfEnd'],
            ['IkKnee', (0, -45, 40), [[0, -1, 0], [0, 0, 1]], [[1, 0, 0], [0, 1, 0]], 1.25, False, None],
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


    def get_connection_pairs(self):
        return (
            ('Calf', 'Thigh'),
            ('CalfEnd', 'Calf'),
            ('AnkleEnd', 'CalfEnd'),
            ('IkKnee', 'Calf')
        )


    def get_vector_handle_attachments(self):
        return {
            'Thigh': ['Calf', 'IkKnee'],
            'Calf': ['CalfEnd', 'IkKnee'],
            'CalfEnd': ['AnkleEnd', None]
        }



    def build_rig_part(self, part):
        rig_part_container, connector, transform_grp, no_transform_grp = self.create_rig_part_grps(part)

        return rig_part_container
