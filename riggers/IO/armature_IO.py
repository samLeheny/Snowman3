# Title: armature_IO.py
# Author: Sam Leheny
# Contact: samleheny@live.com

# Description:


###########################
##### Import Commands #####
import importlib
import pymel.core as pm
import json
import os

import Snowman3.riggers.utilities.classes.class_Armature as class_armature
importlib.reload(class_armature)
Armature = class_armature.Armature
###########################
###########################

###########################
######## Variables ########

###########################
###########################





########################################################################################################################
class ArmatureDataIO(object):

    def __init__(
        self,
        armature = None,
        dirpath = None,
    ):
        self.armature = armature
        self.input_data = {}
        self.dirpath = dirpath
        self.filepaths = {'armature': f'{self.dirpath}/armature_data.json',
                          'modules': f'{self.dirpath}/rig_modules'}
        self.scene_armature = None



    ####################################################################################################################
    def find_armature_in_scene(self):

        found_armatures = pm.ls("::*_ARMATURE", type="transform")
        self.scene_armature = found_armatures[0] if found_armatures else None



    ####################################################################################################################
    def get_data_from_file(self):

        self.input_data = self.get_armature_data_from_file()
        self.input_data['modules'] = self.get_modules_data_from_file()
        return self.input_data



    ####################################################################################################################
    def get_armature_data_from_file(self):

        filepath = self.filepaths['armature']

        if not os.path.exists(filepath):
            print(f'ERROR: Provided file "{filepath}" path not found on disk.')
            return False

        with open(self.filepaths['armature'], 'r') as fh:
            self.input_data = json.load(fh)

        return self.input_data



    ####################################################################################################################
    def get_modules_data_from_file(self):

        filepath = self.filepaths['modules']

        if not os.path.exists(filepath):
            print(f'ERROR: Provided file "{filepath}" path not found on disk.')
            return False

        return "placeholder"



    ####################################################################################################################
    def get_armature_data_from_scene(self):

        self.find_armature_in_scene() if not self.scene_armature else None

        #...Fill in armature data based on values stored in hidden armature attributes
        IO_data_fields = (('name', 'ArmatureName'),
                          ('prefab_key', 'ArmaturePrefabKey'),
                          ('symmetry_mode', 'SymmetryMode'),
                          ('driver_side', 'DriverSide'),
                          ('root_size', 'RootSize'),
                          ('armature_scale', 'ArmatureScale'))
        for IO_key, attr_name in IO_data_fields:
            if not pm.attributeQuery(attr_name, node=self.scene_armature, exists=1):
                pm.error(f'Could not get armature data attr "{attr_name}" from scene armature root.'
                         f'Attribute not found.')
            self.input_data[IO_key] = pm.getAttr(f'{self.scene_armature}.{attr_name}')



    ####################################################################################################################
    def get_armature_data_from_armature(self):

        self.input_data = {'name': self.armature.name,
                           'prefab_key': self.armature.prefab_key,
                           'symmetry_mode': self.armature.symmetry_mode,
                           'root_size': self.armature.root_size,
                           'armature_scale': self.armature.armature_scale}



    ####################################################################################################################
    def save(self):

        self.get_armature_data_from_armature()
        with open(self.filepaths['armature'], 'w') as fh:
            json.dump(self.input_data, fh, indent=5)



    ####################################################################################################################
    def load(self):

        #...
        if not os.path.exists(self.filepaths['armature']):
            print('ERROR: Provided file path not found on disk.')
            return False

        #...Read data
        with open(self.filepaths['armature'], 'r') as fh:
            data = json.load(fh)

        return data



    ####################################################################################################################
    def create_armature_from_data(self, data):

        armature = Armature(
            name = data['name'],
            prefab_key = data['prefab_key'],
            root_size = data['root_size'],
            symmetry_mode = data['symmetry_mode'],
            armature_scale = data['armature_scale'],
            modules = data['modules']
        )

        return armature
