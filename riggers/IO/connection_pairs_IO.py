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
        connection_pairs,
        dirpath
    ):
        self.dirpath = dirpath
        self.connection_pairs = connection_pairs
        self.connection_pairs_data = None
        self.dirpath = dirpath
        self.file = 'connection_pairs.json'





    ####################################################################################################################
    def prep_data_for_export(self):

        self.connection_pairs_data = []
        for pair in self.connection_pairs:
            self.connection_pairs_data.append(pair.get_data_list())





    ####################################################################################################################
    def save(self):

        self.prep_data_for_export() if not self.connection_pairs_data else None
        with open(f'{self.dirpath}/{self.file}', 'w') as fh:
            json.dump(self.connection_pairs_data, fh, indent=5)
