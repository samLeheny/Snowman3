# Title: animCtrls.py
# Author: Sam Leheny
# Contact: samleheny@live.com

# Description:


###########################
##### Import Commands #####
import importlib
import Snowman3.riggers.utilities.classes.class_AnimControl as class_AnimControl
importlib.reload(class_AnimControl)

'''import Snowman3.dictionaries.nurbsCurvePrefabs as nurbs_curve_prefabs
reload(nurbs_curve_prefabs)
curve_prefabs = nurbs_curve_prefabs.create_dict()

import Snowman3.dictionaries.nameConventions as nameConventions
reload(nameConventions)
nom = nameConventions.create_dict()

import Snowman3.riggers.dictionaries.control_colors as ctrl_colors_dict
reload(ctrl_colors_dict)
ctrl_colors = ctrl_colors_dict.create_dict()'''
###########################
###########################


###########################
######## Variables ########
AnimControl = class_AnimControl.AnimControl
###########################
###########################





def create_anim_ctrls(side=None, module_ctrl=None):

    anim_ctrls = {


        "root": AnimControl(
            ctrl_name_tag="root",
            prelim_ctrl_name= "root",
        ),


        "subRoot": AnimControl(
            ctrl_name_tag="subRoot",
            prelim_ctrl_name= "subRoot",
        ),


        "cog": AnimControl(
            ctrl_name_tag="cog",
            prelim_ctrl_name="cog",
        ),

    }

    return anim_ctrls
