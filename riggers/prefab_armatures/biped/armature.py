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

import Snowman3.riggers.utilities.directories.get_armature_data as get_armature_data
importlib.reload(get_armature_data)
###########################
###########################


###########################
######## Variables ########

###########################
###########################





def create_armature(symmetry_mode=None):

    armature = Armature(
        name = 'biped',
        prefab_key = 'biped',
        root_size = 55,
        symmetry_mode = symmetry_mode,
        modules = get_armature_data.modules('biped', symmetry_mode=symmetry_mode),
        placer_connectors = get_armature_data.placer_connectors('biped')
    )

    return armature
