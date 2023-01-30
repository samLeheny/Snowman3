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

###########################
###########################


###########################
######## Functions ########
def create_enter_namespace(namespace):
    pm.namespace(add=namespace)
    pm.namespace(set=namespace)

def return_to_root_namespace():
    pm.namespace(set=":")
###########################
###########################


class RigBuilder:
    def __init__(
        self,
        asset_name,
        prefab_key,
        dirpath,
        symmetry_mode = None
    ):
        self.prefab_key = prefab_key
        self.symmetry_mode = symmetry_mode
        self.asset_name = asset_name
        self.dirpath = dirpath
        self.armature_namespace = nom.setupRigNamespace
        self.rig_namespace = nom.finalRigNamespace
        self.armature_data = None
        self.armature = None
        self.rig = None


    ####################################################################################################################
    def export_armature_data(self):
        armature_IO = ArmatureDataIO(armature=self.armature_data.get_armature(), dirpath=f'{self.dirpath}/test_build')
        armature_IO.save()


    ####################################################################################################################
    def build_armature(self):
        self.armature = self.armature_data.get_armature().populate_armature()


    ####################################################################################################################
    def build_armature_in_scene(self):
        create_enter_namespace(self.armature_namespace)
        self.export_armature_data()
        self.build_armature()
        return_to_root_namespace()


    ####################################################################################################################
    def build_prefab_armature(self):
        self.armature_data = PrefabArmatureData(prefab_key=self.prefab_key, symmetry_mode=self.symmetry_mode)
        self.build_armature_in_scene()


    ####################################################################################################################
    def get_armature_data_from_file(self):
        armature_IO = ArmatureDataIO(self.dirpath)
        self.armature_data = armature_IO.build_armature_data_from_file()
        self.armature_data.modules_from_data()


    ####################################################################################################################
    def build_armature_from_file(self):
        self.get_armature_data_from_file()
        self.build_armature_in_scene()


    ####################################################################################################################
    def build_rig_in_scene(self, scene_armature):
        create_enter_namespace(self.rig_namespace)
        self.build_rig(scene_armature)
        #...Put a bow on this puppy!
        rigWrapup.execute(modules=self.rig.modules)


    ####################################################################################################################
    def build_rig(self, scene_armature):
        self.rig = Rig(name=self.asset_name, armature=scene_armature)
        self.rig.populate_rig()
