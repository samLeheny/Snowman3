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

import Snowman3.riggers.modules.leg_plantigrade.utilities.animCtrls as animCtrls
importlib.reload(animCtrls)

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

    orienters = rig_module.orienters


    # ...Create limb rig -----------------------------------------------------------------------------------------------
    limb_rig = LimbRig(limb_name=rig_module.name,
                       side=rig_module.side,
                       prefab='plantigrade',
                       segment_names=['thigh', 'calf', 'foot'],
                       socket_name='hip',
                       pv_name='knee',
                       jnt_positions=[pm.xform(orienters[n], q=1, ws=1, rp=1) for n in
                                      ('thigh', 'calf', 'calf_end', 'ankle_end')],
                       pv_position=pm.xform(orienters['ik_knee'], q=1, ws=1, rp=1)
                       )

    # ...Conform LimbRig's PV ctrl orientation to that of PV orienter
    pv_ctrl_buffer = limb_rig.ctrls['ik_pv'].getParent()
    pm.delete(pm.orientConstraint(orienters['ik_knee'], pv_ctrl_buffer))
    pm.delete(pm.scaleConstraint(orienters['ik_knee'], pv_ctrl_buffer))

    # ...Move contents of limb rig into biped_leg rig module's groups
    [child.setParent(rig_module.transform_grp) for child in limb_rig.grps['transform'].getChildren()]
    [child.setParent(rig_module.no_transform_grp) for child in limb_rig.grps['noTransform'].getChildren()]

    # ...Migrate Rig Scale attr over to new rig group
    for plug in pm.listConnections(f'{limb_rig.grps["root"]}.RigScale', destination=1, plugs=1):
        pm.connectAttr(f'{rig_module.rig_module_grp}.RigScale', plug, force=1)
    for plug in pm.listConnections(f'{limb_rig.grps["root"]}.RigScale', source=1, plugs=1):
        pm.connectAttr(plug, f'{rig_module.rig_module_grp}.RigScale', force=1)

    pm.delete(limb_rig.grps['root'])



    # ...Controls ------------------------------------------------------------------------------------------------------
    ctrl_data = animCtrls.create_anim_ctrls(side=rig_module.side, module_ctrl=rig_module.setup_module_ctrl)
    ctrls = rig_module.ctrls

    ctrl_pairs = [('fk_thigh', limb_rig.fk_ctrls[0]),
                  ('fk_calf', limb_rig.fk_ctrls[1]),
                  ('fk_foot', limb_rig.fk_ctrls[2]),
                  ('ik_foot', limb_rig.ctrls['ik_extrem']),
                  ('ik_knee', limb_rig.ctrls['ik_pv']),
                  ('hip_pin', limb_rig.ctrls['socket'])]

    for ctrl_str, ctrl_transform in ctrl_pairs:
        ctrls[ctrl_str] = ctrl_data[ctrl_str].initialize_anim_ctrl(
            existing_obj=ctrl_transform)
        ctrl_data[ctrl_str].finalize_anim_ctrl(delete_existing_shapes=True)


    # ------------------------------------------------------------------------------------------------------------------
    '''hip_connector_loc = pm.spaceLocator("{}hipConnector_{}".format(rig_module.side_tag, nom.locator))
    loc_buffer = gen_utils.buffer_obj(hip_connector_loc)
    loc_buffer.setParent(ctrls["hip_pin"])
    gen_utils.zero_out(loc_buffer)
    loc_buffer.setParent(rig_space_connector)
    pm.delete(pm.parentConstraint(ctrls["hip_pin"], hip_connector_loc))

    gen_utils.matrix_constraint(objs=[hip_connector_loc, ctrls["hip_pin"].getParent()], decompose=True,
                                translate=True, rotate=True, scale=False, shear=False, maintain_offset=True)'''


    # ...Give IK foot control world orientation ------------------------------------------------------------------------
    foot_world_orientation.reorient_ik_foot(ik_foot_ctrl=ctrls["ik_foot"], side=rig_module.side)


    # ...Foot connection transform -------------------------------------------------------------------------------------
    rig_module.bind_ankle_socket = limb_rig.blend_jnts[-2]
    rig_module.ik_ankle_jnt_socket = limb_rig.ik_jnts[-2]
    rig_module.ik_ankle_ctrl_socket = ctrls["ik_foot"]
    rig_module.fk_ankle_ctrl_socket = ctrls['fk_foot']
    rig_module.ik_handle_plug = limb_rig.ik_handles["limb"].getParent()

    # ...
    '''gen_utils.convert_offset(ctrls["fk_thigh"].getParent())'''



    pm.select(clear=1)
    return rig_module
