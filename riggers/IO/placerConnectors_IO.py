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
        module_key,
        placer_connectors,
        dirpath
    ):

        self.dirpath = dirpath
        self.placer_connectors = placer_connectors
        self.connectors_data = None
        self.module_key = module_key
        self.dirpath = dirpath
        self.file = f'{self.module_key}_placer_connectors.json'





    ####################################################################################################################
    def prep_data_for_export(self):

        self.connectors_data = {}
        for connector in self.placer_connectors:

            if connector.source_placer_key in self.connectors_data.keys():
                self.connectors_data[connector.source_placer_key].append([connector.destination_module_key,
                                                                          connector.destination_placer_key])
            else:
                self.connectors_data[connector.source_placer_key] = [[connector.destination_module_key,
                                                                      connector.destination_placer_key]]






    ####################################################################################################################
    def save(self):

        self.prep_data_for_export() if not self.connectors_data else None
        with open(f'{self.dirpath}/{self.file}', 'w') as fh:
            json.dump(self.connectors_data, fh, indent=5)
