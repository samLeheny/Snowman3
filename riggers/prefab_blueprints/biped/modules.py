# Title: modules.py
# Author: Sam Leheny
# Contact: samleheny@live.com

# Description:


###########################
##### Import Commands #####
import importlib

import Snowman3.riggers.modules.rig_module_utils as rig_module_utils
importlib.reload(rig_module_utils)
ModuleCreator = rig_module_utils.ModuleCreator
ModuleData = rig_module_utils.ModuleData
###########################
###########################


###########################
######## Variables ########

###########################
###########################


modules = {}
module_inputs = [
    ModuleData('root', 'root', 'M', (0, 0, 0)),
    ModuleData('spine', 'biped_spine', 'M', (0, 101, 0.39)),
    ModuleData('neck', 'biped_neck', 'M', (0, 150, 0.39)),
    ModuleData('clavicle', 'biped_clavicle', 'L', (3, 146.88, 0.39)),
    ModuleData('clavicle', 'biped_clavicle', 'R', (3, 146.88, 0.39)),
    ModuleData('arm', 'biped_arm', 'L', (15, 146.88, 0.39)),
    ModuleData('arm', 'biped_arm', 'R', (15, 146.88, 0.39)),
    ModuleData('hand', 'biped_hand', 'L', (67.64, 146.88, 0.39)),
    ModuleData('hand', 'biped_hand', 'R', (67.64, 146.88, 0.39)),
    ModuleData('leg', 'leg_plantigrade', 'L', (8.5, 101, 0.39)),
    ModuleData('leg', 'leg_plantigrade', 'R', (8.5, 101, 0.39)),
    ModuleData('foot', 'foot_plantigrade', 'L', (8.5, 10, 0.39)),
    ModuleData('foot', 'foot_plantigrade', 'R', (8.5, 10, 0.39)),
]

for module_data in module_inputs:
    module_creator = ModuleCreator(module_data)
    modules[f'{module_data.side}_{module_data.prefab_key}'] = module_creator.create_module()
