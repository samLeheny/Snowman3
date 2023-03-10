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
    Placer(
        name = "root",
        position = (0, 0, 0),
        size = 1.75,
        vector_handle_positions = [[0, 0, 5], [0, 5, 0]],
        orientation = [[0, 0, 1], [0, 1, 0]]
    ),
    Placer(
        name = "COG",
        position = (0, 105, 0.39),
        size = 1.75,
        vector_handle_positions = [[0, 0, 5], [0, 5, 0]],
        orientation = [[0, 0, 1], [0, 1, 0]]
    ),
}
