import random
import pymel.core as pm
import maya.cmds as mc

import Snowman3.rigger.managers.scene_interactor as scene_interactor
SceneInteractor = scene_interactor.SceneInteractor

# ...File directory path
dirpath = r'C:\Users\61451\Desktop\sam_build'

# ...New scene
mc.file(new=True, f=True)

print('-'*120)
# ...Create scene interactor. Populate it with blueprint manager and armature manager
interactor = SceneInteractor()
interactor.create_managers(asset_name='sam', prefab_key='biped', dirpath=dirpath)

# ...Build blueprint and armature
interactor.build_armature_from_prefab()

# ...Scramble placer and part positions in scene
'''scene_placers = pm.ls('*_PLC')
scene_parts = pm.ls('*_PART')
objs_to_move = scene_placers + scene_parts
for obj in objs_to_move:
    current_position = list(obj.translate.get())
    new_position = [current_position[i] + ((random.random()-0.5)*3) for i in range(3)]
    obj.translate.set(tuple(new_position))

# ...Mirror placer and part positions
interactor.update_blueprint_from_scene()
interactor.mirror_armature('L')

# ...Add new part to existing container
interactor.add_part('NewPart', 'foot_plantigrade', side='L')
# ...Remove a part from a container
interactor.remove_part('R_Arm')

# ...Add mirrored part to existing part
interactor.add_mirrored_part('L_Arm')'''

interactor.save_work()

mc.file(new=True, f=True)

interactor.build_armature_from_latest_version()

interactor.build_rig()

#interactor.mirror_all_control_shapes('L')

#
'''
nodes = [pm.PyNode(i) for i in ('L_IkKnee_CTRL', 'L_IkFoot_CTRL')]
constraint = pm.pointConstraint(nodes[0], nodes[1], mo=1)
pm.select(constraint, replace=1)
interactor.add_selected_constraints()
'''