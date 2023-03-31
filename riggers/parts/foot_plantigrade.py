# Title: foot_plantigrade.py
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
            ['Foot', (0, 0, 0), [[0, 0, 1], [0, 1, 0]], [[0, 0, 1], [0, 1, 0]], 1.25, True, None],
            ['Ball', (0, -7.5, 11.8), [[0, 0, 1], [0, 1, 0]], [[0, 0, 1], [0, 1, 0]], 1.25, True, None],
            ['BallEnd', (0, -7.5, 16.73), [[0, 0, 1], [0, 1, 0]], [[0, 0, 1], [0, 1, 0]], 1.25, False, 'Ball'],
            ['SoleToe', (0, -10, 11.8), [[0, 0, 1], [0, 1, 0]], [[0, 0, 1], [0, 1, 0]], 0.6, False, None],
            ['SoleToeEnd', (0, -10, 19), [[0, 0, 1], [0, 1, 0]], [[0, 0, 1], [0, 1, 0]], 0.6, False, None],
            ['SoleInner', (-4.5, -10, 11.8), [[0, 0, 1], [0, 1, 0]], [[0, 0, 1], [0, 1, 0]], 0.6, False, None],
            ['SoleOuter', (4.5, -10, 11.8), [[0, 0, 1], [0, 1, 0]], [[0, 0, 1], [0, 1, 0]], 0.6, False, None],
            ['SoleHeel', (0, -10, -4), [[0, 0, 1], [0, 1, 0]], [[0, 0, 1], [0, 1, 0]], 0.6, False, None],
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
            ('Ball', 'Foot'),
            ('BallEnd', 'Ball')
        )



    def build_rig_part(self, part):
        rig_part_container, transform_grp, no_transform_grp = self.create_rig_part_grps(part)

        return rig_part_container
