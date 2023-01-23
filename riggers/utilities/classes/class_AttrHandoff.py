# Title: class_AttrHandoff.py
# Author: Sam Leheny
# Contact: samleheny@live.com

# Description:


###########################
##### Import Commands #####
import importlib
import pymel.core as pm

import Snowman3.utilities.general_utils as gen_utils
importlib.reload(gen_utils)
###########################
###########################


###########################
######## Variables ########

###########################
###########################





########################################################################################################################
class AttrHandoff:
    def __init__(
        self,
        old_attr_node,
        new_attr_node,
        delete_old_node: bool = False
    ):
        self.old_attr_node = old_attr_node
        self.new_attr_node = new_attr_node
        self.delete_old_node = delete_old_node





    ####################################################################################################################
    def perform_attr_handoff(self):

        attr_exceptions = ("LockAttrData", "LockAttrDataT", "LockAttrDataR", "LockAttrDataS", "LockAttrDataV")

        attrs = pm.listAttr(self.old_attr_node, userDefined=1)
        [attrs.remove(a) if a in attrs else None for a in attr_exceptions]
        [gen_utils.migrate_attr(self.old_attr_node, self.new_attr_node, a) for a in attrs]
        if self.delete_old_node:
            pm.delete(self.old_attr_node)





    ####################################################################################################################
    def get_data_list(self):

        data_dict = {}

        # ...
        IO_data_fields = (('old_attr_node', str(self.old_attr_node)),
                          ('new_attr_node', str(self.new_attr_node)),
                          ('delete_old_node', self.delete_old_node))

        for IO_key, input_attr in IO_data_fields:
            data_dict[IO_key] = input_attr

        return data_dict
