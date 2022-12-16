# Title: connections.py
# Author: Sam Leheny
# Contact: samleheny@live.com

# Description:


###########################
##### Import Commands #####

###########################
###########################


###########################
######## Variables ########

###########################
###########################





def create_handoffs():

    hand_offs = {

        "root": (
        ),


        "spine": (
            #("root", "COG"),
        ),

        "neck": (
            #("spine", "neck"),
        ),


        "L_clavicle": (
            ("spine", "spine_tweak_7")
        ),


        "R_clavicle": (
            ("spine", "spine_tweak_7")
        ),


        "L_arm": (
        ),


        "R_arm": (
        ),


        "L_hand": (
        ),


        "R_hand": (
        ),


        "L_leg": (
        ),


        "R_leg": (
        ),


        "L_foot": (
        ),


        "R_foot": (
        ),

    }

    return hand_offs