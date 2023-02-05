# Title: attr_handoffs_IO.py
# Author: Sam Leheny
# Contact: samleheny@live.com

# Description:


###########################
##### Import Commands #####
import importlib
import pymel.core as pm
import json
import os

import Snowman3.riggers.utilities.classes.class_AttrHandoff as class_attr_handoff
importlib.reload(class_attr_handoff)
AttrHandoff = class_attr_handoff.AttrHandoff
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
        attr_handoffs = None,
        dirpath = None
    ):
        self.dirpath = dirpath
        self.attr_handoffs = attr_handoffs
        self.input_data = None
        self.dirpath = dirpath
        self.file = 'attr_handoffs.json'
        self.filepath = f'{self.dirpath}/{self.file}'





    ####################################################################################################################
    def prep_data_for_export(self):

        self.input_data = []
        for handoff in self.attr_handoffs:
            self.input_data.append(handoff.get_data_list())



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
    def create_handoffs_from_data(self, data):

        attr_handoffs = []

        for handoff_dict in data:
            attr_handoffs.append(AttrHandoff(
                old_attr_node = handoff_dict['old_attr_node'],
                new_attr_node = handoff_dict['new_attr_node'],
                delete_old_node = handoff_dict['delete_old_node']
            ))

        return attr_handoffs

