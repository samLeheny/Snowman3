# Title: parts.py
# Author: Sam Leheny
# Contact: samleheny@live.com

# Description:


###########################
##### Import Commands #####
import importlib

import Snowman3.riggers.utilities.part_utils as part_utils
importlib.reload(part_utils)
Part = part_utils.Part
###########################
###########################


###########################
######## Variables ########

###########################
###########################



parts = {
    'root':
        Part(
            name = 'root',
            prefab_key = 'root',
            position = (0, 0, 0),
            handle_size = 1.0,
        ),
    'cog':
        Part(
            name = 'cog',
            prefab_key = 'cog',
            position = (0, 105, 0.39),
            handle_size = 1.0,
        ),
}
