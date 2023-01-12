# Title: arm_setup.py
# Author: Sam Leheny
# Contact: samleheny@live.com

# Description: Builds setup module of biped biped_spine rig.


###########################
##### Import Commands #####
import importlib
import Snowman3.riggers.modules.biped_arm.data.ctrl_data as prelimCtrls
importlib.reload(prelimCtrls)
###########################
###########################


###########################
######## Variables ########

###########################
###########################





########################################################################################################################
def build(armature_module):


    # Reverse pole vector elbow
    pv_loc = armature_module.placers["ik_elbow"].install_reverse_ik(
        pv_chain_mid=armature_module.placers["lowerarm"].mobject,
        limb_start=armature_module.placers["upperarm"].mobject,
        limb_end=armature_module.placers["lowerarm_end"].mobject,
        connector_crv_parent=armature_module.placers["upperarm"].mobject, module=armature_module)
    pv_loc.setParent(armature_module.rig_subGrps["extra_systems"])

    # Position module
    armature_module.position_module()



    #...Preliminary controls ------------------------------------------------------------------------------------------
    ctrls_dict = prelimCtrls.create_ctrl_data(side=armature_module.side,
                                              is_driven_side=armature_module.is_driven_side,
                                              module_ctrl=armature_module.module_ctrl)
    armature_module.create_prelim_ctrls()




    return armature_module
