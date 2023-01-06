 # Title: build.py
# Author: Sam Leheny
# Contact: samleheny@live.com

# Description: Builds setup module of biped biped_arm rig.


###########################
##### Import Commands #####
import importlib
import pymel.core as pm

import Snowman3.utilities.general_utils as gen_utils
importlib.reload(gen_utils)

import Snowman3.riggers.modules.biped_arm.utilities.animCtrls as animCtrls
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
#def build(rig_module, rig_parent=None, rig_space_connector=None, settings_ctrl_parent=None):
def build(rig_module, rig_parent=None):



    # ...Create limb rig -----------------------------------------------------------------------------------------------
    limb_rig = LimbRig(limb_name = rig_module.name,
                       side = rig_module.side,
                       prefab = 'plantigrade',
                       segment_names = ['upperarm', 'lowerarm', 'hand'],
                       socket_name = 'shoulder',
                       pv_name = 'elbow',
                       jnt_positions = [pm.xform(rig_module.orienters[n], q=1, ws=1, rp=1) for n in
                                        ('upperarm', 'lowerarm', 'lowerarm_end', 'wrist_end')],
                       pv_position = pm.xform(rig_module.orienters['ik_elbow'], q=1, ws=1, rp=1)
                       )

    # ...Move contents of limb rig into biped_arm rig module's groups
    '''for child in limb_rig.transform_grp.getChildren():
        child.setParent(rig_module.transform_grp)

    for child in limb_rig.no_transform_grp.getChildren():
        child.setParent(rig_module.no_transform_grp)

    # ...Move Rig Scale attr over to new rig group
    for plug in pm.listConnections(f"{limb_rig.root_grp}.RigScale", destination=1, plugs=1):
        pm.connectAttr(f"{rig_module.rig_module_grp}.RigScale", plug, force=1)
    for plug in pm.listConnections(f"{limb_rig.root_grp}.RigScale", source=1, plugs=1):
        pm.connectAttr(plug, f"{rig_module.rig_module_grp}.RigScale", force=1)

    pm.delete(limb_rig.root_grp)



    # ...Controls ------------------------------------------------------------------------------------------------------
    ctrl_data = animCtrls.create_anim_ctrls(side=rig_module.side, module_ctrl=rig_module.setup_module_ctrl)
    ctrls = rig_module.ctrls

    ctrl_pairs = [("fk_upperarm", "upperlimb_FK"),
                  ("fk_lowerarm", "lowerlimb_FK"),
                  ("fk_hand", "extrem_FK"),
                  ("ik_hand", "ik_extrem"),
                  ("ik_elbow", "ik_pv"),
                  ("shoulder_pin", "rig_socket"),
                  ("elbow_pin", "mid_limb_pin"),
                  ("upperarm_bend_start", "upperlimb_bend_start"),
                  ("upperarm_bend_mid", "upperlimb_bend_mid"),
                  ("lowerarm_bend_mid", "lowerlimb_bend_mid"),
                  ("lowerarm_bend_end", "lowerlimb_bend_end")]


    for pair in ctrl_pairs:
        ctrls[pair[0]] = ctrl_data[pair[0]].initialize_anim_ctrl(existing_obj=limb_rig.ctrls[pair[1]])
        ctrl_data[pair[0]].finalize_anim_ctrl(delete_existing_shapes=True)

    for key in ("ik_hand_follow",):
        rig_module.ctrls[key] = ctrl_data[key].initialize_anim_ctrl(parent=rig_module.transform_grp)
        ctrl_data[key].finalize_anim_ctrl()

    ctrls = rig_module.ctrls


    blend_mult = gen_utils.get_attr_blend_nodes(attr="fkIk", node=ctrls["shoulder_pin"], mult=True)
    blend_mult.connect(ctrls["ik_hand_follow"].visibility)


    ctrls["ik_hand_follow"].setParent(settings_ctrl_parent) if settings_ctrl_parent else None




    # ...Attach biped_arm rig to greater rig ---------------------------------------------------------------------------
    gen_utils.matrix_constraint(objs=[rig_space_connector, ctrls["shoulder_pin"].getParent()], decompose=True,
                                translate=True, rotate=True, scale=False, shear=False, maintain_offset=True)


    # ...Hand connection transform -------------------------------------------------------------------------------------
    hand_connector = rig_module.hand_connector = limb_rig.blend_jnts[2]


    # ...
    gen_utils.convert_offset(ctrls["fk_upperarm"].getParent())




    pm.select(clear=1)
    return rig_module'''
