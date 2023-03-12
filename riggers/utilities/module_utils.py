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

import Snowman3.riggers.utilities.part_utils as part_utils
importlib.reload(part_utils)
Part = part_utils.Part

import Snowman3.riggers.utilities.metadata_utils as metadata_utils
importlib.reload(metadata_utils)
MetaDataAttr = metadata_utils.MetaDataAttr
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
        side: str = None,
        data_name: str = None,
        scene_name: str = None,
        parts = None
    ):
        self.name = name
        self.side = side
        self.data_name = data_name if data_name else f'{gen.side_tag(side)}{name}'
        self.scene_name = scene_name if scene_name else f'{gen.side_tag(side)}{name}_MODULE'
        self.parts = parts if parts else {}



metadata_attrs = (
    MetaDataAttr(long_name='ModuleTag', attribute_type='string', keyable=0, default_value_attr_string='name'),
    MetaDataAttr(long_name='Side', attribute_type='string', keyable=0, default_value_attr_string='side')
)


########################################################################################################################
def create_scene_module(module, parent=None):
    scene_module = pm.shadingNode('transform', name=module.scene_name, au=1)
    scene_module.setParent(parent) if parent else None
    add_module_metadata(module, scene_module)
    return scene_module


########################################################################################################################
def add_module_metadata(module, scene_module):
    [attr.create(module, scene_module) for attr in metadata_attrs]


########################################################################################################################
def data_from_module(module):
    data = {}
    for param, value in vars(module).items():
        data[param] = value
    return data


########################################################################################################################
def module_from_data(data):
    module = Module(**data)
    return module


########################################################################################################################
def get_scene_module(module):
    module_name = module.scene_name
    scene_module = pm.PyNode(module_name)
    return scene_module


########################################################################################################################
def update_module_from_scene(module):
    data = data_from_module(module)
    # ...Update module parts
    part_data = data['parts']
    for key, part in part_data.items():
        p = part_utils.part_from_data(part_data[key])
        part_utils.update_part_from_scene(p)
        module.parts[key] = part_utils.data_from_part(p)
    # ...Finish
    return True


########################################################################################################################
def mirror_module(module, driver_side='L'):
    for key, part_data in module['parts'].items():
        part = part_utils.part_from_data(part_data)
        if part.side == driver_side:
            part_utils.mirror_part(part, driver_side=driver_side, driven_side=gen.opposite_side(driver_side))
