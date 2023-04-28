# Title: hierarchy.py
# Author: Sam Leheny
# Contact: samleheny@live.com

# Description:


###########################
##### Import Commands #####

###########################
###########################


###########################
######## Variables ########

###########################
###########################


inputs = [
    ['Cog', ['Root', 'SubRoot']],
    ['M_Spine', ['Cog', 'Cog']],
    ['M_Neck', ['M_Spine', 'Spine7']],
    ['L_Clavicle', ['M_Spine', 'Spine7']],
    ['R_Clavicle', ['M_Spine', 'Spine7']],
    ['L_Arm', ['L_Clavicle', 'ClavicleEnd']],
    ['R_Arm', ['R_Clavicle', 'ClavicleEnd']],
    ['L_Hand', ['L_Arm', 'Wrist']],
    ['R_Hand', ['R_Arm', 'Wrist']],
    ['L_Leg', ['M_Spine', 'Spine1']],
    ['R_Leg', ['M_Spine', 'Spine1']],
]
