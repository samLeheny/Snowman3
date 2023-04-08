# Title: custom_constraints.py
# Author: Sam Leheny
# Contact: samleheny@live.com

# Description:


###########################
##### Import Commands #####
import importlib
###########################
###########################


###########################
######## Variables ########

###########################
###########################


constraint_pairs = [
    [['Root', 'SubRoot'], 'Cog', True],
    [['Cog', 'Cog'], 'M_Spine', True],
    [['M_Spine', 'IkChest'], 'M_Neck', True],
    [['M_Spine', 'IkChest'], 'L_Clavicle', True],
    [['M_Spine', 'IkChest'], 'R_Clavicle', True],
    [['L_Clavicle', 'Clavicle'], 'L_Arm', True],
    [['R_Clavicle', 'Clavicle'], 'R_Arm', True],
]
