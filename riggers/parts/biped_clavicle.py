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
###########################
###########################


###########################
######## Variables ########

###########################
###########################


class PlacersGetter:

    def __init__(
        self,
        part_name: str,
        side: str = None,
    ):
        self.part_name = part_name
        self.side = side

    def create_placers(self):
        data_packs = [
            ['Clavicle', 'clavicle', (0, 0, 0), [[5, 0, 0], [0, 0, -5]], [[0, 0, 1], [1, 0, 0]]],
            ['ClavicleEnd', 'clavicle_end', (12, 0, 0), [[5, 0, 0], [0, 0, -5]], [[0, 0, 1], [1, 0, 0]]],
        ]
        placers = []
        for name, data_name, position, vector_handle_positions, orientation in data_packs:
            placer_creator = PlacerCreator(
                name=name,
                data_name=data_name,
                side=self.side,
                parent_part_name=self.part_name,
                position=position,
                size=1.25,
                vector_handle_positions=vector_handle_positions,
                orientation=orientation,
            )
            placers.append(placer_creator.create_placer())
        return placers


    def get_connection_pairs(self):
        return (
            ('clavicle_end', 'clavicle'),
        )
