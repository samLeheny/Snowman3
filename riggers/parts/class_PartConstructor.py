# Title: class_PartConstructor.py
# Author: Sam Leheny
# Contact: samleheny@live.com

# Description:


###########################
##### Import Commands #####
import importlib

import Snowman3.riggers.utilities.placer_utils as placer_utils
importlib.reload(placer_utils)
OrienterManager = placer_utils.OrienterManager
###########################
###########################


###########################
######## Variables ########

###########################
###########################


class PartConstructor:
    def __init__(
        self,
        part_name: str,
        side: str = None
    ):
        self.part_name = part_name
        self.side = side
    

    def proportionalize_vector_handle_positions(self, positions, placer_size, scale_factor=4.0):
        new_positions = [[], []]
        for i, position in enumerate(positions):
            for j in range(3):
                new_positions[i].append(position[j] * (placer_size * scale_factor))
        return new_positions


    def create_placers(self):
        return []


    def create_controls(self):
        return []


    def get_connection_pairs(self):
        return ()


    def get_vector_handle_attachments(self):
        return {}


    def build_rig_part(self, part):
        '''orienters = {}
        for key, placer in part.placers.items():
            orienter_manager = OrienterManager(placer=placer)
            orienters[key] = orienter_manager.get_orienter()'''
        print('PLACE_HOLDER')
