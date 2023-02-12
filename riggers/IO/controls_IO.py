# Title: controls_IO.py
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
default_file_name = 'controls.json'
###########################
###########################





########################################################################################################################
class ControlsDataIO( DataIO ):
    def __init__(
        self,
        data = None,
        ctrls = None,
        dirpath = None,
        file_name = default_file_name
    ):
        super().__init__(data=data, dirpath=dirpath, file_name=file_name)
        self.ctrls = ctrls



    ####################################################################################################################
    def prep_data_for_export(self):
        self.data = {}
        for ctrl_key, ctrl in self.ctrls.items():
            ctrls_data_dict = ctrl.get_data_dictionary()
            self.data[ctrl_key] = ctrls_data_dict



    ####################################################################################################################
    def save(self):
        self.prep_data_for_export() if not self.data else None
        self.save_data_to_file(self.data)
