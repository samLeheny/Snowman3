# Title: class_PrefabModuleData.py
# Author: Sam Leheny
# Contact: samleheny@live.com

# Description:


###########################
##### Import Commands #####
import importlib
###########################
###########################


###########################
######## Variables ########
prefabs_dir = 'Snowman3.riggers.modules'
###########################
###########################





########################################################################################################################
class PrefabModuleData:
    def __init__(
        self,
        prefab_key,
        prefab_module_dir = prefabs_dir,
        side = None
    ):
        self.prefab_dir = prefab_module_dir
        self.prefab_key = prefab_key
        self.side = side
        self.bespoke_setup = None
        self.placers = None
        self.ctrl_data = None

        self.get_placers()
        self.get_ctrl_data()
        self.get_bespoke_setup_py()



    ####################################################################################################################
    def find_py_module(self, name):
        return importlib.import_module(f'{self.prefab_dir}.{self.prefab_key}.{name}')


    ####################################################################################################################
    def get_bespoke_setup_py(self):
        m = self.find_py_module('setup.setup')
        self.bespoke_setup = m
        return self.bespoke_setup


    ####################################################################################################################
    def get_placers(self):
        m = self.find_py_module('data.placers')
        self.placers = m.create_placers(side=self.side)
        return self.placers


    ####################################################################################################################
    def get_ctrl_data(self):
        m = self.find_py_module('data.ctrl_data')
        self.ctrl_data = m.create_ctrl_data(side=self.side)
        return self.ctrl_data
