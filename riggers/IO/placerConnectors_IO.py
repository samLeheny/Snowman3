# Title: placerConnectors_IO.py
# Author: Sam Leheny
# Contact: samleheny@live.com

# Description:


###########################
##### Import Commands #####
import importlib

import Snowman3.riggers.utilities.armature_utils as amtr_utils
import Snowman3.utilities.general_utils as gen_utils
import Snowman3.utilities.general_utils as rig_utils
importlib.reload(amtr_utils)
importlib.reload(gen_utils)
importlib.reload(rig_utils)

import Snowman3.riggers.utilities.classes.class_PlacerConnector as class_placerConnector
importlib.reload(class_placerConnector)
PlacerConnector = class_placerConnector.PlacerConnector

import Snowman3.riggers.IO.data_IO as classDataIO
importlib.reload(classDataIO)
DataIO = classDataIO.DataIO
###########################
###########################

###########################
######## Variables ########
default_file_name = 'placer_connectors.json'
###########################
###########################





########################################################################################################################





class PlacerConnectorsDataIO( DataIO ):
    def __init__(
        self,
        data = None,
        placer_connectors = None,
        dirpath = None,
        file_name = default_file_name
    ):
        super().__init__(data=data, dirpath=dirpath, file_name=file_name)
        self.placer_connectors = placer_connectors



    ####################################################################################################################
    def prep_data_for_export(self):

        self.data = []
        for connector in self.placer_connectors:
            self.data.append(connector.get_data_list())



    ####################################################################################################################
    def save(self):
        self.prep_data_for_export() if not self.data else None
        self.save_data_to_file(self.data)



    ####################################################################################################################
    def create_connectors_from_data(self, data):

        connectors = []

        for connector_dict in data:
            connectors.append(PlacerConnector(
                source_module_key = connector_dict['source_module_key'],
                source_placer_key = connector_dict['source_placer_key'],
                destination_module_key = connector_dict['destination_module_key'],
                destination_placer_key = connector_dict['destination_placer_key']
            ))

        return connectors
