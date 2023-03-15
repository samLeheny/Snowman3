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
    'neck':
        Placer(
            name='neck',
            position=(0, 0, 0),
            size=1.25,
            vector_handle_positions=[[0, 0, 5], [0, 5, 0]],
            orientation=[[0, 1, 0], [0, 0, 1]]
        ),
    'head':
        Placer(
            name='head',
            position=(0, 12.5, 1.8),
            size=1.25,
            vector_handle_positions=[[0, 0, 5], [0, 5, 0]],
            orientation=[[0, 1, 0], [0, 0, 1]]
        )
}