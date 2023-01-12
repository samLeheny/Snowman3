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

    orienters = rig_module.orienters
    side_tag = rig_module.side_tag


    #...Create limb rig -----------------------------------------------------------------------------------------------
    limb_rig = LimbRig(limb_name = rig_module.name,
                       side = rig_module.side,
                       prefab = 'plantigrade',
                       segment_names = ['upperarm', 'lowerarm', 'hand'],
                       socket_name = 'shoulder',
                       pv_name = 'elbow',
                       jnt_positions = [pm.xform(orienters[n], q=1, ws=1, rp=1) for n in
                                        ('upperarm', 'lowerarm', 'lowerarm_end', 'wrist_end')],
                       pv_position = pm.xform(orienters['ik_elbow'], q=1, ws=1, rp=1)
                       )

    #...Conform LimbRig's PV ctrl orientation to that of PV orienter
    pv_ctrl_buffer = limb_rig.ctrls['ik_pv'].getParent()
    pm.delete(pm.orientConstraint(orienters['ik_elbow'], pv_ctrl_buffer))
    pm.delete(pm.scaleConstraint(orienters['ik_elbow'], pv_ctrl_buffer))

    #...Move contents of limb rig into biped_arm rig module's groups
    [child.setParent(rig_module.transform_grp) for child in limb_rig.grps['transform'].getChildren()]
    [child.setParent(rig_module.no_transform_grp) for child in limb_rig.grps['noTransform'].getChildren()]

    #...Migrate Rig Scale attr over to new rig group
    for plug in pm.listConnections(f'{limb_rig.grps["root"]}.RigScale', destination=1, plugs=1):
        pm.connectAttr(f'{rig_module.rig_module_grp}.RigScale', plug, force=1)
    for plug in pm.listConnections(f'{limb_rig.grps["root"]}.RigScale', source=1, plugs=1):
        pm.connectAttr(plug, f'{rig_module.rig_module_grp}.RigScale', force=1)

    pm.delete(limb_rig.grps['root'])



    #...Controls -------------------------------------------------------------------------------------------------------
    anim_ctrl_data, ctrls = {}, {}
    for key, data in rig_module.ctrl_data.items():
        anim_ctrl_data[key] = data.create_anim_ctrl()
    rig_module.ctrls = ctrls

    ctrl_pairs = [('fk_upperarm', limb_rig.fk_ctrls[0]),
                  ('fk_lowerarm', limb_rig.fk_ctrls[1]),
                  ('fk_hand', limb_rig.fk_ctrls[2]),
                  ('ik_hand', limb_rig.ctrls['ik_extrem']),
                  ('ik_elbow', limb_rig.ctrls['ik_pv']),
                  ('shoulder_pin', limb_rig.ctrls['socket'])]

    for ctrl_str, ctrl_transform in ctrl_pairs:
        ctrls[ctrl_str] = anim_ctrl_data[ctrl_str].initialize_anim_ctrl(existing_obj=ctrl_transform)

    #...IK Hand Follow control
    anim_ctrl_data['ik_hand_follow'] = rig_module.ctrl_data['ik_hand_follow'].create_anim_ctrl()
    ctrls['ik_hand_follow'] = anim_ctrl_data['ik_hand_follow'].initialize_anim_ctrl()

    for c in anim_ctrl_data.values():
        c.finalize_anim_ctrl(delete_existing_shapes=True)


    ik_hand_follow_ctrl_buffer = gen_utils.buffer_obj(ctrls['ik_hand_follow'], parent=rig_module.transform_grp)



    #...Hand connection transform -------------------------------------------------------------------------------------
    rig_module.wrist_socket = limb_rig.blend_jnts[-2]




    pm.select(clear=1)
    return rig_module
