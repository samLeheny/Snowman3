# Title: get_armature_data.py
# Author: Sam Leheny
# Contact: samleheny@live.com

# Description:


###########################
##### Import Commands #####
import importlib

import Snowman.utilities.general_utils as gen_utils
reload(gen_utils)
###########################
###########################


###########################
######## Variables ########
dir_string = {"armature":      "Snowman.riggers.prefab_armatures.{}.armature",
              "modules":       "Snowman.riggers.prefab_armatures.{}.modules",
              "attr_handoffs": "Snowman.riggers.prefab_armatures.{}.attr_handoffs"}
###########################
###########################





########################################################################################################################
def armature(key, symmetry_mode=None):
    m = importlib.import_module(dir_string["armature"].format(key))
    reload(m)
    return m.create_armature(symmetry_mode=symmetry_mode)



########################################################################################################################
def modules(key, symmetry_mode=None):
    m = importlib.import_module(dir_string["modules"].format(key))
    reload(m)
    return m.create_modules(symmetry_mode=symmetry_mode)



def attr_handoffs(key):
    m = importlib.import_module(dir_string["attr_handoffs"].format(key))
    reload(m)
    return m.create_handoffs()