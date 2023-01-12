# Title: space_blends.py
# Author: Sam Leheny
# Contact: samleheny@live.com

# Description:


###########################
##### Import Commands #####
import importlib

import Snowman3.dictionaries.nameConventions as nameConventions
importlib.reload(nameConventions)
nom = nameConventions.create_dict()

import Snowman3.utilities.rig_utils as rig_utils
importlib.reload(rig_utils)
###########################
###########################


###########################
######## Variables ########

###########################
###########################





def install_space_blends(modules):

    #...Neck
    rig_utils.space_blender(
        target=modules['neck'].ctrls['neck'].getParent(),
        source=modules['spine'].ctrls['ik_chest'],
        source_name='global',
        name='neck',
        attr_node=modules['neck'].ctrls['neck'],
        attr_name='GlobalSpace',
        global_space_parent=modules['root'].ctrls['subRoot'],
        translate=False, rotate=True, scale=False
    )

    for side in (nom.leftSideTag, nom.rightSideTag):

        #...Arms
        rig_utils.space_switch(
            target=modules[f'{side}_arm'].ctrls['fk_upperarm'].getParent(),
            sources=(modules['spine'].ctrls['ik_chest'],
                     modules[f'{side}_clavicle'].ctrls['clavicle'],
                     modules['root'].ctrls['COG'],),
            source_names=('Chest', 'Clavicle', 'COG'),
            name='shoulder',
            attr_node=modules[f'{side}_arm'].ctrls['fk_upperarm'],
            attr_name='ShoulderSpace',
            global_space_parent=modules['root'].ctrls['subRoot'],
            side=nom.leftSideTag,
            translate=False, rotate=True, scale=False
        )
        rig_utils.space_blender(
            target=modules[f'{side}_arm'].ctrls['ik_hand'].getParent(),
            source=(modules[f'{side}_arm'].ctrls['ik_hand_follow']),
            source_name='global',
            name='ik_hand',
            attr_node=modules[f'{side}_arm'].ctrls['ik_hand'],
            attr_name='FollowSpace',
            global_space_parent=modules['root'].ctrls['subRoot'],
            translate=True, rotate=True, scale=True,
            reverse=True, default_value=0
        )
        rig_utils.space_blender(
            target=modules[f'{side}_arm'].ctrls['ik_elbow'].getParent(),
            source=(modules[f'{side}_arm'].ctrls['ik_hand']),
            source_name='global',
            name='ik_elbow',
            attr_node=modules[f'{side}_arm'].ctrls['ik_elbow'],
            attr_name='GlobalSpace',
            global_space_parent=modules['root'].ctrls['subRoot'],
            translate=True, rotate=True, scale=False,
            reverse=True
        )

        #...Legs
        rig_utils.space_switch(
            target=modules[f'{side}_leg'].ctrls['fk_thigh'].getParent(),
            sources=(modules['spine'].ctrls['ik_pelvis'],
                     modules['root'].ctrls['COG'],),
            source_names=('Pelvis', 'COG'),
            name='hip',
            attr_node=modules[f'{side}_leg'].ctrls['fk_thigh'],
            attr_name='HipSpace',
            global_space_parent=modules['root'].ctrls['subRoot'],
            side=nom.leftSideTag,
            translate=False, rotate=True, scale=False
        )
        rig_utils.space_blender(
            target=modules[f'{side}_leg'].ctrls['ik_foot'].getParent(),
            source=(modules[f'{side}_leg'].ctrls['ik_foot_follow']),
            source_name='global',
            name='ik_foot',
            attr_node=modules[f'{side}_leg'].ctrls['ik_foot'],
            attr_name='FollowSpace',
            global_space_parent=modules['root'].ctrls['subRoot'],
            translate=True, rotate=True, scale=True,
            reverse=True, default_value=0
        )
        rig_utils.space_blender(
            target=modules[f'{side}_leg'].ctrls['ik_knee'].getParent(),
            source=(modules[f'{side}_leg'].ctrls['ik_foot']),
            source_name='global',
            name='ik_knee',
            attr_node=modules[f'{side}_leg'].ctrls['ik_knee'],
            attr_name='GlobalSpace',
            global_space_parent=modules['root'].ctrls['subRoot'],
            translate=True, rotate=True, scale=False,
            reverse=False
        )
