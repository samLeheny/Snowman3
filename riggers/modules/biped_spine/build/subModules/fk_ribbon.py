# Title: fk_ribbon.py
# Author: Sam Leheny
# Contact: samleheny@live.com

# Description:


###########################
##### Import Commands #####
import pymel.core as pm

import Snowman3.utilities.general_utils as gen_utils
reload(gen_utils)

import Snowman3.utilities.node_utils as node_utils
reload(node_utils)

import Snowman3.utilities.rig_utils as rig_utils
reload(rig_utils)

import Snowman3.dictionaries.nameConventions as nameConventions
reload(nameConventions)
nom = nameConventions.create_dict()

import Snowman3.riggers.modules.biped_spine.utilities.animCtrls as animCtrls
reload(animCtrls)
###########################
###########################


###########################
######## Variables ########

###########################
###########################





########################################################################################################################
def build(parent, ctrls, orienters, ribbon_parent):


    # FK nurbs plane ------------------------------------------------------------------------------------------------------
    setup_ribbon = pm.PyNode("{}:spineRibbon_SURF".format(nom.setupRigNamespace))

    fk_ribbon = pm.duplicate(setup_ribbon, name="spineRibbon_FK_SURF")[0]
    for attr in gen_utils.all_transform_attrs:
        pm.setAttr(fk_ribbon+"."+attr, lock=0)
    fk_ribbon.setParent(world=1)

    pm.select(fk_ribbon)
    pm.delete(constructionHistory=1)
    pm.makeIdentity(apply=True, translate=True, rotate=True, scale=True)
    pm.select(clear=1)

    fk_ribbon.setParent(ribbon_parent)


    # FK joints --------------------------------------------------------------------------------------------------------
    def position_joint(jnt, v_value, jnt_parent=None):

        pin = gen_utils.point_on_surface_matrix(fk_ribbon.getShape() + ".worldSpace", parameter_U=0.5,
                                                  parameter_V=v_value, decompose=True)
        pin.outputTranslate.connect(jnt.translate)
        gen_utils.break_connections(jnt.translate)
        pm.delete(pin)

        jnt.setParent(jnt_parent) if jnt_parent else None


    fk_1_jnt = rig_utils.joint(name="FK_1", joint_type=nom.nonBindJnt, radius=1.3)
    position_joint(fk_1_jnt, 0.0, ctrls["fk_hips"])

    fk_1_inv_jnt = rig_utils.joint(name="FK_1_inv", joint_type=nom.nonBindJnt, radius=1)
    pm.delete(pm.pointConstraint(ctrls["fk_hips"], fk_1_inv_jnt))
    fk_1_inv_jnt.setParent(fk_1_jnt)

    buffer = gen_utils.buffer_obj(ctrls["fk_hips"])
    buffer.setParent(parent)



    fk_2_jnt = rig_utils.joint(name="FK_2", joint_type=nom.nonBindJnt, radius=1.3)
    position_joint(fk_2_jnt, 0.32, ctrls["fk_spine_1"])

    fk_2_inv_jnt = rig_utils.joint(name="FK_2_inv", joint_type=nom.nonBindJnt, radius=1)
    position_joint(fk_2_inv_jnt, 0.69, fk_2_jnt)

    buffer = gen_utils.buffer_obj(ctrls["fk_spine_1"])
    buffer.setParent(parent)



    fk_3_jnt = rig_utils.joint(name="FK_3", joint_type=nom.nonBindJnt, radius=1.3)
    pm.delete(pm.pointConstraint(fk_2_inv_jnt, fk_3_jnt))
    fk_3_jnt.setParent(ctrls["fk_spine_2"])

    fk_3_inv_jnt = rig_utils.joint(name="FK_3_inv", joint_type=nom.nonBindJnt, radius=1)
    pm.delete(pm.pointConstraint(ctrls["fk_spine_3"], fk_3_inv_jnt))
    fk_3_inv_jnt.setParent(fk_3_jnt)

    buffer = gen_utils.buffer_obj(ctrls["fk_spine_2"])
    buffer.setParent(fk_2_inv_jnt)



    fk_4_jnt = rig_utils.joint(name="FK_4", joint_type=nom.nonBindJnt, radius=1.3)
    pm.delete(pm.pointConstraint(ctrls["fk_spine_3"], fk_4_jnt))
    fk_4_jnt.setParent(ctrls["fk_spine_3"])

    fk_4_inv_jnt = rig_utils.joint(name="FK_4_inv", joint_type=nom.nonBindJnt, radius=1)
    pm.delete(pm.pointConstraint(orienters["spine_6"], fk_4_inv_jnt))
    fk_4_inv_jnt.setParent(ctrls["fk_spine_3"])

    buffer = gen_utils.buffer_obj(ctrls["fk_spine_3"])
    buffer.setParent(fk_3_inv_jnt)


    fk_jnts = [fk_1_jnt, fk_1_inv_jnt, fk_2_jnt, fk_2_inv_jnt, fk_3_jnt, fk_3_inv_jnt, fk_4_jnt, fk_4_inv_jnt]



    # ...Skin FK Ribbon
    pm.select((fk_jnts[0], fk_jnts[1], fk_jnts[2], fk_jnts[4], fk_jnts[5], fk_jnts[7]), replace=1)
    pm.select(fk_ribbon, add=1)
    pm.skinCluster(toSelectedBones=1, maximumInfluences=1, obeyMaxInfluences=0)
    skin_clust = gen_utils.get_skin_cluster(fk_ribbon)

    # ...Refine weights
    pm.skinPercent(skin_clust, fk_ribbon + '.cv[0:3][0]', transformValue=[(fk_jnts[0], 1.0)])
    pm.skinPercent(skin_clust, fk_ribbon + '.cv[0:3][1]', transformValue=[(fk_jnts[0], 1.0)])
    pm.skinPercent(skin_clust, fk_ribbon + '.cv[0:3][2]', transformValue=[(fk_jnts[0], 0.8), (fk_jnts[1], 0.2)])
    pm.skinPercent(skin_clust, fk_ribbon + '.cv[0:3][3]', transformValue=[(fk_jnts[2], 1.0)])
    pm.skinPercent(skin_clust, fk_ribbon + '.cv[0:3][4]', transformValue=[(fk_jnts[4], 0.9), (fk_jnts[5], 0.1)])
    pm.skinPercent(skin_clust, fk_ribbon + '.cv[0:3][5]', transformValue=[(fk_jnts[4], 0.05), (fk_jnts[7], 0.95)])
    pm.skinPercent(skin_clust, fk_ribbon + '.cv[0:3][6]', transformValue=[(fk_jnts[7], 1.0)])



    return{"nurbsPlane": fk_ribbon,
           "fkJnts": fk_jnts}