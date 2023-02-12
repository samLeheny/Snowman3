# Title: connection_pairs_IO.py
# Author: Sam Leheny
# Contact: samleheny@live.com

# Description:


###########################
##### Import Commands #####
import importlib

import Snowman3.riggers.utilities.classes.class_ConnectionPair as class_moduleConnection
importlib.reload(class_moduleConnection)
ModuleConnection = class_moduleConnection.ConnectionPair

import Snowman3.riggers.IO.data_IO as classDataIO
importlib.reload(classDataIO)
DataIO = classDataIO.DataIO
###########################
###########################

###########################
######## Variables ########
default_file_name = 'connection_pairs.json'
###########################
###########################





########################################################################################################################
class ConnectionPairsDataIO( DataIO ):
    def __init__(
        self,
        data = None,
        connection_pairs = None,
        dirpath = None,
        file_name = default_file_name,
    ):
        super().__init__(data=data, dirpath=dirpath, file_name=file_name)
        self.connection_pairs = connection_pairs



    ####################################################################################################################
    def prep_data_for_export(self):

        self.data = []
        for pair in self.connection_pairs:
            self.data.append(pair.get_data_list())



    ####################################################################################################################
    def save(self):

        self.prep_data_for_export() if not self.data else None
        self.save_data_to_file(self.data)



    ####################################################################################################################
    def create_connection_pairs_from_data(self, data):

        connection_pairs = []

        for connection_dict in data:
            connection_pairs.append(ModuleConnection(
                output_socket = connection_dict['output_socket'],
                input_socket = connection_dict['input_socket']
            ))

        return connection_pairs
