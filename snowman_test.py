### ...Full Body ###################################
import importlib
import pymel.core as pm
import maya.cmds as mc
import Snowman3.riggers.builder.builder as builder
importlib.reload(builder)

import Snowman3.riggers.builder.builder as builder
importlib.reload(builder)
RigBuilder = builder.RigBuilder

import Snowman3.riggers.IO.blueprint_IO as class_blueprint_IO
importlib.reload(class_blueprint_IO)
BlueprintDataIO = class_blueprint_IO.BlueprintDataIO

# ...File directory path
#dirpath = r'C:\Users\User\Desktop'
dirpath = r'C:\Users\61451\Desktop'

# ...New scene
mc.file(new=True, f=True)
print('-'*120)

# ...Build prefab armature
rig_builder = RigBuilder(asset_name='test', prefab_key='biped', dirpath=dirpath)
rig_builder.build_prefab_armature()




# ...Build armature from file
'''rig_builder = RigBuilder(
    dirpath = dirpath
)
rig_builder.build_armature_from_file()'''    
# ...Build rig
rig_builder.build_rig_in_scene(
    scene_armature=pm.ls("::biped_ARMATURE", type="transform")[0])

# ...Build armature from data file
'''mc.file(new=True, f=True)
rig = rig_builder.build_armature_from_file()'''