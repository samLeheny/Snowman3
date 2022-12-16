# Title: handAnimControls.py
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


        "index_meta": AnimControl(
            ctrl_name_tag="index_meta",
            prelim_ctrl_name="index_meta",
            side=side,
            match_transform="index_metacarpal",
            module_ctrl=module_ctrl
        ),


        "index_1": AnimControl(
            ctrl_name_tag="index_1",
            prelim_ctrl_name="index_1",
            side=side,
            match_transform="index_1",
            module_ctrl=module_ctrl
        ),


        "index_2": AnimControl(
            ctrl_name_tag="index_2",
            prelim_ctrl_name="index_2",
            side=side,
            match_transform="index_2",
            module_ctrl=module_ctrl
        ),


        "index_3": AnimControl(
            ctrl_name_tag="index_3",
            prelim_ctrl_name="index_3",
            side=side,
            match_transform="index_3",
            module_ctrl=module_ctrl
        ),


        "middle_meta": AnimControl(
            ctrl_name_tag="middle_meta",
            prelim_ctrl_name="middle_meta",
            side=side,
            match_transform="middle_metacarpal",
            module_ctrl=module_ctrl
        ),


        "middle_1": AnimControl(
            ctrl_name_tag="middle_1",
            prelim_ctrl_name="middle_1",
            side=side,
            match_transform="middle_1",
            module_ctrl=module_ctrl
        ),


        "middle_2": AnimControl(
            ctrl_name_tag="middle_2",
            prelim_ctrl_name="middle_2",
            side=side,
            match_transform="middle_2",
            module_ctrl=module_ctrl
        ),


        "middle_3": AnimControl(
            ctrl_name_tag="middle_3",
            prelim_ctrl_name="middle_3",
            side=side,
            match_transform="middle_3",
            module_ctrl=module_ctrl
        ),


        "ring_meta": AnimControl(
            ctrl_name_tag="ring_meta",
            prelim_ctrl_name="ring_meta",
            side=side,
            match_transform="ring_metacarpal",
            module_ctrl=module_ctrl
        ),


        "ring_1": AnimControl(
            ctrl_name_tag="ring_1",
            prelim_ctrl_name="ring_1",
            side=side,
            match_transform="ring_1",
            module_ctrl=module_ctrl
        ),


        "ring_2": AnimControl(
            ctrl_name_tag="ring_2",
            prelim_ctrl_name="ring_2",
            side=side,
            match_transform="ring_2",
            module_ctrl=module_ctrl
        ),


        "ring_3": AnimControl(
            ctrl_name_tag="ring_3",
            prelim_ctrl_name="ring_3",
            side=side,
            match_transform="ring_3",
            module_ctrl=module_ctrl
        ),


        "pinky_meta": AnimControl(
            ctrl_name_tag="pinky_meta",
            prelim_ctrl_name="pinky_meta",
            side=side,
            match_transform="pinky_metacarpal",
            module_ctrl=module_ctrl
        ),


        "pinky_1": AnimControl(
            ctrl_name_tag="pinky_1",
            prelim_ctrl_name="pinky_1",
            side=side,
            match_transform="pinky_1",
            module_ctrl=module_ctrl
        ),


        "pinky_2": AnimControl(
            ctrl_name_tag="pinky_2",
            prelim_ctrl_name="pinky_2",
            side=side,
            match_transform="pinky_2",
            module_ctrl=module_ctrl
        ),


        "pinky_3": AnimControl(
            ctrl_name_tag="pinky_3",
            prelim_ctrl_name="pinky_3",
            side=side,
            match_transform="pinky_3",
            module_ctrl=module_ctrl
        ),


        "thumb_1": AnimControl(
            ctrl_name_tag="thumb_1",
            prelim_ctrl_name="thumb_1",
            side=side,
            match_transform="thumb_1",
            module_ctrl=module_ctrl
        ),


        "thumb_2": AnimControl(
            ctrl_name_tag="thumb_2",
            prelim_ctrl_name="thumb_2",
            side=side,
            match_transform="thumb_2",
            module_ctrl=module_ctrl
        ),


        "thumb_3": AnimControl(
            ctrl_name_tag="thumb_3",
            prelim_ctrl_name="thumb_3",
            side=side,
            match_transform="thumb_3",
            module_ctrl=module_ctrl
        ),


        "quickPose_fingers": AnimControl(
            ctrl_name_tag="quickPose_fingers",
            prelim_ctrl_name="quickPose_fingers",
            side=side,
            match_transform="center to prelim",
            module_ctrl=module_ctrl
        ),


        "handBend": AnimControl(
            ctrl_name_tag="handBend",
            prelim_ctrl_name="handBend",
            side=side,
            match_transform="pinky_metacarpal",
            module_ctrl=module_ctrl
        ),

    }

    return anim_ctrls