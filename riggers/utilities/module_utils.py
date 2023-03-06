# Title: module_utils.py
# Author: Sam Leheny
# Contact: samleheny@live.com

# Description:


###########################
##### Import Commands #####
import importlib
import pymel.core as pm

import Snowman3.utilities.general_utils as gen
importlib.reload(gen)
###########################
###########################


###########################
######## Variables ########
module_tag = 'MODULE'
###########################
###########################



class Module:
    def __init__(
        self,
        name: str,
        side: str = None
    ):
        self.name = name
        self.side = side



########################################################################################################################
def create_scene_module(module, parent=None):
    scene_module = pm.group(name=get_module_name(module))
    scene_module.setParent(parent) if parent else None
    pm.select(clear=1)
    add_module_metadata(module, scene_module)
    return scene_module



########################################################################################################################
def get_module_name(module):
    side_tag = f'{module.side}_' if module.side else ''
    module_name = f'{side_tag}{module.name}_{module_tag}'
    return module_name



########################################################################################################################
def add_module_metadata(module, scene_module):
    # ...Placer tag
    gen.add_attr(scene_module, long_name="ModuleTag", attribute_type="string", keyable=0, default_value=module.name)
    # ...Side
    side_attr_input = module.side if module.side else "None"
    gen.add_attr(scene_module, long_name="Side", attribute_type="string", keyable=0, default_value=side_attr_input)

