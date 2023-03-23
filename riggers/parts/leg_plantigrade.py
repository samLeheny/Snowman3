# Title: biped_arm.py
# Author: Sam Leheny
# Contact: samleheny@live.com

# Description:


###########################
##### Import Commands #####
import importlib

import Snowman3.riggers.utilities.placer_utils as placer_utils
importlib.reload(placer_utils)
Placer = placer_utils.Placer
###########################
###########################


###########################
######## Variables ########

###########################
###########################


def create_placers(part_name, side=None):
    placers = [
        Placer(
            name='Thigh',
            data_name='thigh',
            side=side,
            parent_part_name=part_name,
            position=(0, 0, 0),
            size=1.25,
            vector_handle_positions=[[0, -5, 0], [0, 0, 5]],
            orientation=[[0, 0, 1], [1, 0, 0]]
        ),
        Placer(
            name='Calf',
            data_name='calf',
            side=side,
            parent_part_name=part_name,
            position=(0, -45, 4.57),
            size=1.25,
            vector_handle_positions=[[0, -5, 0], [0, 0, 5]],
            orientation=[[0, 0, 1], [1, 0, 0]]
        ),
        Placer(
            name='CalfEnd',
            data_name='calf_end',
            side=side,
            parent_part_name=part_name,
            position=(0, -91, 0),
            size=1.25,
            vector_handle_positions=[[0, -5, 0], [0, 0, 5]],
            orientation=[[0, 0, 1], [1, 0, 0]]
        ),
        Placer(
            name='AnkleEnd',
            data_name='ankle_end',
            side=side,
            parent_part_name=part_name,
            position=(0, -101, 0),
            size=1,
            vector_handle_positions=[[0, -5, 0], [0, 0, 5]],
            orientation=[[0, 0, 1], [1, 0, 0]]
        ),
        Placer(
            name="IkKnee",
            data_name='ik_knee',
            side=side,
            parent_part_name=part_name,
            position=(0, -45, 40),
            size=1.25,
            vector_handle_positions=[[0, -5, 0], [0, 0, 5]],
            orientation=[[0, 0, 1], [1, 0, 0]]
        )
    ]

    return placers


def get_connection_pairs():
    return (
        ('calf', 'thigh'),
        ('calf_end', 'calf'),
        ('ankle_end', 'calf_end'),
        ('ik_knee', 'calf')
    )

