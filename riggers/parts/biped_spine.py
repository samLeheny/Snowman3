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
            name='Spine1',
            data_name='spine_1',
            side=side,
            parent_part_name=part_name,
            position=(0, 0, 0),
            size=1.25,
            vector_handle_positions=[[0, 0, 5], [0, 5, 0]],
            orientation=[[0, 1, 0], [0, 0, 1]]
        ),
        Placer(
            name='Spine2',
            data_name='spine_2',
            side=side,
            parent_part_name=part_name,
            position=(0, 8.7, 0),
            size=1.25,
            vector_handle_positions=[[0, 0, 5], [0, 5, 0]],
            orientation=[[0, 1, 0], [0, 0, 1]]
        ),
        Placer(
            name='Spine3',
            data_name='spine_3',
            side=side,
            parent_part_name=part_name,
            position=(0, 20.2, 0),
            size=1.25,
            vector_handle_positions=[[0, 0, 5], [0, 5, 0]],
            orientation=[[0, 1, 0], [0, 0, 1]]
        ),
        Placer(
            name='Spine4',
            data_name='spine_4',
            side=side,
            parent_part_name=part_name,
            position=(0, 27.8, 0),
            size=1.25,
            vector_handle_positions=[[0, 0, 5], [0, 5, 0]],
            orientation=[[0, 1, 0], [0, 0, 1]]
        ),
        Placer(
            name='Spine5',
            data_name='spine_5',
            side=side,
            parent_part_name=part_name,
            position=(0, 42.3, 0),
            size=1.25,
            vector_handle_positions=[[0, 0, 5], [0, 5, 0]],
            orientation=[[0, 1, 0], [0, 0, 1]]
        ),
        Placer(
            name='Spine6',
            data_name='spine_6',
            side=side,
            parent_part_name=part_name,
            position=(0, 49, 0),
            size=1.25,
            vector_handle_positions=[[0, 0, 5], [0, 5, 0]],
            orientation=[[0, 1, 0], [0, 0, 1]]
        ),
    ]

    return placers


def get_connection_pairs():
    return (
        ('spine_2', 'spine_1'),
        ('spine_3', 'spine_2'),
        ('spine_4', 'spine_3'),
        ('spine_5', 'spine_4'),
        ('spine_6', 'spine_5')
    )

