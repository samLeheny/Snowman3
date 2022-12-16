# Title: attr_handoffs.py
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
            #("settings", ("root", "COG"), True),
        ),

        "neck": (
            ("settings", ("neck", "neck"), True),
        ),


        "L_clavicle": (
        ),


        "R_clavicle": (
        ),


        "L_arm": (
        ),


        "R_arm": (
        ),


        "L_hand": (
            ("settings", ("L_arm", "settings"), True),
        ),


        "R_hand": (
            ("settings", ("R_arm", "settings"), True),
        ),


        "L_leg": (
        ),


        "R_leg": (
        ),


        "L_foot": (
            ("settings", ("L_leg", "settings"), True),
        ),


        "R_foot": (
            ("settings", ("R_leg", "settings"), True),
        ),

    }

    return hand_offs