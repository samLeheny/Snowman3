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
ModuleConnectorsDataIO = connection_pairs_IO.ConnectionPairsDataIO

import Snowman3.riggers.IO.space_blends_IO as space_blends_IO
importlib.reload(space_blends_IO)
SpaceBlendsDataIO = space_blends_IO.SpaceBlendsDataIO

import Snowman3.riggers.IO.placerConnectors_IO as placerConnectors_IO
importlib.reload(placerConnectors_IO)
PlacerConnectorsDataIO = placerConnectors_IO.PlacerConnectorsDataIO

import Snowman3.riggers.IO.rig_module_IO as rigModule_IO
importlib.reload(rigModule_IO)
RigModuleDataIO = rigModule_IO.RigModuleDataIO
###########################
###########################



###########################
######## Variables ########
decimal_count = 9
###########################
###########################





########################################################################################################################
class BlueprintDataIO(object):

    def __init__(
        self,
        blueprint = None,
        dirpath = None,
    ):
        self.blueprint = blueprint
        self.blueprint_data = {}
        self.dirpath = f'{dirpath}/test_build'



    ####################################################################################################################
    def save(self):

        data_IOs = {
            'armature': ArmatureDataIO(armature=self.blueprint.armature, dirpath=self.dirpath),
            'attr_handoffs': AttrHandoffsDataIO(attr_handoffs=self.blueprint.attr_handoffs, dirpath=self.dirpath),
            'module_connectors': ModuleConnectorsDataIO(connection_pairs=self.blueprint.module_connectors,
                                                      dirpath=self.dirpath),
            'space_blends': SpaceBlendsDataIO(space_blends=self.blueprint.space_blends, dirpath=self.dirpath),
            'placer_connectors': PlacerConnectorsDataIO(placer_connectors=self.blueprint.placer_connectors,
                                                        dirpath=self.dirpath)
        }

        for key, rig_module in self.blueprint.rig_modules.items():
            IO = RigModuleDataIO(rig_module=rig_module, module_key=key)
            data_IOs[f'{key}_rig_module'] = IO

        [IO.save() for IO in data_IOs.values()]