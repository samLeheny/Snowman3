# Title: prelimCtrls.py
# Author: Sam Leheny
# Contact: samleheny@live.com

# Description:


###########################
##### Import Commands #####
import importlib
import Snowman3.riggers.utilities.classes.class_PrelimControl as class_PrelimControl
importlib.reload(class_PrelimControl)

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
PrelimControl = class_PrelimControl.PrelimControl
###########################
###########################





def create_prelim_ctrls(side=None, is_driven_side=None):

    prelim_ctrls = {


        "fk_upperarm": PrelimControl(
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
            is_driven_side = is_driven_side
        ),


        "fk_lowerarm": PrelimControl(
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
            is_driven_side=is_driven_side
        ),


        "fk_hand": PrelimControl(
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
            is_driven_side=is_driven_side
        ),


        "ik_hand": PrelimControl(
            name="ik_hand",
            shape="cylinder",
            size=[0.7, 7, 7],
            up_direction=[1, 0, 0],
            color=[ctrl_colors[nom.leftSideTag], ctrl_colors[nom.rightSideTag]],
            position=("lowerarm_end",),
            orientation={"match_to": "lowerarm_end"},
            locks={"v":1},
            side=side,
            is_driven_side=is_driven_side
        ),


        "ik_elbow": PrelimControl(
            name="ik_elbow",
            shape="sphere",
            size=[2, 2, 2],
            color=[ctrl_colors[nom.leftSideTag], ctrl_colors[nom.rightSideTag]],
            position=("ik_elbow",),
            orientation={"match_to": "module_ctrl"},
            locks={"r":[1, 1, 1], "s":[1, 1, 1], "v":1},
            side=side,
            is_driven_side=is_driven_side
        ),


        "ik_hand_follow": PrelimControl(
            name="ik_hand_follow",
            shape="tetrahedron",
            size=[1.5, 1.5, 1.5],
            shape_offset=[15, 10, 3],
            color=[ctrl_colors[nom.leftSideTag2], ctrl_colors[nom.rightSideTag2]],
            position=("upperarm",),
            orientation={"match_to": "module_ctrl"},
            locks={"v": 1},
            side=side,
            is_driven_side=is_driven_side
        ),


        "shoulder_pin": PrelimControl(
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
            is_driven_side=is_driven_side
        ),


        "elbow_pin": PrelimControl(
            name="elbow_pin",
            shape="circle",
            size=[5, 5, 5],
            up_direction=[1, 0, 0],
            color=[ctrl_colors[nom.leftSideTag2], ctrl_colors[nom.rightSideTag2]],
            position=("lowerarm",),
            orientation={"match_to": ("lowerarm",)},
            locks={"v": 1},
            side=side,
            is_driven_side=is_driven_side
        ),


        "upperarm_bend_start": PrelimControl(
            name="upperarm_bend_start",
            shape="circle",
            size=[5, 5, 5],
            up_direction=[1, 0, 0],
            color=[ctrl_colors[nom.leftSideTag2], ctrl_colors[nom.rightSideTag2]],
            position=("upperarm",),
            orientation={"match_to": ("upperarm",)},
            locks={"v": 1},
            side=side,
            is_driven_side=is_driven_side
        ),


        "upperarm_bend_mid": PrelimControl(
            name="upperarm_bend_mid",
            shape="circle",
            size=[5, 5, 5],
            up_direction=[1, 0, 0],
            color=[ctrl_colors[nom.leftSideTag2], ctrl_colors[nom.rightSideTag2]],
            position=("upperarm", "lowerarm"),
            orientation={"match_to": ("upperarm",)},
            locks={"v": 1},
            side=side,
            is_driven_side=is_driven_side
        ),


        "lowerarm_bend_mid": PrelimControl(
            name="lowerarm_bend_mid",
            shape="circle",
            size=[5, 5, 5],
            up_direction=[1, 0, 0],
            color=[ctrl_colors[nom.leftSideTag2], ctrl_colors[nom.rightSideTag2]],
            position=("lowerarm", "lowerarm_end"),
            orientation={"match_to": ("lowerarm",)},
            locks={"v": 1},
            side=side,
            is_driven_side=is_driven_side
        ),


        "lowerarm_bend_end": PrelimControl(
            name="lowerarm_bend_end",
            shape="circle",
            size=[5, 5, 5],
            up_direction=[1, 0, 0],
            color=[ctrl_colors[nom.leftSideTag2], ctrl_colors[nom.rightSideTag2]],
            position=("lowerarm_end",),
            orientation={"match_to": ("lowerarm",)},
            locks={"v": 1},
            side=side,
            is_driven_side=is_driven_side
        ),

    }

    return prelim_ctrls