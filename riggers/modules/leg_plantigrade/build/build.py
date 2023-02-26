# Title: build.py
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

import Snowman3.riggers.utilities.classes.class_LimbRig as class_LimbRig
importlib.reload(class_LimbRig)
LimbRig = class_LimbRig.LimbRig

import Snowman3.riggers.modules.leg_plantigrade.build.subScripts.foot_world_orientation as foot_world_orientation
importlib.reload(foot_world_orientation)
###########################
###########################


###########################
######## Variables ########

###########################
###########################





########################################################################################################################
#def build(rig_module=None, rig_parent=None, rig_space_connector=None, ctrl_parent=None, include_fk_foot_rot=False):
def build(rig_module, rig_parent=None):

    placers = rig_module.placers


    #...Create limb rig -----------------------------------------------------------------------------------------------
    limb_rig = LimbRig(
        limb_name=rig_module.name,
        side=rig_module.side,
        prefab='plantigrade',
        segment_names=['thigh', 'calf', 'foot'],
        socket_name='hip',
        pv_name='knee',
        jnt_positions=[placers[p].world_position for p in ('thigh', 'calf', 'calf_end', 'ankle_end')],
        pv_position=placers['ik_knee'].world_position
    )

    #...Conform LimbRig's PV ctrl orientation to that of PV orienter
    pv_ctrl_buffer = limb_rig.ctrls['ik_pv'].getParent()
    pv_ctrl_buffer.rotate.set(placers['ik_knee'].orientation)
    ###pm.delete(pm.orientConstraint(placers['ik_knee'], pv_ctrl_buffer))
    ###pm.delete(pm.scaleConstraint(placers['ik_knee'], pv_ctrl_buffer))

    #...Move contents of limb rig into biped_leg rig module's groups
    [child.setParent(rig_module.transform_grp) for child in limb_rig.grps['transform'].getChildren()]
    [child.setParent(rig_module.no_transform_grp) for child in limb_rig.grps['noTransform'].getChildren()]

    #...Migrate Rig Scale attr over to new rig group
    for plug in pm.listConnections(f'{limb_rig.grps["root"]}.RigScale', destination=1, plugs=1):
        pm.connectAttr(f'{rig_module.rig_module_grp}.RigScale', plug, force=1)
    for plug in pm.listConnections(f'{limb_rig.grps["root"]}.RigScale', source=1, plugs=1):
        pm.connectAttr(plug, f'{rig_module.rig_module_grp}.RigScale', force=1)

    pm.delete(limb_rig.grps['root'])



    #...Controls ------------------------------------------------------------------------------------------------------
    anim_ctrl_data, ctrls = {}, {}
    for key, data in rig_module.ctrl_data.items():
        anim_ctrl_data[key] = data.create_anim_ctrl()
    rig_module.ctrls = ctrls

    ctrl_pairs = [('fk_thigh', limb_rig.fk_ctrls[0]),
                  ('fk_calf', limb_rig.fk_ctrls[1]),
                  ('fk_foot', limb_rig.fk_ctrls[2]),
                  ('ik_foot', limb_rig.ctrls['ik_extrem']),
                  ('ik_knee', limb_rig.ctrls['ik_pv']),
                  ('hip_pin', limb_rig.ctrls['socket'])]

    for ctrl_str, ctrl_transform in ctrl_pairs:
        ctrls[ctrl_str] = anim_ctrl_data[ctrl_str].initialize_anim_ctrl(existing_obj=ctrl_transform)

    # ...IK Foot Follow control
    anim_ctrl_data['ik_foot_follow'] = rig_module.ctrl_data['ik_foot_follow'].create_anim_ctrl()
    ctrls['ik_foot_follow'] = anim_ctrl_data['ik_foot_follow'].initialize_anim_ctrl()

    for c in anim_ctrl_data.values():
        c.finalize_anim_ctrl(delete_existing_shapes=True)


    ik_foot_follow_ctrl_buffer = gen_utils.buffer_obj(ctrls['ik_foot_follow'], parent=rig_module.transform_grp)



    #...Give IK foot control world orientation ------------------------------------------------------------------------
    foot_world_orientation.reorient_ik_foot(ik_foot_ctrl=ctrls["ik_foot"], side=rig_module.side)


    #...Foot connection transform -------------------------------------------------------------------------------------
    rig_module.bind_ankle_socket = limb_rig.blend_jnts[-2]
    rig_module.ik_ankle_jnt_socket = limb_rig.ik_jnts[-2]
    rig_module.ik_ankle_ctrl_socket = ctrls["ik_foot"]
    rig_module.fk_ankle_ctrl_socket = ctrls['fk_foot']
    rig_module.ik_handle_plug = limb_rig.ik_handles["limb"].getParent()



    pm.select(clear=1)
    return rig_module
