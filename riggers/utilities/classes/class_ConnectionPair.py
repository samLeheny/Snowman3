# Title: class_ConnectionPairs.py
# Author: Sam Leheny
# Contact: samleheny@live.com

# Description:


###########################
##### Import Commands #####
import importlib
import pymel.core as pm

import Snowman3.utilities.general_utils as gen_utils
importlib.reload(gen_utils)

import Snowman3.dictionaries.nameConventions as nameConventions
importlib.reload(nameConventions)
nom = nameConventions.create_dict()
###########################
###########################


###########################
######## Variables ########

###########################
###########################





########################################################################################################################
class ConnectionPair:
    def __init__(
        self,
        output_socket,
        input_socket
    ):
        self.output_socket = output_socket
        self.input_socket = input_socket






    ####################################################################################################################
    def connect_sockets(self):

        # ...Create a locator to hold transforms
        loc = pm.spaceLocator(name=f'{gen_utils.get_clean_name(self.input_socket)}_SPACE')
        # ...Match locator to rotate + scale of DRIVEN node (to account for modules in flipped space)
        loc.setParent(self.input_socket)
        gen_utils.zero_out(loc)
        # ...Match locator to translate of DRIVER node (so scaling the driver won't offset the pivot position)
        loc.setParent(self.output_socket)
        loc.translate.set(0, 0, 0)
        # ...Constraint DRIVEN node to locator (with offset!)
        pm.parentConstraint(loc, self.input_socket, mo=1)






    ####################################################################################################################
    def get_data_list(self):

        data_dict = {}

        # ...
        IO_data_fields = (('output_socket', str(self.output_socket)),
                          ('input_socket', str(self.input_socket)))

        for IO_key, input_attr in IO_data_fields:
            data_dict[IO_key] = input_attr

        return data_dict
