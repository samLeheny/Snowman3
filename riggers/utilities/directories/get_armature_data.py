# Title: get_armature_data.py
# Author: Sam Leheny
# Contact: samleheny@live.com

# Description:


###########################
##### Import Commands #####
import importlib
import importlib

import Snowman3.utilities.general_utils as gen_utils
importlib.reload(gen_utils)
###########################
###########################


###########################
######## Variables ########
dir_string = {'armature':           'Snowman3.riggers.prefab_armatures.{}.armature',
              'modules':            'Snowman3.riggers.prefab_armatures.{}.modules',
              'attr_handoffs':      'Snowman3.riggers.prefab_armatures.{}.attr_handoffs',
              'module_connections': 'Snowman3.riggers.prefab_armatures.{}.connection_pairs',
              'space_blends':       'Snowman3.riggers.prefab_armatures.{}.space_blends',
              'placer_connectors':  'Snowman3.riggers.prefab_armatures.{}.placer_connectors'}
###########################
###########################





########################################################################################################################
def armature(key, symmetry_mode=None):
    m = importlib.import_module(dir_string["armature"].format(key))
    importlib.reload(m)
    return m.create_armature(symmetry_mode=symmetry_mode)


########################################################################################################################
def modules(key, symmetry_mode=None):
    m = importlib.import_module(dir_string["modules"].format(key))
    importlib.reload(m)
    return m.create_modules(symmetry_mode=symmetry_mode)


########################################################################################################################
def attr_handoffs(key, rig_modules):
    m = importlib.import_module(dir_string["attr_handoffs"].format(key))
    importlib.reload(m)
    return m.create_handoffs(rig_modules)


########################################################################################################################
def module_connections(key, rig_modules):
    m = importlib.import_module(dir_string["module_connections"].format(key))
    importlib.reload(m)
    return m.create_connection_pairs_dict(rig_modules)


########################################################################################################################
def space_blends(key, rig_modules):
    m = importlib.import_module(dir_string["space_blends"].format(key))
    importlib.reload(m)
    return m.create_space_blends(rig_modules)


########################################################################################################################
def placer_connectors(key):
    m = importlib.import_module(dir_string["placer_connectors"].format(key))
    importlib.reload(m)
    return m.create_placer_connectors()
