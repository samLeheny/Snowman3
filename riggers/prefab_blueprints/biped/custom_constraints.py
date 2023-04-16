# Title: custom_constraints.py
# Author: Sam Leheny
# Contact: samleheny@live.com

# Description:


###########################
##### Import Commands #####
import importlib
from dataclasses import dataclass
###########################
###########################


###########################
######## Variables ########

###########################
###########################


@dataclass
class CustomConstraintInput:
    driver_part_name: str
    driver_node_name: str
    driven_part_name: str
    driven_node_name: str
    match_transform: bool
    constraint_type: str



constraint_pairs = [
        CustomConstraintInput('Root', 'SubRoot_CTRL', 'Cog', 'Connector', True, 'parent'),
        CustomConstraintInput('Cog', 'Cog_CTRL', 'M_Spine', 'Connector', True, 'parent'),
        CustomConstraintInput('M_Spine', 'M_IkChest_CTRL', 'M_Neck', 'Connector', True, 'parent'),
        CustomConstraintInput('M_Spine', 'M_IkChest_CTRL', 'L_Clavicle', 'Connector', True, 'parent'),
        CustomConstraintInput('M_Spine', 'M_IkChest_CTRL', 'R_Clavicle', 'Connector', True, 'parent'),
        CustomConstraintInput('L_Clavicle', 'L_ClavicleEnd_BIND', 'L_Arm', 'Connector', True, 'parent'),
        CustomConstraintInput('R_Clavicle', 'R_ClavicleEnd_BIND', 'R_Arm', 'Connector', True, 'parent'),
        CustomConstraintInput('L_Arm', 'L_Hand_blend_JNT', 'L_Hand', 'Connector', True, 'parent'),
        CustomConstraintInput('R_Arm', 'R_Hand_blend_JNT', 'R_Hand', 'Connector', True, 'parent'),
        CustomConstraintInput('M_Spine', 'M_IkPelvis_CTRL', 'L_Leg', 'Connector', True, 'parent'),
        CustomConstraintInput('M_Spine', 'M_IkPelvis_CTRL', 'R_Leg', 'Connector', True, 'parent'),
        CustomConstraintInput('L_Leg', 'L_IkFoot_CTRL', 'L_Foot', 'L_FootRollSoleHeel_JNT_OFFSET', False, 'parent'),
        CustomConstraintInput('R_Leg', 'R_IkFoot_CTRL', 'R_Foot', 'R_FootRollSoleHeel_JNT_OFFSET', False, 'parent'),
        CustomConstraintInput('L_Leg', 'L_Foot_blend_JNT', 'L_Foot', 'L_Foot_BIND_buffer', False, 'point'),
        CustomConstraintInput('R_Leg', 'R_Foot_blend_JNT', 'R_Foot', 'R_Foot_BIND_buffer', False, 'point'),
        CustomConstraintInput('L_Leg', 'L_FkFoot_CTRL', 'L_Foot', 'L_FkFootSpace', False, 'parent'),
        CustomConstraintInput('R_Leg', 'R_FkFoot_CTRL', 'R_Foot', 'R_FkFootSpace', False, 'parent'),
        CustomConstraintInput('L_Foot', 'L_FootRollFoot_JNT', 'L_Leg', 'L_Leg_IKH', False, 'point'),
        CustomConstraintInput('R_Foot', 'R_FootRollFoot_JNT', 'R_Leg', 'R_Leg_IKH', False, 'point'),
        CustomConstraintInput('L_Foot', 'L_FootRollFoot_JNT', 'L_Leg', 'L_Foot_IKH', False, 'parent'),
        CustomConstraintInput('R_Foot', 'R_FootRollFoot_JNT', 'R_Leg', 'R_Foot_IKH', False, 'parent'),
    ]
