# Title: ik_rotate_ribbon.py
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
def build(ctrls, ik_translate_ribbon, ribbon_parent, ik_parent):
    ik_rotate_ribbon = pm.duplicate(ik_translate_ribbon, name="spineRibbon_IK_rotate_SURF")[0]
    for attr in gen_utils.all_transform_attrs:
        pm.setAttr(ik_rotate_ribbon + "." + attr, lock=0)
    ik_rotate_ribbon.setParent(world=1)

    ik_rotate_ribbon.setParent(ribbon_parent)

    # ...IK Rotate joints
    def ik_rotate_jnt_sys(name, v_value, ctrl=None):
        grp = pm.group(name="spine_{}_ik_rotate".format(name), p=ik_parent, em=1)

        pin = gen_utils.point_on_surface_matrix(ik_translate_ribbon.getShape() + ".worldSpace", parameter_U=0.5,
                                                parameter_V=v_value, decompose=True)
        pin.outputTranslate.connect(grp.translate)
        pin.outputRotate.connect(grp.rotate)

        jnt = rig_utils.joint(name="spine_{}_ik_rotate".format(name), joint_type=nom.nonBindJnt)

        offset = gen_utils.buffer_obj(jnt, parent=grp)
        pm.rename(offset, "spine_{}_ik_rotate_OFFSET".format(name))

        base_jnt = rig_utils.joint(name="spine_{}_ik_rotate_base".format(name), joint_type=nom.nonBindJnt,
                                   parent=offset)

        offset.translate.set(0, 0, 0)

        buffer = gen_utils.buffer_obj(jnt)
        if ctrl:
            ctrl.rotate.connect(buffer.rotate)

        return grp, jnt, base_jnt

    ik_rotate_bottom_sys = ik_rotate_jnt_sys("pelvis", 0.0, ctrls["ik_pelvis"])
    ik_rotate_mid_sys = ik_rotate_jnt_sys("waist", 0.5)
    ik_rotate_top_sys = ik_rotate_jnt_sys("chest", 1.0, ctrls["ik_chest"])

    # ...Skin IK Rotate Ribbon
    pm.select((ik_rotate_bottom_sys[1], ik_rotate_mid_sys[1], ik_rotate_top_sys[1]), replace=1)
    pm.select(ik_rotate_ribbon, add=1)
    pm.skinCluster(toSelectedBones=1, maximumInfluences=1, obeyMaxInfluences=0)
    skin_clust = gen_utils.get_skin_cluster(ik_rotate_ribbon)

    # ...Use IK Translate Ribbon as input shape for IK Rotate Ribbon's skin cluster
    rig_utils.mesh_to_skinClust_input(ik_translate_ribbon.getShape(), skin_clust)

    # ...Use IK Rotate base joints as preBindMatrix inputs for skin cluster to avoid double transforms from the IK
    # ...Translate Ribbon
    ik_rotate_bottom_sys[2].worldInverseMatrix[0].connect(skin_clust.bindPreMatrix[0])
    ik_rotate_mid_sys[2].worldInverseMatrix[0].connect(skin_clust.bindPreMatrix[1])
    ik_rotate_top_sys[2].worldInverseMatrix[0].connect(skin_clust.bindPreMatrix[2])

    # ...Refine weights
    pm.skinPercent(skin_clust, ik_rotate_ribbon + '.cv[0:3][0]', transformValue=[(ik_rotate_bottom_sys[1], 1.0)])
    pm.skinPercent(skin_clust, ik_rotate_ribbon + '.cv[0:3][1]', transformValue=[(ik_rotate_bottom_sys[1], 1.0)])
    pm.skinPercent(skin_clust, ik_rotate_ribbon + '.cv[0:3][2]', transformValue=[(ik_rotate_bottom_sys[1], 0.715),
                                                                                 (ik_rotate_mid_sys[1], 0.285)])
    pm.skinPercent(skin_clust, ik_rotate_ribbon + '.cv[0:3][3]', transformValue=[(ik_rotate_mid_sys[1], 1.0)])
    pm.skinPercent(skin_clust, ik_rotate_ribbon + '.cv[0:3][4]', transformValue=[(ik_rotate_top_sys[1], 1.0)])
    pm.skinPercent(skin_clust, ik_rotate_ribbon + '.cv[0:3][5]', transformValue=[(ik_rotate_top_sys[1], 1.0)])
    pm.skinPercent(skin_clust, ik_rotate_ribbon + '.cv[0:3][6]', transformValue=[(ik_rotate_top_sys[1], 1.0)])

    # ...Template IK Translate Ribbon for visual clarity
    ik_translate_ribbon.getShape().template.set(1)



    return{"nurbsPlane": ik_rotate_ribbon,
           "bottom_sys": ik_rotate_bottom_sys,
           "mid_sys": ik_rotate_mid_sys,
           "top_sys": ik_rotate_top_sys,}