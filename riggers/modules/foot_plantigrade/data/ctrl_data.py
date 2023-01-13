# Title: prelimCtrls.py
# Author: Sam Leheny
# Contact: samleheny@live.com

# Description:


###########################
##### Import Commands #####
import importlib

import Snowman3.riggers.utilities.classes.class_ControlData as class_ControlData
importlib.reload(class_ControlData)
ControlData = class_ControlData.ControlData

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

###########################
###########################





def create_ctrl_data(side=None, is_driven_side=None, module_ctrl=None):

    ctrl_data = {


        "fk_toe": ControlData(
            name = "fk_toe",
            shape = "toe",
            size = [8, 8, 6.8],
            shape_offset = [1, 0, 0.4],
            up_direction = [0, 0, -1],
            forward_direction = [1, 0, 0],
            color = [ctrl_colors[nom.leftSideTag], ctrl_colors[nom.rightSideTag]],
            position = ("ball",),
            orientation = {"match_to": "ball"},
            locks = {"v": 1},
            side = side,
            is_driven_side = is_driven_side,
            match_transform="ball",
            module_ctrl=module_ctrl
        ),

        "ik_toe": ControlData(
            name="ik_toe",
            shape="toe",
            size=[8, 8, 6.8],
            shape_offset=[1, 0, 0.4],
            up_direction=[0, 0, -1],
            forward_direction=[1, 0, 0],
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

    return ctrl_data
