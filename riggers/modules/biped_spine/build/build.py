# Title: spine_build.py
# Author: Sam Leheny
# Contact: samleheny@live.com

# Description: Builds setup module of biped biped_spine rig.


###########################
##### Import Commands #####
import importlib
import pymel.core as pm

import Snowman3.utilities.general_utils as gen_utils
importlib.reload(gen_utils)

import Snowman3.utilities.node_utils as node_utils
importlib.reload(node_utils)

import Snowman3.utilities.rig_utils as rig_utils
importlib.reload(rig_utils)

import Snowman3.dictionaries.nameConventions as nameConventions
importlib.reload(nameConventions)
nom = nameConventions.create_dict()

import Snowman3.riggers.modules.biped_spine.build.subModules.fk_ribbon as build_fk_ribbon
importlib.reload(build_fk_ribbon)

import Snowman3.riggers.modules.biped_spine.build.subModules.ik_translate_ribbon \
    as build_ik_translate_ribbon
importlib.reload(build_ik_translate_ribbon)

import Snowman3.riggers.modules.biped_spine.build.subModules.ik_rotate_ribbon \
    as build_ik_rotate_ribbon
importlib.reload(build_ik_rotate_ribbon)

import Snowman3.riggers.modules.biped_spine.build.subModules.ik_output_ribbon as build_ik_output_ribbon
importlib.reload(build_ik_output_ribbon)

import Snowman3.riggers.modules.biped_spine.utilities.animCtrls as animCtrls
importlib.reload(animCtrls)
###########################
###########################


###########################
######## Variables ########
bind_jnt_count = 7
attr_names = {"spine_volume": "SpineVolume",
              "tweak_ctrl_vis": "TweakCtrls",
              "pivot_height": "pivotHeight"}
###########################
###########################





