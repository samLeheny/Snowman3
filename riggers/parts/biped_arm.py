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

import Snowman3.riggers.utilities.part_utils as part_utils
importlib.reload(part_utils)
SceneRigPartManager = part_utils.SceneRigPartManager
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
            ['UpperArm', 'upperarm', (0, 0, 0), [[1, 0, 0], [0, 0, -1]], [[0, 0, 1], [1, 0, 0]], 1.25, True, None],
            ['LowerArm', 'lowerarm', (26.94, 0, -2.97), [[1, 0, 0], [0, 0, -1]], [[0, 0, 1], [1, 0, 0]], 1.25, True,
             None],
            ['LowerArmEnd', 'lowerarm_end', (52.64, 0, 0), [[1, 0, 0], [0, 1, 0]], [[0, 0, 1], [0, 1, 0]], 1.25, True,
             None],
            ['WristEnd', 'wrist_end', (59, 0, 0), [[1, 0, 0], [0, 1, 0]], [[0, 0, 1], [0, 1, 0]], 0.7, False,
             'LowerArmEnd'],
            ['IkElbow', 'ik_elbow', (26.94, 0, -35), [[1, 0, 0], [0, 1, 0]], [[0, 0, 1], [0, 1, 0]], 1.25, False,
             None]
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
                match_orienter=p[7],
                has_vector_handles=p[6]
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


    def get_vector_handle_attachments(self):
        return{
            'upperarm': ['lowerarm', 'ik_elbow'],
            'lowerarm': ['lowerarm_end', 'ik_elbow'],
            'lowerarm_end': ['wrist_end', None]
        }



    def build_rig_part(self, part):
        rig_part_manager = SceneRigPartManager(part)
        rig_part = rig_part_manager.create_scene_rig_part()
