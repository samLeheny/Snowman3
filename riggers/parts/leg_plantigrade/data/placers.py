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
        'thigh':
            Placer(
                name = 'thigh',
                side = side,
                parent_part_name = parent_part_name,
                position = (0, 0, 0),
                size = 1.25,
                vector_handle_positions=[[0, -5, 0], [0, 0, 5]],
                orientation=[[0, 0, 1], [1, 0, 0]]
            ),
        'calf':
            Placer(
                name = 'calf',
                side = side,
                parent_part_name = parent_part_name,
                position = (0, -45, 4.57),
                size = 1.25,
                vector_handle_positions=[[0, -5, 0], [0, 0, 5]],
                orientation=[[0, 0, 1], [1, 0, 0]]
            ),
        'calf_end':
            Placer(
                name = 'calf_end',
                side = side,
                parent_part_name = parent_part_name,
                position = (0, -91, 0),
                size = 1.25,
                vector_handle_positions=[[0, -5, 0], [0, 0, 5]],
                orientation=[[0, 0, 1], [1, 0, 0]]
            ),
        'ankle_end':
            Placer(
                name = 'ankle_end',
                side = side,
                parent_part_name = parent_part_name,
                position = (0, -101, 0),
                size = 1,
                vector_handle_positions=[[0, -5, 0], [0, 0, 5]],
                orientation=[[0, 0, 1], [1, 0, 0]]
            ),
        'ik_knee':
            Placer(
                name = "ik_knee",
                side = side,
                parent_part_name = parent_part_name,
                position = (0, -45, 40),
                size = 1.25,
                vector_handle_positions=[[0, -5, 0], [0, 0, 5]],
                orientation=[[0, 0, 1], [1, 0, 0]]
            )
    }
    return placers
