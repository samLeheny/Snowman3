# Title: placers.py
# Author: Sam Leheny
# Contact: samleheny@live.com

# Description:


###########################
##### Import Commands #####
import Snowman.riggers.utilities.classes.class_Placer as classPlacer
reload(classPlacer)
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
            name = "neck",
            side = side,
            position = (0, 0, 0),
            size = 1.25,
            aim_obj = (0, 5, 0),
            up_obj = (5, 0, 0),
            orienter_data = {"aim_vector" : (0, 1 ,0),
                             "up_vector" : (1, 0, 0)},
        ),


        Placer(
            name = "head",
            side = side,
            position = (0, 12.5, 1.8),
            size = 1.25,
            aim_obj = (0, 5, 0),
            up_obj = (5, 0, 0),
            orienter_data = {"aim_vector" : (0, 1 ,0),
                             "up_vector" : (1, 0, 0)},
            connect_targets=("neck",)
        )

    )

    return placers

