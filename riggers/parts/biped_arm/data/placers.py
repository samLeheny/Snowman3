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



placers = {
    'upperarm':
        Placer(
            name = "upperarm",
            position = (0, 0, 0),
            size = 1.25,
            vector_handle_positions=[[5, 0, 0], [0, 0, -5]],
            orientation=[[0, 0, 1], [1, 0, 0]]
        ),
    'lowerarm':
        Placer(
            name = "lowerarm",
            position = (26.94, 0, -2.97),
            size = 1.25,
            vector_handle_positions=[[5, 0, 0], [0, 0, -5]],
            orientation=[[0, 0, 1], [1, 0, 0]]
        ),
    'lowerarm_end':
        Placer(
            name = "lowerarm_end",
            position = (52.64, 0, 0),
            size = 1.25,
            vector_handle_positions=[[5, 0, 0], [0, 0, -5]],
            orientation=[[0, 0, 1], [1, 0, 0]]
        ),
    'wrist_end':
        Placer(
            name = "wrist_end",
            position = (59, 0, 0),
            size = 1,
            vector_handle_positions=[[5, 0, 0], [0, 0, -5]],
            orientation=[[0, 0, 1], [1, 0, 0]]
        ),
    'ik_elbow':
        Placer(
            name = "ik_elbow",
            position = (26.94, 0, -35),
            size = 1.25,
            vector_handle_positions=[[5, 0, 0], [0, 0, -5]],
            orientation=[[0, 0, 1], [1, 0, 0]]
        )
}
