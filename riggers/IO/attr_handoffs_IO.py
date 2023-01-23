# Title: attr_handoffs_IO.py
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
class AttrHandoffsDataIO(object):

    def __init__(
        self,
        attr_handoffs,
        dirpath
    ):
        self.dirpath = dirpath
        self.attr_handoffs = attr_handoffs
        self.attr_handoffs_data = None
        self.dirpath = dirpath
        self.file = 'attr_handoffs.json'





    ####################################################################################################################
    def prep_data_for_export(self):

        self.attr_handoffs_data = []
        for handoff in self.attr_handoffs:
            self.attr_handoffs_data.append(handoff.get_data_list())





    ####################################################################################################################
    def save(self):

        self.prep_data_for_export() if not self.attr_handoffs_data else None
        with open(f'{self.dirpath}/{self.file}', 'w') as fh:
            json.dump(self.attr_handoffs_data, fh, indent=5)
