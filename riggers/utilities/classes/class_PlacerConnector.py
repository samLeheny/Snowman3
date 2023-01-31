# Title: class_PlacerConnector.py
# Author: Sam Leheny
# Contact: samleheny@live.com

# Description:


###########################
##### Import Commands #####
import importlib
import pymel.core as pm

import Snowman3.utilities.rig_utils as rig_utils
importlib.reload(rig_utils)
###########################
###########################


###########################
######## Variables ########

###########################
###########################





########################################################################################################################
class PlacerConnector:
    def __init__(
        self,
        source_module_key: str,
        source_placer_key: str,
        destination_module_key: str,
        destination_placer_key: str
    ):
        self.source_module_key = source_module_key
        self.source_placer_key = source_placer_key
        self.destination_module_key = destination_module_key
        self.destination_placer_key = destination_placer_key





    ####################################################################################################################
    def get_end_nodes(self, source_module):

        end_1_node = source_module.placers[self.source_placer_key].mobject

        target_module_ctrl = source_module.get_other_module(name=self.destination_module_key, return_module_ctrl=True)
        end_2_node = pm.listConnections(f'{target_module_ctrl}.PlacerNodes.{self.destination_placer_key}', source=1)[0]

        return end_1_node, end_2_node





    ####################################################################################################################
    def create_connector(self, source_module, parent):

        end_1_node, end_2_node = self.get_end_nodes(source_module)

        rig_utils.connector_curve(
            name = self.source_placer_key,
            line_width = 1.5,
            end_driver_1 = end_1_node,
            end_driver_2 = end_2_node,
            override_display_type = 2,
            parent = parent,
            inheritsTransform = False
        )





    ####################################################################################################################
    def get_data_list(self):

        data_dict = {'source_module_key': self.source_module_key,
                     'source_placer_key': self.source_placer_key,
                     'destination_module_key': self.destination_module_key,
                     'destination_placer_key': self.destination_placer_key}

        return data_dict
