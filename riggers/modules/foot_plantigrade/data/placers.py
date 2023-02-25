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





def create_placers(side=None, placer_size=1.25, ground_coord=-10):

    placers = (


        Placer(
            name = "foot",
            side = side,
            position = (0, 0, 0),
            size = placer_size,
            vector_handle_data={"aim": {"obj": "ball"},
                                "up": {"coord": (0, 1, 0)}},
            orienter_data = {"aim_vector" : (1, 0 ,0),
                             "up_vector" : (0, 0, -1)},
        ),


        Placer(
            name = "ball",
            side = side,
            position = (0, -7.5, 11.8),
            size = placer_size,
            vector_handle_data={"aim": {"obj": "ball_end"},
                                "up": {"coord": (0, 1, 0)}},
            orienter_data = {"aim_vector" : (1, 0, 0),
                             "up_vector" : (0, 0, -1)},
            connect_targets = ("foot",)
        ),


        Placer(
            name = "ball_end",
            side = side,
            position = (0, -7.5, 16.73),
            size = placer_size,
            vector_handle_data={"aim": {"coord": (0, 0, 1)},
                                "up": {"coord": (0, 1, 0)}},
            orienter_data = {"match_to" : "ball"},
            connect_targets = ("ball",)
        ),


        Placer(
            name = "sole_toe",
            side = side,
            position = (0, ground_coord, 11.8),
            size = placer_size * 0.55,
            vector_handle_data={"aim": {"coord": (0, 0, 1)},
                                "up": {"coord": (0, 1, 0)}},
        ),


        Placer(
            name = "sole_toe_end",
            side = side,
            position = (0, ground_coord, 19),
            size = placer_size * 0.55,
            vector_handle_data={"aim": {"coord": (0, 0, 1)},
                                "up": {"coord": (0, 1, 0)}},
        ),


        Placer(
            name = "sole_inner",
            side = side,
            position = (-4.5, ground_coord, 11.8),
            size = placer_size * 0.55,
            vector_handle_data={"aim": {"coord": (0, 0, 1)},
                                "up": {"coord": (0, 1, 0)}},
        ),


        Placer(
            name = "sole_outer",
            side = side,
            position = (4.5, ground_coord, 11.8),
            size = placer_size * 0.55,
            vector_handle_data={"aim": {"coord": (0, 0, 1)},
                                "up": {"coord": (0, 1, 0)}},
        ),


        Placer(
            name = "sole_heel",
            side = side,
            position = (0, ground_coord, -4),
            size = placer_size * 0.55,
            vector_handle_data={"aim": {"coord": (0, 0, 1)},
                                "up": {"coord": (0, 1, 0)}},
        )

    )

    return placers
