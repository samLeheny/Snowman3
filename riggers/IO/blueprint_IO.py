# Title: blueprint_IO.py
# Author: Sam Leheny
# Contact: samleheny@live.com

# Description:


###########################
##### Import Commands #####
import json
import importlib

import Snowman3.riggers.utilities.classes.class_Blueprint as class_Blueprint
importlib.reload(class_Blueprint)
Blueprint = class_Blueprint.Blueprint
###########################
###########################

###########################
######## Variables ########
core_data_filename = 'core_data'
###########################
###########################



########################################################################################################################
class BlueprintIO:
    def __init__(
        self,
        blueprint = None,
        data = None,
        dirpath = None,
    ):
        self.blueprint = blueprint
        self.data = data
        self.dirpath = dirpath


    ####################################################################################################################
    def save(self, dirpath):
        self.data_from_blueprint()
        filepath = f'{dirpath}/{core_data_filename}.json'
        print(f'\nExporting blueprint data to dir: {filepath}...')
        with open(filepath, 'w') as fh:
            json.dump(self.data, fh, indent=5)


    ####################################################################################################################
    def data_from_blueprint(self):
        self.data = {
            'asset_name': self.blueprint.asset_name,
            'dirpath': self.blueprint.dirpath,
            'loose_parts': self.blueprint.loose_parts
        }


    ####################################################################################################################
    def load(self, dirpath):
        self.data_from_file(dirpath)
        self.blueprint_from_data(self.data)
        return self.blueprint


    ####################################################################################################################
    def data_from_file(self, dirpath):
        with open(f'{dirpath}/{core_data_filename}.json', 'r') as fh:
            self.data = json.load(fh)


    ####################################################################################################################
    def blueprint_from_data(self, data):
        self.blueprint = Blueprint(
            asset_name = data['asset_name'],
            dirpath = data['dirpath'],
            loose_parts = data['loose_parts']
        )


    ####################################################################################################################
    def blueprint_from_file(self, dirpath):
        self.data_from_file(dirpath)
        self.blueprint_from_data(self.data)
        return self.blueprint
