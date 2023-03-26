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
            ['Thigh', 'thigh', (0, 0, 0), [[5, 0, 0], [0, 0, -5]], [[0, 0, 1], [1, 0, 0]]],
            ['Calf', 'calf', (0, -45, 4.57), [[5, 0, 0], [0, 0, -5]], [[0, 0, 1], [1, 0, 0]]],
            ['CalfEnd', 'calf_end', (0, -91, 0), [[5, 0, 0], [0, 0, -5]], [[0, 0, 1], [1, 0, 0]]],
            ['AnkleEnd', 'ankle_end', (0, -101, 0), [[5, 0, 0], [0, 0, -5]], [[0, 0, 1], [1, 0, 0]]],
            ['IkKnee', 'ik_knee', (0, -45, 40), [[5, 0, 0], [0, 0, -5]], [[0, 0, 1], [1, 0, 0]]],
        ]
        placers = []
        for p in data_packs:
            placer_creator = PlacerCreator(
                name=p[0],
                data_name=p[1],
                side=self.side,
                parent_part_name=self.part_name,
                position=p[2],
                size=1.25,
                vector_handle_positions=p[3],
                orientation=p[4],
            )
            placers.append(placer_creator.create_placer())
        return placers


    def get_connection_pairs(self):
        return (
            ('calf', 'thigh'),
            ('calf_end', 'calf'),
            ('ankle_end', 'calf_end'),
            ('ik_knee', 'calf')
        )

