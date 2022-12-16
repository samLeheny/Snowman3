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


        "fk_thigh": AnimControl(
            ctrl_name_tag="fk_thigh",
            prelim_ctrl_name = "fk_thigh",
            side = side,
            match_transform = "thigh",
            module_ctrl = module_ctrl
        ),


        "fk_calf": AnimControl(
            ctrl_name_tag="fk_calf",
            prelim_ctrl_name="fk_calf",
            side=side,
            match_transform = "calf",
            module_ctrl = module_ctrl
        ),


        "fk_foot": AnimControl(
            ctrl_name_tag="fk_foot",
            prelim_ctrl_name="fk_foot",
            side=side,
            match_transform = "calf_end",
            module_ctrl = module_ctrl
        ),


        "ik_foot": AnimControl(
            ctrl_name_tag="ik_foot",
            prelim_ctrl_name="ik_foot",
            side=side,
            module_ctrl = module_ctrl
        ),


        "ik_foot_rot": AnimControl(
            ctrl_name_tag="ik_foot_rot",
            prelim_ctrl_name="fk_foot",
            side=side,
            match_transform = "calf_end",
            module_ctrl = module_ctrl
        ),


        "ik_knee": AnimControl(
            ctrl_name_tag="ik_knee",
            prelim_ctrl_name="ik_knee",
            side=side,
            module_ctrl=module_ctrl
        ),


        "knee_pin": AnimControl(
            ctrl_name_tag="knee_pin",
            prelim_ctrl_name="knee_pin",
            side=side,
            module_ctrl = module_ctrl
        ),


        "thigh_bend_start": AnimControl(
            ctrl_name_tag="thigh_bend_start",
            prelim_ctrl_name="thigh_bend_start",
            side=side,
            module_ctrl = module_ctrl
        ),


        "thigh_bend_mid": AnimControl(
            ctrl_name_tag="thigh_bend_mid",
            prelim_ctrl_name="thigh_bend_mid",
            side=side,
            module_ctrl=module_ctrl
        ),


        "calf_bend_mid": AnimControl(
            ctrl_name_tag="calf_bend_mid",
            prelim_ctrl_name="calf_bend_mid",
            side=side,
            module_ctrl = module_ctrl
        ),


        "calf_bend_end": AnimControl(
            ctrl_name_tag="calf_bend_end",
            prelim_ctrl_name="calf_bend_end",
            side=side,
            module_ctrl = module_ctrl
        ),


        "hip_pin": AnimControl(
            ctrl_name_tag="hip_pin",
            prelim_ctrl_name="hip_pin",
            side=side,
            match_transform = "thigh",
            module_ctrl = module_ctrl
        ),


        "ik_foot_follow": AnimControl(
            ctrl_name_tag="ik_foot_follow",
            prelim_ctrl_name="ik_foot_follow",
            side=side,
            match_transform="center to prelim",
            module_ctrl=module_ctrl
        ),

    }

    return anim_ctrls