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
decimal_count = 9
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

            ctrls_data_dict = {}

            # ...
            IO_data_fields = (('name', ctrl.name),
                              ('shape', ctrl.shape),
                              ('size', ctrl.size),
                              ('shape_offset', ctrl.shape_offset),
                              ('color', ctrl.color),
                              ('position', ctrl.position),
                              ('position_weights', ctrl.position_weights),
                              ('orientation', ctrl.orientation),
                              ('locks', ctrl.locks),
                              ('forward_direction', ctrl.forward_direction),
                              ('up_direction', ctrl.up_direction),
                              ('is_driven_side', ctrl.is_driven_side),
                              ('body_module', ctrl.body_module),
                              ('match_transform', ctrl.match_transform),
                              ('side', ctrl.side))

            for IO_key, input_attr in IO_data_fields:
                ctrls_data_dict[IO_key] = input_attr
            self.ctrls_data[ctrl_key] = ctrls_data_dict





    ####################################################################################################################
    def save(self):

        self.prep_data_for_export() if not self.ctrls_data else None
        with open(f'{self.dirpath}/{self.file}', 'w') as fh:
            json.dump(self.ctrls_data, fh, indent=5)
