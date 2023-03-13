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

import Snowman3.dictionaries.colorCode as color_code
importlib.reload(color_code)
###########################
###########################


###########################
######## Variables ########
part_tag = 'PART'
color_code = color_code.sided_ctrl_color
###########################
###########################



class Part:
    def __init__(
        self,
        name: str,
        side: str = None,
        handle_size: float = None,
        position = None,
        placers = None,
        data_name: str = None,
        scene_name: str = None,
    ):
        self.name = name
        self.side = side
        self.handle_size = handle_size if handle_size else 1.0
        self.position = position if position else [0, 0, 0]
        self.placers = placers if placers else {}
        self.data_name = data_name if data_name else f'{gen.side_tag(side)}{name}'
        self.scene_name = scene_name


########################################################################################################################
def create_scene_part(part, parent=None):
    scene_part = create_part_handle(part)
    position_part(part)
    scene_part.setParent(parent) if parent else None
    pm.select(clear=1)
    add_part_metadata(part, scene_part)
    return scene_part


########################################################################################################################
def create_part_handle(part):
    handle = gen.prefab_curve_construct(prefab='cube', name=part.scene_name, scale=part.handle_size, side=part.side)
    color_part_handle(part)
    return handle


########################################################################################################################
def position_part(part):
    handle = get_part_handle(part)
    handle.translate.set(tuple(part.position))


########################################################################################################################
def part_conflict_action(part):
    print(f"Cannot create part '{part.scene_name}' - a part with this name already exists in scene.")


########################################################################################################################
def add_part_metadata(part, scene_part):
    # ...Placer tag
    gen.add_attr(scene_part, long_name='PartTag', attribute_type='string', keyable=0, default_value=part.name)
    # ...Side
    side_attr_input = part.side if part.side else 'None'
    gen.add_attr(scene_part, long_name='Side', attribute_type='string', keyable=0, default_value=side_attr_input)
    # ...Handle size
    gen.add_attr(scene_part, long_name='HandleSize', attribute_type='float', keyable=0, default_value=part.handle_size)
    pm.setAttr(f'{scene_part}.HandleSize', channelBox=1)
    for a in ('sx', 'sy', 'sz'):
        pm.connectAttr(f'{scene_part}.HandleSize', f'{scene_part}.{a}')
        pm.setAttr(f'{scene_part}.{a}', keyable=0)


########################################################################################################################
def data_from_part(part):
    data = {}
    for param, value in vars(part).items():
        data[param] = value
    return data


########################################################################################################################
def get_part_handle(part):
    if not pm.objExists(part.scene_name):
        return False
    part_handle = pm.PyNode(part.scene_name)
    return part_handle


########################################################################################################################
def part_from_data(data):
    part = Part(**data)
    return part


########################################################################################################################
def update_part_from_scene(part):
    part_handle = get_part_handle(part)
    # ...Update position
    part.position = list(part_handle.translate.get())
    # ...Update handle size
    part.handle_size = pm.getAttr(f'{part_handle}.HandleSize')


########################################################################################################################
def mirror_part(part):
    part_handle = get_part_handle(part)
    opposite_part_handle = get_opposite_part_handle(part_handle)
    # ...Mirror position
    pm.setAttr(f'{opposite_part_handle}.tx', pm.getAttr(f'{part_handle}.tx') * -1)
    [pm.setAttr(f'{opposite_part_handle}.{a}', pm.getAttr(f'{part_handle}.{a}')) for a in ('ty', 'tz')]
    # ...Match handle size
    pm.setAttr(f'{opposite_part_handle}.HandleSize', pm.getAttr(f'{part_handle}.HandleSize'))


########################################################################################################################
def get_opposite_part_handle(part_handle):
    sided_prefixes = {'L_': 'R_', 'R_': 'L_'}
    this_prefix = None
    opposite_part_handle = None
    for prefix in sided_prefixes.keys():
        if str(part_handle).startswith(prefix):
            this_prefix = prefix
    if this_prefix:
        opposite_part_handle = pm.PyNode(str(part_handle).replace(this_prefix, sided_prefixes[this_prefix]))
    return opposite_part_handle


########################################################################################################################
def get_scene_part(part):
    scene_part = pm.PyNode(part.scene_name)
    return scene_part


########################################################################################################################
def color_part_handle(part, color=None):
    if not color:
        color = color_code[part.side]
    gen.set_color(get_part_handle(part), color)
