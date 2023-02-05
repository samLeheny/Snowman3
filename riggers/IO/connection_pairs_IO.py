# Title: connection_pairs_IO.py
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

import Snowman3.riggers.utilities.classes.class_ConnectionPair as class_moduleConnection
importlib.reload(class_moduleConnection)
ModuleConnection = class_moduleConnection.ConnectionPair
###########################
###########################

###########################
######## Variables ########

###########################
###########################





########################################################################################################################
class ConnectionPairsDataIO(object):

    def __init__(
        self,
        connection_pairs = None,
        dirpath = None
    ):
        self.dirpath = dirpath
        self.connection_pairs = connection_pairs
        self.input_data = None
        self.dirpath = dirpath
        self.file = 'connection_pairs.json'
        self.filepath = f'{self.dirpath}/{self.file}'





    ####################################################################################################################
    def prep_data_for_export(self):

        self.input_data = []
        for pair in self.connection_pairs:
            self.input_data.append(pair.get_data_list())





    ####################################################################################################################
    def save(self):

        self.prep_data_for_export() if not self.input_data else None
        with open(f'{self.dirpath}/{self.file}', 'w') as fh:
            json.dump(self.input_data, fh, indent=5)



    ####################################################################################################################
    def get_data_from_file(self):

        if not os.path.exists(self.filepath):
            print('ERROR: Provided file path not found on disk.')
            return False

        with open(self.filepath, 'r') as fh:
            self.input_data = json.load(fh)

        return self.input_data



    ####################################################################################################################
    def create_connection_pairs_from_data(self, data):

        connection_pairs = []

        for connection_dict in data:
            connection_pairs.append(ModuleConnection(
                output_socket = connection_dict['output_socket'],
                input_socket = connection_dict['input_socket']
            ))

        return connection_pairs
