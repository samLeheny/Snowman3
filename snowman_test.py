import importlib
import random
import pymel.core as pm
import maya.cmds as mc

import Snowman3.riggers.managers.blueprint_manager as blueprint_manager
importlib.reload(blueprint_manager)
BlueprintManager = blueprint_manager.BlueprintManager

import Snowman3.riggers.managers.armature_manager as armature_builder
importlib.reload(armature_builder)
ArmatureManager = armature_builder.ArmatureManager

import Snowman3.riggers.managers.scene_interactor as scene_interactor
importlib.reload(scene_interactor)
SceneInteractor = scene_interactor.SceneInteractor

# ...File directory path
#dirpath = r'C:\Users\User\Desktop\test_build'
dirpath = r'C:\Users\61451\Desktop\sam_build'

# ...New scene
mc.file(new=True, f=True)

print('-'*120)
# ...Build blueprint
BPManager = BlueprintManager(asset_name='sam', prefab_key='biped', dirpath=dirpath)
blueprint = BPManager.create_blueprint_from_prefab()

# ...Build armature
armature_builder = ArmatureManager(blueprint_manager=BPManager)
armature_builder.build_armature_from_blueprint()

BPManager.save_work()

# ...Scramble placer and part positions in scene
scene_placers = pm.ls('*_PLC')
scene_parts = pm.ls('*_PART')
objs_to_move = scene_placers + scene_parts
for obj in objs_to_move:
    current_position = list(obj.translate.get())
    new_position = [current_position[i] + (random.random()*15) for i in range(3)]
    obj.translate.set(tuple(new_position))

# ...Mirror placer and part positions
BPManager.update_blueprint_from_scene()
interactor = SceneInteractor(blueprint_manager=BPManager, armature_builder=armature_builder)
interactor.mirror_armature('L')

BPManager.save_work()

# ...Add new (prefab) module
interactor.add_module('ThirdArm', side='L', prefab_key='biped_arm', parts_prefix='Third')
# ...Add new (empty) module
interactor.add_module('Tail', side='M', prefab_key=None, parts_prefix=None)
# ...Remove a module
interactor.remove_module('M_Spine')

BPManager.save_work()
