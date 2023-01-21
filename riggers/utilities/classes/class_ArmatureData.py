# Title: class_ArmatureData.py
# Author: Sam Leheny
# Contact: samleheny@live.com

# Description:


###########################
##### Import Commands #####
from dataclasses import dataclass

###########################
###########################


###########################
######## Variables ########

###########################
###########################





########################################################################################################################
@dataclass
class ArmatureData:

    name: str
    prefab_key: str = None
    root_size: float = 55.0
    symmetry_mode: str = None
    driver_side: str = None
    modules: dict = None
    armature_scale: float = 1.0
