# Title: modules.py
# Author: Sam Leheny
# Contact: samleheny@live.com

# Description:


###########################
##### Import Commands #####
import importlib

import Snowman3.riggers.utilities.classes.class_Armature as armature
importlib.reload(armature)
Armature = armature.Armature
###########################
###########################


###########################
######## Variables ########

###########################
###########################





def create_armature(symmetry_mode=None, modules=None, placer_connectors=None):

    armature = Armature(
        name = 'biped',
        prefab_key = 'biped',
        root_size = 55,
        symmetry_mode = symmetry_mode,
        modules = modules,
        placer_connectors = placer_connectors
    )

    return armature
