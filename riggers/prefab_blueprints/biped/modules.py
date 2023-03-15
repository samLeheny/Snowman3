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


modules = {

    'root':
        Module(
            prefab_key = 'root',
            name = 'root',
            side = 'M',
        ),

    'spine':
        Module(
            prefab_key = 'biped_spine',
            name = 'spine',
            side = 'M',
        ),

    'neck':
        Module(
            prefab_key = 'biped_neck',
            name = 'neck',
            side = 'M',
        ),

    'L_clavicle':
        Module(
            prefab_key = 'biped_clavicle',
            name = 'clavicle',
            side = 'L',
        ),

    'R_clavicle':
        Module(
            prefab_key = 'biped_clavicle',
            name = 'clavicle',
            side = 'R',
        ),

    'L_arm':
        Module(
            prefab_key = 'biped_arm',
            name = 'arm',
            side = 'L',
        ),

    'R_arm':
        Module(
            prefab_key = 'biped_arm',
            name = 'arm',
            side = 'R',
        ),

    'L_hand':
        Module(
            prefab_key = 'biped_hand',
            name = 'hand',
            side = 'L',
        ),

    'R_hand':
        Module(
            prefab_key = 'biped_hand',
            name = 'hand',
            side = 'R',
        ),

    'L_leg':
        Module(
            prefab_key = 'leg_plantigrade',
            name = 'leg',
            side = 'L',
        ),

    'R_leg':
        Module(
            prefab_key = 'leg_plantigrade',
            name = 'leg',
            side = 'R',
        ),

    'L_foot':
        Module(
            prefab_key = 'foot_plantigrade',
            name = 'foot',
            side = 'L',
        ),

    'R_foot':
        Module(
            prefab_key = 'foot_plantigrade',
            name = 'foot',
            side = 'R',
        )
}
