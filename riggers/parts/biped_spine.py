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
        segment_count: int = 6
    ):
        self.part_name = part_name
        self.side = side
        self.segment_count = segment_count
        self.jnt_count = segment_count + 1


    def create_placers(self):
        spine_length = 49.0
        spine_seg_length = spine_length / self.segment_count
        placers = []
        for i in range(self.jnt_count):
            n = i + 1
            has_vector_handles = True
            size = 1.25
            if i == range(self.jnt_count):
                has_vector_handles = False
                size = 0.8
            placer_creator = PlacerCreator(
                name=f'Spine{str(n)}',
                data_name=f'spine_{str(n)}',
                side=self.side,
                parent_part_name=self.part_name,
                position=(0, spine_seg_length * i, 0),
                size=size,
                vector_handle_positions=[[0, 0, 1], [0, 1, 0]],
                orientation=[[0, 1, 0], [0, 0, 1]],
                has_vector_handles=has_vector_handles
            )
            placers.append(placer_creator.create_placer())
        return placers


    def get_connection_pairs(self):
        pairs = []
        for i in range(self.segment_count):
            n = i + 1
            pairs.append(
                (f'spine_{str(n+1)}', f'spine_{str(n)}')
            )
        return tuple(pairs)


    def get_vector_handle_attachments(self):
        return{}
