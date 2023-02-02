# Title: attr_handoffs.py
# Author: Sam Leheny
# Contact: samleheny@live.com

# Description:


###########################
##### Import Commands #####
import importlib
import Snowman3.riggers.utilities.classes.class_AttrHandoff as classAttrHandoff
importlib.reload(classAttrHandoff)
AttrHandoff = classAttrHandoff.AttrHandoff
###########################
###########################


###########################
######## Variables ########

###########################
###########################





def create_handoffs():

    hand_offs = (

        AttrHandoff(
            old_attr_node = "modules['spine'].ctrls['settings']",
            new_attr_node = "modules['root'].ctrls['COG']",
            delete_old_node = True
        ),

        AttrHandoff(
            old_attr_node = "modules['neck'].ctrls['settings']",
            new_attr_node = "modules['neck'].ctrls['neck']",
            delete_old_node = True
        ),

        AttrHandoff(
            old_attr_node = "modules['L_foot'].foot_attr_loc",
            new_attr_node = "modules['L_leg'].ctrls['ik_foot']",
            delete_old_node = True
        ),

        AttrHandoff(
            old_attr_node = "modules['L_foot'].leg_attr_loc",
            new_attr_node = "modules['L_leg'].ctrls['hip_pin']",
            delete_old_node = True
        ),

        AttrHandoff(
            old_attr_node = "modules['R_foot'].foot_attr_loc",
            new_attr_node = "modules['R_leg'].ctrls['ik_foot']",
            delete_old_node = True
        ),

        AttrHandoff(
            old_attr_node = "modules['R_foot'].leg_attr_loc",
            new_attr_node = "modules['R_leg'].ctrls['hip_pin']",
            delete_old_node = True
        )

    )

    return hand_offs