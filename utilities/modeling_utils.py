# Title: modeling_utils.py
# Author: Sam Leheny
# Contact: samleheny@live.com

# Description: Utility functions specific to modeling.


###########################
##### Import Commands #####
import pymel.core as pm

import Snowman3.utilities.general_utils as gen

import Snowman3.utilities.node_utils as nodes

import Snowman3.dictionaries.nameConventions as nameConventions
nom = nameConventions.create_dict()
###########################
###########################



########################################################################################################################
############# ------------------------------    TABLE OF CONTENTS    ----------------------------------- ###############
########################################################################################################################
'''
reset_transform
reset_transform_on_hierarchy
safe_mirror_obj
'''
########################################################################################################################
########################################################################################################################
########################################################################################################################



#-----------------------------------------------------------------------------------------------------------------------
def reset_transform(obj):
    parent = obj.getParent()
    if parent:
        obj.setParent(world=1)

    children = pm.listRelatives(obj, children=1, type='transform', fullPath=1)
    if children:
        [child.setParent(world=1) for child in children]

    pm.makeIdentity(obj, apply=1, normal=1)
    pm.xform(obj, zeroTransformPivots=1)

    if children:
        [child.setParent(obj) for child in children]

    if parent:
        obj.setParent(parent)

    pm.select(clear=1)



#-----------------------------------------------------------------------------------------------------------------------
def reset_transform_on_hierarchy(top_obj):
    reset_transform(top_obj)
    children = pm.listRelatives(top_obj, children=1, type='transform', fullPath=1)
    if not children:
        return
    for child in children:
        reset_transform_on_hierarchy(child)



# ----------------------------------------------------------------------------------------------------------------------
def safe_mirror_obj(obj):
    obj_name = obj.nodeName()
    dup_obj = pm.duplicate(obj, rename=gen.get_opposite_side_string(obj_name))[0]
    [ d.rename(gen.get_opposite_side_string(d.nodeName())) for d in pm.listRelatives(dup_obj, ad=1, type='transform') ]
    reset_transform(obj)
    obj.sx.set(-1)
    reset_transform_on_hierarchy(obj)