########################################################################################################################
def build(rig_module, rig_parent=None):

    ctrl_data = animCtrls.create_anim_ctrls(side=rig_module.side, module_ctrl=rig_module.setup_module_ctrl)
    ctrls = rig_module.ctrls
    for key in ctrl_data:
        ctrls[key] = ctrl_data[key].initialize_anim_ctrl()
        ctrl_data[key].finalize_anim_ctrl()


    ctrls["settings"].setParent(rig_module.transform_grp)



    # Ribbon system ----------------------------------------------------------------------------------------------------
    # Uses several ribbons layered via connected skinClusters.
    # There are four ribbons: FK ribbon > IK Translate > IK Rotate > IK Output (final output ribbon)

    # ...Group to house ribbons
    ribbons_grp = pm.group(name="spine_ribbons", p=rig_module.no_transform_grp, em=1)

    ik_ctrls_grp = pm.group(name="ik_spine_ctrls", em=1, p=rig_module.no_transform_grp)

    # ...FK
    fk_ribbon = build_fk_ribbon.build(rig_module.transform_grp, ctrls, rig_module.orienters, ribbon_parent=ribbons_grp)
    # ...IK Translate
    ik_translate_ribbon = build_ik_translate_ribbon.build(ctrls, fk_ribbon["nurbsPlane"], ribbon_parent=ribbons_grp,
                                                          ik_parent=ik_ctrls_grp)
    # ...IK Rotate
    ik_rotate_ribbon = build_ik_rotate_ribbon.build(ctrls, ik_translate_ribbon["nurbsPlane"],
                                                    ribbon_parent=ribbons_grp, ik_parent=ik_ctrls_grp)
    # ...IK Output
    ik_output_ribbon = build_ik_output_ribbon.build(ctrls, ik_rotate_ribbon, ribbon_parent=ribbons_grp,
                                                    jnt_parent=ctrls["ik_waist"].getParent())





    # Bind Joints ------------------------------------------------------------------------------------------------------
    bind_jnts_grp = pm.group(name="spine_bindJnts", p=rig_module.no_transform_grp, em=1)

    bind_jnts = []
    bind_jnt_attach_nodes = []
    for i in range(bind_jnt_count):

        jnt = rig_utils.joint(name="spine_{}".format(str(i+1)), joint_type=nom.bindJnt, radius=1.25)
        jnt_buffer = gen_utils.buffer_obj(jnt)
        pin = gen_utils.point_on_surface_matrix(ik_output_ribbon["nurbsPlane"].getShape() + ".worldSpace",
                                                parameter_U=0.5, parameter_V=(1.0/6)*i, decompose=True)

        attach = pm.group(name=f"{str(jnt)}_ATTACH", em=1, p=bind_jnts_grp)
        pin.outputTranslate.connect(attach.translate)
        pin.outputRotate.connect(attach.rotate)

        jnt_buffer.setParent(attach)
        jnt_buffer.translate.set(0, 0, 0)

        mult_matrix = node_utils.multMatrix(matrixIn=(rig_module.rig_module_grp.worldMatrix,
                                                      jnt_buffer.parentInverseMatrix))
        node_utils.decomposeMatrix(inputMatrix=mult_matrix.matrixSum, outputScale=jnt_buffer.scale)

        bind_jnts.append(jnt)
        bind_jnt_attach_nodes.append(attach)


    for pack in ( (ctrls["ik_pelvis"], (0, 1)), (ctrls["ik_waist"], (2, 3, 4)), (ctrls["ik_chest"], (5,)) ):
        ctrl, indices = pack[0], pack[1]
        for i in indices:
            mod = gen_utils.buffer_obj(bind_jnts[i], suffix="MOD")
            mult_matrix = node_utils.multMatrix(matrixIn=(ctrl.worldMatrix, mod.parentInverseMatrix))
            node_utils.decomposeMatrix(inputMatrix=mult_matrix.matrixSum,
                                       outputScale=mod.scale)



    # Control scaling --------------------------------------------------------------------------------------------------
    for ctrl in (ctrls["ik_pelvis"], ctrls["ik_waist"], ctrls["ik_chest"]):
        node = ctrl.getParent(generations=2)
        mult_matrix = node_utils.multMatrix(matrixIn=(rig_module.rig_module_grp.worldMatrix, node.parentInverseMatrix))
        node_utils.decomposeMatrix(inputMatrix=mult_matrix.matrixSum, outputScale=node.scale)



    # Install tweak controls above bind joints -------------------------------------------------------------------------
    pm.addAttr(ctrls["settings"], longName=attr_names["tweak_ctrl_vis"], attributeType="enum", keyable=0,
               enumName="Off:On")
    pm.setAttr(ctrls["settings"] + '.' + attr_names["tweak_ctrl_vis"], channelBox=1)

    for i in range(7):
        ctrl = ctrls["spine_tweak_{}".format(i+1)]
        ctrl_buffer = gen_utils.buffer_obj(ctrl)
        ctrl_buffer.setParent(bind_jnts[i].getParent())
        bind_jnts[i].setParent(ctrl)
        pm.connectAttr(ctrls["settings"] + "." + attr_names["tweak_ctrl_vis"], ctrl.getShape().visibility)



    # Spine volume -----------------------------------------------------------------------------------------------------
    pm.addAttr(ctrls["settings"], longName=attr_names["spine_volume"], attributeType="float", minValue=0, maxValue=10,
               defaultValue=0, keyable=1)

    len_1 = pm.shadingNode("arcLengthDimension", au=1)
    len_2 = pm.shadingNode("arcLengthDimension", au=1)
    for length in (len_1, len_2):
        length.visibility.set(0, lock=1)
        length.uParamValue.set(0.5)
        length.vParamValue.set(4.0)

    len_1.getParent().setParent(fk_ribbon["nurbsPlane"])
    len_2.getParent().setParent(ik_output_ribbon["nurbsPlane"])

    fk_ribbon["nurbsPlane"].worldSpace[0].connect(len_1.nurbsGeometry)
    ik_output_ribbon["nurbsPlane"].worldSpace[0].connect(len_2.nurbsGeometry)

    div = node_utils.floatMath(floatA=len_1.arcLengthInV, floatB=len_2.arcLengthInV, operation=3)

    remap = node_utils.remapValue(inputValue=f'{ctrls["settings"]}.{attr_names["spine_volume"]}', inputMax=10, outputMin=1,
                                  outputMax=div.outFloat)

    for i in (2, 3, 4, 5):
        for attr in ("sx", "sz"):
            pm.connectAttr(remap.outValue, f'{ctrls[f"spine_tweak_{i}"].getParent()}.{attr}')



    # IK control pivot height settings ---------------------------------------------------------------------------------
    for node_set in (("settings", [],), ("ik_pelvis", [ik_rotate_ribbon["bottom_sys"][1].getParent()],),
                        ("ik_chest", [ik_rotate_ribbon["top_sys"][1].getParent()])):
        ctrl = ctrls[node_set[0]]
        target_nodes = node_set[1]
        target_nodes.append(ctrl)
        pm.addAttr(ctrl, longName=attr_names["pivot_height"], keyable=1, attributeType='float', defaultValue=0)
        for node in target_nodes:
            pm.connectAttr(ctrl+'.'+attr_names["pivot_height"], node+'.rotatePivotY')




    # ------------------------------------------------------------------------------------------------------------------
    rig_module.hips_socket = ctrls["ik_pelvis"]
    rig_module.clavicles_socket = ctrls["ik_chest"]
    rig_module.neck_socket = fk_ribbon["fkJnts"][-1]

    '''neck_socket = rig_module.socket["neck"] = pm.spaceLocator(name="neckRig_socket")
    neck_socket.setParent(ctrls["ik_chest"])
    pm.matchTransform(neck_socket, fk_ribbon["fkJnts"][-1])'''




    pm.select(clear=1)
    return rig_module
