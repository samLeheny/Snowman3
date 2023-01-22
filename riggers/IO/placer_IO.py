# Title: armature_module_IO.py
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





class PlacerDataIO(object):

    def __init__(
        self,
        module_key,
        placers,
        dirpath
    ):

        self.dirpath = dirpath
        self.placers = placers
        self.placer_data = None
        self.module_key = module_key
        self.dirpath = dirpath
        self.file = f'{self.module_key}_placers.json'





    ####################################################################################################################
    def prep_data_for_export(self):

        self.placer_data = {}
        for placer in self.placers:
            placer_data_dict = placer.get_data_dictionary()
            self.placer_data[placer.name] = placer_data_dict






    ####################################################################################################################
    def save(self):

        self.prep_data_for_export() if not self.placer_data else None
        with open(f'{self.dirpath}/{self.file}', 'w') as fh:
            json.dump(self.placer_data, fh, indent=5)
