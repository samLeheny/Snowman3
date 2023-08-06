# Title: ngSkinTools_utils.py
# Author: Sam Leheny
# Contact: samleheny@live.com

# Description: Utility functions specific to rigging.


###########################
##### Import Commands #####
import pymel.core as pm
import maya.cmds as mc
from ngSkinTools.mllInterface import MllInterface

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
get_skin_cluster
copy_joint_influence
copy_skin_weight
copy_skin_weights
setup_ng_mirror_pairs
'''
########################################################################################################################
########################################################################################################################
########################################################################################################################



#-----------------------------------------------------------------------------------------------------------------------
def get_skin_cluster(obj):
    skin_clust = None
    for node in obj.connections(s=1, d=0):
        if node.nodeType() == 'skinCluster':
            skin_clust = node
            break
    return skin_clust



#-----------------------------------------------------------------------------------------------------------------------
def copy_joint_influence(*objs):
    source_mesh = objs[0]
    dest_meshes = objs[1:]
    source_skin_clust = get_skin_cluster(source_mesh)
    joint_list = pm.skinCluster(source_skin_clust, q=1, influence=1)
    return [pm.skinCluster(joint_list, mesh, toSelectedBones=1, n='skin')[0] for mesh in dest_meshes]



#-----------------------------------------------------------------------------------------------------------------------
def copy_skin_weight(*objs):
    uv_space = False
    source_mesh = objs[0]
    dest_meshes = objs[1:]
    source_skin_clust = get_skin_cluster(source_mesh)
    for dest_mesh in dest_meshes:
        dest_skin_clust = get_skin_cluster(dest_mesh)
        if uv_space:
            pm.copySkinWeights(ss=source_skin_clust, destinationSkin=dest_skin_clust, noMirror=1,
                               uvspace=['map1', 'map1'], influenceAssociation='closestJoint')
        else:
            pm.copySkinWeights(ss=source_skin_clust, destinationSkin=dest_skin_clust, noMirror=1, sa='closestPoint',
                               influenceAssociation='closestJoint')
        pm.skinCluster(dest_skin_clust, e=1, removeUnusedInfluence=1)



#-----------------------------------------------------------------------------------------------------------------------
def copy_skin_weights(*objs):
    copy_joint_influence(*objs)
    copy_skin_weight(*objs)



#-----------------------------------------------------------------------------------------------------------------------
def setup_ng_mirror_pairs(*objs):

    objs = objs or pm.ls(sl=1)
    if not objs:
        return False

    def setup_mirror_pairs_on_obj(obj_):
        jnts = [influ.fullPath() for influ in pm.skinCluster(obj_, q=1, influence=1)]
        mll = MllInterface()
        mll.setCurrentMesh(pm.selected()[0].name())
        influ_indices = mll.listInfluenceIndexes()
        influ_paths = mll.listInfluencePaths()

        influ_dict = {i: id_ for id_, i in zip(influ_indices, influ_paths)}

        mirror_dict = {}
        for jnt in jnts:
            if 'L_' in jnt and jnt.replace('L_', 'R_') in jnts:
                mirror_dict[ influ_dict[jnt] ] = influ_dict[ jnt.replace('L_', 'R_') ]
                mirror_dict[ influ_dict[ jnt.replace('L_', 'R_') ] ] = influ_dict[jnt]

        mll.setManualInfluences(mirror_dict)

    for obj in objs:
        setup_mirror_pairs_on_obj(obj)
