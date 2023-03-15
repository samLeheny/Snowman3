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
    'clavicle':
        Part(
            name = 'clavicle',
            prefab_key = 'biped_clavicle',
            position = (0, 0, 0),
            handle_size = 1.0,
        ),
}
