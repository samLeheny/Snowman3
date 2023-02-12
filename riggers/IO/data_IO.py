# Title: data_IO.py
# Author: Sam Leheny
# Contact: samleheny@live.com

# Description:


###########################
##### Import Commands #####
import json
import os
###########################
###########################

###########################
######## Variables ########

###########################
###########################



########################################################################################################################
class DataIO:

    def __init__(
        self,
        data = None,
        dirpath = None,
        file_name = None,
    ):
        self.data = data
        self.dirpath = dirpath
        self.file_name = file_name
        self.filepath = f'{self.dirpath}/{self.file_name}'



    ####################################################################################################################
    def validate_filepath(self):
        if not os.path.exists(self.filepath):
            print(f'ERROR: Provided file path "{self.filepath}" not found on disk.')
            return False
        return True



    ####################################################################################################################
    def get_data_from_file(self):

        if not self.validate_filepath():
            return False

        with open(self.filepath, 'r') as fh:
            self.data = json.load(fh)

        return self.data



    ####################################################################################################################
    def save_data_to_file(self, data=None):

        if not data: data = self.data

        if not self.validate_filepath():
            return False

        with open(self.filepath, 'w') as fh:
            json.dump(data, fh, indent=5)
