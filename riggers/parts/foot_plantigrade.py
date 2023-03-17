# Title: foot_plantigrade.py
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
        prefab_key = 'foot_plantigrade',
        side = side,
        position=position,
        handle_size=1.0,
        placers={
            'foot':
                Placer(
                    name='foot',
                    side=side,
                    parent_part_name=name,
                    position=(0, 0, 0),
                    size=1,
                    vector_handle_positions=[[0, 0, 5], [0, 5, 0]],
                    orientation=[[0, 0, 1], [1, 0, 0]]
                ),
            'ball':
                Placer(
                    name='ball',
                    side=side,
                    parent_part_name=name,
                    position=(0, -7.5, 11.8),
                    size=1,
                    vector_handle_positions=[[0, 0, 5], [0, 5, 0]],
                    orientation=[[0, 0, 1], [1, 0, 0]]
                ),
            'ball_end':
                Placer(
                    name='ball_end',
                    side=side,
                    parent_part_name=name,
                    position=(0, -7.5, 16.73),
                    size=1,
                    vector_handle_positions=[[0, 0, 5], [0, 5, 0]],
                    orientation=[[0, 0, 1], [1, 0, 0]]
                ),
            'sole_toe':
                Placer(
                    name='sole_toe',
                    side=side,
                    parent_part_name=name,
                    position=(0, -10, 11.8),
                    size=0.65,
                    vector_handle_positions=[[0, 0, 5], [0, 5, 0]],
                    orientation=[[0, 0, 1], [1, 0, 0]]
                ),
            'sole_toe_end':
                Placer(
                    name='sole_toe_end',
                    side=side,
                    parent_part_name=name,
                    position=(0, -10, 19),
                    size=0.65,
                    vector_handle_positions=[[0, 0, 5], [0, 5, 0]],
                    orientation=[[0, 0, 1], [1, 0, 0]]
                ),
            'sole_inner':
                Placer(
                    name='sole_inner',
                    side=side,
                    parent_part_name=name,
                    position=(-4.5, -10, 11.8),
                    size=0.65,
                    vector_handle_positions=[[0, 0, 5], [0, 5, 0]],
                    orientation=[[0, 0, 1], [1, 0, 0]]
                ),
            'sole_outer':
                Placer(
                    name='sole_outer',
                    side=side,
                    parent_part_name=name,
                    position=(4.5, -10, 11.8),
                    size=0.65,
                    vector_handle_positions=[[0, 0, 5], [0, 5, 0]],
                    orientation=[[0, 0, 1], [1, 0, 0]]
                ),
            'sole_heel':
                Placer(
                    name='sole_heel',
                    side=side,
                    parent_part_name=name,
                    position=(0, -10, -4),
                    size=0.65,
                    vector_handle_positions=[[0, 0, 5], [0, 5, 0]],
                    orientation=[[0, 0, 1], [1, 0, 0]]
                )
        }
    )
    return part
