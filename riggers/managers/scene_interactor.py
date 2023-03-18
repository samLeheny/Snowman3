# Title: scene_interactor.py
# Author: Sam Leheny
# Contact: samleheny@live.com

# Description:


###########################
##### Import Commands #####
import os
import importlib

import pymel.core as pm

import Snowman3.utilities.general_utils as gen
importlib.reload(gen)

import Snowman3.riggers.managers.blueprint_manager as blueprint_manager_util
importlib.reload(blueprint_manager_util)
BlueprintManager = blueprint_manager_util.BlueprintManager
###########################
###########################

###########################
######## Variables ########

###########################
###########################


dirpath = r'C:\Users\61451\Desktop\sam_build'
blueprint_manager = BlueprintManager(asset_name='sam', dirpath=dirpath)
blueprint = blueprint_manager.get_blueprint_from_working_dir()


def mirror_placer_position(placer_key, part_key, module_key):
    part_data = get_blueprint_part(part_key, module_key)
    placer = part_data['placers'][placer_key]
    scene_placer = pm.PyNode(placer['scene_name'])
    opposite_scene_placer = gen.get_opposite_side_obj(scene_placer)
    if not opposite_scene_placer:
        return False
    scene_placer_local_position = scene_placer.translate.get()
    opposite_scene_placer.translate.set(tuple(scene_placer_local_position))


def mirror_part(part_key, module_key):
    mirror_part_handle(part_key, module_key)
    mirror_part_placer_positions(part_key, module_key)


def mirror_part_handle(part_key, module_key):
    part_data = get_blueprint_part(part_key, module_key)
    scene_part_handle = pm.PyNode(part_data['scene_name'])
    opposite_scene_part_handle = gen.get_opposite_side_obj(scene_part_handle)
    scene_part_handle_position = scene_part_handle.translate.get()
    opposite_scene_part_handle.translate.set(scene_part_handle_position)


def mirror_part_placer_positions(part_key, module_key):
    part_data = get_blueprint_part(part_key, module_key)
    part_placers = part_data['placers']
    [mirror_placer_position(key, part_key, module_key) for key in part_placers.keys()]


def get_blueprint_part(part_key, module_key):
    module_data = get_blueprint_module(module_key)
    return module_data['parts'][part_key]


def get_blueprint_module(module_key, blueprint=blueprint):
    blueprint_modules = get_all_modules_data(blueprint)
    return blueprint_modules[module_key]


def mirror_module_placer_positions(module_key):
    module_data = get_blueprint_module(module_key)
    for part_key in module_data['parts'].keys():
        mirror_part_placer_positions(part_key, module_key)


def get_all_modules_data(blueprint=blueprint):
    modules_data = blueprint.modules
    return modules_data


def mirror_armature_placer_positions(driver_side, blueprint=blueprint):
    modules_data = get_all_modules_data(blueprint)
    for key, module_data in modules_data.items():
        if module_data['side'] == driver_side:
            mirror_module_placer_positions(key)
