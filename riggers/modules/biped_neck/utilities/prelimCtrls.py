# Title: prelimCtrls.py
# Author: Sam Leheny
# Contact: samleheny@live.com

# Description:


###########################
##### Import Commands #####
import Snowman.riggers.utilities.classes.class_PrelimControl as class_PrelimControl
reload(class_PrelimControl)

import Snowman.dictionaries.nurbsCurvePrefabs as nurbs_curve_prefabs
reload(nurbs_curve_prefabs)
curve_prefabs = nurbs_curve_prefabs.create_dict()

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
            vis_category = "neck"
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
            vis_category = "neck"
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
            vis_category = "neck"
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
            vis_category = "tweakers"
        )

    }

    return prelim_ctrls
