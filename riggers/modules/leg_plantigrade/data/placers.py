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
            name = "thigh",
            side = side,
            position = (0, 0, 0),
            size = 1.25,
            vector_handle_data={"aim": {"obj": "calf"},
                                "up": {"obj": "ik_knee"}},
            orienter_data ={"aim_vector" : (1, 0 ,0),
                            "up_vector" : (0, 0, -1)}
        ),


        Placer(
            name = "calf",
            side = side,
            position = (0, -45, 4.57),
            size = 1.25,
            vector_handle_data={"aim": {"obj": "calf_end"},
                                "up": {"obj": "ik_knee"}},
            orienter_data ={"aim_vector" : (1, 0 ,0),
                            "up_vector" : (0, 0, -1)},
            connect_targets=("thigh",)
        ),


        Placer(
            name = "calf_end",
            side = side,
            position = (0, -91, 0),
            size = 1.25,
            vector_handle_data={"aim": {"obj": "ankle_end"},
                                "up": {"coord": (0, 0, 1)}},
            orienter_data = {"aim_vector" : (1, 0 ,0),
                             "up_vector" : (0, 0, -1)},
            connect_targets=("calf",)
        ),


        Placer(
            name = "ankle_end",
            side = side,
            position = (0, -101, 0),
            size = 1,
            orienter_data = {"match_to" : "calf_end"},
            connect_targets=("calf_end",)
        ),


        PoleVectorPlacer(
            name = "ik_knee",
            side = side,
            pv_distance = 50,
            size = 1.25,
        )

    )

    return placers
