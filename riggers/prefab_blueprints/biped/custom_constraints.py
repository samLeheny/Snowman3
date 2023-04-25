# Title: custom_constraints.py
# Author: Sam Leheny
# Contact: samleheny@live.com

# Description:


###########################
##### Import Commands #####
import importlib
import pymel.core as pm

import Snowman3.riggers.utilities.constraint_utils as constraint_utils
importlib.reload(constraint_utils)
CustomConstraint = constraint_utils.CustomConstraint
###########################
###########################


###########################
######## Variables ########

###########################
###########################


inputs = [
    CustomConstraint(name='x1',
                     constraint_type='parentConstraint',
                     target_list=['SubRoot_CTRL'],
                     constrained_node='Cog_CONNECTOR'),
    CustomConstraint(name='x2',
                     constraint_type='parentConstraint',
                     target_list=['Cog_CTRL'],
                     constrained_node='M_Spine_CONNECTOR'),
    CustomConstraint(name='x3',
                     constraint_type='parentConstraint',
                     target_list=['M_IkChest_CTRL'],
                     constrained_node='M_Neck_CONNECTOR'),
    CustomConstraint(name='x4',
                     constraint_type='parentConstraint',
                     target_list=['M_IkChest_CTRL'],
                     constrained_node='L_Clavicle_CONNECTOR'),
    CustomConstraint(name='x5',
                     constraint_type='parentConstraint',
                     target_list=['M_IkChest_CTRL'],
                     constrained_node='R_Clavicle_CONNECTOR'),
    CustomConstraint(name='x6',
                     constraint_type='parentConstraint',
                     target_list=['L_ClavicleEnd_BIND'],
                     constrained_node='L_Arm_CONNECTOR'),
    CustomConstraint(name='x7',
                     constraint_type='parentConstraint',
                     target_list=['R_ClavicleEnd_BIND'],
                     constrained_node='R_Arm_CONNECTOR'),
    CustomConstraint(name='x8',
                     constraint_type='parentConstraint',
                     target_list=['L_Hand_blend_JNT'],
                     constrained_node='L_Hand_CONNECTOR'),
    CustomConstraint(name='x9',
                     constraint_type='parentConstraint',
                     target_list=['R_Hand_blend_JNT'],
                     constrained_node='R_Hand_CONNECTOR'),
    CustomConstraint(name='x10',
                     constraint_type='parentConstraint',
                     target_list=['M_IkPelvis_CTRL'],
                     constrained_node='L_Leg_CONNECTOR'),
    CustomConstraint(name='x11',
                     constraint_type='parentConstraint',
                     target_list=['M_IkPelvis_CTRL'],
                     constrained_node='R_Leg_CONNECTOR'),
    CustomConstraint(name='x12',
                     constraint_type='parentConstraint',
                     target_list=['L_IkFoot_CTRL'],
                     constrained_node='L_FootRollSoleHeel_JNT_OFFSET'),
    CustomConstraint(name='x13',
                          constraint_type='parentConstraint',
                          target_list=['R_IkFoot_CTRL'],
                          constrained_node='R_FootRollSoleHeel_JNT_OFFSET'),
    CustomConstraint(name='x14',
                          constraint_type='parentConstraint',
                          target_list=['L_Foot_blend_JNT'],
                          constrained_node='L_Tarsus_BIND_buffer'),
    CustomConstraint(name='x15',
                          constraint_type='parentConstraint',
                          target_list=['R_Foot_blend_JNT'],
                          constrained_node='R_Tarsus_BIND_buffer'),
    CustomConstraint(name='x16',
                          constraint_type='parentConstraint',
                          target_list=['L_FkFoot_CTRL'],
                          constrained_node='L_FkFootSpace'),
    CustomConstraint(name='x17',
                          constraint_type='parentConstraint',
                          target_list=['R_FkFoot_CTRL'],
                          constrained_node='R_FkFootSpace'),
    CustomConstraint(name='x18',
                          constraint_type='parentConstraint',
                          target_list=['L_FootRollTarsus_JNT'],
                          constrained_node='L_Leg_IKH'),
    CustomConstraint(name='x19',
                          constraint_type='parentConstraint',
                          target_list=['R_FootRollTarsus_JNT'],
                          constrained_node='R_Leg_IKH'),
    CustomConstraint(name='x20',
                          constraint_type='parentConstraint',
                          target_list=['L_FootRollTarsus_JNT'],
                          constrained_node='L_Foot_IKH'),
    CustomConstraint(name='x21',
                          constraint_type='parentConstraint',
                          target_list=['R_FootRollTarsus_JNT'],
                          constrained_node='R_Foot_IKH'),
]
