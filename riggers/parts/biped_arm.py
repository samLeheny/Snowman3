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
part_tag = 'PART'
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
            ['UpperArm', (0, 0, 0), [[1, 0, 0], [0, 0, -1]], [[0, 0, 1], [1, 0, 0]], 1.25, True, None],
            ['LowerArm', (26.94, 0, -2.97), [[1, 0, 0], [0, 0, -1]], [[0, 0, 1], [1, 0, 0]], 1.25, True, None],
            ['LowerArmEnd', (52.64, 0, 0), [[1, 0, 0], [0, 1, 0]], [[0, 0, 1], [0, 1, 0]], 1.25, True, None],
            ['WristEnd', (59, 0, 0), [[1, 0, 0], [0, 1, 0]], [[0, 0, 1], [0, 1, 0]], 0.7, False, 'LowerArmEnd'],
            ['IkElbow', (26.94, 0, -35), [[1, 0, 0], [0, 1, 0]], [[0, 0, 1], [0, 1, 0]], 1.25, False, None]
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
            ('LowerArm', 'UpperArm'),
            ('LowerArmEnd', 'LowerArm'),
            ('WristEnd', 'LowerArmEnd'),
            ('IkElbow', 'LowerArm')
        )


    def get_vector_handle_attachments(self):
        return{
            'UpperArm': ['LowerArm', 'IkElbow'],
            'LowerArm': ['LowerArmEnd', 'IkElbow'],
            'LowerArmEnd': ['WristEnd', None]
        }



    def build_rig_part(self, part):
        rig_part_container, transform_grp, no_transform_grp = self.create_rig_part_grps(part)

        return rig_part_container