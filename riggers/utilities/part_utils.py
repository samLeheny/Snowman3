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
        handle_size: float = None
    ):
        self.name = name
        self.side = side
        self.side_tag = f'{side}_' if side else ''
        self.handle_size = handle_size if handle_size else 1.0



####################################################################################################################
def create_scene_part(part, parent=None):
    check_for_part(part)
    scene_part = gen.prefab_curve_construct(prefab='cube', name=get_part_name(part),
                                            scale=part.handle_size, side=part.side)
    scene_part.setParent(parent) if parent else None
    pm.select(clear=1)
    add_part_metadata(part, scene_part)
    add_part_to_blueprint(part)
    return scene_part



########################################################################################################################
def check_for_part(part):
    part_name = get_part_name(part)
    if pm.objExists(part_name):
        part_conflict_action(part)



########################################################################################################################
def part_conflict_action(part):
    part_name = get_part_name(part)
    print(f"Cannot create part '{part_name}' - a part with this name already exists in scene.")



####################################################################################################################
def get_part_name(part):
    return f'{part.side_tag}{part.name}_{part_tag}'



####################################################################################################################
def add_part_metadata(part, scene_part):
    # ...Placer tag
    gen.add_attr(scene_part, long_name='PartTag', attribute_type='string', keyable=0, default_value=part.name)
    # ...Side
    side_attr_input = part.side if part.side else 'None'
    gen.add_attr(scene_part, long_name='Side', attribute_type='string', keyable=0, default_value=side_attr_input)
    # ...Handle size
    gen.add_attr(scene_part, long_name='HandleSize', attribute_type='float', keyable=0, default_value=part.handle_size)



########################################################################################################################
def add_part_to_blueprint(part):
    dirpath = r'C:\Users\61451\Desktop\test_build\working'
    blueprint_IO = BlueprintIO(dirpath=dirpath)
    working_blueprint = blueprint_IO.blueprint_from_file(blueprint_IO.dirpath)
    working_blueprint.loose_parts[f'{part.side_tag}{part.name}'] = data_from_part(part)
    # ...Update disk
    blueprint_IO = BlueprintIO(blueprint=working_blueprint)
    blueprint_IO.save(dirpath=dirpath)



########################################################################################################################
def data_from_part(part):
    data = {}
    pairs = (
        ('name', part.name),
        ('side', part.side),
        ('handle_size', part.handle_size)
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



########################################################################################################################
def remove_part_from_blueprint(part):
    dirpath = r'C:\Users\61451\Desktop\test_build\working'
    blueprint_IO = BlueprintIO(dirpath=dirpath)
    working_blueprint = blueprint_IO.blueprint_from_file(blueprint_IO.dirpath)
    print(working_blueprint.loose_parts)
    working_blueprint.loose_parts.pop(f'{part.side_tag}{part.name}')
    # ...Update disk
    blueprint_IO = BlueprintIO(blueprint=working_blueprint)
    blueprint_IO.save(dirpath=dirpath)
