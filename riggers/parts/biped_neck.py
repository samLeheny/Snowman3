# Title: biped_arm.py
# Author: Sam Leheny
# Contact: samleheny@live.com

# Description:


###########################
##### Import Commands #####
import importlib

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
            ['Neck', 'neck', (0, 0, 0), [[0, 1, 0], [0, 0, 1]], [[0, 1, 0], [0, 0, 1]], 1.25, True],
            ['Head', 'head', (0, 12.5, 1.8), [[0, 1, 0], [0, 0, 1]], [[0, 1, 0], [0, 0, 1]], 1.25, True],
        ]
        placers = []
        for p in data_packs:
            placer_creator = PlacerCreator(
                name=p[0],
                data_name=p[1],
                side=self.side,
                parent_part_name=self.part_name,
                position=p[2],
                size=p[5],
                vector_handle_positions=self.proportionalize_vector_handle_positions(p[3], p[5]),
                orientation=p[4],
                has_vector_handles=p[6]
            )
            placers.append(placer_creator.create_placer())
        return placers


    def get_connection_pairs(self):
        return (
            ('head', 'neck'),
        )


    def get_vector_handle_attachments(self):
        return{}
