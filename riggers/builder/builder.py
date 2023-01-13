# Title: build_biped.py
# Author: Sam Leheny
# Contact: samleheny@live.com

# Description: Class to handle the building of biped armature and final rig.


###########################
##### Import Commands #####
import importlib
import pymel.core as pm
import Snowman3.riggers.utilities.classes.class_Armature as classArmature
import Snowman3.riggers.utilities.classes.class_Rig as classRig
importlib.reload(classArmature)
importlib.reload(classRig)
Armature = classArmature.Armature
Rig = classRig.Rig

import Snowman3.utilities.general_utils as gen_utils
importlib.reload(gen_utils)

import Snowman3.dictionaries.nameConventions as nameConventions
importlib.reload(nameConventions)
nom = nameConventions.create_dict()

import Snowman3.riggers.utilities.bodyRigWrapup as rigWrapup
importlib.reload(rigWrapup)

import Snowman3.riggers.utilities.directories.get_armature_data as get_armature_data
importlib.reload(get_armature_data)
###########################
###########################


###########################
######## Variables ########

###########################
###########################



#...Symmetry and side variables
symmetry_info = gen_utils.symmetry_info("Left drives Right")
default_symmetry_mode = symmetry_info[0]





########################################################################################################################
def build_armature_in_scene(armature):

    #...Create and move into armature namespace
    pm.namespace(add=nom.setupRigNamespace)
    pm.namespace(set=nom.setupRigNamespace)

    #...Build armature
    armature.populate_armature()

    #...Return to default scene namespace
    pm.namespace(set=":")
    pm.select(clear=1)
    return armature





########################################################################################################################
def build_prefab_armature(prefab_tag, symmetry_mode=None):

    armature = get_armature_data.armature(prefab_tag, symmetry_mode=symmetry_mode)
    build_armature_in_scene(armature)

    return armature





########################################################################################################################
def build_armature_from_data(data):

    armature = Armature(name = data['name'],
                        prefab_key = data['prefab_key'],
                        root_size = data['root_size'],
                        symmetry_mode = data['symmetry_mode'],
                        modules = data['modules'])
    armature.modules_from_data()
    build_armature_in_scene(armature)

    return armature





########################################################################################################################
def build_rig_in_scene(asset_name=None, armature=None):

    #...Create namespace for final rig and set it as current namespace
    pm.namespace(add=nom.finalRigNamespace)
    pm.namespace(set=nom.finalRigNamespace)

    rig = Rig(name=asset_name, armature=armature)
    rig.populate_rig()

    #...Put a bow on this puppy!
    rigWrapup.execute(modules=rig.modules)
    pm.select(clear=1)

