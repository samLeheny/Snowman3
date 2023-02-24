# Title: prelimCtrls.py
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





def create_ctrl_data(side=None):

    ctrl_data = {


        "index_meta": ControlData(
            name = "index_meta",
            shape = "cube",
            size = [0.4, 0.4, 0.4],
            shape_offset = [0, 0, 0],
            color = [ctrl_colors[nom.leftSideTag], ctrl_colors[nom.rightSideTag]],
            position = ("index_metacarpal", "index_1"),
            orientation = {"match_to": "index_metacarpal"},
            locks = {"v": 1},
            side = side,
            match_transform="index_metacarpal"
        ),


        "index_1": ControlData(
            name="index_1",
            shape="cube",
            size=[1.2, 0.6, 0.6],
            shape_offset=[0, 0, 0],
            color=[ctrl_colors[nom.leftSideTag], ctrl_colors[nom.rightSideTag]],
            position=("index_1", "index_2"),
            orientation={"match_to": "index_1"},
            locks={"v": 1},
            side=side,
            match_transform="index_1"
        ),


        "index_2": ControlData(
            name="index_2",
            shape="cube",
            size=[1.2, 0.6, 0.6],
            shape_offset=[0, 0, 0],
            color=[ctrl_colors[nom.leftSideTag], ctrl_colors[nom.rightSideTag]],
            position=("index_2", "index_3"),
            orientation={"match_to": "index_2"},
            locks={"v": 1},
            side=side,
            match_transform="index_2"
        ),


        "index_3": ControlData(
            name="index_3",
            shape="cube",
            size=[1.2, 0.6, 0.6],
            shape_offset=[0, 0, 0],
            color=[ctrl_colors[nom.leftSideTag], ctrl_colors[nom.rightSideTag]],
            position=("index_3", "index_end"),
            orientation={"match_to": "index_3"},
            locks={"v": 1},
            side=side,
            match_transform="index_3"
        ),


        "middle_meta": ControlData(
            name = "middle_meta",
            shape = "cube",
            size = [0.4, 0.4, 0.4],
            shape_offset = [0, 0, 0],
            color = [ctrl_colors[nom.leftSideTag], ctrl_colors[nom.rightSideTag]],
            position = ("middle_metacarpal", "middle_1"),
            orientation = {"match_to": "middle_metacarpal"},
            locks = {"v": 1},
            side = side,
            match_transform="middle_metacarpal"
        ),


        "middle_1": ControlData(
            name="middle_1",
            shape="cube",
            size=[1.2, 0.6, 0.6],
            shape_offset=[0, 0, 0],
            color=[ctrl_colors[nom.leftSideTag], ctrl_colors[nom.rightSideTag]],
            position=("middle_1", "middle_2"),
            orientation={"match_to": "middle_1"},
            locks={"v": 1},
            side=side,
            match_transform="middle_1"
        ),


        "middle_2": ControlData(
            name="middle_2",
            shape="cube",
            size=[1.2, 0.6, 0.6],
            shape_offset=[0, 0, 0],
            color=[ctrl_colors[nom.leftSideTag], ctrl_colors[nom.rightSideTag]],
            position=("middle_2", "middle_3"),
            orientation={"match_to": "middle_2"},
            locks={"v": 1},
            side=side,
            match_transform="middle_2"
        ),


        "middle_3": ControlData(
            name="middle_3",
            shape="cube",
            size=[1.2, 0.6, 0.6],
            shape_offset=[0, 0, 0],
            color=[ctrl_colors[nom.leftSideTag], ctrl_colors[nom.rightSideTag]],
            position=("middle_3", "middle_end"),
            orientation={"match_to": "middle_3"},
            locks={"v": 1},
            side=side,
            match_transform="middle_3"
        ),


        "ring_meta": ControlData(
            name = "ring_meta",
            shape = "cube",
            size = [0.4, 0.4, 0.4],
            shape_offset = [0, 0, 0],
            color = [ctrl_colors[nom.leftSideTag], ctrl_colors[nom.rightSideTag]],
            position = ("ring_metacarpal", "ring_1"),
            orientation = {"match_to": "ring_metacarpal"},
            locks = {"v": 1},
            side = side,
            match_transform="ring_metacarpal"
        ),


        "ring_1": ControlData(
            name="ring_1",
            shape="cube",
            size=[1.2, 0.6, 0.6],
            shape_offset=[0, 0, 0],
            color=[ctrl_colors[nom.leftSideTag], ctrl_colors[nom.rightSideTag]],
            position=("ring_1", "ring_2"),
            orientation={"match_to": "ring_1"},
            locks={"v": 1},
            side=side,
            match_transform="ring_1"
        ),


        "ring_2": ControlData(
            name="ring_2",
            shape="cube",
            size=[1.2, 0.6, 0.6],
            shape_offset=[0, 0, 0],
            color=[ctrl_colors[nom.leftSideTag], ctrl_colors[nom.rightSideTag]],
            position=("ring_2", "ring_3"),
            orientation={"match_to": "ring_2"},
            locks={"v": 1},
            side=side,
            match_transform="ring_2"
        ),


        "ring_3": ControlData(
            name="ring_3",
            shape="cube",
            size=[1.2, 0.6, 0.6],
            shape_offset=[0, 0, 0],
            color=[ctrl_colors[nom.leftSideTag], ctrl_colors[nom.rightSideTag]],
            position=("ring_3", "ring_end"),
            orientation={"match_to": "ring_3"},
            locks={"v": 1},
            side=side,
            match_transform="ring_3"
        ),


        "pinky_meta": ControlData(
            name = "pinky_meta",
            shape = "cube",
            size = [0.4, 0.4, 0.4],
            color = [ctrl_colors[nom.leftSideTag], ctrl_colors[nom.rightSideTag]],
            position = ("pinky_metacarpal", "pinky_1"),
            orientation = {"match_to": "pinky_metacarpal"},
            locks = {"v": 1},
            side = side,
            match_transform="pinky_metacarpal"
        ),


        "pinky_1": ControlData(
            name="pinky_1",
            shape="cube",
            size=[1.2, 0.6, 0.6],
            shape_offset=[0, 0, 0],
            color=[ctrl_colors[nom.leftSideTag], ctrl_colors[nom.rightSideTag]],
            position=("pinky_1", "pinky_2"),
            orientation={"match_to": "pinky_1"},
            locks={"v": 1},
            side=side,
            match_transform="pinky_1"
        ),


        "pinky_2": ControlData(
            name="pinky_2",
            shape="cube",
            size=[1.2, 0.6, 0.6],
            shape_offset=[0, 0, 0],
            color=[ctrl_colors[nom.leftSideTag], ctrl_colors[nom.rightSideTag]],
            position=("pinky_2", "pinky_3"),
            orientation={"match_to": "pinky_2"},
            locks={"v": 1},
            side=side,
            match_transform="pinky_2"
        ),


        "pinky_3": ControlData(
            name="pinky_3",
            shape="cube",
            size=[1.2, 0.6, 0.6],
            shape_offset=[0, 0, 0],
            color=[ctrl_colors[nom.leftSideTag], ctrl_colors[nom.rightSideTag]],
            position=("pinky_3", "pinky_end"),
            orientation={"match_to": "pinky_3"},
            locks={"v": 1},
            side=side,
            match_transform="pinky_3"
        ),


        "thumb_1": ControlData(
            name="thumb_1",
            shape="cube",
            size=[1.2, 0.6, 0.6],
            shape_offset=[0, 0, 0],
            color=[ctrl_colors[nom.leftSideTag], ctrl_colors[nom.rightSideTag]],
            position=("thumb_1", "thumb_2"),
            orientation={"match_to": "thumb_1"},
            locks={"v": 1},
            side=side,
            match_transform="thumb_1"
        ),


        "thumb_2": ControlData(
            name="thumb_2",
            shape="cube",
            size=[1.2, 0.6, 0.6],
            shape_offset=[0, 0, 0],
            color=[ctrl_colors[nom.leftSideTag], ctrl_colors[nom.rightSideTag]],
            position=("thumb_2", "thumb_3"),
            orientation={"match_to": "thumb_2"},
            locks={"v": 1},
            side=side,
            match_transform="thumb_2"
        ),


        "thumb_3": ControlData(
            name="thumb_3",
            shape="cube",
            size=[1.2, 0.6, 0.6],
            shape_offset=[0, 0, 0],
            color=[ctrl_colors[nom.leftSideTag], ctrl_colors[nom.rightSideTag]],
            position=("thumb_3", "thumb_end"),
            orientation={"match_to": "thumb_3"},
            locks={"v": 1},
            side=side,
            match_transform="thumb_3"
        ),


        "quickPose_fingers": ControlData(
            name="quickPose_fingers",
            shape="smooth_tetrahedron",
            size=[1, 1, 1],
            shape_offset=[0, 3, 0],
            color=[ctrl_colors[nom.leftSideTag2], ctrl_colors[nom.rightSideTag2]],
            position=("index_metacarpal", "pinky_1"),
            orientation={"match_to": "hand"},
            locks={"v": 1, "t": [1, 1, 0], "r": [0, 1, 0], "s": [1, 1, 0]},
            side=side,
            match_transform="center to prelim"
        ),


        "handBend": ControlData(
            name="handBend",
            shape="hand_bend",
            size=[1, 1, 1],
            shape_offset=[0, 0, 0],
            forward_direction=[0, -1, 0],
            up_direction=[0, 0, 1],
            color=[ctrl_colors[nom.leftSideTag], ctrl_colors[nom.rightSideTag]],
            position=("pinky_metacarpal", "pinky_1"),
            orientation={"match_to": "pinky_metacarpal"},
            locks={"v": 1, "t": [1, 1, 1], "s": [1, 1, 1]},
            side=side,
            match_transform="pinky_metacarpal"
        ),

    }

    return ctrl_data
