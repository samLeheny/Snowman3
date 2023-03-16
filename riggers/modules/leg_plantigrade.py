# Title: biped_arm.py
# Author: Sam Leheny
# Contact: samleheny@live.com

# Description:


###########################
##### Import Commands #####
import importlib

import Snowman3.riggers.utilities.part_utils as part_utils
importlib.reload(part_utils)
Part = part_utils.Part

import Snowman3.riggers.utilities.module_utils as module_utils
importlib.reload(module_utils)
Module = module_utils.Module
###########################
###########################


###########################
######## Variables ########

###########################
###########################


def create_module(name, side=None):
    module = Module(
            name = name,
            prefab_key = 'leg_plantigrade',
            side = side,
            parts = {
                'leg':
                    Part(
                        name='leg',
                        prefab_key='leg_plantigrade',
                        side=side,
                        position=(0, 0, 0),
                        handle_size=1.0,
                    ),
            }
        )
    return module
