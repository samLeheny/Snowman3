# Title: foot_plantigrade.py
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
            name='Foot',
            data_name='foot',
            side=side,
            parent_part_name=part_name,
            position=(0, 0, 0),
            size=1,
            vector_handle_positions=[[0, 0, 5], [0, 5, 0]],
            orientation=[[0, 0, 1], [1, 0, 0]]
        ),
        Placer(
            name='Ball',
            data_name='ball',
            side=side,
            parent_part_name=part_name,
            position=(0, -7.5, 11.8),
            size=1,
            vector_handle_positions=[[0, 0, 5], [0, 5, 0]],
            orientation=[[0, 0, 1], [1, 0, 0]]
        ),
        Placer(
            name='BallEnd',
            data_name='ball_end',
            side=side,
            parent_part_name=part_name,
            position=(0, -7.5, 16.73),
            size=1,
            vector_handle_positions=[[0, 0, 5], [0, 5, 0]],
            orientation=[[0, 0, 1], [1, 0, 0]]
        ),
        Placer(
            name='SoleToe',
            data_name='sole_toe',
            side=side,
            parent_part_name=part_name,
            position=(0, -10, 11.8),
            size=0.65,
            vector_handle_positions=[[0, 0, 5], [0, 5, 0]],
            orientation=[[0, 0, 1], [1, 0, 0]]
        ),
        Placer(
            name='SoleToeEnd',
            data_name='sole_toe_end',
            side=side,
            parent_part_name=part_name,
            position=(0, -10, 19),
            size=0.65,
            vector_handle_positions=[[0, 0, 5], [0, 5, 0]],
            orientation=[[0, 0, 1], [1, 0, 0]]
        ),
        Placer(
            name='SoleInner',
            data_name='sole_inner',
            side=side,
            parent_part_name=part_name,
            position=(-4.5, -10, 11.8),
            size=0.65,
            vector_handle_positions=[[0, 0, 5], [0, 5, 0]],
            orientation=[[0, 0, 1], [1, 0, 0]]
        ),
        Placer(
            name='SoleOuter',
            data_name='sole_outer',
            side=side,
            parent_part_name=part_name,
            position=(4.5, -10, 11.8),
            size=0.65,
            vector_handle_positions=[[0, 0, 5], [0, 5, 0]],
            orientation=[[0, 0, 1], [1, 0, 0]]
        ),
        Placer(
            name='SoleHeel',
            data_name='sole_heel',
            side=side,
            parent_part_name=part_name,
            position=(0, -10, -4),
            size=0.65,
            vector_handle_positions=[[0, 0, 5], [0, 5, 0]],
            orientation=[[0, 0, 1], [1, 0, 0]]
        )
    ]

    return placers


def get_connection_pairs():
    return (
        ('ball', 'foot'),
        ('ball_end', 'ball')
    )

