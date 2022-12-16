# Title: waist_ribbon.py
# Author: Sam Leheny
# Contact: samleheny@live.com

# Description: Installs ribbon set up on the waist placers of the biped_spine setup module.


###########################
##### Import Commands #####
import importlib
import pymel.core as pm

import Snowman3.utilities.general_utils as gen_utils
importlib.reload(gen_utils)

import Snowman3.utilities.rig_utils as rig_utils
importlib.reload(rig_utils)

import Snowman3.utilities.node_utils as node_utils
importlib.reload(node_utils)

import Snowman3.dictionaries.nameConventions as nameConventions
importlib.reload(nameConventions)
nom = nameConventions.create_dict()
###########################
###########################


###########################
######## Variables ########
###########################
###########################





########################################################################################################################
def install(spine_module, symmetry):

    spine_placers = spine_module.placers

    # ...Get total length of waist (will serve as distance between bottom and top waist placer)
    waist_length = gen_utils.distance_between(spine_placers["spine_1"].mobject,
                                              spine_placers["spine_5"].mobject)

    # ...Create ribbon nurbsPlane
    nurbs_plane = pm.nurbsPlane(name="spineRibbon_{}".format("SURF"), lengthRatio=17, width=waist_length / 17,
                                patchesU=1, patchesV=4, axis=[0, 0, 1])[0]

    # ...Move ribbon to match start and end placers
    nurbs_plane.ty.set(waist_length/2)

    # ...Match isoparms to placers
    for i in range(2, 5):
        for j in range (4):

            cv = pm.ls(nurbs_plane.getShape().cv[j][i])[0]

            current_pos = pm.pointPosition(nurbs_plane.getShape().cv[j][i], world=1)

            placer_pos = pm.xform(spine_placers["spine_{}".format(i)].mobject, rotatePivot=1,
                                  worldSpace=1, q=1)

            y = placer_pos[1] - current_pos[1]

            pm.move(cv, (0, y, 0), relative=1)



    # ...Create joints that will drive ribbon nurbsPlane
    ribbon_jnts = [rig_utils.joint(name="setupSpineRibbon_{}".format(str(i + 1)),
                                   joint_type=nom.nonBindJnt) for i in range(0, 5)]

    ribbon_jnts_grp = pm.group(name="ribbon_jnts", world=1, em=1)
    ribbon_jnts_grp.visibility.set(0)

    # ...Position joints
    for i in range(0, 5):
        mult_matrix = node_utils.multMatrix(matrixIn=(spine_placers["spine_{}".format(i+1)].mobject.worldMatrix,
                                                      ribbon_jnts[i].parentInverseMatrix))
        node_utils.decomposeMatrix(inputMatrix=mult_matrix.matrixSum, outputTranslate=ribbon_jnts[i].translate,
                                   outputRotate=ribbon_jnts[i].rotate,
                                   outputScale=ribbon_jnts[i].scale)
        ribbon_jnts[i].setParent(ribbon_jnts_grp)


    # ...Skin bind ribbon
    pm.select(ribbon_jnts, replace=1)
    pm.select(nurbs_plane, add=1)
    pm.skinCluster(toSelectedBones=1, maximumInfluences=1, obeyMaxInfluences=0)
    skin_clust = gen_utils.get_skin_cluster(nurbs_plane)

    pm.skinPercent(skin_clust, nurbs_plane + '.cv[0:3][1]',
                   transformValue=[(ribbon_jnts[0], 0.6), (ribbon_jnts[1], 0.4)])
    pm.skinPercent(skin_clust, nurbs_plane + '.cv[0:3][5]',
                   transformValue=[(ribbon_jnts[-2], 0.4), (ribbon_jnts[-1], 0.6)])




    return {"nurbsPlane": nurbs_plane,
            "joints": ribbon_jnts,
            "joints_group": ribbon_jnts_grp}
