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
    'foot':
        Placer(
            name='foot',
            position=(0, 0, 0),
            size=1,
            vector_handle_positions=[[0, 0, 5], [0, 5, 0]],
            orientation=[[0, 0, 1], [1, 0, 0]]
        ),
    'ball':
        Placer(
            name='ball',
            position=(0, -7.5, 11.8),
            size=1,
            vector_handle_positions=[[0, 0, 5], [0, 5, 0]],
            orientation=[[0, 0, 1], [1, 0, 0]]
        ),
    'ball_end':
        Placer(
            name='ball_end',
            position=(0, -7.5, 16.73),
            size=1,
            vector_handle_positions=[[0, 0, 5], [0, 5, 0]],
            orientation=[[0, 0, 1], [1, 0, 0]]
        ),
    'sole_toe':
        Placer(
            name='sole_toe',
            position=(0, 0, 11.8),
            size=0.65,
            vector_handle_positions=[[0, 0, 5], [0, 5, 0]],
            orientation=[[0, 0, 1], [1, 0, 0]]
        ),
    'sole_toe_end':
        Placer(
            name='sole_toe_end',
            position=(0, 0, 19),
            size=0.65,
            vector_handle_positions=[[0, 0, 5], [0, 5, 0]],
            orientation=[[0, 0, 1], [1, 0, 0]]
        ),
    'sole_inner':
        Placer(
            name='sole_inner',
            position=(-4.5, 0, 11.8),
            size=0.65,
            vector_handle_positions=[[0, 0, 5], [0, 5, 0]],
            orientation=[[0, 0, 1], [1, 0, 0]]
        ),
    'sole_outer':
        Placer(
            name='sole_outer',
            position=(4.5, 0, 11.8),
            size=0.65,
            vector_handle_positions=[[0, 0, 5], [0, 5, 0]],
            orientation=[[0, 0, 1], [1, 0, 0]]
        ),
    'sole_heel':
        Placer(
            name='sole_heel',
            position=(0, 0, -4),
            size=0.65,
            vector_handle_positions=[[0, 0, 5], [0, 5, 0]],
            orientation=[[0, 0, 1], [1, 0, 0]]
        )
}
