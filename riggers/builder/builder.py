# Title: build_biped.py
# Author: Sam Leheny
# Contact: samleheny@live.com

# Description: Class to handle the building of biped armature and final rig.


###########################
##### Import Commands #####
import importlib
import pymel.core as pm
import Snowman3.riggers.utilities.classes.class_Rig as classRig
importlib.reload(classRig)
Rig = classRig.Rig

import Snowman3.utilities.general_utils as gen_utils
importlib.reload(gen_utils)

import Snowman3.dictionaries.nameConventions as nameConventions
importlib.reload(nameConventions)
nom = nameConventions.create_dict()

import Snowman3.riggers.utilities.bodyRigWrapup as rigWrapup
importlib.reload(rigWrapup)

import Snowman3.riggers.IO.armature_IO as iO
importlib.reload(iO)
ArmatureDataIO = iO.ArmatureDataIO

import Snowman3.riggers.utilities.classes.class_PrefabArmatureData as classPrefabArmatureData
importlib.reload(classPrefabArmatureData)
PrefabArmatureData = classPrefabArmatureData.PrefabArmatureData
###########################
###########################


###########################
######## Variables ########
default_symmetry_arg = "Left drives Right"
symmetry_info = gen_utils.symmetry_info(default_symmetry_arg)
default_symmetry_mode = symmetry_info[0]
###########################
###########################





########################################################################################################################
def create_enter_namespace(namespace):
    pm.namespace(add=namespace)
    pm.namespace(set=namespace)



########################################################################################################################
def export_armature_data(armature_data):
    armature_IO = ArmatureDataIO(armature=armature_data)
    armature_IO.save()



########################################################################################################################
def build_armature(armature_data):
    armature_data.populate_armature()
    return armature_data



########################################################################################################################
def return_to_root_namespace():
    pm.namespace(set=":")



########################################################################################################################
def build_armature_in_scene(armature_data):
    create_enter_namespace(nom.setupRigNamespace)
    export_armature_data(armature_data)
    armature = build_armature(armature_data)
    return_to_root_namespace()
    return armature



########################################################################################################################
def build_prefab_armature(prefab_tag, symmetry_mode=None):
    armature_data = PrefabArmatureData(prefab_key=prefab_tag, symmetry_mode=symmetry_mode)
    armature = build_armature_in_scene(armature_data.get_armature())
    return armature



########################################################################################################################
def get_armature_data_from_file(dirpath):
    armature_IO = ArmatureDataIO(dirpath)
    armature_data = armature_IO.build_armature_data_from_file()
    armature_data.modules_from_data()
    return armature_data



########################################################################################################################
def build_armature_from_file(dirpath):
    armature = get_armature_data_from_file(dirpath)
    build_armature_in_scene(armature)
    return armature



########################################################################################################################
def build_rig(asset_name, armature):
    rig = Rig(name=asset_name, armature=armature)
    rig.populate_rig()
    return rig



########################################################################################################################
def build_rig_in_scene(asset_name=None, armature=None):
    create_enter_namespace(nom.finalRigNamespace)
    rig = build_rig(asset_name, armature)
    #...Put a bow on this puppy!
    rigWrapup.execute(modules=rig.modules)
