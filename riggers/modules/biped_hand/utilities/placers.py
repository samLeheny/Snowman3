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
            name = "hand",
            side = side,
            position = (0, 0, 0),
            size = 1.25,
            aim_obj = (1, 0, 0),
            up_obj = (0, 1, 0),
            orienter_data ={"aim_vector" : (1, 0 ,0),
                            "up_vector" : (0, 1, 0)}
        ),


        Placer(
            name = "index_metacarpal",
            side = side,
            position = (2.5, 0, 2.21),
            size = 0.5,
            aim_obj = "index_1",
            up_obj = (0, 1, 0),
            orienter_data ={"aim_vector" : (1, 0 ,0),
                            "up_vector" : (0, 1, 0)},
            connect_targets=("hand",)
        ),


        Placer(
            name = "index_1",
            side = side,
            position = (8.75, 0, 2.49),
            size = 0.5,
            aim_obj = "index_2",
            up_obj = (0, 1, 0),
            orienter_data ={"aim_vector" : (1, 0 ,0),
                            "up_vector" : (0, 1, 0)},
            connect_targets=("index_metacarpal",)
        ),


        Placer(
            name = "index_2",
            side = side,
            position = (12.36, 0.02, 2.49),
            size = 0.5,
            aim_obj = "index_3",
            up_obj = (0, 1, 0),
            orienter_data ={"aim_vector" : (1, 0 ,0),
                            "up_vector" : (0, 1, 0)},
            connect_targets=("index_1",)
        ),


        Placer(
            name = "index_3",
            side = side,
            position = (14.26, 0.02, 2.49),
            size = 0.5,
            aim_obj = "index_end",
            up_obj = (0, 1, 0),
            orienter_data ={"aim_vector" : (1, 0 ,0),
                            "up_vector" : (0, 1, 0)},
            connect_targets=("index_2",)
        ),


        Placer(
            name = "index_end",
            side = side,
            position = (15.96, 0, 2.49),
            size = 0.5,
            has_vector_handles = False,
            orienter_data ={"match_to" : "index_3"},
            connect_targets=("index_3",)
        ),


        Placer(
            name = "middle_metacarpal",
            side = side,
            position = (2.5, 0, 0.49),
            size = 0.5,
            aim_obj = "middle_1",
            up_obj = (0, 1, 0),
            orienter_data ={"aim_vector" : (1, 0 ,0),
                            "up_vector" : (0, 1, 0)},
            connect_targets=("hand",)
        ),


        Placer(
            name = "middle_1",
            side = side,
            position = (8.75, 0, 0.49),
            size = 0.5,
            aim_obj = "middle_2",
            up_obj = (0, 1, 0),
            orienter_data ={"aim_vector" : (1, 0 ,0),
                            "up_vector" : (0, 1, 0)},
            connect_targets=("middle_metacarpal",)
        ),


        Placer(
            name = "middle_2",
            side = side,
            position = (12.76, 0.02, 0.49),
            size = 0.5,
            aim_obj = "middle_3",
            up_obj = (0, 1, 0),
            orienter_data ={"aim_vector" : (1, 0 ,0),
                            "up_vector" : (0, 1, 0)},
            connect_targets=("middle_1",)
        ),


        Placer(
            name = "middle_3",
            side = side,
            position = (14.86, 0.02, 0.49),
            size = 0.5,
            aim_obj = "middle_end",
            up_obj = (0, 1, 0),
            orienter_data ={"aim_vector" : (1, 0 ,0),
                            "up_vector" : (0, 1, 0)},
            connect_targets=("middle_2",)
        ),


        Placer(
            name = "middle_end",
            side = side,
            position = (16.56, 0, 0.49),
            size = 0.5,
            has_vector_handles = False,
            orienter_data ={"match_to" : "middle_3"},
            connect_targets=("middle_3",)
        ),


        Placer(
            name = "ring_metacarpal",
            side = side,
            position = (2.5, 0, -1.29),
            size = 0.5,
            aim_obj = "ring_1",
            up_obj = (0, 1, 0),
            orienter_data ={"aim_vector" : (1, 0 ,0),
                            "up_vector" : (0, 1, 0)},
            connect_targets=("hand",)
        ),


        Placer(
            name = "ring_1",
            side = side,
            position = (8.36, 0, -1.51),
            size = 0.5,
            aim_obj = "ring_2",
            up_obj = (0, 1, 0),
            orienter_data ={"aim_vector" : (1, 0 ,0),
                            "up_vector" : (0, 1, 0)},
            connect_targets=("ring_metacarpal",)
        ),


        Placer(
            name = "ring_2",
            side = side,
            position = (12.36, 0.02, -1.51),
            size = 0.5,
            aim_obj = "ring_3",
            up_obj = (0, 1, 0),
            orienter_data ={"aim_vector" : (1, 0 ,0),
                            "up_vector" : (0, 1, 0)},
            connect_targets=("ring_1",)
        ),


        Placer(
            name = "ring_3",
            side = side,
            position = (14.26, 0.02, -1.51),
            size = 0.5,
            aim_obj = "ring_end",
            up_obj = (0, 1, 0),
            orienter_data ={"aim_vector" : (1, 0 ,0),
                            "up_vector" : (0, 1, 0)},
            connect_targets=("ring_2",)
        ),


        Placer(
            name = "ring_end",
            side = side,
            position = (15.86, 0, -1.51),
            size = 0.5,
            has_vector_handles = False,
            orienter_data ={"match_to" : "ring_3"},
            connect_targets=("ring_3",)
        ),


        Placer(
            name = "pinky_metacarpal",
            side = side,
            position = (2.5, 0, -3.04),
            size = 0.5,
            aim_obj = "pinky_1",
            up_obj = (0, 1, 0),
            orienter_data ={"aim_vector" : (1, 0 ,0),
                            "up_vector" : (0, 1, 0)},
            connect_targets=("hand",)
        ),


        Placer(
            name = "pinky_1",
            side = side,
            position = (7.36, 0, -3.51),
            size = 0.5,
            aim_obj = "pinky_2",
            up_obj = (0, 1, 0),
            orienter_data ={"aim_vector" : (1, 0 ,0),
                            "up_vector" : (0, 1, 0)},
            connect_targets=("pinky_metacarpal",)
        ),


        Placer(
            name = "pinky_2",
            side = side,
            position = (9.95, 0.02, -3.51),
            size = 0.5,
            aim_obj = "pinky_3",
            up_obj = (0, 1, 0),
            orienter_data ={"aim_vector" : (1, 0 ,0),
                            "up_vector" : (0, 1, 0)},
            connect_targets=("pinky_1",)
        ),


        Placer(
            name = "pinky_3",
            side = side,
            position = (12.06, 0.02, -3.51),
            size = 0.5,
            aim_obj = "pinky_end",
            up_obj = (0, 1, 0),
            orienter_data ={"aim_vector" : (1, 0 ,0),
                            "up_vector" : (0, 1, 0)},
            connect_targets=("pinky_2",)
        ),


        Placer(
            name = "pinky_end",
            side = side,
            position = (13.86, 0, -3.51),
            size = 0.5,
            has_vector_handles = False,
            orienter_data ={"match_to" : "pinky_3"},
            connect_targets=("pinky_3",)
        ),


        Placer(
            name = "thumb_1",
            side = side,
            position = (1.65, 0, 3.91),
            size = 0.5,
            aim_obj = "thumb_2",
            up_obj = (1, 0, 0),
            orienter_data ={"aim_vector" : (1, 0 ,0),
                            "up_vector" : (0, 1, 0)},
            connect_targets=("hand",)
        ),


        Placer(
            name = "thumb_2",
            side = side,
            position = (4.95, 0, 4.51),
            size = 0.5,
            aim_obj = "thumb_3",
            up_obj = (1, 0, 0),
            orienter_data ={"aim_vector" : (1, 0 ,0),
                            "up_vector" : (0, 1, 0)},
            connect_targets=("thumb_1",)
        ),


        Placer(
            name = "thumb_3",
            side = side,
            position = (8.25, 0, 4.51),
            size = 0.5,
            aim_obj = "thumb_end",
            up_obj = (1, 0, 0),
            orienter_data ={"aim_vector" : (1, 0 ,0),
                            "up_vector" : (0, 1, 0)},
            connect_targets=("thumb_2",)
        ),


        Placer(
            name = "thumb_end",
            side = side,
            position = (11.22, 0, 4.5),
            size = 0.5,
            has_vector_handles = False,
            orienter_data = {"match_to" : "thumb_3"},
            connect_targets=("thumb_3",)
        ),


        Placer(
            name = "ik_index",
            side = side,
            position = (12.36, 10, 2.49),
            ik_distance = 10,
            size = 0.35,
            has_vector_handles = False,
        ),


        Placer(
            name = "ik_middle",
            side = side,
            position = (12.76, 10, 0.49),
            ik_distance = 10,
            size = 0.35,
            has_vector_handles = False,
        ),


        Placer(
            name = "ik_ring",
            side = side,
            position = (12.36, 10, -1.51),
            ik_distance = 10,
            size = 0.35,
            has_vector_handles = False,
        ),


        Placer(
            name = "ik_pinky",
            side = side,
            position = (9.95, 10, -3.51),
            ik_distance = 10,
            size = 0.35,
            has_vector_handles = False,
        ),


        Placer(
            name = "ik_thumb",
            side = side,
            position = (8.25, 0, 14.51),
            ik_distance = 10,
            size = 0.35,
            has_vector_handles = False,
        )

    )

    return placers
