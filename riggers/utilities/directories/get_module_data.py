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
dir_string = {"setup":       "Snowman.riggers.modules.{}.setup.setup",
              "placers":     "Snowman.riggers.modules.{}.utilities.placers",
              "prelimCtrls": "Snowman.riggers.modules.{}.utilities.prelimCtrls",
              "animCtrls":   "Snowman.riggers.modules.{}.utilities.animCtrls"}
###########################
###########################





########################################################################################################################
def bespokeSetup(key):
    m = importlib.import_module(dir_string["setup"].format(key))
    reload(m)
    return m


########################################################################################################################
def placers(key, side=None, is_driven_side=False):
    m = importlib.import_module(dir_string["placers"].format(key))
    reload(m)
    return m.create_placers(side=side, is_driven_side=is_driven_side)


########################################################################################################################
def prelim_ctrls(key, side=None, is_driven_side=False):
    m = importlib.import_module(dir_string["prelimCtrls"].format(key))
    reload(m)
    return m.create_prelim_ctrls(side=side, is_driven_side=is_driven_side)


########################################################################################################################
def anim_ctrls(key, side=None, module_ctrl=None):
    m = importlib.import_module(dir_string["animCtrls"].format(key))
    reload(m)
    return m.create_anim_ctrls(side=side, module_ctrl=module_ctrl)
