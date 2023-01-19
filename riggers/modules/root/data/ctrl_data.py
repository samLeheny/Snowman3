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

import Snowman3.dictionaries.nurbsCurvePrefabs as nurbs_curve_prefabs
importlib.reload(nurbs_curve_prefabs)
curve_prefabs = nurbs_curve_prefabs.create_dict()

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



def create_ctrl_data(side=None, is_driven_side=None):

    ctrl_data = {
        'root': ControlData(
            name = "root",
            shape = "COG",
            size = [60, 0, 60],
            forward_direction = [0, 0, 1],
            up_direction = [0, 1, 0],
            color = ctrl_colors["root"],
            position = ("root",),
            locks = {"s": [1, 1, 1], "v": 1},
        ),


        'subRoot': ControlData(
            name = "subRoot",
            shape = "circle",
            size = [50, 0, 50],
            forward_direction = [0, 0, 1],
            up_direction = [0, 1, 0],
            color = ctrl_colors["root"],
            position = ("root",),
            locks = {"s": [1, 1, 1], "v": 1},
        ),


        "COG": ControlData(
            name = "COG",
            shape = "COG",
            size = [20, 20, 20],
            color = ctrl_colors[nom.majorSideTag],
            position = ("COG",),
            orientation = {"aim_vector": ("y", (0, 1, 0)),
                           "up_vector": ("z", (0, 0, 1))},
            locks = {"v": 1},
        )
    }

    return ctrl_data
