# Title: kill_ctrls.py
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
class AttributeHandoffInput:
    old_attr_node: str
    new_attr_node: str
    delete_old_node: bool = False



inputs = [
    AttributeHandoffInput('L_leg_attr_LOC', 'L_Hip_CTRL', True),
    AttributeHandoffInput('R_leg_attr_LOC', 'R_Hip_CTRL', True),
    AttributeHandoffInput('L_FootSettings_CTRL', 'L_IkFoot_CTRL', False),
    AttributeHandoffInput('R_FootSettings_CTRL', 'R_IkFoot_CTRL', False),
    AttributeHandoffInput('M_SpineSettings_CTRL', 'Cog_CTRL', False),
    AttributeHandoffInput('M_NeckSettings_CTRL', 'M_Neck_CTRL', False),
]
