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
part_tag = 'PART'
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
            ['UpperArm', 'upperarm', (0, 0, 0), [[5, 0, 0], [0, 0, -5]], [[0, 0, 1], [1, 0, 0]], 1.25],
            ['LowerArm', 'lowerarm', (26.94, 0, -2.97), [[5, 0, 0], [0, 0, -5]], [[0, 0, 1], [1, 0, 0]], 1.25],
            ['LowerArmEnd', 'lowerarm_end', (52.64, 0, 0), [[5, 0, 0], [0, 0, -5]], [[0, 0, 1], [1, 0, 0]], 1.25],
            ['WristEnd', 'wrist_end', (59, 0, 0), [[5, 0, 0], [0, 0, -5]], [[0, 0, 1], [1, 0, 0]], 0.7],
            ['IkElbow', 'ik_elbow', (26.94, 0, -35), [[5, 0, 0], [0, 0, -5]], [[0, 0, 1], [1, 0, 0]], 1.25],
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
                vector_handle_positions=p[3],
                orientation=p[4],
            )
            placers.append(placer_creator.create_placer())
        return placers


    def get_connection_pairs(self):
        return (
            ('lowerarm', 'upperarm'),
            ('lowerarm_end', 'lowerarm'),
            ('wrist_end', 'lowerarm_end'),
            ('ik_elbow', 'lowerarm')
        )
