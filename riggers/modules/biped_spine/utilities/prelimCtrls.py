# Title: spineControls.py
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



        "ik_chest": PrelimControl(
            name = "ik_chest",
            shape = "circle",
            size = [14, 14, 14],
            shape_offset = [0, -3, 0],
            color = ctrl_colors[nom.midSideTag],
            orientation = {"aim_vector": ("y", (0, 1, 0)),
                           "up_vector": ("z", (0, 0, 1))},
            locks = {"v": 1},
            side = side,
            is_driven_side = is_driven_side,
            vis_category = "spine"
        ),


        "ik_waist": PrelimControl(
            name = "ik_waist",
            shape = "circle",
            size = [14, 14, 14],
            color = ctrl_colors[nom.midSideTag],
            orientation = {"aim_vector": ("y", (0, 1, 0)),
                           "up_vector": ("z", (0, 0, 1))},
            locks = {"v": 1},
            side = side,
            is_driven_side = is_driven_side,
            vis_category = "spine"
        ),


        "ik_pelvis": PrelimControl(
            name = "ik_pelvis",
            shape = "circle",
            shape_offset = [0, -2, 0],
            size = [14, 14, 14],
            color = ctrl_colors[nom.midSideTag],
            orientation = {"aim_vector": ("y", (0, 1, 0)),
                           "up_vector": ("z", (0, 0, 1))},
            locks = {"v": 1},
            side = side,
            is_driven_side = is_driven_side,
            vis_category = "spine"
        ),


        "fk_spine_1": PrelimControl(
            name = "fk_spine_1",
            shape = "directional_circle",
            size = [12, 12, 12],
            color = ctrl_colors[nom.midSideTag2],
            orientation = {"aim_vector": ("y", (0, 1, 0)),
                           "up_vector": ("z", (0, 0, 1))},
            locks = {"v": 1},
            side = side,
            is_driven_side = is_driven_side,
            vis_category = "spine",
            up_direction = [0, -1, 0]
        ),


        "fk_spine_2": PrelimControl(
            name = "fk_spine_2",
            shape = "directional_circle",
            size = [12, 12, 12],
            shape_offset = [0, 2, 0],
            color = ctrl_colors[nom.midSideTag2],
            orientation = {"aim_vector": ("y", (0, 1, 0)),
                           "up_vector": ("z", (0, 0, 1))},
            locks = {"v": 1},
            side = side,
            is_driven_side = is_driven_side,
            vis_category = "spine",
            up_direction = [0, -1, 0]
        ),


        "fk_spine_3": PrelimControl(
            name = "fk_spine_3",
            shape = "directional_circle",
            size = [12, 12, 12],
            shape_offset = [0, -3, 0],
            color = ctrl_colors[nom.midSideTag2],
            orientation = {"aim_vector": ("y", (0, 1, 0)),
                           "up_vector": ("z", (0, 0, 1))},
            locks = {"v": 1},
            side = side,
            is_driven_side = is_driven_side,
            vis_category = "spine",
            up_direction = [0, -1, 0]
        ),


        "fk_hips": PrelimControl(
            name = "fk_hips",
            shape = "directional_circle",
            shape_offset = [0, -5, 0],
            size = [12, 12, 12],
            color = ctrl_colors[nom.midSideTag2],
            orientation = {"aim_vector": ("y", (0, 1, 0)),
                           "up_vector": ("z", (0, 0, 1))},
            locks = {"v": 1},
            side = side,
            is_driven_side = is_driven_side,
            vis_category = "spine",
        ),


        "spine_tweak_1": PrelimControl(
            name = "spine_tweak_1",
            shape = "square",
            size = [12, 12, 12],
            color = ctrl_colors[nom.midSideTag3],
            up_direction = [0, 0, 1],
            forward_direction= [0, 1, 0],
            orientation = {"aim_vector": ("y", (0, 1, 0)),
                           "up_vector": ("z", (0, 0, 1))},
            locks = {"v": 1},
            side = side,
            is_driven_side=is_driven_side,
            vis_category="tweakers",
        ),


        "spine_tweak_2": PrelimControl(
            name = "spine_tweak_2",
            shape = "square",
            size = [12, 12, 12],
            color = ctrl_colors[nom.midSideTag3],
            up_direction = [0, 0, 1],
            forward_direction= [0, 1, 0],
            orientation = {"aim_vector": ("y", (0, 1, 0)),
                           "up_vector": ("z", (0, 0, 1))},
            locks = {"v": 1},
            side = side,
            is_driven_side=is_driven_side,
            vis_category="tweakers",
        ),


        "spine_tweak_3": PrelimControl(
            name = "spine_tweak_3",
            shape = "square",
            size = [12, 12, 12],
            color = ctrl_colors[nom.midSideTag3],
            up_direction = [0, 0, 1],
            forward_direction= [0, 1, 0],
            orientation = {"aim_vector": ("y", (0, 1, 0)),
                           "up_vector": ("z", (0, 0, 1))},
            locks = {"v": 1},
            side = side,
            is_driven_side=is_driven_side,
            vis_category="tweakers",
        ),


        "spine_tweak_4": PrelimControl(
            name = "spine_tweak_4",
            shape = "square",
            size = [12, 12, 12],
            color = ctrl_colors[nom.midSideTag3],
            up_direction = [0, 0, 1],
            forward_direction= [0, 1, 0],
            orientation = {"aim_vector": ("y", (0, 1, 0)),
                           "up_vector": ("z", (0, 0, 1))},
            locks = {"v": 1},
            side = side,
            is_driven_side=is_driven_side,
            vis_category="tweakers",
        ),


        "spine_tweak_5": PrelimControl(
            name = "spine_tweak_5",
            shape = "square",
            size = [12, 12, 12],
            color = ctrl_colors[nom.midSideTag3],
            up_direction = [0, 0, 1],
            forward_direction= [0, 1, 0],
            orientation = {"aim_vector": ("y", (0, 1, 0)),
                           "up_vector": ("z", (0, 0, 1))},
            locks = {"v": 1},
            side = side,
            is_driven_side=is_driven_side,
            vis_category="tweakers",
        ),


        "spine_tweak_6": PrelimControl(
            name = "spine_tweak_6",
            shape = "square",
            size = [12, 12, 12],
            color = ctrl_colors[nom.midSideTag3],
            up_direction = [0, 0, 1],
            forward_direction= [0, 1, 0],
            orientation = {"aim_vector": ("y", (0, 1, 0)),
                           "up_vector": ("z", (0, 0, 1))},
            locks = {"v": 1},
            side = side,
            is_driven_side=is_driven_side,
            vis_category="tweakers",
        ),


        "spine_tweak_7": PrelimControl(
            name = "spine_tweak_7",
            shape = "square",
            size = [12, 12, 12],
            color = ctrl_colors[nom.midSideTag3],
            up_direction = [0, 0, 1],
            forward_direction= [0, 1, 0],
            orientation = {"aim_vector": ("y", (0, 1, 0)),
                           "up_vector": ("z", (0, 0, 1))},
            locks = {"v": 1},
            side = side,
            is_driven_side = is_driven_side,
            vis_category = "tweakers",
        ),


        "settings": PrelimControl(
            name = "spine_settings",
            shape = "gear",
            size = [1, 1, 1],
            position = ("spine_1",),
            shape_offset = [18.5, 8, 0],
            color =ctrl_colors["settings"],
            locks = {"v": 1, "t": [1, 1, 1], "r": [1, 1, 1], "s": [1, 1, 1]},
            side = side,
            is_driven_side = is_driven_side,
            vis_category = "tweakers"
        )

    }

    return prelim_ctrls