# Title: placers.py
# Author: Sam Leheny
# Contact: samleheny@live.com

# Description:


###########################
##### Import Commands #####
import importlib
import Snowman3.riggers.utilities.classes.class_Placer as classPlacer
import Snowman3.riggers.utilities.classes.class_PoleVectorPlacer as classPoleVectorPlacer
importlib.reload(classPlacer)
importlib.reload(classPoleVectorPlacer)
Placer = classPlacer.Placer
PoleVectorPlacer = classPoleVectorPlacer.PoleVectorPlacer
###########################
###########################


###########################
######## Variables ########

###########################
###########################





def create_placers(side=None):

    placers = (


        Placer(
            name = "upperarm",
            side = side,
            position = (0, 0, 0),
            size = 1.25,
            vector_handle_data = {"aim": {"obj": "lowerarm"},
                                  "up": {"obj": "ik_elbow"}},
            orienter_data ={"aim_vector" : (1, 0 ,0),
                            "up_vector" : (0, 0, -1)}
        ),


        Placer(
            name = "lowerarm",
            side = side,
            position = (26.94, 0, -2.97),
            size = 1.25,
            vector_handle_data = {"aim": {"obj": "lowerarm_end"},
                                  "up": {"obj": "ik_elbow"}},
            orienter_data ={"aim_vector" : (1, 0 ,0),
                            "up_vector" : (0, 0, -1)},
            connect_targets=("upperarm",)
        ),


        Placer(
            name = "lowerarm_end",
            side = side,
            position = (52.64, 0, 0),
            size = 1.25,
            vector_handle_data = {"aim": {"obj": "wrist_end"},
                                  "up": {"coord": (0, 1, 0)}},
            orienter_data = {"aim_vector" : (1, 0 ,0),
                             "up_vector" : (0, 1, 0)},
            connect_targets=("lowerarm",)
        ),


        Placer(
            name = "wrist_end",
            side = side,
            position = (59, 0, 0),
            size = 1,
            vector_handle_data = {"aim": {"coord": (0, 0, 1)},
                                  "up": {"coord": (0, 1, 0)}},
            orienter_data = {"match_to" : "lowerarm_end"},
            connect_targets=("lowerarm_end",)
        ),


        PoleVectorPlacer(
            name = "ik_elbow",
            side = side,
            pv_distance = 40,
            size = 1.25,
            vector_handle_data = {"aim": {"coord": (0, 0, 1)},
                                  "up": {"coord": (0, 1, 0)}},
        )

    )

    return placers
