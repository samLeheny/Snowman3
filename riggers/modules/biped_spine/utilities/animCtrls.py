# Title: animCtrls.py
# Author: Sam Leheny
# Contact: samleheny@live.com

# Description:


###########################
##### Import Commands #####
import Snowman.riggers.utilities.classes.class_AnimControl as class_AnimControl
reload(class_AnimControl)
###########################
###########################


###########################
######## Variables ########
AnimControl = class_AnimControl.AnimControl
###########################
###########################





def create_anim_ctrls(side=None, module_ctrl=None):

    anim_ctrls = {


        "ik_pelvis": AnimControl(
            ctrl_name_tag="ik_pelvis",
            prelim_ctrl_name="ik_pelvis",
            side=side,
            module_ctrl = module_ctrl
        ),


        "ik_waist": AnimControl(
            ctrl_name_tag="ik_waist",
            prelim_ctrl_name="ik_waist",
            side=side,
            module_ctrl = module_ctrl
        ),


        "ik_chest": AnimControl(
            ctrl_name_tag="ik_chest",
            prelim_ctrl_name="ik_chest",
            side=side,
            module_ctrl = module_ctrl
        ),


        "fk_spine_1": AnimControl(
            ctrl_name_tag="fk_spine_1",
            prelim_ctrl_name="fk_spine_1",
            side=side,
            module_ctrl = module_ctrl
        ),


        "fk_spine_2": AnimControl(
            ctrl_name_tag="fk_spine_2",
            prelim_ctrl_name="fk_spine_2",
            side=side,
            module_ctrl = module_ctrl
        ),


        "fk_spine_3": AnimControl(
            ctrl_name_tag="fk_spine_3",
            prelim_ctrl_name="fk_spine_3",
            side=side,
            module_ctrl = module_ctrl
        ),


        "fk_hips": AnimControl(
            ctrl_name_tag="fk_hips",
            prelim_ctrl_name="fk_hips",
            side=side,
            module_ctrl = module_ctrl
        ),


        "spine_tweak_1": AnimControl(
            ctrl_name_tag="spine_tweak_1",
            prelim_ctrl_name="spine_tweak_1",
            side=side,
            module_ctrl = module_ctrl
        ),


        "spine_tweak_2": AnimControl(
            ctrl_name_tag="spine_tweak_2",
            prelim_ctrl_name="spine_tweak_2",
            side=side,
            module_ctrl = module_ctrl
        ),


        "spine_tweak_3": AnimControl(
            ctrl_name_tag="spine_tweak_3",
            prelim_ctrl_name="spine_tweak_3",
            side=side,
            module_ctrl = module_ctrl
        ),


        "spine_tweak_4": AnimControl(
            ctrl_name_tag="spine_tweak_4",
            prelim_ctrl_name="spine_tweak_4",
            side=side,
            module_ctrl = module_ctrl
        ),


        "spine_tweak_5": AnimControl(
            ctrl_name_tag="spine_tweak_5",
            prelim_ctrl_name="spine_tweak_5",
            side=side,
            module_ctrl = module_ctrl
        ),


        "spine_tweak_6": AnimControl(
            ctrl_name_tag="spine_tweak_6",
            prelim_ctrl_name="spine_tweak_6",
            side=side,
            module_ctrl = module_ctrl
        ),


        "spine_tweak_7": AnimControl(
            ctrl_name_tag="spine_tweak_7",
            prelim_ctrl_name="spine_tweak_7",
            side=side,
            module_ctrl = module_ctrl
        ),

        "settings": AnimControl(
            ctrl_name_tag = "spine_settings",
            prelim_ctrl_name = "spine_settings",
            side = side,
            module_ctrl = module_ctrl
        ),

    }

    return anim_ctrls
