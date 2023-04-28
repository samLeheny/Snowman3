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
    PartCreator(name='Root', prefab_key='root', side=None, position=(0, 0, 0), construction_inputs={}),
    PartCreator(name='Cog', prefab_key='cog', side=None, position=(0, 108, 0.39), construction_inputs={}),
    PartCreator(name='Spine', prefab_key='biped_spine', side='M', position=(0, 101, 0.39),
                construction_inputs={'segment_count': 6}),
    PartCreator(name='Neck', prefab_key='biped_neck', side='M', position=(0, 150, 0.39), construction_inputs={}),
    PartCreator(name='Clavicle', prefab_key='biped_clavicle', side='L', position=(3, 146.88, 0.39),
                construction_inputs={}),
    PartCreator(name='Clavicle', prefab_key='biped_clavicle', side='R', position=(-3, 146.88, 0.39),
                construction_inputs={}),
    PartCreator(name='Arm', prefab_key='biped_arm', side='L', position=(15, 146.88, 0.39), construction_inputs={}),
    PartCreator(name='Arm', prefab_key='biped_arm', side='R', position=(-15, 146.88, 0.39), construction_inputs={}),
    PartCreator(name='Hand', prefab_key='hand', side='L', position=(67.64, 146.88, 0.39),
                construction_inputs={'finger_count': 4,
                                     'finger_segment_count': 3,
                                     'thumb_count': 1,
                                     'thumb_segment_count': 3,
                                     'include_metacarpals': True}),
    PartCreator(name='Hand', prefab_key='hand', side='R', position=(-67.64, 146.88, 0.39),
                construction_inputs={'finger_count': 4,
                                     'finger_segment_count': 3,
                                     'thumb_count': 1,
                                     'thumb_segment_count': 3,
                                     'include_metacarpals': True}),
    PartCreator(name='Leg', prefab_key='leg_plantigrade', side='L', position=(8.5, 101, 0.39), construction_inputs={}),
    PartCreator(name='Leg', prefab_key='leg_plantigrade', side='R', position=(-8.5, 101, 0.39), construction_inputs={}),
]


parts = {}
for part_creator in part_creators:
    new_part = part_creator.create_part()
    parts[new_part.data_name] = new_part



'''PartCreator(name='Foot', prefab_key='foot_plantigrade', side='L', position=(8.5, 10, 0.39), construction_inputs={}),
PartCreator(name='Foot', prefab_key='foot_plantigrade', side='R', position=(-8.5, 10, 0.39),
            construction_inputs={}),------------------------------------------------------------------------------------------------------------'''