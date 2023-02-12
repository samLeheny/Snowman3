# Title: placer_IO.py
# Author: Sam Leheny
# Contact: samleheny@live.com

# Description:


###########################
##### Import Commands #####
import importlib

import Snowman3.riggers.IO.data_IO as classDataIO
importlib.reload(classDataIO)
DataIO = classDataIO.DataIO
###########################
###########################

###########################
######## Variables ########
default_file_name = 'placers.json'
###########################
###########################





########################################################################################################################
class PlacerDataIO( DataIO ):
    def __init__(
        self,
        data = None,
        placers = None,
        dirpath = None,
        file_name = default_file_name
    ):
        super().__init__(data=data, dirpath=dirpath, file_name=file_name)
        self.placers = placers



    ####################################################################################################################
    def prep_data_for_export(self):
        self.data = {}
        for placer in self.placers:
            placer_data_dict = placer.get_data_dictionary()
            self.data[placer.name] = placer_data_dict



    ####################################################################################################################
    def save(self):
        self.prep_data_for_export() if not self.data else None
        self.save_data_to_file(self.data)
