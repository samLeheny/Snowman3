# Title: leg_setup.py
# Author: Sam Leheny
# Contact: samleheny@live.com

# Description: Builds setup module of biped biped_spine rig.


###########################
##### Import Commands #####
import importlib
import Snowman3.riggers.modules.leg_plantigrade.data.ctrl_data as prelimCtrls
importlib.reload(prelimCtrls)
###########################
###########################


###########################
######## Variables ########

###########################
###########################





########################################################################################################################
def build(armature_module):


    #...Reverse pole vector elbow
    pv_loc = armature_module.placers["ik_knee"].install_reverse_ik(
        pv_chain_mid = armature_module.placers["calf"].mobject,
        limb_start = armature_module.placers["thigh"].mobject,
        limb_end = armature_module.placers["calf_end"].mobject,
        connector_crv_parent = armature_module.placers["thigh"].mobject,
        module = armature_module,
        aim_vector = (0, 0, 1), up_vector = (0, -1, 0)
    )
    pv_loc.setParent(armature_module.rig_subGrps["extra_systems"])


    #...Position module
    armature_module.position_module()



    #...Preliminary controls ------------------------------------------------------------------------------------------
    armature_module.ctrl_data = prelimCtrls.create_ctrl_data(side=armature_module.side)
    armature_module.create_prelim_ctrls()




    return armature_module
