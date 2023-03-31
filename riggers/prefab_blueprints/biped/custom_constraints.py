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
    [['Root', 'SubRoot'], 'Cog'],
    [['Cog', 'Cog'], 'M_Spine'],
    [['M_Spine', 'IkChest'], 'M_Neck'],
    [['M_Spine', 'IkChest'], 'L_Clavicle'],
    [['M_Spine', 'IkChest'], 'R_Clavicle']
]
