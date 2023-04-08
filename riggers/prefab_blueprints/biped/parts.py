# Title: parts.py
# Author: Sam Leheny
# Contact: samleheny@live.com

# Description:


###########################
##### Import Commands #####
import importlib

import Snowman3.riggers.utilities.part_utils as part_utils
importlib.reload(part_utils)
PartCreator = part_utils.PartCreator
###########################
###########################


###########################
######## Variables ########

###########################
###########################


part_creators = [
    PartCreator('Root', 'root', None, (0, 0, 0), {}),
    PartCreator('Cog', 'cog', None, (0, 108, 0.39), {}),
    PartCreator('Spine', 'biped_spine', 'M', (0, 101, 0.39), {
        'segment_count': 6}),
    PartCreator('Neck', 'biped_neck', 'M', (0, 150, 0.39), {}),
    PartCreator('Clavicle', 'biped_clavicle', 'L', (3, 146.88, 0.39), {}),
    PartCreator('Clavicle', 'biped_clavicle', 'R', (-3, 146.88, 0.39), {}),
    PartCreator('Arm', 'biped_arm', 'L', (15, 146.88, 0.39), {}),
    PartCreator('Arm', 'biped_arm', 'R', (-15, 146.88, 0.39), {}),
    PartCreator('Hand', 'biped_hand', 'L', (67.64, 146.88, 0.39), {
        'finger_count': 4,
        'finger_segment_count': 3,
        'thumb_count': 1,
        'thumb_segment_count': 3,
        'include_metacarpals': True}),
    PartCreator('Hand', 'biped_hand', 'R', (-67.64, 146.88, 0.39), {
        'finger_count': 4,
        'finger_segment_count': 3,
        'thumb_count': 1,
        'thumb_segment_count': 3,
        'include_metacarpals': True}),
    PartCreator('Leg', 'leg_plantigrade', 'L', (8.5, 101, 0.39), {}),
    PartCreator('Leg', 'leg_plantigrade', 'R', (-8.5, 101, 0.39), {}),
    PartCreator('Foot', 'foot_plantigrade', 'L', (8.5, 10, 0.39), {}),
    PartCreator('Foot', 'foot_plantigrade', 'R', (-8.5, 10, 0.39), {})
]


parts = {}
for part_creator in part_creators:
    new_part = part_creator.create_part()
    parts[new_part.data_name] = new_part
