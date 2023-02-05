# Title: space_blends_IO.py
# Author: Sam Leheny
# Contact: samleheny@live.com

# Description:


###########################
##### Import Commands #####
import importlib
import pymel.core as pm
import maya.cmds as mc
import json
import os

import Snowman3.riggers.utilities.classes.class_SpaceBlend as class_spaceBlend
importlib.reload(class_spaceBlend)
SpaceBlend = class_spaceBlend.SpaceBlend
###########################
###########################

###########################
######## Variables ########

###########################
###########################





########################################################################################################################
class SpaceBlendsDataIO(object):

    def __init__(
        self,
        space_blends = None,
        dirpath = None
    ):
        self.dirpath = dirpath
        self.space_blends = space_blends
        self.input_data = None
        self.dirpath = dirpath
        self.file = 'space_blends.json'
        self.filepath = f'{self.dirpath}/{self.file}'





    ####################################################################################################################
    def prep_data_for_export(self):

        self.input_data = []
        for blend in self.space_blends:
            self.input_data.append(blend.get_data_list())



    ####################################################################################################################
    def get_data_from_file(self):

        if not os.path.exists(self.filepath):
            print('ERROR: Provided file path not found on disk.')
            return False

        with open(self.filepath, 'r') as fh:
            self.input_data = json.load(fh)

        return self.input_data



    ####################################################################################################################
    def save(self):

        self.prep_data_for_export() if not self.input_data else None
        with open(f'{self.dirpath}/{self.file}', 'w') as fh:
            json.dump(self.input_data, fh, indent=5)



    ####################################################################################################################
    def create_blends_from_data(self, data):

        blends = []

        for blend_dict in data:

            params = ('target', 'source', 'source_name', 'attr_node', 'global_space_parent', 'translate', 'rotate',
                      'scale', 'attr_name', 'name', 'type', 'default_value', 'side', 'reverse')

            for param in params:
                if not param in blend_dict: blend_dict[param] = None

            blends.append(SpaceBlend(
                target = blend_dict['target'],
                source = blend_dict['source'],
                source_name = blend_dict['source_name'],
                attr_node = blend_dict['attr_node'],
                global_space_parent = blend_dict['global_space_parent'],
                translate = blend_dict['translate'],
                rotate = blend_dict['rotate'],
                scale = blend_dict['scale'],
                attr_name = blend_dict['attr_name'],
                name = blend_dict['name'],
                type = blend_dict['type'],
                default_value = blend_dict['default_value'],
                side = blend_dict['side'],
                reverse = blend_dict['reverse']
            ))

        return blends
