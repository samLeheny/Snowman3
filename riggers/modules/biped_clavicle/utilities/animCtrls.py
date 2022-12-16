# Title: clavicleControls.py
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


        "clavicle": AnimControl(
            ctrl_name_tag="clavicle",
            prelim_ctrl_name = "clavicle",
            side = side,
            match_transform = "module_ctrl",
            module_ctrl = module_ctrl,
        ),

    }

    return anim_ctrls