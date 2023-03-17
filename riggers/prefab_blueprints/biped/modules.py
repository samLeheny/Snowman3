# Title: modules.py
# Author: Sam Leheny
# Contact: samleheny@live.com

# Description:


###########################
##### Import Commands #####
import importlib
import Snowman3.riggers.utilities.module_utils as module_utils
importlib.reload(module_utils)
Module = module_utils.Module
###########################
###########################


###########################
######## Variables ########

###########################
###########################


modules = {}
module_inputs = [
    ['root', 'root', 'M', (0, 0, 0)],
    ['spine', 'biped_spine', 'M', (0, 101, 0.39)],
    ['neck', 'biped_neck', 'M', (0, 150, 0.39)],
    ['clavicle', 'biped_clavicle', 'L', (3, 146.88, 0.39)],
    ['clavicle', 'biped_clavicle', 'R', (3, 146.88, 0.39)],
    ['arm', 'biped_arm', 'L', (15, 146.88, 0.39)],
    ['arm', 'biped_arm', 'R', (15, 146.88, 0.39)],
    ['hand', 'biped_hand', 'L', (67.64, 146.88, 0.39)],
    ['hand', 'biped_hand', 'R', (67.64, 146.88, 0.39)],
    ['leg', 'leg_plantigrade', 'L', (8.5, 101, 0.39)],
    ['leg', 'leg_plantigrade', 'R', (8.5, 101, 0.39)],
    ['foot', 'foot_plantigrade', 'L', (8.5, 10, 0.39)],
    ['foot', 'foot_plantigrade', 'R', (8.5, 10, 0.39)],
]
for inputs in module_inputs:
    name, prefab_key, side, part_offset = inputs

    dir_string = f'Snowman3.riggers.modules.{prefab_key}'
    module_data = importlib.import_module(dir_string)
    importlib.reload(module_data)

    module = modules[f'{side}_{prefab_key}'] = module_data.create_module(name, side, part_offset)
