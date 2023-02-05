# Title: placerConnectors_IO.py
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
import Snowman3.riggers.utilities.armature_utils as amtr_utils
import Snowman3.utilities.general_utils as gen_utils
import Snowman3.utilities.general_utils as rig_utils
importlib.reload(amtr_utils)
importlib.reload(gen_utils)
importlib.reload(rig_utils)

import Snowman3.riggers.utilities.classes.class_PlacerConnector as class_placerConnector
importlib.reload(class_placerConnector)
PlacerConnector = class_placerConnector.PlacerConnector
###########################
###########################

###########################
######## Variables ########

###########################
###########################





########################################################################################################################





class PlacerConnectorsDataIO(object):

    def __init__(
        self,
        placer_connectors = None,
        dirpath = None
    ):

        self.dirpath = dirpath
        self.placer_connectors = placer_connectors
        self.input_data = None
        self.dirpath = dirpath
        self.file = 'placer_connectors.json'
        self.filepath = f'{self.dirpath}/{self.file}'





    ####################################################################################################################
    def prep_data_for_export(self):

        self.input_data = []
        for connector in self.placer_connectors:
            self.input_data.append(connector.get_data_list())



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
    def create_connectors_from_data(self, data):

        connectors = []

        for connector_dict in data:
            connectors.append(PlacerConnector(
                source_module_key = connector_dict['source_module_key'],
                source_placer_key = connector_dict['source_placer_key'],
                destination_module_key = connector_dict['destination_module_key'],
                destination_placer_key = connector_dict['destination_placer_key']
            ))

        return connectors
