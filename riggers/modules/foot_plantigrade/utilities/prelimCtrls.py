# Title: prelimCtrls.py
# Author: Sam Leheny
# Contact: samleheny@live.com

# Description:


###########################
##### Import Commands #####
import importlib

import Snowman3.riggers.utilities.classes.class_PrelimControl as class_PrelimControl
importlib.reload(class_PrelimControl)

import Snowman3.dictionaries.nurbsCurvePrefabs as nurbsCurvePrefabs
importlib.reload(nurbsCurvePrefabs)
curve_prefabs = nurbsCurvePrefabs.create_dict()

import Snowman3.dictionaries.nameConventions as nameConventions
importlib.reload(nameConventions)
nom = nameConventions.create_dict()

import Snowman3.riggers.dictionaries.control_colors as ctrl_colors_dict
importlib.reload(ctrl_colors_dict)
ctrl_colors = ctrl_colors_dict.create_dict()
###########################
###########################


###########################
######## Variables ########
PrelimControl = class_PrelimControl.PrelimControl
###########################
###########################





def create_prelim_ctrls(side=None, is_driven_side=None, module_ctrl=None):

    prelim_ctrls = {


        "fk_toe": PrelimControl(
            name = "fk_toe",
            shape = "toe",
            size = [8, 8, 6.8],
            shape_offset = [1, 0, 0.4],
            up_direction = [-1, 0, 0],
            forward_direction = [0, 1, 0],
            color = [ctrl_colors[nom.leftSideTag], ctrl_colors[nom.rightSideTag]],
            position = ("ball",),
            orientation = {"match_to": "ball"},
            locks = {"v": 1},
            side = side,
            is_driven_side = is_driven_side,
            match_transform="ball",
            module_ctrl=module_ctrl
        ),

        "ik_toe": PrelimControl(
            name="ik_toe",
            shape="toe",
            size=[8, 8, 6.8],
            shape_offset=[1, 0, 0.4],
            up_direction=[-1, 0, 0],
            forward_direction=[0, 1, 0],
            color=[ctrl_colors[nom.leftSideTag], ctrl_colors[nom.rightSideTag]],
            position=("ball",),
            orientation={"match_to": "ball"},
            locks={"v": 1},
            side=side,
            is_driven_side=is_driven_side,
            match_transform="ball",
            module_ctrl=module_ctrl
        ),


    }

    return prelim_ctrls
