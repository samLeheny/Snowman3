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
    ['root', 'root', 'M'],
    ['spine', 'biped_spine', 'M'],
    ['neck', 'biped_neck', 'M'],
    ['clavicle', 'biped_clavicle', 'L'],
    ['clavicle', 'biped_clavicle', 'R'],
    ['arm', 'biped_arm', 'L'],
    ['arm', 'biped_arm', 'R'],
    ['hand', 'biped_hand', 'L'],
    ['hand', 'biped_hand', 'R'],
    ['leg', 'leg_plantigrade', 'L'],
    ['leg', 'leg_plantigrade', 'R'],
    ['foot', 'foot_plantigrade', 'L'],
    ['foot', 'foot_plantigrade', 'R'],
]
for inputs in module_inputs:
    name, prefab_key, side = inputs

    dir_string = f'Snowman3.riggers.modules.{prefab_key}'
    module_data = importlib.import_module(dir_string)
    importlib.reload(module_data)

    module = modules[f'{side}_{prefab_key}'] = module_data.create_module(name, side)
