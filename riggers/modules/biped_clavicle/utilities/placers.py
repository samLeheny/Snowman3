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
            name = "clavicle",
            side = side,
            position = (0, 0, 0),
            size = 1.25,
            vector_handle_data={"aim": {"obj": "clavicle_end"},
                                "up": {"coord": (0, 5, 0)}},
            orienter_data ={"aim_vector" : (1, 0 ,0),
                            "up_vector" : (0, 1, 0)}
        ),


        Placer(
            name = "clavicle_end",
            side = side,
            position = (12, 0, 0),
            size = 1.25,
            orienter_data = {"match_to" : "clavicle"},
            connect_targets=("clavicle",)
        )

    )

    return placers
