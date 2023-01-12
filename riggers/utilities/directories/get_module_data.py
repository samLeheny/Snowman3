# Title: get_module_data.py
# Author: Sam Leheny
# Contact: samleheny@live.com

# Description:


###########################
##### Import Commands #####

import importlib
###########################
###########################


###########################
######## Variables ########
dir_string = {"setup":       "Snowman3.riggers.modules.{}.setup.setup",
              "placers":     "Snowman3.riggers.modules.{}.data.placers",
              "ctrl_data":   "Snowman3.riggers.modules.{}.data.ctrl_data"}
###########################
###########################





########################################################################################################################
def bespokeSetup(key):
    m = importlib.import_module(dir_string["setup"].format(key))
    importlib.reload(m)
    return m


########################################################################################################################
def placers(key, side=None, is_driven_side=False):
    m = importlib.import_module(dir_string["placers"].format(key))
    importlib.reload(m)
    return m.create_placers(side=side, is_driven_side=is_driven_side)


########################################################################################################################
def ctrl_data(key, side=None, is_driven_side=False, module_ctrl=None):
    m = importlib.import_module(dir_string["ctrl_data"].format(key))
    importlib.reload(m)
    return m.create_ctrl_data(side=side, is_driven_side=is_driven_side, module_ctrl=module_ctrl)

