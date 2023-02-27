# Title: rootPlacers.py
# Author: Sam Leheny
# Contact: samleheny@live.com

# Description:


###########################
##### Import Commands #####
import importlib

import Snowman3.riggers.utilities.classes.class_Placer as classPlacer
importlib.reload(classPlacer)
Placer = classPlacer.Placer
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
