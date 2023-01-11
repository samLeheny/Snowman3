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





def create_prelim_ctrls(side=None, is_driven_side=None, module_ctrl=None):

    prelim_ctrls = {


        "neck": PrelimControl(
            name = "neck",
            shape = "circle",
            size = [7, 7, 7],
            color = ctrl_colors[nom.midSideTag],
            position = ("neck",),
            orientation = {"match_to": "neck"},
            locks = {"v": 1},
            side = side,
            is_driven_side = is_driven_side,
            module_ctrl = module_ctrl
        ),


        "neckBend": PrelimControl(
            name = "neckBend",
            shape = "circle",
            size = [7, 7, 7],
            color = ctrl_colors[nom.midSideTag],
            position = ("neck", "head"),
            orientation = {"match_to": "neck"},
            locks = {"s": [0, 0, 0], "v": 1},
            side = side,
            is_driven_side = is_driven_side,
            module_ctrl = module_ctrl
        ),


        "head": PrelimControl(
            name = "head",
            shape = "cylinder",
            size = [9, 0.65, 9],
            shape_offset = [0, 8, 0],
            color = ctrl_colors[nom.midSideTag],
            position = ("head",),
            orientation = {"match_to": "head"},
            locks = {"v": 1},
            side = side,
            is_driven_side = is_driven_side,
            module_ctrl = module_ctrl
        ),


        "settings": PrelimControl(
            name = "neck_settings",
            shape = "gear",
            size = [1, 1, 1],
            position = ("neck",),
            shape_offset = [8, 2, 0],
            color =ctrl_colors["settings"],
            locks = {"v": 1, "t": [1, 1, 1], "r": [1, 1, 1], "s": [1, 1, 1]},
            side = side,
            is_driven_side = is_driven_side,
            module_ctrl = module_ctrl
        )

    }

    return prelim_ctrls
