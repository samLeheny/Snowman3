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
        prefab_key = 'leg_plantigrade',
        side = side,
        position=position,
        handle_size=1.0,
        placers={
            'thigh':
                Placer(
                    name='Thigh',
                    side=side,
                    parent_part_name=name,
                    position=(0, 0, 0),
                    size=1.25,
                    vector_handle_positions=[[0, -5, 0], [0, 0, 5]],
                    orientation=[[0, 0, 1], [1, 0, 0]]
                ),
            'calf':
                Placer(
                    name='Calf',
                    side=side,
                    parent_part_name=name,
                    position=(0, -45, 4.57),
                    size=1.25,
                    vector_handle_positions=[[0, -5, 0], [0, 0, 5]],
                    orientation=[[0, 0, 1], [1, 0, 0]]
                ),
            'calf_end':
                Placer(
                    name='CalfEnd',
                    side=side,
                    parent_part_name=name,
                    position=(0, -91, 0),
                    size=1.25,
                    vector_handle_positions=[[0, -5, 0], [0, 0, 5]],
                    orientation=[[0, 0, 1], [1, 0, 0]]
                ),
            'ankle_end':
                Placer(
                    name='AnkleEnd',
                    side=side,
                    parent_part_name=name,
                    position=(0, -101, 0),
                    size=1,
                    vector_handle_positions=[[0, -5, 0], [0, 0, 5]],
                    orientation=[[0, 0, 1], [1, 0, 0]]
                ),
            'ik_knee':
                Placer(
                    name="IkKnee",
                    side=side,
                    parent_part_name=name,
                    position=(0, -45, 40),
                    size=1.25,
                    vector_handle_positions=[[0, -5, 0], [0, 0, 5]],
                    orientation=[[0, 0, 1], [1, 0, 0]]
                )
        }
    )
    return part
