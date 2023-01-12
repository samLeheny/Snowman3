# Title: rootPlacers.py
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
            name = "root",
            side = side,
            position = (0, 0, 0),
            size = 1.75,
            vector_handle_data={"aim": {"coord": (0, 0, 5)},
                                "up": {"coord": (0, 5, 0)}},
            orienter_data = {"aim_vector": (0, 0, 1),
                             "up_vector": (0, 1, 0)},
        ),


        Placer(
            name="COG",
            side=side,
            position=(0, 105, 0.39),
            size=1.75,
            vector_handle_data={"aim": {"coord": (0, 0, 5)},
                                "up": {"coord": (0, 5, 0)}},
            orienter_data={"aim_vector": (0, 0, 1),
                           "up_vector": (0, 1, 0)},
        ),


    )


    return placers
