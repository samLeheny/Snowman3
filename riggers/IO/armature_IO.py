# Title: armature_IO.py
# Author: Sam Leheny
# Contact: samleheny@live.com

# Description:


###########################
##### Import Commands #####
import pymel.core as pm
import json
import os
###########################
###########################

###########################
######## Variables ########
decimal_count = 9
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
        self.armature_data = {}
        self.dirpath = dirpath
        self.filepath = f'{self.dirpath}/test_armature_data.json'
        self.scene_armature = None



    ####################################################################################################################
    def find_armature_in_scene(self):

        found_armatures = pm.ls("::*_ARMATURE", type="transform")
        self.scene_armature = found_armatures[0] if found_armatures else None



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
            self.armature_data[IO_key] = pm.getAttr(f'{self.scene_armature}.{attr_name}')



    ####################################################################################################################
    def get_armature_data_from_armature(self):

        #...
        IO_data_fields = (('name', self.armature.name),
                          ('prefab_key', self.armature.prefab_key),
                          ('symmetry_mode', self.armature.symmetry_mode),
                          ('driver_side', self.armature.driver_side),
                          ('root_size', self.armature.root_size),
                          ('armature_scale', self.armature.armature_scale))
        for IO_key, input_attr in IO_data_fields:
            self.armature_data[IO_key] = input_attr



    ####################################################################################################################
    def save(self):

        #self.get_armature_data_from_scene() if not self.armature_data else None
        self.get_armature_data_from_armature()
        with open(self.filepath, 'w') as fh:
            json.dump(self.armature_data, fh, indent=5)



    ####################################################################################################################
    def load(self):

        #...
        if not os.path.exists(self.filepath):
            print('ERROR: Provided file path not found on disk.')
            return False

        #...Read data
        with open(self.filepath, 'r') as fh:
            data = json.load(fh)

        return data



    ####################################################################################################################
    def build_armature_data_from_file(self):
        pass
    '''
        data = self.load()
        armature = Armature(name=data['name'],
                            prefab_key=data['prefab_key'],
                            root_size=data['root_size'],
                            symmetry_mode=data['symmetry_mode'],
                            modules=data['modules'])

        return armature
    '''
