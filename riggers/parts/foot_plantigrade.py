# Title: foot_plantigrade.py
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
            ['Foot', 'foot', (0, 0, 0), [[1, 0, 0], [0, 0, -1]], [[0, 0, 1], [1, 0, 0]], 1.25, True, None],
            ['Ball', 'ball', (0, -7.5, 11.8), [[1, 0, 0], [0, 0, -1]], [[0, 0, 1], [1, 0, 0]], 1.25, True, None],
            ['BallEnd', 'ball_end', (0, -7.5, 16.73), [[1, 0, 0], [0, 0, -1]], [[0, 0, 1], [1, 0, 0]], 1.25, False,
             'Ball'],
            ['SoleToe', 'sole_toe', (0, -10, 11.8), [[1, 0, 0], [0, 0, -1]], [[0, 0, 1], [1, 0, 0]], 0.6, False, None],
            ['SoleToeEnd', 'sole_toe_end', (0, -10, 19), [[1, 0, 0], [0, 0, -1]], [[0, 0, 1], [1, 0, 0]], 0.6, False,
             None],
            ['SoleInner', 'sole_inner', (-4.5, -10, 11.8), [[1, 0, 0], [0, 0, -1]], [[0, 0, 1], [1, 0, 0]], 0.6, False,
             None],
            ['SoleOuter', 'sole_outer', (4.5, -10, 11.8), [[1, 0, 0], [0, 0, -1]], [[0, 0, 1], [1, 0, 0]], 0.6, False,
             None],
            ['SoleHeel', 'sole_heel', (0, -10, -4), [[1, 0, 0], [0, 0, -1]], [[0, 0, 1], [1, 0, 0]], 0.6, False, None],
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
                match_orienter=p[7],
                has_vector_handles=p[6]
            )
            placers.append(placer_creator.create_placer())
        return placers


    def get_connection_pairs(self):
        return (
            ('ball', 'foot'),
            ('ball_end', 'ball')
        )


    def get_vector_handle_attachments(self):
        return{}
