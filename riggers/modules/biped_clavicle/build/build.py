# Title: clavicle_build.py
# Author: Sam Leheny
# Contact: samleheny@live.com

# Description: Builds setup module of biped biped_spine rig.


###########################
##### Import Commands #####
import importlib
import pymel.core as pm

import Snowman3.utilities.general_utils as gen_utils
importlib.reload(gen_utils)

import Snowman3.utilities.rig_utils as rig_utils
importlib.reload(rig_utils)

import Snowman3.dictionaries.nameConventions as nameConventions
importlib.reload(nameConventions)
nom = nameConventions.create_dict()
###########################
###########################


###########################
######## Variables ########

###########################
###########################





########################################################################################################################
#def build(rig_module=None, rig_parent=None, rig_space_connector=None):
def build(rig_module, rig_parent=None):


    # ...Create controls -----------------------------------------------------------------------------------------------
    anim_ctrl_data, ctrls = {}, {}
    for key, data in rig_module.ctrl_data.items():
        anim_ctrl_data[key] = data.create_anim_ctrl()
        ctrls[key] = anim_ctrl_data[key].initialize_anim_ctrl()
        anim_ctrl_data[key].finalize_anim_ctrl()
    rig_module.ctrls = ctrls


    placers = rig_module.placers
    side_tag = rig_module.side_tag


    # Bind joints ------------------------------------------------------------------------------------------------------
    clavicle_jnt = rig_utils.joint(name="clavicle", side=rig_module.side, joint_type=nom.bindJnt, radius=1.0)
    temp_buffer = gen_utils.buffer_obj(clavicle_jnt, parent=ctrls["clavicle"])
    gen_utils.zero_out(temp_buffer)
    clavicle_jnt.setParent(ctrls["clavicle"])
    pm.delete(temp_buffer)

    rig_module.bind_jnts["clavicle"] = clavicle_jnt



    # ------------------------------------------------------------------------------------------------------------------
    clavicle_ctrl_buffer = gen_utils.buffer_obj(ctrls["clavicle"], parent=rig_module.transform_grp)



    #...Arm connection transform --------------------------------------------------------------------------------------
    rig_module.shoulder_socket = ctrls["clavicle"]



    # ------------------------------------------------------------------------------------------------------------------
    pm.select(clear=1)
    return rig_module
