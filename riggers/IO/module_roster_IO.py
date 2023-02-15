# Title: module_roster_IO.py
# Author: Sam Leheny
# Contact: samleheny@live.com

# Description:


###########################
##### Import Commands #####
import importlib

import Snowman3.riggers.utilities.classes.class_ModuleRoster as class_moduleRoster
importlib.reload(class_moduleRoster)
ModuleRoster = class_moduleRoster.ModuleRoster

import Snowman3.riggers.IO.data_IO as classDataIO
importlib.reload(classDataIO)
DataIO = classDataIO.DataIO
###########################
###########################

###########################
######## Variables ########
default_file_name = 'module_roster.json'
###########################
###########################





########################################################################################################################
class ModuleRosterDataIO( DataIO ):
    def __init__(
        self,
        data = None,
        module_names = None,
        dirpath = None,
        file_name = default_file_name
    ):
        super().__init__(data=data, dirpath=dirpath, file_name=file_name)
        self.module_roster = module_names



    ####################################################################################################################
    def prep_data_for_export(self):
        self.data = self.module_roster



    ####################################################################################################################
    def save(self):
        self.prep_data_for_export() if not self.data else None
        self.save_data_to_file(self.data)



    ####################################################################################################################
    def create_module_roster_from_data(self, data):
        self.module_roster = data
        return self.module_roster
