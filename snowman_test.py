### ...Full Body ###################################
import importlib
import pymel.core as pm
import maya.cmds as mc
import json
import Snowman3.riggers.builder.builder as builder
importlib.reload(builder)
import Snowman3.riggers.IO.armature_IO as IO
importlib.reload(IO)
ArmatureDataIO = IO.ArmatureDataIO

# ...File directory path
#dirpath = r'C:\Users\User\Desktop'
dirpath = r'C:\Users\61451\Desktop\test_build'

# ...New scene
mc.file(new=True, f=True)

# ...Build armature
rig = builder.build_prefab_armature(
    prefab_tag = "biped",
    symmetry_mode = "Left drives Right")
    
# ...Build rig
builder.build_rig_in_scene(
    armature=pm.ls( "::biped_ARMATURE",
    type="transform")[0], asset_name="test" )

# ...Save armature data to file
armature_data = ArmatureDataIO(dirpath)
armature_data.save()

# ...Build armature from data file
mc.file(new=True, f=True)
rig = builder.build_armature_from_file(dirpath)
