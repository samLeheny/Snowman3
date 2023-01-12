# Title: leg_build.py
# Author: Sam Leheny
# Contact: samleheny@live.com

# Description: Builds setup module of biped biped_leg rig.


###########################
##### Import Commands #####
import importlib
import pymel.core as pm

import Snowman3.utilities.general_utils as gen_utils
importlib.reload(gen_utils)

import Snowman3.dictionaries.nameConventions as nameConventions
importlib.reload(nameConventions)
nom = nameConventions.create_dict()

import Snowman3.riggers.modules.leg_plantigrade.utilities.ctrl_data as animCtrls
importlib.reload(animCtrls)

import Snowman3.riggers.utilities.classes.class_LimbRig as class_LimbRig
importlib.reload(class_LimbRig)
LimbRig = class_LimbRig.LimbRig
###########################
###########################


###########################
######## Variables ########

###########################
###########################





########################################################################################################################
def build(rig_module=None, rig_parent=None, rig_space_connector=None, ctrl_parent=None, include_fk_foot_rot=False):


    side_tag = "{}_".format(rig_module.side) if rig_module.side else ""


    #...Create biped_leg rig group
    rig_module_grp = rig_module.create_rig_module_grp(parent=rig_parent)
    #...Get orienters from armature
    rig_module.get_armature_orienters()
    setup_module_ctrl = rig_module.get_setup_module_ctrl()


    #...Create limb rig -----------------------------------------------------------------------------------------------
    limb_rig = LimbRig(limb_name = rig_module.name,
                       side = rig_module.side,
                       segment_names=("thigh", "calf", "foot", "footEnd"),
                       socket_name = "hip",
                       midlimb_name = "knee",
                       final_pose_nodes = (rig_module.orienters["thigh"],
                                           rig_module.orienters["calf"],
                                           rig_module.orienters["calf_end"],
                                           rig_module.orienters["ankle_end"],
                                           rig_module.orienters["ik_knee"]))

    #...Move contents of limb rig into biped_leg rig module's groups
    for child in limb_rig.transform_grp.getChildren():
        child.setParent(rig_module.transform_grp)

    for child in limb_rig.no_transform_grp.getChildren():
        child.setParent(rig_module.no_transform_grp)

    #...Move Rig Scale attr over to new rig group
    for plug in pm.listConnections(f'{limb_rig.root_grp}.RigScale', destination=1, plugs=1):
        pm.connectAttr(f'{rig_module_grp}.RigScale', plug, force=1)
    for plug in pm.listConnections(f'{limb_rig.root_grp}.RigScale', source=1, plugs=1):
        pm.connectAttr(plug, f'{rig_module_grp}.RigScale', force=1)

    pm.delete(limb_rig.root_grp)



    #...Controls ------------------------------------------------------------------------------------------------------
    ctrl_data = animCtrls.create_prelim_ctrls(side=rig_module.side, module_ctrl=setup_module_ctrl)
    ctrls = rig_module.ctrls

    ctrl_pairs = [("fk_thigh", "upperlimb_FK"),
                  ("fk_calf", "lowerlimb_FK"),
                  ("fk_foot", "extrem_FK"),
                  ("ik_foot", "ik_extrem"),
                  ("ik_knee", "ik_pv"),
                  ("hip_pin", "rig_socket"),
                  ("knee_pin", "mid_limb_pin"),
                  ("thigh_bend_start", "upperlimb_bend_start"),
                  ("thigh_bend_mid", "upperlimb_bend_mid"),
                  ("calf_bend_mid", "lowerlimb_bend_mid"),
                  ("calf_bend_end", "lowerlimb_bend_end")]
    if include_fk_foot_rot:
        ctrl_pairs.append(("ik_foot_rot", "ik_extrem_rot"))


    for pair in ctrl_pairs:
        ctrls[pair[0]] = ctrl_data[pair[0]].initialize_anim_ctrl(existing_obj=limb_rig.ctrls[pair[1]])
        ctrl_data[pair[0]].finalize_anim_ctrl(delete_existing_shapes=True)

    for key in ("ik_foot_follow",):
        rig_module.ctrls[key] = ctrl_data[key].initialize_anim_ctrl(parent=rig_module.transform_grp)
        ctrl_data[key].finalize_anim_ctrl()

    ctrls = rig_module.ctrls


    blend_mult = gen_utils.get_attr_blend_nodes(attr="fkIk", node=ctrls["hip_pin"], mult=True)
    blend_mult.connect(ctrls["ik_foot_follow"].visibility)


    ctrls["ik_foot_follow"].setParent(ctrl_parent) if ctrl_parent else None




    # ------------------------------------------------------------------------------------------------------------------
    hip_connector_loc = pm.spaceLocator("{}hipConnector_{}".format(side_tag, nom.locator))
    loc_buffer = gen_utils.buffer_obj(hip_connector_loc)
    loc_buffer.setParent(ctrls["hip_pin"])
    gen_utils.zero_out(loc_buffer)
    loc_buffer.setParent(rig_space_connector)
    pm.delete(pm.parentConstraint(ctrls["hip_pin"], hip_connector_loc))

    gen_utils.matrix_constraint(objs=[hip_connector_loc, ctrls["hip_pin"].getParent()], decompose=True,
                                translate=True, rotate=True, scale=False, shear=False, maintain_offset=True)



    #...Give IK foot control world orientation ------------------------------------------------------------------------
    ctrl = ctrls["ik_foot"]
    ctrl_buffer = ctrl.getParent()

    #...Temporarily moved shapes into a holder node (will move them back after reorientation)
    temp_shape_holder = pm.shadingNode("transform", name="TEMP_shape_holder", au=1)
    gen_utils.copy_shapes(ctrl, temp_shape_holder, keep_original=True)
    [pm.delete(shape) for shape in ctrl.getShapes()]


    ori_offset = pm.shadingNode("transform", name="{}ikFoot_ori_OFFSET".format(side_tag), au=1)
    ori_offset.setParent(ctrl_buffer)
    gen_utils.zero_out(ori_offset)
    ori_offset.setParent(world=1)

    [child.setParent(ori_offset) for child in ctrl.getChildren()]

    par = ctrl_buffer.getParent()
    ctrl_buffer.setParent(world=1)

    if rig_module.side == nom.leftSideTag:
        ctrl_buffer.rotate.set(0, 0, 0)
        ctrl_buffer.scale.set(1, 1, 1)
    elif rig_module.side == nom.rightSideTag:
        ctrl_buffer.rotate.set(0, 180, 0)
        ctrl_buffer.scale.set(1, 1, -1)
    ctrl_buffer.setParent(par)

    ori_offset.setParent(ctrl)

    #...Return shapes to control transform
    gen_utils.copy_shapes(temp_shape_holder, ctrl, keep_original=False)




    #...Foot connection transform -------------------------------------------------------------------------------------
    rig_module.leg_end_bind_connector = limb_rig.blend_jnts[2]
    rig_module.leg_end_ik_jnt_connector = limb_rig.ik_jnts[2]
    rig_module.leg_end_ik_connector = ctrls["ik_foot"]
    rig_module.ik_handle = limb_rig.ik_handles["limb"]
    rig_module.ik_foot_dist_node = limb_rig.ik_extrem_dist

    #...
    gen_utils.convert_offset(ctrls["fk_thigh"].getParent())




    pm.select(clear=1)
    return rig_module
