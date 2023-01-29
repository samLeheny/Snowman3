# Title: controls_IO.py
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





class ControlsDataIO(object):

    def __init__(
        self,
        module_key,
        ctrls,
        dirpath
    ):

        self.dirpath = dirpath
        self.ctrls = ctrls
        self.ctrls_data = None
        self.module_key = module_key
        self.dirpath = dirpath
        self.file = f'{self.module_key}_controls.json'





    ####################################################################################################################
    def prep_data_for_export(self):

        self.ctrls_data = {}
        for ctrl_key, ctrl in self.ctrls.items():
            ctrls_data_dict = ctrl.get_data_dictionary()
            self.ctrls_data[ctrl_key] = ctrls_data_dict





    ####################################################################################################################
    def save(self):

        self.prep_data_for_export() if not self.ctrls_data else None
        with open(f'{self.dirpath}/{self.file}', 'w') as fh:
            json.dump(self.ctrls_data, fh, indent=5)