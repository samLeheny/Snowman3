import importlib
import random
import pymel.core as pm
import maya.cmds as mc

import Snowman3.riggers.managers.blueprint_manager as blueprint_manager
importlib.reload(blueprint_manager)
BlueprintManager = blueprint_manager.BlueprintManager

import Snowman3.riggers.managers.armature_manager as armature_manager
importlib.reload(armature_manager)
ArmatureManager = armature_manager.ArmatureManager

import Snowman3.riggers.managers.scene_interactor as scene_interactor
importlib.reload(scene_interactor)
SceneInteractor = scene_interactor.SceneInteractor

# ...File directory path
dirpath = r'C:\Users\61451\Desktop\sam_build'

# ...New scene
mc.file(new=True, f=True)

print('-'*120)
# ...Build blueprint
BPManager = BlueprintManager(asset_name='sam', prefab_key='biped', dirpath=dirpath)
blueprint = BPManager.create_blueprint_from_prefab()

# ...Build armature
armature_manager = ArmatureManager(blueprint_manager=BPManager)
armature_manager.build_armature_from_blueprint()

# ...Scramble placer and part positions in scene
scene_placers = pm.ls('*_PLC')
scene_parts = pm.ls('*_PART')
objs_to_move = scene_placers + scene_parts
for obj in objs_to_move:
    current_position = list(obj.translate.get())
    new_position = [current_position[i] + (random.random()*5) for i in range(3)]
    obj.translate.set(tuple(new_position))

# ...Mirror placer and part positions
BPManager.update_blueprint_from_scene()
interactor = SceneInteractor(blueprint_manager=BPManager, armature_manager=armature_manager)
interactor.mirror_armature('L')

# ...Add new (prefab) container
interactor.add_container('ThirdArm', side='L', prefab_key='biped_arm', parts_prefix='Third')
# ...Add new (empty) container
interactor.add_container('Tail', side='M', prefab_key=None, parts_prefix=None)
# ...Remove a container
interactor.remove_container('R_Leg')
# ...Add new part to existing container
interactor.add_part('NewPart', 'foot_plantigrade', 'L_Hand', side='L')
# ...Remove a part from a container
interactor.remove_part('biped_arm', 'R_Arm')

# ...Add mirrored part to existing part
interactor.add_mirrored_part('biped_arm', 'L_Arm')
# ...Add mirrored container to existing container
interactor.add_mirrored_container('L_Leg')

interactor.save_work()
