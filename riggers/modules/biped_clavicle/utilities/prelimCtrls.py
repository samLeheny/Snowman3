# Title: clavicleControls.py
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


        "clavicle": PrelimControl(
            name = "clavicle",
            shape = "biped_clavicle",
            size = [9, 9, 9],
            shape_offset = [6, 0, 0],
            color = [ctrl_colors[nom.leftSideTag], ctrl_colors[nom.rightSideTag]],
            position = "clavicle",
            orientation = {"match_to": "module_ctrl"},
            locks = {"v": 1},
            side = side,
            is_driven_side = is_driven_side,
            vis_category = "fk limbs"
        ),

    }

    return prelim_ctrls
