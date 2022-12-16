# Title: ik_output_ribbon.py
# Author: Sam Leheny
# Contact: samleheny@live.com

# Description:


###########################
##### Import Commands #####
import pymel.core as pm

import Snowman.utilities.general_utils as gen_utils
reload(gen_utils)

import Snowman.utilities.node_utils as node_utils
reload(node_utils)

import Snowman.utilities.rig_utils as rig_utils
reload(rig_utils)

import Snowman.dictionaries.nameConventions as nameConventions
reload(nameConventions)
nom = nameConventions.create_dict()

import Snowman.riggers.modules.biped_spine.utilities.animCtrls as animCtrls
reload(animCtrls)
###########################
###########################


###########################
######## Variables ########

###########################
###########################





########################################################################################################################
def build(ctrls, ik_rotate_ribbon, ribbon_parent, jnt_parent):
    # ...IK Output nurbs plane
    ik_output_ribbon = pm.duplicate(ik_rotate_ribbon["nurbsPlane"], name="spineRibbon_IK_output_SURF")[0]
    for attr in gen_utils.all_transform_attrs:
        pm.setAttr(ik_output_ribbon + "." + attr, lock=0)
    ik_output_ribbon.setParent(world=1)

    ik_output_ribbon.setParent(ribbon_parent)

    # ...IK Output joints
    def ik_output_jnt_sys(name):

        jnt = rig_utils.joint(name="spine_{}_ik_output".format(name), joint_type=nom.nonBindJnt, parent=jnt_parent)

        base_jnt = rig_utils.joint(name="spine_{}_ik_output_base".format(name), joint_type=nom.nonBindJnt,
                                   parent=jnt_parent)

        [j.translate.set(0, 0, 0) for j in (jnt, base_jnt)]

        ctrls["ik_waist"].translate.connect(jnt.translate)
        ctrls["ik_waist"].rotate.connect(jnt.rotate)

        return jnt, base_jnt

    ik_output_mid_sys = ik_output_jnt_sys("waist")

    # ...Skin IK Rotate Ribbon
    pm.select((ik_rotate_ribbon["bottom_sys"][2], ik_rotate_ribbon["top_sys"][2], ik_output_mid_sys[0]), replace=1)
    pm.select(ik_output_ribbon, add=1)
    pm.skinCluster(toSelectedBones=1, maximumInfluences=1, obeyMaxInfluences=0)
    skin_clust = gen_utils.get_skin_cluster(ik_output_ribbon)

    # ...Use IK Rotate Ribbon as input shape for IK Output Ribbon's skin cluster
    rig_utils.mesh_to_skinClust_input(ik_rotate_ribbon["nurbsPlane"].getShape(), skin_clust)

    # ...Use IK Rotate base joints as preBindMatrix inputs for skin cluster to avoid double transforms from the IK
    # ...Translate Ribbon
    ik_rotate_ribbon["bottom_sys"][2].worldInverseMatrix[0].connect(skin_clust.bindPreMatrix[0])
    ik_rotate_ribbon["top_sys"][2].worldInverseMatrix[0].connect(skin_clust.bindPreMatrix[1])
    ik_output_mid_sys[1].worldInverseMatrix[0].connect(skin_clust.bindPreMatrix[2])

    # ...Refine weights
    pm.skinPercent(skin_clust, ik_output_ribbon + '.cv[0:3][0]', transformValue=[(ik_rotate_ribbon["bottom_sys"][2], 1.0)])
    pm.skinPercent(skin_clust, ik_output_ribbon + '.cv[0:3][1]', transformValue=[(ik_rotate_ribbon["bottom_sys"][2], 1.0)])
    pm.skinPercent(skin_clust, ik_output_ribbon + '.cv[0:3][2]', transformValue=[(ik_rotate_ribbon["bottom_sys"][2], 0.715),
                                                                                 (ik_output_mid_sys[0], 0.285)])
    pm.skinPercent(skin_clust, ik_output_ribbon + '.cv[0:3][3]', transformValue=[(ik_output_mid_sys[0], 1.0)])
    pm.skinPercent(skin_clust, ik_output_ribbon + '.cv[0:3][4]', transformValue=[(ik_rotate_ribbon["top_sys"][2], 0.75),
                                                                                 (ik_output_mid_sys[0], 0.25)])
    pm.skinPercent(skin_clust, ik_output_ribbon + '.cv[0:3][5]', transformValue=[(ik_rotate_ribbon["top_sys"][2], 1.0)])
    pm.skinPercent(skin_clust, ik_output_ribbon + '.cv[0:3][6]', transformValue=[(ik_rotate_ribbon["top_sys"][2], 1.0)])

    # ...Template FK Ribbon for visual clarity
    ik_rotate_ribbon["nurbsPlane"].getShape().template.set(1)



    return{"nurbsPlane": ik_output_ribbon}