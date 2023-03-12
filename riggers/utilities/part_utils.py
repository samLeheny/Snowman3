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
    scene_part = gen.prefab_curve_construct(prefab='cube', name=part.scene_name, scale=part.handle_size,
                                            side=part.side)
    position_part(part)
    scene_part.setParent(parent) if parent else None
    pm.select(clear=1)
    add_part_metadata(part, scene_part)
    return scene_part


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
    part_name = part.scene_name
    if not pm.objExists(part_name):
        return False
    part_handle = pm.PyNode(part_name)
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
def mirror_part(part, driver_side='L', driven_side='R'):
    part_handle = get_part_handle(part)
    opposite_part = get_opposite_part(part)
    if not opposite_part:
        return False
    opposite_part_handle = get_part_handle(opposite_part)
    # ...Mirror position
    pm.setAttr(f'{opposite_part_handle}.tx', pm.getAttr(f'{part_handle}.tx') * -1)
    [pm.setAttr(f'{opposite_part_handle}.{a}', pm.getAttr(f'{part_handle}.{a}')) for a in ('ty', 'tz')]
    # ...Match handle size
    pm.setAttr(f'{opposite_part_handle}.HandleSize', pm.getAttr(f'{part_handle}.HandleSize'))


########################################################################################################################
def get_opposite_part(part):
    opposite_part_args = get_opposite_side_part_args(part)
    opposite_part = Part(**opposite_part_args)
    if not get_part_handle(opposite_part):
        return False
    return opposite_part


########################################################################################################################
def get_opposite_side_part_args(part):
    opposite_part_args = vars(part)
    opposite_part_args['side'] = gen.opposite_side(part.side)
    return opposite_part_args


########################################################################################################################
def get_scene_part(part):
    scene_part = pm.PyNode(part.scene_name)
    return scene_part
