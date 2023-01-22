# Title: class_PlacerConnector.py
# Author: Sam Leheny
# Contact: samleheny@live.com

# Description:


###########################
##### Import Commands #####
import importlib
import pymel.core as pm

import Snowman3.utilities.general_utils as gen_utils
import Snowman3.utilities.rig_utils as rig_utils
import Snowman3.utilities.node_utils as node_utils
importlib.reload(gen_utils)
importlib.reload(rig_utils)
importlib.reload(node_utils)

import Snowman3.dictionaries.nameConventions as nameConventions
importlib.reload(nameConventions)
nom = nameConventions.create_dict()

import Snowman3.riggers.utilities.classes.class_VectorHandle as classVectorHandle
import Snowman3.riggers.utilities.classes.class_Orienter as classOrienter
importlib.reload(classVectorHandle)
importlib.reload(classOrienter)
VectorHandle = classVectorHandle.VectorHandle
Orienter = classOrienter.Orienter

import Snowman3.riggers.dictionaries.control_colors as ctrl_colors_dict
importlib.reload(ctrl_colors_dict)
ctrl_colors = ctrl_colors_dict.create_dict()
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
        destination_placer_key: str,
        parent = None,
        source_module = None
    ):
        self.source_module_key = source_module_key
        self.source_placer_key = source_placer_key
        self.destination_module_key = destination_module_key
        self.destination_placer_key = destination_placer_key
        self.parent = parent
        self.source_module = source_module





    ####################################################################################################################
    def create_connector(self):

        end_1_node = self.source_module.placers[self.source_placer_key].mobject

        target_module_ctrl = self.source_module.get_other_module(name=self.destination_module_key,
                                                                 return_module_ctrl=True)

        end_2_node = pm.listConnections(f'{target_module_ctrl}.PlacerNodes.{self.destination_placer_key}', source=1)[0]

        connector = rig_utils.connector_curve(
            name=self.source_placer_key, line_width=1.5, end_driver_1=end_1_node,
            end_driver_2=end_2_node, override_display_type=2, parent=self.parent, inheritsTransform=False)[0]

        # ...Connect curve to module attribute
        '''pm.addAttr(connector, longName="Module", dataType="string", keyable=0)
        pm.connectAttr(f'{self.source_module.rig_root_grp}.ExtraDrawnConnections', f'{connector}.Module')'''





    ####################################################################################################################
    def get_data_list(self):

        data_dict = {}

        # ...
        IO_data_fields = (('source_module_key', self.source_module_key),
                          ('source_placer_key', self.source_placer_key),
                          ('destination_module_key', self.destination_module_key),
                          ('destination_placer_key', self.destination_placer_key))

        for IO_key, input_attr in IO_data_fields:
            data_dict[IO_key] = input_attr

        return data_dict
