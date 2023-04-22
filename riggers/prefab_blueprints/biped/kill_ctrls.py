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
class KillCtrlInput:
    part_name: str
    ctrl_node_name: str
    hide: bool = True
    lock: bool = True
    rename: bool = True



inputs = [
    KillCtrlInput('L_Hand', 'L_Wrist_CTRL'),
    KillCtrlInput('R_Hand', 'R_Wrist_CTRL'),
    KillCtrlInput('L_Foot', 'L_FootSettings_CTRL'),
    KillCtrlInput('R_Foot', 'R_FootSettings_CTRL'),
    KillCtrlInput('M_Spine', 'M_SpineSettings_CTRL'),
    KillCtrlInput('M_Neck', 'M_NeckSettings_CTRL'),
]
