# Title: animCtrls.py
# Author: Sam Leheny
# Contact: samleheny@live.com

# Description:


###########################
##### Import Commands #####
import importlib
import Snowman3.riggers.utilities.classes.class_AnimControl as class_AnimControl
importlib.reload(class_AnimControl)
###########################
###########################


###########################
######## Variables ########
AnimControl = class_AnimControl.AnimControl
###########################
###########################





def create_anim_ctrls(side=None, module_ctrl=None):

    anim_ctrls = {


        "neck": AnimControl(
            ctrl_name_tag="neck",
            prelim_ctrl_name= "neck",
            side=side,
            module_ctrl = module_ctrl
        ),


        "neckBend": AnimControl(
            ctrl_name_tag="neckBend",
            prelim_ctrl_name="neckBend",
            side=side,
            module_ctrl = module_ctrl
        ),


        "head": AnimControl(
            ctrl_name_tag="head",
            prelim_ctrl_name="head",
            side=side,
            module_ctrl = module_ctrl
        ),


        "settings": AnimControl(
            ctrl_name_tag = "neck_settings",
            prelim_ctrl_name = "neck_settings",
            side = side,
            module_ctrl = module_ctrl
        ),

    }

    return anim_ctrls
