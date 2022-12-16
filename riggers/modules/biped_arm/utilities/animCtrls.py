# Title: armAnimControls.py
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


        "fk_upperarm": AnimControl(
            ctrl_name_tag="fk_upperarm",
            prelim_ctrl_name = "fk_upperarm",
            side = side,
            match_transform = "upperarm",
            module_ctrl = module_ctrl
        ),


        "fk_lowerarm": AnimControl(
            ctrl_name_tag="fk_lowerarm",
            prelim_ctrl_name="fk_lowerarm",
            side=side,
            match_transform = "lowerarm",
            module_ctrl = module_ctrl
        ),


        "fk_hand": AnimControl(
            ctrl_name_tag="fk_hand",
            prelim_ctrl_name="fk_hand",
            side=side,
            match_transform = "lowerarm_end",
            module_ctrl = module_ctrl
        ),


        "ik_hand": AnimControl(
            ctrl_name_tag="ik_hand",
            prelim_ctrl_name="ik_hand",
            side=side,
            module_ctrl = module_ctrl
        ),


        "ik_hand_rot": AnimControl(
            ctrl_name_tag = "ik_hand_rot",
            prelim_ctrl_name = "fk_hand",
            side = side,
            match_transform = "lowerarm_end",
            module_ctrl = module_ctrl
        ),


        "ik_elbow": AnimControl(
            ctrl_name_tag="ik_elbow",
            prelim_ctrl_name="ik_elbow",
            side=side,
            module_ctrl=module_ctrl
        ),


        "elbow_pin": AnimControl(
            ctrl_name_tag="elbow_pin",
            prelim_ctrl_name="elbow_pin",
            side=side,
            module_ctrl = module_ctrl
        ),


        "upperarm_bend_start": AnimControl(
            ctrl_name_tag="upperarm_bend_start",
            prelim_ctrl_name="upperarm_bend_start",
            side=side,
            module_ctrl = module_ctrl
        ),


        "upperarm_bend_mid": AnimControl(
            ctrl_name_tag="upperarm_bend_mid",
            prelim_ctrl_name="upperarm_bend_mid",
            side=side,
            module_ctrl = module_ctrl
        ),


        "lowerarm_bend_mid": AnimControl(
            ctrl_name_tag="lowerarm_bend_mid",
            prelim_ctrl_name="lowerarm_bend_mid",
            side=side,
            module_ctrl = module_ctrl
        ),


        "lowerarm_bend_end": AnimControl(
            ctrl_name_tag="lowerarm_bend_end",
            prelim_ctrl_name="lowerarm_bend_end",
            side=side,
            module_ctrl = module_ctrl
        ),


        "shoulder_pin": AnimControl(
            ctrl_name_tag="shoulder_pin",
            prelim_ctrl_name="shoulder_pin",
            side=side,
            match_transform = "upperarm",
            module_ctrl = module_ctrl
        ),


        "ik_hand_follow": AnimControl(
            ctrl_name_tag="ik_hand_follow",
            prelim_ctrl_name="ik_hand_follow",
            side=side,
            match_transform="center to prelim",
            module_ctrl=module_ctrl
        ),

    }

    return anim_ctrls