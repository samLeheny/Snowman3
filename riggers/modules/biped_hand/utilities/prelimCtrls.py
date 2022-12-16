# Title: prelimCtrls.py
# Title: prelimCtrls.py
# Author: Sam Leheny
# Contact: samleheny@live.com

# Description:


###########################
##### Import Commands #####
import Snowman.riggers.utilities.classes.class_PrelimControl as class_PrelimControl
reload(class_PrelimControl)

import Snowman.dictionaries.nurbsCurvePrefabs as nurbsCurvePrefabs
reload(nurbsCurvePrefabs)
curve_prefabs = nurbsCurvePrefabs.create_dict()

import Snowman.dictionaries.nameConventions as nameConventions
reload(nameConventions)
nom = nameConventions.create_dict()

import Snowman.riggers.dictionaries.control_colors as ctrl_colors_dict
reload(ctrl_colors_dict)
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


        "index_meta": PrelimControl(
            name = "index_meta",
            shape = "cube",
            size = [0.4, 0.4, 0.4],
            shape_offset = [0, 0, 0],
            color = [ctrl_colors[nom.leftSideTag], ctrl_colors[nom.rightSideTag]],
            position = ("index_metacarpal", "index_1"),
            orientation = {"match_to": "index_metacarpal"},
            locks = {"v": 1},
            side = side,
            is_driven_side = is_driven_side,
            vis_category = "fk limbs"
        ),


        "index_1": PrelimControl(
            name="index_1",
            shape="cube",
            size=[1.2, 0.6, 0.6],
            shape_offset=[0, 0, 0],
            color=[ctrl_colors[nom.leftSideTag], ctrl_colors[nom.rightSideTag]],
            position=("index_1", "index_2"),
            orientation={"match_to": "index_1"},
            locks={"v": 1},
            side=side,
            is_driven_side=is_driven_side,
            vis_category="fk limbs"
        ),


        "index_2": PrelimControl(
            name="index_2",
            shape="cube",
            size=[1.2, 0.6, 0.6],
            shape_offset=[0, 0, 0],
            color=[ctrl_colors[nom.leftSideTag], ctrl_colors[nom.rightSideTag]],
            position=("index_2", "index_3"),
            orientation={"match_to": "index_2"},
            locks={"v": 1},
            side=side,
            is_driven_side=is_driven_side,
            vis_category="fk limbs"
        ),


        "index_3": PrelimControl(
            name="index_3",
            shape="cube",
            size=[1.2, 0.6, 0.6],
            shape_offset=[0, 0, 0],
            color=[ctrl_colors[nom.leftSideTag], ctrl_colors[nom.rightSideTag]],
            position=("index_3", "index_end"),
            orientation={"match_to": "index_3"},
            locks={"v": 1},
            side=side,
            is_driven_side=is_driven_side,
            vis_category="fk limbs"
        ),


        "middle_meta": PrelimControl(
            name = "middle_meta",
            shape = "cube",
            size = [0.4, 0.4, 0.4],
            shape_offset = [0, 0, 0],
            color = [ctrl_colors[nom.leftSideTag], ctrl_colors[nom.rightSideTag]],
            position = ("middle_metacarpal", "middle_1"),
            orientation = {"match_to": "middle_metacarpal"},
            locks = {"v": 1},
            side = side,
            is_driven_side = is_driven_side,
            vis_category = "fk limbs"
        ),


        "middle_1": PrelimControl(
            name="middle_1",
            shape="cube",
            size=[1.2, 0.6, 0.6],
            shape_offset=[0, 0, 0],
            color=[ctrl_colors[nom.leftSideTag], ctrl_colors[nom.rightSideTag]],
            position=("middle_1", "middle_2"),
            orientation={"match_to": "middle_1"},
            locks={"v": 1},
            side=side,
            is_driven_side=is_driven_side,
            vis_category="fk limbs"
        ),


        "middle_2": PrelimControl(
            name="middle_2",
            shape="cube",
            size=[1.2, 0.6, 0.6],
            shape_offset=[0, 0, 0],
            color=[ctrl_colors[nom.leftSideTag], ctrl_colors[nom.rightSideTag]],
            position=("middle_2", "middle_3"),
            orientation={"match_to": "middle_2"},
            locks={"v": 1},
            side=side,
            is_driven_side=is_driven_side,
            vis_category="fk limbs"
        ),


        "middle_3": PrelimControl(
            name="middle_3",
            shape="cube",
            size=[1.2, 0.6, 0.6],
            shape_offset=[0, 0, 0],
            color=[ctrl_colors[nom.leftSideTag], ctrl_colors[nom.rightSideTag]],
            position=("middle_3", "middle_end"),
            orientation={"match_to": "middle_3"},
            locks={"v": 1},
            side=side,
            is_driven_side=is_driven_side,
            vis_category="fk limbs"
        ),


        "ring_meta": PrelimControl(
            name = "ring_meta",
            shape = "cube",
            size = [0.4, 0.4, 0.4],
            shape_offset = [0, 0, 0],
            color = [ctrl_colors[nom.leftSideTag], ctrl_colors[nom.rightSideTag]],
            position = ("ring_metacarpal", "ring_1"),
            orientation = {"match_to": "ring_metacarpal"},
            locks = {"v": 1},
            side = side,
            is_driven_side = is_driven_side,
            vis_category = "fk limbs"
        ),


        "ring_1": PrelimControl(
            name="ring_1",
            shape="cube",
            size=[1.2, 0.6, 0.6],
            shape_offset=[0, 0, 0],
            color=[ctrl_colors[nom.leftSideTag], ctrl_colors[nom.rightSideTag]],
            position=("ring_1", "ring_2"),
            orientation={"match_to": "ring_1"},
            locks={"v": 1},
            side=side,
            is_driven_side=is_driven_side,
            vis_category="fk limbs"
        ),


        "ring_2": PrelimControl(
            name="ring_2",
            shape="cube",
            size=[1.2, 0.6, 0.6],
            shape_offset=[0, 0, 0],
            color=[ctrl_colors[nom.leftSideTag], ctrl_colors[nom.rightSideTag]],
            position=("ring_2", "ring_3"),
            orientation={"match_to": "ring_2"},
            locks={"v": 1},
            side=side,
            is_driven_side=is_driven_side,
            vis_category="fk limbs"
        ),


        "ring_3": PrelimControl(
            name="ring_3",
            shape="cube",
            size=[1.2, 0.6, 0.6],
            shape_offset=[0, 0, 0],
            color=[ctrl_colors[nom.leftSideTag], ctrl_colors[nom.rightSideTag]],
            position=("ring_3", "ring_end"),
            orientation={"match_to": "ring_3"},
            locks={"v": 1},
            side=side,
            is_driven_side=is_driven_side,
            vis_category="fk limbs"
        ),


        "pinky_meta": PrelimControl(
            name = "pinky_meta",
            shape = "cube",
            size = [0.4, 0.4, 0.4],
            color = [ctrl_colors[nom.leftSideTag], ctrl_colors[nom.rightSideTag]],
            position = ("pinky_metacarpal", "pinky_1"),
            orientation = {"match_to": "pinky_metacarpal"},
            locks = {"v": 1},
            side = side,
            is_driven_side = is_driven_side,
            vis_category = "fk limbs"
        ),


        "pinky_1": PrelimControl(
            name="pinky_1",
            shape="cube",
            size=[1.2, 0.6, 0.6],
            shape_offset=[0, 0, 0],
            color=[ctrl_colors[nom.leftSideTag], ctrl_colors[nom.rightSideTag]],
            position=("pinky_1", "pinky_2"),
            orientation={"match_to": "pinky_1"},
            locks={"v": 1},
            side=side,
            is_driven_side=is_driven_side,
            vis_category="fk limbs"
        ),


        "pinky_2": PrelimControl(
            name="pinky_2",
            shape="cube",
            size=[1.2, 0.6, 0.6],
            shape_offset=[0, 0, 0],
            color=[ctrl_colors[nom.leftSideTag], ctrl_colors[nom.rightSideTag]],
            position=("pinky_2", "pinky_3"),
            orientation={"match_to": "pinky_2"},
            locks={"v": 1},
            side=side,
            is_driven_side=is_driven_side,
            vis_category="fk limbs"
        ),


        "pinky_3": PrelimControl(
            name="pinky_3",
            shape="cube",
            size=[1.2, 0.6, 0.6],
            shape_offset=[0, 0, 0],
            color=[ctrl_colors[nom.leftSideTag], ctrl_colors[nom.rightSideTag]],
            position=("pinky_3", "pinky_end"),
            orientation={"match_to": "pinky_3"},
            locks={"v": 1},
            side=side,
            is_driven_side=is_driven_side,
            vis_category="fk limbs"
        ),


        "thumb_1": PrelimControl(
            name="thumb_1",
            shape="cube",
            size=[1.2, 0.6, 0.6],
            shape_offset=[0, 0, 0],
            color=[ctrl_colors[nom.leftSideTag], ctrl_colors[nom.rightSideTag]],
            position=("thumb_1", "thumb_2"),
            orientation={"match_to": "thumb_1"},
            locks={"v": 1},
            side=side,
            is_driven_side=is_driven_side,
            vis_category="fk limbs"
        ),


        "thumb_2": PrelimControl(
            name="thumb_2",
            shape="cube",
            size=[1.2, 0.6, 0.6],
            shape_offset=[0, 0, 0],
            color=[ctrl_colors[nom.leftSideTag], ctrl_colors[nom.rightSideTag]],
            position=("thumb_2", "thumb_3"),
            orientation={"match_to": "thumb_2"},
            locks={"v": 1},
            side=side,
            is_driven_side=is_driven_side,
            vis_category="fk limbs"
        ),


        "thumb_3": PrelimControl(
            name="thumb_3",
            shape="cube",
            size=[1.2, 0.6, 0.6],
            shape_offset=[0, 0, 0],
            color=[ctrl_colors[nom.leftSideTag], ctrl_colors[nom.rightSideTag]],
            position=("thumb_3", "thumb_end"),
            orientation={"match_to": "thumb_3"},
            locks={"v": 1},
            side=side,
            is_driven_side=is_driven_side,
            vis_category="fk limbs"
        ),


        "quickPose_fingers": PrelimControl(
            name="quickPose_fingers",
            shape="smooth_tetrahedron",
            size=[1, 1, 1],
            shape_offset=[0, 3, 0],
            color=[ctrl_colors[nom.leftSideTag2], ctrl_colors[nom.rightSideTag2]],
            position=("index_metacarpal", "pinky_1"),
            orientation={"match_to": "hand"},
            locks={"v": 1, "t": [1, 1, 0], "r": [0, 1, 0], "s": [1, 1, 0]},
            side=side,
            is_driven_side=is_driven_side,
            vis_category="fk limbs"
        ),


        "handBend": PrelimControl(
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
            is_driven_side=is_driven_side,
            vis_category="fk limbs"
        ),

    }

    return prelim_ctrls
