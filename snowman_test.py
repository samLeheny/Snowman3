### ...Full Body ###################################
import importlib
import pymel.core as pm
import maya.cmds as mc
import Snowman3.riggers.builder.builder as builder
importlib.reload(builder)

import Snowman3.riggers.builder.builder as builder
importlib.reload(builder)
RigBuilder = builder.RigBuilder

import Snowman3.riggers.utilities.classes.class_PrefabBlueprint as class_prefabBlueprint
importlib.reload(class_prefabBlueprint)
PrefabBlueprint = class_prefabBlueprint.PrefabBlueprint

# ...File directory path
dirpath = r'C:\Users\User\Desktop'
#dirpath = r'C:\Users\61451\Desktop'

# ...New scene
mc.file(new=True, f=True)

blueprint = PrefabBlueprint(
    prefab_key = 'biped',
    symmetry_mode = None)
print(blueprint.attr_handoffs.items())

rig_builder = RigBuilder(
    asset_name = 'test',
    prefab_key = 'biped',
    dirpath = dirpath,
    symmetry_mode = 'Left drives Right')

# ...Build armature
rig_builder.build_prefab_armature()
    
# ...Build rig
'''rig_builder.build_rig_in_scene(
    scene_armature=pm.ls("::biped_ARMATURE",
    type="transform")[0])'''

# ...Build armature from data file
mc.file(new=True, f=True)
rig = rig_builder.build_armature_from_file()
