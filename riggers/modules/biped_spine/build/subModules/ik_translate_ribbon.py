# Title: ik_translate_ribbon.py
# Author: Sam Leheny
# Contact: samleheny@live.com

# Description:


###########################
##### Import Commands #####
import pymel.core as pm
import importlib

import Snowman3.utilities.general_utils as gen_utils
importlib.reload(gen_utils)

import Snowman3.utilities.node_utils as node_utils
importlib.reload(node_utils)

import Snowman3.utilities.rig_utils as rig_utils
importlib.reload(rig_utils)

import Snowman3.dictionaries.nameConventions as nameConventions
importlib.reload(nameConventions)
nom = nameConventions.create_dict()

import Snowman3.riggers.modules.biped_spine.utilities.animCtrls as animCtrls
importlib.reload(animCtrls)
###########################
###########################


###########################
######## Variables ########

###########################
###########################





########################################################################################################################
def build(ctrls, fk_ribbon, ribbon_parent, ik_parent):

    # ...IK Translate nurbs plane
    ik_translate_ribbon = pm.duplicate(fk_ribbon, name="spineRibbon_IK_translate_SURF")[0]
    for attr in gen_utils.all_transform_attrs:
        pm.setAttr(ik_translate_ribbon + "." + attr, lock=0)
    ik_translate_ribbon.setParent(world=1)

    ik_translate_ribbon.setParent(ribbon_parent)


    # ...IK Translate joints
    def ik_translate_jnt_sys(name, v_value, ctrl, mid=False):
        grp = pm.group(name="spine_{}_ik_translate".format(name), p=ik_parent, em=1)

        ctrl_driver_ribbon = fk_ribbon.getShape()
        if mid:
            ctrl_driver_ribbon = ik_translate_ribbon.getShape()
        pin = gen_utils.point_on_surface_matrix(ctrl_driver_ribbon + ".worldSpace", parameter_U=0.5,
                                                parameter_V=v_value, decompose=True)
        pin.outputTranslate.connect(grp.translate)
        pin.outputRotate.connect(grp.rotate)

        ctrl.setParent(ctrl, grp)
        buffer = gen_utils.buffer_obj(ctrl)

        jnt, base_jnt = None, None
        if not mid:
            jnt = rig_utils.joint(name="spine_{}_ik_translate".format(name), joint_type=nom.nonBindJnt, parent=buffer)
            base_jnt = rig_utils.joint(name="spine_{}_ik_translate_base".format(name), joint_type=nom.nonBindJnt,
                                       parent=buffer)
            [gen_utils.zero_out(j) for j in (jnt, base_jnt)]

            ctrl.translate.connect(jnt.translate)

        return grp, jnt, base_jnt


    ik_translate_bottom_sys = ik_translate_jnt_sys("pelvis", 0.0, ctrls["ik_pelvis"])
    ik_translate_mid_sys = ik_translate_jnt_sys("waist", 0.5, ctrls["ik_waist"], mid=True)
    ik_translate_top_sys = ik_translate_jnt_sys("chest", 1.0, ctrls["ik_chest"])


    # ...Skin IK Translate Ribbon
    pm.select((ik_translate_bottom_sys[1], ik_translate_top_sys[1]), replace=1)
    pm.select(ik_translate_ribbon, add=1)
    pm.skinCluster(toSelectedBones=1, maximumInfluences=1, obeyMaxInfluences=0)
    skin_clust = gen_utils.get_skin_cluster(ik_translate_ribbon)

    # ...Use FK Ribbon as input shape for IK Translate Ribbon's skin cluster
    rig_utils.mesh_to_skinClust_input(fk_ribbon.getShape(), skin_clust)

    # ...Use IK Translate base joints as preBindMatrix inputs for skin cluster to avoid double transforms from the FK
    # ...Ribbon
    ik_translate_bottom_sys[2].worldInverseMatrix[0].connect(skin_clust.bindPreMatrix[0])
    ik_translate_top_sys[2].worldInverseMatrix[0].connect(skin_clust.bindPreMatrix[1])

    # ...Refine weights
    pm.skinPercent(skin_clust, ik_translate_ribbon + '.cv[0:3][0]', transformValue=[(ik_translate_bottom_sys[1], 1.0)])
    pm.skinPercent(skin_clust, ik_translate_ribbon + '.cv[0:3][1]', transformValue=[(ik_translate_bottom_sys[1], 1.0)])
    pm.skinPercent(skin_clust, ik_translate_ribbon + '.cv[0:3][2]', transformValue=[(ik_translate_bottom_sys[1], 1.0)])
    pm.skinPercent(skin_clust, ik_translate_ribbon + '.cv[0:3][3]', transformValue=[(ik_translate_bottom_sys[1], 0.6),
                                                                                    (ik_translate_top_sys[1], 0.4)])
    pm.skinPercent(skin_clust, ik_translate_ribbon + '.cv[0:3][4]', transformValue=[(ik_translate_bottom_sys[1], 0.05),
                                                                                    (ik_translate_top_sys[1], 0.95)])
    pm.skinPercent(skin_clust, ik_translate_ribbon + '.cv[0:3][5]', transformValue=[(ik_translate_top_sys[1], 1.0)])
    pm.skinPercent(skin_clust, ik_translate_ribbon + '.cv[0:3][6]', transformValue=[(ik_translate_top_sys[1], 1.0)])

    # ...Template FK Ribbon for visual clarity
    fk_ribbon.getShape().template.set(1)



    return{"nurbsPlane": ik_translate_ribbon}