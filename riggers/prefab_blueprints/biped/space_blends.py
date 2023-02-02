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

import Snowman3.riggers.utilities.classes.class_SpaceBlend as classSpaceBlend
importlib.reload(classSpaceBlend)
SpaceBlend = classSpaceBlend.SpaceBlend
###########################
###########################


###########################
######## Variables ########

###########################
###########################





def create_space_blends():

        space_blends = [

            #...Neck
            SpaceBlend(
                type='blend',
                target="modules['neck'].ctrls['neck'].getParent()",
                source="modules['spine'].ctrls['ik_chest']",
                source_name='global',
                name='neck',
                attr_node="modules['neck'].ctrls['neck']",
                attr_name='GlobalSpace',
                global_space_parent="modules['root'].ctrls['subRoot']",
                translate=False,
                rotate=True,
                scale=False
            )

        ]

        for side in (nom.leftSideTag, nom.rightSideTag):

            sided_space_blends = [

                # ...Arms
                SpaceBlend(
                    type='switch',
                    target="modules[f'{side}_arm'].ctrls['fk_upperarm'].getParent()",
                    source=("modules['spine'].ctrls['ik_chest']",
                            "modules[f'{side}_clavicle'].ctrls['clavicle']",
                            "modules['root'].ctrls['COG']"),
                    source_name=('Chest', 'Clavicle', 'COG'),
                    name='shoulder',
                    attr_node="modules[f'{side}_arm'].ctrls['fk_upperarm']",
                    attr_name='ShoulderSpace',
                    global_space_parent="modules['root'].ctrls['subRoot']",
                    side=side,
                    translate=False, rotate=True, scale=False
                ),
                SpaceBlend(
                    type='blend',
                    target="modules[f'{side}_arm'].ctrls['ik_hand'].getParent()",
                    source=("modules[f'{side}_arm'].ctrls['ik_hand_follow']"),
                    source_name='global',
                    name='ik_hand',
                    attr_node="modules[f'{side}_arm'].ctrls['ik_hand']",
                    attr_name='FollowSpace',
                    global_space_parent="modules['root'].ctrls['subRoot']",
                    translate=True,
                    rotate=True,
                    scale=True,
                    reverse=True,
                    default_value=0
                ),
                SpaceBlend(
                    type='blend',
                    target="modules[f'{side}_arm'].ctrls['ik_elbow'].getParent()",
                    source=("modules[f'{side}_arm'].ctrls['ik_hand']",),
                    source_name='global',
                    name='ik_elbow',
                    attr_node="modules[f'{side}_arm'].ctrls['ik_elbow']",
                    attr_name='GlobalSpace',
                    global_space_parent="modules['root'].ctrls['subRoot']",
                    translate=True,
                    rotate=True,
                    scale=False
                ),

                # ...Legs
                SpaceBlend(
                    type='switch',
                    target="modules[f'{side}_leg'].ctrls['fk_thigh'].getParent()",
                    source=("modules['spine'].ctrls['ik_pelvis']",
                            "modules['root'].ctrls['COG']"),
                    source_name=('Pelvis', 'COG'),
                    name='hip',
                    attr_node="modules[f'{side}_leg'].ctrls['fk_thigh']",
                    attr_name='HipSpace',
                    global_space_parent="modules['root'].ctrls['subRoot']",
                    side=side,
                    translate=False, rotate=True, scale=False
                ),
                SpaceBlend(
                    type='blend',
                    target="modules[f'{side}_leg'].ctrls['ik_foot'].getParent()",
                    source=("modules[f'{side}_leg'].ctrls['ik_foot_follow']",),
                    source_name='global',
                    name='ik_foot',
                    attr_node="modules[f'{side}_leg'].ctrls['ik_foot']",
                    attr_name='FollowSpace',
                    global_space_parent="modules['root'].ctrls['subRoot']",
                    translate=True,
                    rotate=True,
                    scale=True,
                    reverse=True,
                    default_value=0
                ),
                SpaceBlend(
                    type='blend',
                    target="modules[f'{side}_leg'].ctrls['ik_knee'].getParent()",
                    source=("modules[f'{side}_leg'].ctrls['ik_foot']",),
                    source_name='global',
                    name='ik_knee',
                    attr_node="modules[f'{side}_leg'].ctrls['ik_knee']",
                    attr_name='GlobalSpace',
                    global_space_parent="modules['root'].ctrls['subRoot']",
                    translate=True,
                    rotate=True,
                    scale=False
                )

            ]

            for blend_instance in sided_space_blends:
                space_blends.append(blend_instance)


        return space_blends

'''
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
        translate=True, rotate=True, scale=False
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
        translate=True, rotate=True, scale=False
    )
'''
