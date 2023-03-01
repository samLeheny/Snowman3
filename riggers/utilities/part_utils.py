# Title: part_utils.py
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
part_tag = 'PART'
###########################
###########################



class Part:
    def __init__(
        self,
        name: str,
        side: str = None,
        handle_size: float = None
    ):
        self.name = name
        self.side = side
        self.handle_size = handle_size if handle_size else 1.0



####################################################################################################################
def create_scene_part(part, parent=None):
    scene_part = gen.prefab_curve_construct(prefab='cube', name=get_part_name(part),
                                            scale=part.size, side=part.side)
    scene_part.setParent(parent) if parent else None
    pm.select(clear=1)
    add_part_metadata(part, scene_part)
    return scene_part



####################################################################################################################
def get_part_name(part):
    side_tag = f'{part.side}_' if part.side else ''
    return f'{side_tag}{part.name}_{part_tag}'



####################################################################################################################
def add_part_metadata(part, scene_part):
    # ...Placer tag
    gen.add_attr(scene_part, long_name='PartTag', attribute_type='string', keyable=0, default_value=part.name)
    # ...Side
    side_attr_input = part.side if part.side else 'None'
    gen.add_attr(scene_part, long_name='Side', attribute_type='string', keyable=0, default_value=side_attr_input)
    # ...Handle size
    gen.add_attr(scene_part, long_name='HandleSize', attribute_type='float', keyable=0, default_value=part.handle_size)
