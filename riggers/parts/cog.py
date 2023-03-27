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
        placers = []
        placer_creator = PlacerCreator(
            name='Cog',
            data_name='cog',
            side=self.side,
            parent_part_name=self.part_name,
            position=(0, 0, 0),
            size=1.75,
            vector_handle_positions=[[0, 0, 1], [0, 1, 0]],
            orientation=[[0, 0, 1], [0, 1, 0]],
            has_vector_handles=False
        )
        placers.append(placer_creator.create_placer())
        return placers


    def get_connection_pairs(self):
        return ()


    def get_vector_handle_attachments(self):
        return{}
