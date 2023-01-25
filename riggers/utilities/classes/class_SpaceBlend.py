# Title: class_SpaceBlend.py
# Author: Sam Leheny
# Contact: samleheny@live.com

# Description:


###########################
##### Import Commands #####
import importlib
import pymel.core as pm

import Snowman3.utilities.general_utils as gen_utils
import Snowman3.utilities.rig_utils as rig_utils
importlib.reload(gen_utils)
importlib.reload(rig_utils)
###########################
###########################


###########################
######## Variables ########

###########################
###########################





########################################################################################################################
class SpaceBlend:
    def __init__(
        self,
        target,
        source,
        source_name,
        attr_node,
        global_space_parent,
        translate: bool,
        rotate: bool,
        scale: bool,
        attr_name: str,
        name: str,
        type: str,
        default_value = None,
        side: str = None,
        reverse: bool = None,
    ):
        self.type = type
        self.target = target
        self.source = source
        self.source_name = source_name
        self.name = name
        self.attr_node = attr_node
        self.attr_name = attr_name
        self.global_space_parent = global_space_parent
        self.translate = translate
        self.rotate = rotate,
        self.scale = scale
        self.side = side
        self.reverse = reverse
        self.default_value = default_value





    ####################################################################################################################
    def install_blend(self):

        if self.type == 'blend':
            self.create_space_blend()
        elif self.type == 'switch':
            self.create_space_switch()





    ####################################################################################################################
    def create_space_blend(self):

        rig_utils.space_blender(
            target=self.target,
            source=self.source,
            source_name=self.source_name,
            name=self.name,
            attr_node=self.attr_node,
            attr_name=self.attr_name,
            global_space_parent=self.global_space_parent,
            translate=self.translate,
            rotate=self.rotate,
            scale=self.scale,
            reverse=self.reverse,
            default_value=self.default_value
        )





    ####################################################################################################################
    def create_space_switch(self):

        rig_utils.space_switch(
            target=self.target,
            sources=self.source,
            source_names=self.source_name,
            name=self.name,
            attr_node=self.attr_node,
            attr_name=self.attr_name,
            global_space_parent=self.global_space_parent,
            side=self.side,
            translate=self.translate,
            rotate=self.rotate,
            scale=self.scale
        )





    ####################################################################################################################
    def get_data_list(self):

        data_dict = {}

        # ...
        IO_data_fields = (('target', str(self.target)),
                          ('source', str(self.source)),
                          ('source_name', self.source_name),
                          ('attr_node', str(self.attr_node)),
                          ('global_space_parent', str(self.global_space_parent)),
                          ('translate', self.translate),
                          ('rotate', self.rotate),
                          ('scale', self.scale),
                          ('attr_name', self.attr_name),
                          ('name', self.name),
                          ('type', self.type),
                          ('default_value', self.default_value),
                          ('side', self.side),
                          ('reverse', self.reverse))

        for IO_key, input_attr in IO_data_fields:
            data_dict[IO_key] = input_attr

        return data_dict
