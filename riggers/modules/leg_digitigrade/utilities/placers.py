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
            name = "thigh",
            side = side,
            position = (0, 0, 0),
            size = 1.25,
            aim_obj = "calf",
            up_obj = "ik_knee",
            orienter_data ={"aim_vector" : (1, 0 ,0),
                            "up_vector" : (0, 0, -1)}
        ),


        Placer(
            name = "calf",
            side = side,
            position = (0, -45, 4.57),
            size = 1.25,
            aim_obj = "tarsus",
            up_obj = "ik_knee",
            orienter_data ={"aim_vector" : (1, 0 ,0),
                            "up_vector" : (0, 0, -1)},
            connect_targets=("thigh",)
        ),


        Placer(
            name="tarsus",
            side=side,
            position=(0, -45, 4.57),
            size=1.25,
            aim_obj="tarsus_end",
            up_obj="ik_knee",
            orienter_data={"aim_vector": (1, 0, 0),
                           "up_vector": (0, 0, -1)},
            connect_targets=("calf",)
        ),


        Placer(
            name = "tarsus_end",
            side = side,
            position = (0, -91, 0),
            size = 1.25,
            aim_obj = "ankle_end",
            up_obj = (0, 0, 1),
            orienter_data = {"aim_vector" : (1, 0 ,0),
                             "up_vector" : (0, 0, -1)},
            connect_targets=("tarsus",)
        ),


        Placer(
            name = "ankle_end",
            side = side,
            position = (0, -101, 0),
            size = 1,
            has_vector_handles = False,
            orienter_data = {"match_to" : "tarsus_end"},
            connect_targets=("tarsus_end",)
        ),


        Placer(
            name = "ik_knee",
            side = side,
            position = (0, -45, 54.57),
            ik_distance = 50,
            size = 1.25,
            has_vector_handles = False,
        )

    )

    return placers
