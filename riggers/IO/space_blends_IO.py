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
        space_blends,
        dirpath
    ):
        self.dirpath = dirpath
        self.space_blends = space_blends
        self.space_blends_data = None
        self.dirpath = dirpath
        self.file = 'space_blends.json'





    ####################################################################################################################
    def prep_data_for_export(self):

        self.space_blends_data = []
        for handoff in self.space_blends:
            self.space_blends_data.append(handoff.get_data_list())





    ####################################################################################################################
    def save(self):

        self.prep_data_for_export() if not self.space_blends_data else None
        with open(f'{self.dirpath}/{self.file}', 'w') as fh:
            json.dump(self.space_blends_data, fh, indent=5)
