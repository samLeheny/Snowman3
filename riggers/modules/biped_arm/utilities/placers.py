# Title: placers.py
# Author: Sam Leheny
# Contact: samleheny@live.com

# Description:


###########################
##### Import Commands #####
import importlib
import Snowman3.riggers.utilities.classes.class_Placer as classPlacer
importlib.reload(classPlacer)
Placer = classPlacer.Placer
###########################
###########################


###########################
######## Variables ########

###########################
###########################





def create_placers(side=None, is_driven_side=None):

    placers = (


        Placer(
            name = "upperarm",
            side = side,
            position = (0, 0, 0),
            size = 1.25,
            aim_obj = "lowerarm",
            up_obj = "ik_elbow",
            orienter_data ={"aim_vector" : (1, 0 ,0),
                            "up_vector" : (0, 0, -1)}
        ),


        Placer(
            name = "lowerarm",
            side = side,
            position = (26.94, 0, -2.97),
            size = 1.25,
            aim_obj = "lowerarm_end",
            up_obj = "ik_elbow",
            orienter_data ={"aim_vector" : (1, 0 ,0),
                            "up_vector" : (0, 0, -1)},
            connect_targets=("upperarm",)
        ),


        Placer(
            name = "lowerarm_end",
            side = side,
            position = (52.64, 0, 0),
            size = 1.25,
            aim_obj = "wrist_end",
            up_obj = (0, 1, 0),
            orienter_data = {"aim_vector" : (1, 0 ,0),
                             "up_vector" : (0, 1, 0)},
            connect_targets=("lowerarm",)
        ),


        Placer(
            name = "wrist_end",
            side = side,
            position = (59, 0, 0),
            size = 1,
            has_vector_handles = False,
            orienter_data = {"match_to" : "lowerarm_end"},
            connect_targets=("lowerarm_end",)
        ),


        Placer(
            name = "ik_elbow",
            side = side,
            position = (26.94, 0, -42.58),
            ik_distance = 40,
            size = 1.25,
            has_vector_handles = False,
        )

    )

    return placers
