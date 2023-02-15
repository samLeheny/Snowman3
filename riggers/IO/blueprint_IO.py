# Title: blueprint_IO.py
# Author: Sam Leheny
# Contact: samleheny@live.com

# Description:


###########################
##### Import Commands #####
import importlib
import pymel.core as pm
import json
import os

import Snowman3.riggers.IO.armature_IO as armature_IO
importlib.reload(armature_IO)
ArmatureDataIO = armature_IO.ArmatureDataIO

import Snowman3.riggers.IO.attr_handoffs_IO as attr_handoffs_IO
importlib.reload(attr_handoffs_IO)
AttrHandoffsDataIO = attr_handoffs_IO.AttrHandoffsDataIO

import Snowman3.riggers.IO.connection_pairs_IO as connection_pairs_IO
importlib.reload(connection_pairs_IO)
ModuleConnectionsDataIO = connection_pairs_IO.ConnectionPairsDataIO

import Snowman3.riggers.IO.space_blends_IO as space_blends_IO
importlib.reload(space_blends_IO)
SpaceBlendsDataIO = space_blends_IO.SpaceBlendsDataIO

import Snowman3.riggers.IO.placerConnectors_IO as placerConnectors_IO
importlib.reload(placerConnectors_IO)
PlacerConnectorsDataIO = placerConnectors_IO.PlacerConnectorsDataIO

import Snowman3.riggers.IO.rig_module_IO as rigModule_IO
importlib.reload(rigModule_IO)
RigModuleDataIO = rigModule_IO.RigModuleDataIO

import Snowman3.riggers.utilities.classes.class_Blueprint as class_blueprint
importlib.reload(class_blueprint)
Blueprint = class_blueprint.Blueprint

import Snowman3.riggers.IO.module_roster_IO as module_roster_IO
importlib.reload(module_roster_IO)
ModuleRosterDataIO = module_roster_IO.ModuleRosterDataIO
###########################
###########################



###########################
######## Variables ########
decimal_count = 9
###########################
###########################





########################################################################################################################
class BlueprintDataIO:

    def __init__(
        self,
        blueprint = None,
        dirpath = None,
    ):
        self.blueprint = blueprint
        self.dirpath = dirpath
        self.IOs = {}
        self.input_data = {}



    ####################################################################################################################
    ################################################### OUTPUT #########################################################
    ####################################################################################################################

    ####################################################################################################################
    def export_armature_data(self):

        data_IOs = {
            'armature': ArmatureDataIO(armature=self.blueprint.armature, dirpath=self.dirpath),
            'attr_handoffs': AttrHandoffsDataIO(attr_handoffs=self.blueprint.attr_handoffs, dirpath=self.dirpath),
            'module_connectors': ModuleConnectionsDataIO(connection_pairs=self.blueprint.module_connectors,
                                                         dirpath=self.dirpath),
            'space_blends': SpaceBlendsDataIO(space_blends=self.blueprint.space_blends, dirpath=self.dirpath),
            'placer_connectors': PlacerConnectorsDataIO(placer_connectors=self.blueprint.placer_connectors,
                                                        dirpath=self.dirpath),
            'module_roster': ModuleRosterDataIO(module_names=self.blueprint.rig_modules_roster, dirpath=self.dirpath)
        }
        [IO.save() for IO in data_IOs.values()]

        print("\nCollected data packages:")  # _
        print(" - Armature data")  # _
        print(data_IOs['armature'])  # _
        print(" - Attr Handoffs data")  # _
        print(data_IOs['attr_handoffs'])  # _
        print(" - Module Connections data")  # _
        print(data_IOs['module_connectors'])  # _
        print(" - Space Blends data")  # _
        print(data_IOs['space_blends'])  # _
        print(" - Placer Connectors data")  # _
        print(data_IOs['placer_connectors'])  # _
        print(" - Module Roster data")  # _
        print(data_IOs['module_roster'])  # _



    ####################################################################################################################
    def export_modules_data(self):

        module_data_IOs = {}
        for key, rig_module in self.blueprint.rig_modules.items():
            print(f"{key}  -  {rig_module}")  # _
            IO = RigModuleDataIO(dirpath=self.dirpath, rig_module=rig_module, module_key=key)
            IO.get_prefab_module_data()
            module_data_IOs[f'{key}_rig_module'] = IO
        [IO.save() for IO in module_data_IOs.values()]

        print("\nBlueprint data export complete!")#_



    ####################################################################################################################
    def save(self):

        print('\nExporting blueprint data to external file...')#_
        self.export_armature_data()
        print("\nExporting module data...")#_
        self.export_modules_data()



    ####################################################################################################################
    ################################################### INPUT ##########################################################
    ####################################################################################################################

    ####################################################################################################################
    def get_blueprint_data_from_file(self):

        for key, IO_type in (('armature', ArmatureDataIO),
                             ('attr_handoffs', AttrHandoffsDataIO),
                             ('module_connections', ModuleConnectionsDataIO),
                             ('placer_connectors', PlacerConnectorsDataIO),
                             ('space_blends', SpaceBlendsDataIO),
                             ('rig_modules_roster', ModuleRosterDataIO)):
            self.IOs[key] = IO_type(dirpath=self.dirpath)
            self.input_data[key] = self.IOs[key].get_data_from_file()

        self.get_modules_data_from_file()



    ####################################################################################################################
    def get_modules_data_from_file(self):

        self.input_data['modules'] = {}
        module_dir_names = list(os.walk(f'{self.dirpath}/rig_modules'))[0][1]
        for dir_name in module_dir_names:
            module_dir = f'{self.dirpath}/rig_modules/{dir_name}'
            module_IO = RigModuleDataIO(dirpath=module_dir)

            module_data = module_IO.get_module_data_from_file()
            module_key = list(module_data)[0]
            self.input_data['modules'][module_key] = module_data[module_key]



    ####################################################################################################################
    def create_blueprint_from_data(self):

        armature_data = self.input_data['armature']
        armature_data['modules'] = self.input_data['modules']
        armature = self.IOs['armature'].create_armature_from_data(armature_data)

        attr_handoffs = self.IOs['attr_handoffs'].create_handoffs_from_data(self.input_data['attr_handoffs'])

        module_connections = self.IOs['module_connections'].create_connection_pairs_from_data(
            self.input_data['module_connections'])

        placer_connectors = self.IOs['placer_connectors'].create_connectors_from_data(
            self.input_data['placer_connectors'])

        space_blends = self.IOs['space_blends'].create_blends_from_data(self.input_data['space_blends'])

        rig_modules_roster = self.IOs['rig_modules_roster'].create_module_roster_from_data(
            self.input_data['rig_modules_roster'])

        blueprint = Blueprint(armature = armature,
                              attr_handoffs = attr_handoffs,
                              module_connections = module_connections,
                              placer_connectors = placer_connectors,
                              space_blends = space_blends,
                              rig_modules_roster = rig_modules_roster)

        return blueprint
