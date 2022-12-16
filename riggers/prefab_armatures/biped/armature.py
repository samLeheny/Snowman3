# Title: modules.py
# Author: Sam Leheny
# Contact: samleheny@live.com

# Description:


###########################
##### Import Commands #####
import Snowman.riggers.utilities.classes.class_Armature as armature
reload(armature)
Armature = armature.Armature

import Snowman.riggers.utilities.directories.get_armature_data as get_armature_data
reload(get_armature_data)
###########################
###########################


###########################
######## Variables ########

###########################
###########################





def create_armature(symmetry_mode=None):

    armature = Armature(
        name = "biped",
        root_size = 55,
        symmetry_mode = symmetry_mode,
        modules = get_armature_data.modules("biped", symmetry_mode=symmetry_mode)
    )

    return armature
