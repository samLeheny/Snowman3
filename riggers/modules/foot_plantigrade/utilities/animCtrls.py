# Title: footAnimControls.py
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


        "fk_toe": AnimControl(
            ctrl_name_tag="fk_toe",
            prelim_ctrl_name="fk_toe",
            side=side,
            match_transform="ball",
            module_ctrl=module_ctrl
        ),


        "ik_toe": AnimControl(
            ctrl_name_tag="ik_toe",
            prelim_ctrl_name="ik_toe",
            side=side,
            match_transform="ball",
            module_ctrl=module_ctrl
        ),


    }

    return anim_ctrls
