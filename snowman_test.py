###...Full Body #########################################################################
import importlib
import pymel.core as pm
import maya.cmds as mc
import json
import Snowman3.riggers.builder.builder as builder
importlib.reload(builder)
import Snowman3.riggers.IO.armature_IO as IO
importlib.reload(IO)
ArmatureDataIO = IO.ArmatureDataIO

#...New Scene
mc.file(new=True, f=True)

#...Build armature
rig = builder.build_prefab_armature(
    prefab_tag = "biped",
    symmetry_mode = "Left drives Right")
    
#...Build rig
builder.build_rig_in_scene(
    armature=pm.ls("::biped_ARMATURE", type="transform")[0],
    asset_name="test")

'''
# ----------------------------------------------------------------------------------------
#dirpath = r'C:\Users\User\Desktop'
dirpath = r'C:\Users\61451\Desktop'

armature_data = ArmatureDataIO(dirpath)
armature_data.save()


#
mc.file(new=True, f=True)
#

#dirpath = r'C:/Users/User/Desktop'
dirpath = r'C:/Users/61451/Desktop'
data = armature_data.load(dirpath + "/test_armature_data.json")

rig = builder.build_armature_from_data(data)
'''