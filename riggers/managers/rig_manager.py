# Title: rig_manager.py
# Author: Sam Leheny
# Contact: samleheny@live.com

# Description:


###########################
##### Import Commands #####
import importlib

import Snowman3.riggers.utilities.placer_utils as placer_utils
importlib.reload(placer_utils)
OrienterManager = placer_utils.OrienterManager
###########################
###########################

###########################
######## Variables ########

###########################
###########################



########################################################################################################################
class RigManager:
    def __init__(
        self,
        blueprint_manager = None
    ):
        self.blueprint_manager = blueprint_manager


    def build_rig_from_armature(self):
        parts = self.blueprint_manager.blueprint.parts
        for key, part in parts.items():
            self.build_rig_part(part)


    def build_rig_part(self, part):
        dir_string = f"Snowman3.riggers.parts.{part.prefab_key}"
        getter = importlib.import_module(dir_string)
        importlib.reload(getter)
        BespokePartConstructor = getter.BespokePartConstructor

        part_manager = BespokePartConstructor(part_name = part.name, side = part.side)
        part_manager.build_rig_part(part)
