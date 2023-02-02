# Title: connection_pairs.py
# Author: Sam Leheny
# Contact: samleheny@live.com

# Description:


###########################
##### Import Commands #####
import importlib

import Snowman3.riggers.utilities.classes.class_ConnectionPair as classConnectionPair
importlib.reload(classConnectionPair)
ConnectionPair = classConnectionPair.ConnectionPair
###########################
###########################


###########################
######## Variables ########

###########################
###########################





def create_connection_pairs_dict():

    connection_pairs = (
        ConnectionPair(
            "modules['root'].ctrls['COG']", "modules['spine'].transform_grp"),

        ConnectionPair(
            "modules['spine'].neck_socket", "modules['neck'].transform_grp"),

        ConnectionPair(
            "modules['spine'].clavicles_socket", "modules['L_clavicle'].transform_grp"),
        ConnectionPair(
            "modules['spine'].clavicles_socket", "modules['R_clavicle'].transform_grp"),

        ConnectionPair(
            "modules['L_clavicle'].shoulder_socket", "modules['L_arm'].transform_grp"),
        ConnectionPair(
            "modules['R_clavicle'].shoulder_socket", "modules['R_arm'].transform_grp"),

        ConnectionPair(
            "modules['L_arm'].wrist_socket", "modules['L_hand'].transform_grp"),
        ConnectionPair(
            "modules['R_arm'].wrist_socket", "modules['R_hand'].transform_grp"),

        ConnectionPair(
            "modules['spine'].hips_socket", "modules['R_leg'].transform_grp"),
        ConnectionPair(
            "modules['spine'].hips_socket", "modules['L_leg'].transform_grp"),

        ConnectionPair(
            "modules['L_leg'].bind_ankle_socket", "modules['L_foot'].bind_ankle_plug"),
        ConnectionPair(
            "modules['L_leg'].ik_ankle_ctrl_socket", "modules['L_foot'].ik_ankle_ctrl_plug"),
        ConnectionPair(
            "modules['L_leg'].ik_ankle_jnt_socket", "modules['L_foot'].ik_ankle_jnt_plug"),
        ConnectionPair(
            "modules['L_leg'].fk_ankle_ctrl_socket", "modules['L_foot'].fk_ankle_ctrl_plug"),
        ConnectionPair(
            "modules['R_leg'].bind_ankle_socket", "modules['R_foot'].bind_ankle_plug"),
        ConnectionPair(
            "modules['R_leg'].ik_ankle_ctrl_socket", "modules['R_foot'].ik_ankle_ctrl_plug"),
        ConnectionPair(
            "modules['R_leg'].ik_ankle_jnt_socket", "modules['R_foot'].ik_ankle_jnt_plug"),
        ConnectionPair(
            "modules['R_leg'].fk_ankle_ctrl_socket", "modules['R_foot'].fk_ankle_ctrl_plug"),

        ConnectionPair(
            "modules['L_foot'].ik_foot_roll_socket", "modules['L_leg'].ik_handle_plug"),
        ConnectionPair(
            "modules['R_foot'].ik_foot_roll_socket", "modules['R_leg'].ik_handle_plug"),
    )

    return connection_pairs
