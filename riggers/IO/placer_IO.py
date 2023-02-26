# Title: placer_IO.py
# Author: Sam Leheny
# Contact: samleheny@live.com

# Description:


###########################
##### Import Commands #####
import importlib
import pymel.core as pm

import Snowman3.riggers.IO.data_IO as classDataIO
importlib.reload(classDataIO)
DataIO = classDataIO.DataIO

import Snowman3.riggers.utilities.classes.class_Placer as classPlacer
importlib.reload(classPlacer)
Placer = classPlacer.Placer
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
    def get_placers_from_data(self):
        self.placers = []
        for key, data in self.data.items():
            placer = Placer(
                name = data['name'],
                side = data['side'],
                position = data['position'],
                size = data['size'],
                vector_handle_data = data['vector_handle_data'],
                orienter_data = data['orienter_data'],
                connect_targets = data['connect_targets']
            )
            self.placers.append(placer)
        return self.placers



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
