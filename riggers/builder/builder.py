# Title: build_biped.py
# Author: Sam Leheny
# Contact: samleheny@live.com

# Description: Class to handle the building of biped armature and final rig.


###########################
##### Import Commands #####
import os
import importlib
import json
import pymel.core as pm
import Snowman3.riggers.utilities.classes.class_Rig as classRig
importlib.reload(classRig)
Rig = classRig.Rig

import Snowman3.dictionaries.nameConventions as nameConventions
importlib.reload(nameConventions)
nom = nameConventions.create_dict()

import Snowman3.riggers.utilities.bodyRigWrapup as rigWrapup
importlib.reload(rigWrapup)

import Snowman3.riggers.utilities.classes.class_Armature as classArmature
importlib.reload(classArmature)
Armature = classArmature.Armature

import Snowman3.riggers.IO.armature_IO as iO
importlib.reload(iO)
ArmatureDataIO = iO.ArmatureDataIO

import Snowman3.riggers.utilities.classes.class_PrefabArmatureData as classPrefabArmatureData
importlib.reload(classPrefabArmatureData)
PrefabArmatureData = classPrefabArmatureData.PrefabArmatureData

import Snowman3.riggers.utilities.classes.class_Blueprint as class_Blueprint
importlib.reload(class_Blueprint)
Blueprint = class_Blueprint.Blueprint

import Snowman3.riggers.utilities.classes.class_PrefabBlueprint as class_prefabBlueprint
importlib.reload(class_prefabBlueprint)
PrefabBlueprint = class_prefabBlueprint.PrefabBlueprint

import Snowman3.riggers.IO.blueprint_IO as class_blueprint_IO
importlib.reload(class_blueprint_IO)
BlueprintDataIO = class_blueprint_IO.BlueprintDataIO

import Snowman3.riggers.IO.placer_IO as placerIO
importlib.reload(placerIO)
PlacerDataIO = placerIO.PlacerDataIO

import Snowman3.riggers.utilities.classes.class_Placer as classPlacer
importlib.reload(classPlacer)
Placer = classPlacer.Placer
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
        asset_name = None,
        prefab_key = None,
        dirpath = None,
    ):
        self.prefab_key = prefab_key
        self.asset_name = asset_name
        self.dirpath = f'{dirpath}/test_build'
        self.blueprint = None
        self.scene_armature = None
        self.armature_data = None
        self.rig = None



    ####################################################################################################################
    def build_prefab_armature(self):
        print(f"Building prefab armature: '{self.prefab_key}'")
        self.gather_and_export_prefab_blueprint_data()
        self.build_armature_from_file()


    ####################################################################################################################
    def build_armature_from_file(self):
        self.build_blueprint_from_file()
        self.armature_data = self.blueprint.armature
        self.armature_data.modules_from_data()
        self.build_armature_in_scene(self.armature_data)


    ####################################################################################################################
    def build_blueprint_from_file(self):
        blueprint_IO = BlueprintDataIO(dirpath=self.dirpath)
        blueprint_IO.get_blueprint_data_from_file()
        self.blueprint = blueprint_IO.create_blueprint_from_data()


    ####################################################################################################################
    def build_armature_in_scene(self, armature_data):
        create_enter_namespace(nom.setupRigNamespace)
        self.scene_armature = armature_data.populate_armature()
        return_to_root_namespace()


    ####################################################################################################################
    def gather_and_export_prefab_blueprint_data(self):
        prefab_blueprint = self.gather_prefab_blueprint_data()
        self.export_prefab_blueprint_data(prefab_blueprint)


    ####################################################################################################################
    def gather_prefab_blueprint_data(self):
        print('Gathering prefab blueprint data...')
        prefab_blueprint = PrefabBlueprint(prefab_key=self.prefab_key)
        return prefab_blueprint


    ####################################################################################################################
    def export_prefab_blueprint_data(self, prefab_blueprint):
        blueprint_IO = BlueprintDataIO(blueprint=prefab_blueprint, dirpath=self.dirpath)
        blueprint_IO.save()


    ####################################################################################################################
    def build_rig_in_scene(self, scene_armature):
        self.update_placer_positions()
        return
        create_enter_namespace(nom.finalRigNamespace)
        self.build_rig(scene_armature)
        #...Put a bow on this puppy!
        rigWrapup.execute(modules=self.rig.modules)


    ####################################################################################################################
    def build_rig(self, scene_armature):
        print(f"{'-'*120}\nBuilding rig from armature...")
        self.rig = Rig(name=self.asset_name, armature=scene_armature)
        self.rig.populate_rig(dirpath=self.dirpath)


    ####################################################################################################################
    '''def export_armature_data(self):
        armature_IO = ArmatureDataIO(armature=self.armature_data, dirpath=self.dirpath)
        armature_IO.save()'''


    ####################################################################################################################
    def update_placer_positions(self):
        with open(self.dirpath+'/module_roster.json', 'r') as fh:
            module_roster = json.load(fh)
        for module_key in module_roster:
            module_directory = self.dirpath + '/rig_modules/' + module_key
            with open(module_directory + '/placers.json', 'r') as fh:
                placers_data = json.load(fh)
                placers_IO = PlacerDataIO(data=placers_data)
                module_placers = placers_IO.get_placers_from_data()

            for i, p in enumerate(module_placers):
                module_placers[i].get_scene_placer()
                module_placers[i].update_data_from_scene()
            placers_IO = PlacerDataIO(placers=module_placers, dirpath=module_directory)
            placers_IO.save()
