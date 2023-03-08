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

import Snowman3.riggers.IO.blueprint_IO as blueprintIO
importlib.reload(blueprintIO)
BlueprintIO = blueprintIO.BlueprintIO
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
        position = None
    ):
        self.name = name
        self.side = side
        self.side_tag = f'{side}_' if side else ''
        self.handle_size = handle_size if handle_size else 1.0
        self.position = position if position else [0, 0, 0]



########################################################################################################################
def create_scene_part(part, parent=None):
    if check_for_part(part):
        return False
    scene_part = gen.prefab_curve_construct(prefab='cube', name=get_part_name(part), scale=part.handle_size,
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
def create_loose_scene_part(part, parent=None):
    scene_part = create_scene_part(part, parent=parent)
    add_part_to_blueprint(part)
    return scene_part



########################################################################################################################
def check_for_part(part):
    part_name = get_part_name(part)
    if pm.objExists(part_name):
        part_conflict_action(part)
        return True
    return False



########################################################################################################################
def part_conflict_action(part):
    part_name = get_part_name(part)
    print(f"Cannot create part '{part_name}' - a part with this name already exists in scene.")



########################################################################################################################
def get_part_name(part):
    return f'{part.side_tag}{part.name}_{part_tag}'



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
def add_part_to_blueprint(part, check_for_clashes=True):
    dirpath = r'C:\Users\61451\Desktop\test_build\working'
    blueprint_IO = BlueprintIO(dirpath=dirpath)
    working_blueprint = blueprint_IO.blueprint_from_file(blueprint_IO.dirpath)
    part_key = f'{part.side_tag}{part.name}'
    if check_for_clashes:
        if part_key in working_blueprint.loose_parts:
            print(f"Cannot add part '{part_key}' to blueprint - a part with this name already exists in blueprint.")
            return False
    working_blueprint.loose_parts[part_key] = data_from_part(part)
    # ...Update disk
    blueprint_IO = BlueprintIO(blueprint=working_blueprint)
    blueprint_IO.save(dirpath=dirpath)



########################################################################################################################
def data_from_part(part):
    data = {}
    pairs = (
        ('name', part.name),
        ('side', part.side),
        ('handle_size', part.handle_size),
        ('position', part.position)
    )
    for key, value in pairs:
        data[key] = value
    return data



########################################################################################################################
def remove_scene_part(part):
    part_name = get_part_name(part)
    if not pm.objExists(part_name):
        print(f"Cannot delete part {''} - part not found in scene.")
        return False
    pm.delete(pm.PyNode(part_name))
    remove_part_from_blueprint(part)
    return True



########################################################################################################################
def remove_part_from_blueprint(part):
    dirpath = r'C:\Users\61451\Desktop\test_build\working'
    blueprint_IO = BlueprintIO(dirpath=dirpath)
    working_blueprint = blueprint_IO.blueprint_from_file(blueprint_IO.dirpath)
    working_blueprint.loose_parts.pop(f'{part.side_tag}{part.name}')
    # ...Update disk
    blueprint_IO = BlueprintIO(blueprint=working_blueprint)
    blueprint_IO.save(dirpath=dirpath)



########################################################################################################################
def get_part_handle(part):
    part_name = get_part_name(part)
    if not pm.objExists(part_name):
        return False
    part_handle = pm.PyNode(part_name)
    return part_handle



########################################################################################################################
def part_from_data(data):
    part = Part(
        name=data['name'],
        side=data['side'],
        handle_size=data['handle_size'],
        position=data['position']
    )
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
    pm.setAttr(f'{opposite_part_handle}.ty', pm.getAttr(f'{part_handle}.ty'))
    pm.setAttr(f'{opposite_part_handle}.tz', pm.getAttr(f'{part_handle}.tz'))
    # ...Match handle size
    pm.setAttr(f'{opposite_part_handle}.HandleSize', pm.getAttr(f'{part_handle}.HandleSize'))



########################################################################################################################
def get_opposite_part(part):
    opposite_sides = {'L':'R', 'R':'L'}
    opposite_part = Part(
        name = part.name,
        side = opposite_sides[part.side],
        handle_size = part.handle_size,
        position = part.position
    )
    if not get_part_handle(opposite_part):
        return False
    return opposite_part

