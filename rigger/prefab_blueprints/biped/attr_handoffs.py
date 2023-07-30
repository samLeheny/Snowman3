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
    AttributeHandoffInput('M_SpineSettings_CTRL', 'Cog_CTRL', False),
    AttributeHandoffInput('M_NeckSettings_CTRL', 'M_Neck_CTRL', False),
]
