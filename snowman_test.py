### ...Full Body ###################################
import importlib
import pymel.core as pm
import maya.cmds as mc

import Snowman3.riggers.managers.blueprint_manager as blueprint_manager
importlib.reload(blueprint_manager)
BlueprintManager = blueprint_manager.BlueprintManager

import Snowman3.riggers.utilities.armatureBuilder as armature_builder
importlib.reload(armature_builder)
ArmatureBuilder = armature_builder.ArmatureBuilder

# ...File directory path
#dirpath = r'C:\Users\User\Desktop\test_build'
dirpath = r'C:\Users\61451\Desktop\sam_build'

# ...New scene
mc.file(new=True, f=True)

# ...Build prefab armature
print('-'*120)
BPManager = BlueprintManager(asset_name='sam', prefab_key='biped', dirpath=dirpath)
blueprint = BPManager.create_blueprint_from_prefab()
armature_builder = ArmatureBuilder(blueprint=blueprint)
armature_builder.build_armature_from_blueprint()

BPManager.save_work()



BPManager.test(1)
BPManager.test(2)
BPManager.test(3)
BPManager.test(4)

# ...Build armature from file
'''rig_builder = RigBuilder(
    dirpath = dirpath
)
rig_builder.build_armature_from_file()'''    
# ...Build rig
'''rig_builder.build_rig_in_scene(
    scene_armature=pm.ls("::biped_ARMATURE", type="transform")[0])'''

# ...Build armature from data file
'''mc.file(new=True, f=True)
rig = rig_builder.build_armature_from_file()'''