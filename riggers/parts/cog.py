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

import Snowman3.riggers.utilities.placer_utils as placer_utils
importlib.reload(placer_utils)
Placer = placer_utils.Placer
###########################
###########################


###########################
######## Variables ########

###########################
###########################


def create_part(name, side=None, position=(0, 0, 0)):
    part = Part(
        name = name,
        prefab_key = 'cog',
        side = side,
        position=position,
        handle_size=1.0,
        placers={
            'cog':
                Placer(
                    name='cog',
                    side=side,
                    parent_part_name=name,
                    position=(0, 105, 0.39),
                    size=1.75,
                    vector_handle_positions=[[0, 0, 5], [0, 5, 0]],
                    orientation=[[0, 0, 1], [0, 1, 0]]
                ),
        }
    )
    return part
