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


        "root": PrelimControl(
            name = "root",
            shape = "COG",
            size = [60, 0, 60],
            forward_direction = [0, 0, 1],
            up_direction = [0, 1, 0],
            color = ctrl_colors["root"],
            position=("root",),
            locks = {"s": [1, 1, 1], "v": 1},
            side = side,
            is_driven_side = is_driven_side,
            vis_category = "root"
        ),


        "subRoot": PrelimControl(
            name="subRoot",
            shape="circle",
            size=[50, 0, 50],
            forward_direction=[0, 0, 1],
            up_direction=[0, 1, 0],
            color=ctrl_colors["root"],
            position=("root",),
            locks={"s": [1, 1, 1], "v": 1},
            side=side,
            is_driven_side=is_driven_side,
            vis_category="root"
        ),


        "COG": PrelimControl(
            name="cog",
            shape="COG",
            size=[20, 20, 20],
            color=ctrl_colors[nom.majorSideTag],
            position=("COG",),
            orientation={"aim_vector": ("y", (0, 1, 0)),
                         "up_vector": ("z", (0, 0, 1))},
            locks={"v": 1},
            side=side,
            is_driven_side=is_driven_side,
            vis_category="root"
        ),

    }

    return prelim_ctrls
