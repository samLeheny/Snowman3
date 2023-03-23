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
part_tag = 'PART'
###########################
###########################


def create_placers(part_name, side=None):

    placers = [
        Placer(
            name="UpperArm",
            data_name='upperarm',
            side=side,
            parent_part_name=part_name,
            position=(0, 0, 0),
            size=1.25,
            vector_handle_positions=[[5, 0, 0], [0, 0, -5]],
            orientation=[[0, 0, 1], [1, 0, 0]],
        ),
        Placer(
            name="LowerArm",
            data_name='lowerarm',
            side=side,
            parent_part_name=part_name,
            position=(26.94, 0, -2.97),
            size=1.25,
            vector_handle_positions=[[5, 0, 0], [0, 0, -5]],
            orientation=[[0, 0, 1], [1, 0, 0]],
        ),
        Placer(
            name="LowerArmEnd",
            data_name='lowerarm_end',
            side=side,
            parent_part_name=part_name,
            position=(52.64, 0, 0),
            size=1.25,
            vector_handle_positions=[[5, 0, 0], [0, 0, -5]],
            orientation=[[0, 0, 1], [1, 0, 0]],
        ),
        Placer(
            name="WristEnd",
            data_name='wrist_end',
            side=side,
            parent_part_name=part_name,
            position=(59, 0, 0),
            size=1,
            vector_handle_positions=[[5, 0, 0], [0, 0, -5]],
            orientation=[[0, 0, 1], [1, 0, 0]]
        ),
        Placer(
            name="IkElbow",
            data_name='ik_elbow',
            side=side,
            parent_part_name=part_name,
            position=(26.94, 0, -35),
            size=1.25,
            vector_handle_positions=[[5, 0, 0], [0, 0, -5]],
            orientation=[[0, 0, 1], [1, 0, 0]]
        )
    ]

    return placers


def get_connection_pairs():
    return (
        ('lowerarm', 'upperarm'),
        ('lowerarm_end', 'lowerarm'),
        ('wrist_end', 'lowerarm_end'),
        ('ik_elbow', 'lowerarm')
    )
