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





def create_handoffs(modules):

    hand_offs = {

        (modules['spine'].ctrls['settings'], modules['root'].ctrls['COG'], True),

        (modules['neck'].ctrls['settings'], modules['neck'].ctrls['neck'], True),

        (modules['L_foot'].foot_attr_loc, modules['L_leg'].ctrls['ik_foot'], True),
        (modules['L_foot'].leg_attr_loc, modules['L_leg'].ctrls['hip_pin'], True),

        (modules['R_foot'].foot_attr_loc, modules['R_leg'].ctrls['ik_foot'], True),
        (modules['R_foot'].leg_attr_loc, modules['R_leg'].ctrls['hip_pin'], True),

    }

    return hand_offs