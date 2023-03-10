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
        parts = None
    ):
        self.name = name
        self.side = side
        self.side_tag = f'{side}_' if side else ''
        self.parts = parts if parts else {}



########################################################################################################################
def create_scene_module(module, parent=None):
    scene_module = pm.group(name=get_module_name(module))
    scene_module.setParent(parent) if parent else None
    pm.select(clear=1)
    add_module_metadata(module, scene_module)
    ###add_module_to_blueprint(module)
    return scene_module



########################################################################################################################
def get_module_name(module):
    module_name = f'{module.side_tag}{module.name}_{module_tag}'
    return module_name



########################################################################################################################
def add_module_metadata(module, scene_module):
    # ...Placer tag
    gen.add_attr(scene_module, long_name="ModuleTag", attribute_type="string", keyable=0, default_value=module.name)
    # ...Side
    side_attr_input = module.side if module.side else "None"
    gen.add_attr(scene_module, long_name="Side", attribute_type="string", keyable=0, default_value=side_attr_input)



########################################################################################################################
def data_from_module(module):
    data = {}
    pairs = (
        ('name', module.name),
        ('side', module.side),
        ('parts', module.parts)
    )
    for key, value in pairs:
        data[key] = value
    return data



########################################################################################################################
def module_from_data(data):
    module = Module(
        name = data['name'],
        side = data['side'],
        parts = data['parts']
    )
    return module



########################################################################################################################
def get_scene_module(module):
    module_name = get_module_name(module)
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
def mirror_module(module, driver_side='L', driven_side='R'):
    for key, part_data in module['parts'].items():
        part = part_utils.part_from_data(part_data)
        if part.side == driver_side:
            part_utils.mirror_part(part, driver_side=driver_side, driven_side=driven_side)
