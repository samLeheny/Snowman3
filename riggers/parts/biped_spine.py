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
        prefab_key = 'biped_spine',
        side = side,
        position=position,
        handle_size=1.0,
        placers={
            'spine_1':
                Placer(
                    name='spine_1',
                    side=side,
                    parent_part_name=name,
                    position=(0, 0, 0),
                    size=1.25,
                    vector_handle_positions=[[0, 0, 5], [0, 5, 0]],
                    orientation=[[0, 1, 0], [0, 0, 1]]
                ),
            'spine_2':
                Placer(
                    name='spine_2',
                    side=side,
                    parent_part_name=name,
                    position=(0, 8.7, 0),
                    size=1.25,
                    vector_handle_positions=[[0, 0, 5], [0, 5, 0]],
                    orientation=[[0, 1, 0], [0, 0, 1]]
                ),
            'spine_3':
                Placer(
                    name='spine_3',
                    side=side,
                    parent_part_name=name,
                    position=(0, 20.2, 0),
                    size=1.25,
                    vector_handle_positions=[[0, 0, 5], [0, 5, 0]],
                    orientation=[[0, 1, 0], [0, 0, 1]]
                ),
            'spine_4':
                Placer(
                    name='spine_4',
                    side=side,
                    parent_part_name=name,
                    position=(0, 27.8, 0),
                    size=1.25,
                    vector_handle_positions=[[0, 0, 5], [0, 5, 0]],
                    orientation=[[0, 1, 0], [0, 0, 1]]
                ),
            'spine_5':
                Placer(
                    name='spine_5',
                    side=side,
                    parent_part_name=name,
                    position=(0, 42.3, 0),
                    size=1.25,
                    vector_handle_positions=[[0, 0, 5], [0, 5, 0]],
                    orientation=[[0, 1, 0], [0, 0, 1]]
                ),
            'spine_6':
                Placer(
                    name='spine_6',
                    side=side,
                    parent_part_name=name,
                    position=(0, 49, 0),
                    size=1.25,
                    vector_handle_positions=[[0, 0, 5], [0, 5, 0]],
                    orientation=[[0, 1, 0], [0, 0, 1]]
                ),
        }
    )
    return part
