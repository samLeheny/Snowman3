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


        "fk_upperarm": ControlData(
            name = "fk_upperarm",
            shape = "body_section_tube",
            size = [25, 6.5, 6.5],
            shape_offset = [0, 0, 0],
            up_direction = [1, 0, 0],
            forward_direction = [0, 0, 1],
            color = [ctrl_colors[nom.leftSideTag], ctrl_colors[nom.rightSideTag]],
            position = ("upperarm", "lowerarm"),
            orientation = {"match_to": "upperarm"},
            locks = {"v": 1},
            side = side,
            match_transform = "upperarm"
        ),


        "fk_lowerarm": ControlData(
            name="fk_lowerarm",
            shape="body_section_tube",
            size=[25, 6.5, 6.5],
            shape_offset=[0, 0, 0],
            up_direction=[1, 0, 0],
            forward_direction=[0, 0, 1],
            color=[ctrl_colors[nom.leftSideTag], ctrl_colors[nom.rightSideTag]],
            position=("lowerarm", "lowerarm_end"),
            orientation={"match_to": "lowerarm"},
            locks={"v": 1},
            side=side,
            match_transform = "lowerarm"
        ),


        "fk_hand": ControlData(
            name="fk_hand",
            shape="body_section_tube",
            size=[6.5, 4, 8],
            shape_offset=[4, 0, 0],
            up_direction=[1, 0, 0],
            forward_direction=[0, 0, 1],
            color=[ctrl_colors[nom.leftSideTag], ctrl_colors[nom.rightSideTag]],
            position=("lowerarm_end",),
            orientation={"match_to": "lowerarm_end"},
            locks={"v": 1},
            side=side,
            match_transform = "lowerarm_end"
        ),


        "ik_hand": ControlData(
            name="ik_hand",
            shape="cylinder",
            size=[0.7, 7, 7],
            up_direction=[1, 0, 0],
            color=[ctrl_colors[nom.leftSideTag], ctrl_colors[nom.rightSideTag]],
            position=("lowerarm_end",),
            orientation={"match_to": "lowerarm_end"},
            locks={"v":1},
            side=side,
        ),


        "ik_elbow": ControlData(
            name="ik_elbow",
            shape="sphere",
            size=[2, 2, 2],
            color=[ctrl_colors[nom.leftSideTag], ctrl_colors[nom.rightSideTag]],
            position=("ik_elbow",),
            orientation={"match_to": "module_ctrl"},
            locks={"r":[1, 1, 1], "s":[1, 1, 1], "v":1},
            side=side,
        ),


        "shoulder_pin": ControlData(
            name="shoulder_pin",
            shape="tag_hexagon",
            size=[6, 6, 6],
            shape_offset=[0, 0, 0],
            up_direction=[0, 1, 0],
            forward_direction=[0, 0, 1],
            color=[ctrl_colors[nom.leftSideTag2], ctrl_colors[nom.rightSideTag2]],
            position=("upperarm",),
            orientation = {"match_to": "module_ctrl"},
            locks={"r": [1, 1, 1], "s": [1, 1, 1], "v": 1},
            side=side,
            match_transform = "upperarm"
        ),

        'ik_hand_follow': ControlData(
            name='ik_hand_follow',
            shape='tetrahedron',
            size=[1.5, 1.5, 1.5],
            shape_offset=[6, 10, 0],
            color=[ctrl_colors[nom.leftSideTag2], ctrl_colors[nom.rightSideTag2]],
            position=('upperarm',),
            orientation={'match_to': 'module_ctrl'},
            locks={'v': 1},
            side=side,
            match_transform='center to prelim'
        ),

    }

    return ctrl_data
