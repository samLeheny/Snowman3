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

    def get_prefab_part(name, prefab_key, position):
        dir_string = f'Snowman3.riggers.parts.{prefab_key}'
        part_data = importlib.import_module(dir_string)
        importlib.reload(part_data)
        part = part_data.create_part(name, side, position)
        return part

    module = Module(
        name = name,
        prefab_key = 'biped_neck',
        side = side,
        parts = {
            'neck': get_prefab_part('neck', 'biped_neck', (0, 0, 0))
        }
    )
    return module
