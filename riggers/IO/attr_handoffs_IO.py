# Title: attr_handoffs_IO.py
# Author: Sam Leheny
# Contact: samleheny@live.com

# Description:


###########################
##### Import Commands #####
import importlib

import Snowman3.riggers.utilities.classes.class_AttrHandoff as class_attr_handoff
importlib.reload(class_attr_handoff)
AttrHandoff = class_attr_handoff.AttrHandoff

import Snowman3.riggers.IO.data_IO as classDataIO
importlib.reload(classDataIO)
DataIO = classDataIO.DataIO
###########################
###########################

###########################
######## Variables ########
default_file_name = 'attr_handoffs.json'
###########################
###########################





########################################################################################################################
class AttrHandoffsDataIO( DataIO ):
    def __init__(
        self,
        data = None,
        attr_handoffs = None,
        dirpath = None,
        file_name = default_file_name
    ):
        super().__init__(data=data, dirpath=dirpath, file_name=file_name)
        self.attr_handoffs = attr_handoffs



    ####################################################################################################################
    def prep_data_for_export(self):

        self.data = []
        for handoff in self.attr_handoffs:
            self.data.append(handoff.get_data_list())



    ####################################################################################################################
    def save(self):

        self.prep_data_for_export() if not self.data else None
        self.save_data_to_file(self.data)



    ####################################################################################################################
    def create_handoffs_from_data(self, data):

        attr_handoffs = []

        for handoff_dict in data:
            attr_handoffs.append(AttrHandoff(
                old_attr_node = handoff_dict['old_attr_node'],
                new_attr_node = handoff_dict['new_attr_node'],
                delete_old_node = handoff_dict['delete_old_node']
            ))

        return attr_handoffs

