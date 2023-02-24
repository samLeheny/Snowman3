# Title: class_PrefabBlueprint.py
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
default_prefabs_dir = 'Snowman3.riggers.prefab_blueprints'
###########################
###########################





########################################################################################################################
class PrefabBlueprint:
    def __init__(
        self,
        prefab_key,
        prefab_dir = None
    ):
        self.prefab_key = prefab_key
        self.prefab_dir = prefab_dir if prefab_dir else default_prefabs_dir

        self.armature = self.get_armature()
        self.rig_modules = self.get_rig_modules()
        self.rig_modules_roster = self.get_rig_modules_roster()
        self.attr_handoffs = self.get_attr_handoffs()
        self.module_connectors = self.get_module_connections()
        self.space_blends = self.get_space_blends()
        self.placer_connectors = self.get_placer_connectors()



    ####################################################################################################################
    def find_py_module(self, name):
        return importlib.import_module(f'{self.prefab_dir}.{self.prefab_key}.{name}')


    ####################################################################################################################
    def get_armature(self):
        m = self.find_py_module('armature')
        return m.create_armature()


    ####################################################################################################################
    def get_rig_modules(self):
        m = self.find_py_module('modules')
        return m.create_modules()


    ####################################################################################################################
    def get_rig_modules_roster(self):
        return [key for key in self.rig_modules]


    ####################################################################################################################
    def get_attr_handoffs(self):
        m = self.find_py_module('attr_handoffs')
        return m.create_handoffs()


    ####################################################################################################################
    def get_module_connections(self):
        m = self.find_py_module('connection_pairs')
        return m.create_connection_pairs_dict()


    ####################################################################################################################
    def get_space_blends(self):
        m = self.find_py_module('space_blends')
        return m.create_space_blends()


    ####################################################################################################################
    def get_placer_connectors(self):
        m = self.find_py_module('placer_connectors')
        return m.create_placer_connectors()