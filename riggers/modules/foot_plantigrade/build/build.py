# Title: foot_build.py
# Author: Sam Leheny
# Contact: samleheny@live.com

# Description: Builds setup module of biped foot rig.


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

import Snowman3.riggers.modules.foot_plantigrade.utilities.animCtrls as animCtrls
importlib.reload(animCtrls)

import Snowman3.riggers.modules.foot_plantigrade.build.fkFoot as fkFoot
importlib.reload(fkFoot)
import Snowman3.riggers.modules.foot_plantigrade.build.ikFoot as ikFoot
importlib.reload(ikFoot)
###########################
###########################


###########################
######## Variables ########

###########################
###########################





########################################################################################################################
#def build(rig_module, rig_parent=None, settings_ctrl=None, foot_roll_ctrl=None):
def build(rig_module, rig_parent=None):


    '''
    [ctrls[key].setParent(rig_module.transform_grp) for key in ctrl_data]

    # ...Ensure a kinematic blend attribute is present on given control
    if not pm.attributeQuery("fkIk", node=settings_ctrl, exists=1):
        pm.addAttr(settings_ctrl, longName="fkIk", niceName="FK / IK", attributeType="float", minValue=0, maxValue=10,
                   defaultValue=10, keyable=1)

        kinematic_blend_mult = gen_utils.create_attr_blend_nodes(attr="fkIk", node=settings_ctrl)
        kinematic_blend_rev = gen_utils.create_attr_blend_nodes(attr="fkIk", node=settings_ctrl, reverse=True)


    kinematic_blend_mult = gen_utils.get_attr_blend_nodes(attr="fkIk", node=settings_ctrl, mult=True)
    kinematic_blend_rev = gen_utils.get_attr_blend_nodes(attr="fkIk", node=settings_ctrl, reverse=True)

    kinematic_blend_mult.connect(ctrls["ik_toe"].visibility)
    kinematic_blend_rev.connect(ctrls["fk_toe"].visibility)




    # ...Bind joints ---------------------------------------------------------------------------------------------------
    bind_jnts = {}
    bind_jnt_keys = ("foot", "ball", "ball_end")
    bind_chain_buffer = None
    for i in range(len(bind_jnt_keys)):
        key = bind_jnt_keys[i]
        par = bind_jnts[bind_jnt_keys[i-1]] if i > 0 else None
        bind_jnts[key] = rig_utils.joint(name=key, joint_type=nom.bindJnt, side=rig_module.side, radius=0.5, parent=par)
        if i == 0:
            bind_chain_buffer = gen_utils.buffer_obj(bind_jnts[key])

    bind_chain_buffer.setParent(rig_module.transform_grp)
    gen_utils.zero_out(bind_chain_buffer)

    for i in range(len(bind_jnt_keys)):
        key = bind_jnt_keys[i]
        if i == 0:
            pm.matchTransform(bind_chain_buffer, rig_module.orienters[key])
        else:
            pm.matchTransform(bind_jnts[key], rig_module.orienters[key])


    bind_connector = rig_module.bind_connector = pm.spaceLocator(name="{}bindConnector".format(rig_module.side_tag))
    pm.matchTransform(bind_connector, bind_chain_buffer)

    mult_matrix = node_utils.multMatrix(matrixIn=(bind_connector.worldMatrix,
                                                  bind_chain_buffer.parentInverseMatrix))
    node_utils.decomposeMatrix(inputMatrix=mult_matrix.matrixSum, outputTranslate=bind_chain_buffer.translate)




    # ...IK rig
    ik_foot_rig = ikFoot.build(side=rig_module.side, parent=rig_module.transform_grp, bind_jnt_keys=bind_jnt_keys,
                               orienters=rig_module.orienters, ctrls=ctrls, foot_roll_ctrl=foot_roll_ctrl)
    rig_module.ik_connector = ik_foot_rig["ik_connector"]
    rig_module.ik_chain_connector = ik_foot_rig["ik_chain_connector"]
    ik_jnts = rig_module.ik_jnts = ik_foot_rig["ik_jnts"]
    rig_module.foot_roll_jnts = ik_foot_rig["foot_roll_jnts"]




    # ...FK rig
    fk_foot_rig = fkFoot.build(side=rig_module.side, parent=rig_module.transform_grp,
                               ankle_orienter=rig_module.orienters["foot"], fk_toe_ctrl=ctrls["fk_toe"])
    rig_module.fk_root_input = fk_foot_rig["fk_root_input"]





    # ...Blending ------------------------------------------------------------------------------------------------------
    rotate_constraint = gen_utils.matrix_constraint(objs=[fk_foot_rig["fk_foot_loc"], ik_jnts["foot"],
                                                          bind_jnts["foot"]], decompose=True, translate=False,
                                                    rotate=True, scale=True,shear=False)
    kinematic_blend_mult.connect(rotate_constraint["weights"][0])

    t_values = bind_jnts["ball"].translate.get()
    rotate_constraint = gen_utils.matrix_constraint(objs=[ctrls["fk_toe"], ik_jnts["ball"], bind_jnts["ball"]],
                                                    decompose=True, translate=False, rotate=True, scale=True,
                                                    shear=False)
    kinematic_blend_mult.connect(rotate_constraint["weights"][0])
    bind_jnts["ball"].translate.set(t_values)




    # ...Clean control transforms --------------------------------------------------------------------------------------
    for ctrl in ctrls.values():
        gen_utils.convert_offset(ctrl)



    # ------------------------------------------------------------------------------------------------------------------
    pm.select(clear=1)
    return rig_module'''
