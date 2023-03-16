# Title: rootPlacers.py
# Author: Sam Leheny
# Contact: samleheny@live.com

# Description:


###########################
##### Import Commands #####
import importlib

import Snowman3.riggers.utilities.placer_utils as placer_utils
importlib.reload(placer_utils)
Placer = placer_utils.Placer
###########################
###########################


###########################
######## Variables ########

###########################
###########################


def create_placers(side=None, parent_part_name=None):
    placers = {
        'clavicle':
            Placer(
                name = 'clavicle',
                side = side,
                parent_part_name = parent_part_name,
                position = (0, 0, 0),
                size = 1.25,
                vector_handle_positions=[[5, 0, 0], [0, 5, 0]],
                orientation=[[0, 0, 1], [0, 1, 0]]
            ),
        'clavicle_end':
            Placer(
                name = 'clavicle_end',
                side = side,
                parent_part_name = parent_part_name,
                position = (12, 0, 0),
                size = 1.25,
                vector_handle_positions=[[5, 0, 0], [0, 5, 0]],
                orientation=[[0, 0, 1], [0, 1, 0]]
            )
    }
    return placers
