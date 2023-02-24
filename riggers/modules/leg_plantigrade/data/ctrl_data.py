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





def create_ctrl_data(side=None):

    ctrl_data = {


        "fk_thigh": ControlData(
            name = "fk_thigh",
            shape = "body_section_tube",
            size = [42, 10, 10],
            shape_offset = [0, 0, 0],
            up_direction = [1, 0, 0],
            forward_direction = [0, 0, 1],
            color = [ctrl_colors[nom.leftSideTag], ctrl_colors[nom.rightSideTag]],
            position = ("thigh", "calf"),
            orientation = {"match_to": "thigh"},
            locks = {"v": 1},
            side = side,
            match_transform = "thigh"
        ),


        "fk_calf": ControlData(
            name="fk_calf",
            shape="body_section_tube",
            size=[42, 10, 10],
            shape_offset=[0, 0, 0],
            up_direction=[1, 0, 0],
            forward_direction=[0, 0, 1],
            color=[ctrl_colors[nom.leftSideTag], ctrl_colors[nom.rightSideTag]],
            position=("calf", "calf_end"),
            orientation={"match_to": "calf"},
            locks={"v": 1},
            side=side,
            match_transform = "calf"
        ),


        "fk_foot": ControlData(
            name="fk_foot",
            shape="biped_foot",
            size=[6.4, 8, 7],
            shape_offset=[4, 0, -3],
            up_direction=[-1, 0, 0],
            forward_direction=[0, 0, -1],
            color=[ctrl_colors[nom.leftSideTag], ctrl_colors[nom.rightSideTag]],
            position=("calf_end",),
            orientation={"match_to": "calf_end"},
            locks={"v": 1},
            side=side,
            match_transform = "calf_end"
        ),


        "ik_foot": ControlData(
            name="ik_foot",
            shape="tablet",
            size=[0.7, 12, 12],
            up_direction=[-1, 0, 0],
            forward_direction=[0, 0, -1],
            shape_offset=[9.65, 0, -6],
            color=[ctrl_colors[nom.leftSideTag], ctrl_colors[nom.rightSideTag]],
            position=("calf_end",),
            orientation={"match_to": "calf_end"},
            locks={"v":1},
            side=side,
        ),


        "ik_knee": ControlData(
            name="ik_knee",
            shape="sphere",
            size=[2, 2, 2],
            color=[ctrl_colors[nom.leftSideTag], ctrl_colors[nom.rightSideTag]],
            position=("ik_knee",),
            orientation={"match_to": "module_ctrl"},
            locks={"r":[1, 1, 1], "s":[1, 1, 1], "v":1},
            side=side
        ),


        "ik_foot_follow": ControlData(
            name="ik_foot_follow",
            shape="tetrahedron",
            size=[2, 2, 2],
            shape_offset=[10, 6, 0],
            color=[ctrl_colors[nom.leftSideTag2], ctrl_colors[nom.rightSideTag2]],
            position=("thigh",),
            orientation={"match_to": "module_ctrl"},
            locks={"v": 1},
            side=side,
            match_transform="center to prelim"
        ),


        "hip_pin": ControlData(
            name="hip_pin",
            shape="tag_hexagon",
            size=[6, 6, 6],
            shape_offset=[0, 0, 0],
            up_direction=[1, 0, 0],
            forward_direction=[0, 0, -1],
            color=[ctrl_colors[nom.leftSideTag2], ctrl_colors[nom.rightSideTag2]],
            position=("thigh",),
            orientation = {"match_to": "module_ctrl"},
            locks={"r": [1, 1, 1], "s": [1, 1, 1], "v": 1},
            side=side,
            match_transform = "thigh"
        ),

    }

    return ctrl_data