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
            prefab_key = 'biped_arm',
            side = side,
            position=position,
            handle_size=1.0,
            placers={
                'upperarm':
                    Placer(
                        name="upperarm",
                        side=side,
                        parent_part_name=name,
                        position=(0, 0, 0),
                        size=1.25,
                        vector_handle_positions=[[5, 0, 0], [0, 0, -5]],
                        orientation=[[0, 0, 1], [1, 0, 0]]
                    ),
                'lowerarm':
                    Placer(
                        name="lowerarm",
                        side=side,
                        parent_part_name=name,
                        position=(26.94, 0, -2.97),
                        size=1.25,
                        vector_handle_positions=[[5, 0, 0], [0, 0, -5]],
                        orientation=[[0, 0, 1], [1, 0, 0]]
                    ),
                'lowerarm_end':
                    Placer(
                        name="lowerarm_end",
                        side=side,
                        parent_part_name=name,
                        position=(52.64, 0, 0),
                        size=1.25,
                        vector_handle_positions=[[5, 0, 0], [0, 0, -5]],
                        orientation=[[0, 0, 1], [1, 0, 0]]
                    ),
                'wrist_end':
                    Placer(
                        name="wrist_end",
                        side=side,
                        parent_part_name=name,
                        position=(59, 0, 0),
                        size=1,
                        vector_handle_positions=[[5, 0, 0], [0, 0, -5]],
                        orientation=[[0, 0, 1], [1, 0, 0]]
                    ),
                'ik_elbow':
                    Placer(
                        name="ik_elbow",
                        side=side,
                        parent_part_name=name,
                        position=(26.94, 0, -35),
                        size=1.25,
                        vector_handle_positions=[[5, 0, 0], [0, 0, -5]],
                        orientation=[[0, 0, 1], [1, 0, 0]]
                    )
            }
    )
    return part
