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
waist_y_positions = y = {"1" : 4, "4": 22.1}
y["2"] = y["1"] + (( (y["4"] - y["1"]) / 3 ) * 1)
y["3"] = y["1"] + (( (y["4"] - y["1"]) / 3 ) * 2)
###########################
###########################





def create_placers(side=None):

    placers = (


        Placer(
            name = "spine_1",
            position = (0, 0, 0),
            size = 1.25,
            vector_handle_data={"aim": {"obj": "spine_2"},
                                "up": {"coord": (5, 0, 0)}},
            orienter_data = {"aim_vector" : (0, 1 ,0),
                             "up_vector" : (1, 0, 0)},
        ),


        Placer(
            name = "spine_2",
            position = (0, 8.7, 0),
            size = 1.25,
            vector_handle_data={"aim": {"obj": "spine_3"},
                                "up": {"coord": (5, 0, 0)}},
            orienter_data = {"aim_vector" : (0, 1 ,0),
                             "up_vector" : (1, 0, 0)},
            connect_targets = ("spine_1",)
        ),


        Placer(
            name = "spine_3",
            position = (0, 20.2, 0),
            size = 1.25,
            vector_handle_data={"aim": {"obj": "spine_4"},
                                "up": {"coord": (5, 0, 0)}},
            orienter_data = {"aim_vector" : (0, 1 ,0),
                             "up_vector" : (1, 0, 0)},
            connect_targets = ("spine_2",)
        ),


        Placer(
            name = "spine_4",
            position = (0, 27.8, 0),
            size = 1.25,
            vector_handle_data={"aim": {"obj": "spine_5"},
                                "up": {"coord": (5, 0, 0)}},
            orienter_data = {"aim_vector" : (0, 1 ,0),
                             "up_vector" : (1, 0, 0)},
            connect_targets = ("spine_3",)
        ),


        Placer(
            name = "spine_5",
            position = (0, 42.3, 0),
            size = 1.25,
            vector_handle_data={"aim": {"obj": "spine_6"},
                                "up": {"coord": (5, 0, 0)}},
            orienter_data = {"aim_vector" : (0, 1 ,0),
                             "up_vector" : (1, 0, 0)},
            connect_targets = ("spine_4",)
        ),


        Placer(
            name = "spine_6",
            position = (0, 49, 0),
            size = 1.25,
            vector_handle_data={"aim": {"coord": (0, 5, 0)},
                                "up": {"coord": (5, 0, 0)}},
            orienter_data = {"aim_vector" : (0, 1 ,0),
                             "up_vector" : (1, 0, 0)},
            connect_targets = ("spine_5",)
        ),

    )

    return placers
