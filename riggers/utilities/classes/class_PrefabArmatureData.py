# Title: class_PrefabArmatureData.py
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
prefabs_dir = 'Snowman3.riggers.prefab_blueprints'
###########################
###########################




########################################################################################################################
class PrefabArmatureData:
    def __init__(
        self,
        prefab_key,
        prefab_armature_dir = prefabs_dir,
        symmetry_mode = None,
        rig_modules = None
    ):
        self.prefab_dir = prefab_armature_dir
        self.prefab_key = prefab_key
        self.symmetry_mode = symmetry_mode
        self.rig_modules = rig_modules
        self.armature = None
        self.modules = None
        self.attr_handoffs = None
        self.module_connections = None
        self.space_blends = None
        self.placer_connectors = None



    ####################################################################################################################
    def find_py_module(self, name):
        return importlib.import_module(f'{self.prefab_dir}.{self.prefab_key}.{name}')


    ####################################################################################################################
    def get_armature(self):
        m = self.find_py_module('armature')
        self.armature = m.create_armature(symmetry_mode=self.symmetry_mode, modules=self.get_rig_modules(),
                                          placer_connectors=self.get_placer_connectors())
        return self.armature


    ####################################################################################################################
    def get_rig_modules(self):
        m = self.find_py_module('modules')
        self.modules = m.create_modules(symmetry_mode=self.symmetry_mode)
        return self.modules


    ####################################################################################################################
    def get_attr_handoffs(self):
        m = self.find_py_module('attr_handoffs')
        self.attr_handoffs = m.create_handoffs()
        return self.attr_handoffs


    ####################################################################################################################
    def get_module_connections(self):
        m = self.find_py_module('connection_pairs')
        self.module_connections = m.create_connection_pairs_dict(self.rig_modules)
        return self.module_connections


    ####################################################################################################################
    def get_space_blends(self):
        m = self.find_py_module('space_blends')
        self.space_blends = m.create_space_blends(self.rig_modules)
        return self.space_blends


    ####################################################################################################################
    def get_placer_connectors(self):
        m = self.find_py_module('placer_connectors')
        self.placer_connectors = m.create_placer_connectors()
        return self.placer_connectors
