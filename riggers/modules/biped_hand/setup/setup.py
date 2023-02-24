# Title: hand_setup.py
# Author: Sam Leheny
# Contact: samleheny@live.com

# Description: Builds setup module of biped biped_spine rig.


###########################
##### Import Commands #####
import importlib
import pymel.core as pm

import Snowman3.riggers.modules.biped_hand.data.ctrl_data as prelimCtrls
importlib.reload(prelimCtrls)

import Snowman3.riggers.utilities.classes.class_ArmatureModuleHandle as class_ArmatureModuleHandle
importlib.reload(class_ArmatureModuleHandle)
ArmatureModuleHandle = class_ArmatureModuleHandle.ArmatureModuleHandle
###########################
###########################


###########################
######## Variables ########

###########################
###########################





########################################################################################################################
def build(armature_module):


    #...Finger reverse pole vectors
    for key in ["thumb", "index", "middle", "ring", "pinky"]:
        pv_loc = armature_module.placers[f'ik_{key}'].install_reverse_ik(
            pv_chain_mid=armature_module.placers[f'{key}_2'].mobject,
            limb_start=armature_module.placers[f'{key}_1'].mobject,
            limb_end=armature_module.placers[f'{key}_end'].mobject,
            connector_crv_parent=armature_module.placers[f'{key}_1'].mobject,
            module=armature_module,
            hide=True)
        pv_loc.setParent(armature_module.rig_subGrps["extra_systems"])


    #...Position module
    armature_module.position_module()



    #...Add a control for each finger ---------------------------------------------------------------------------------
    for key in ["thumb", "index", "middle", "ring", "pinky"]:

        finger_ctrl = armature_module.module_handles[key] = ArmatureModuleHandle(
            name=key,
            locks={"v": 1},
            scale=[0.5, 0.5, 0.5],
            side=armature_module.side,
            parent=armature_module.rig_subGrps["placers"],
            color=armature_module.ctrl_color
        )

        finger_ctrl.create()

        pm.delete(pm.parentConstraint(armature_module.placers[f"{key}_1"].mobject, finger_ctrl.mobject))

        finger_placer_grp = pm.group(name=f"{key}_placers", p=armature_module.rig_subGrps["placers"], em=1)

        pm.delete(pm.parentConstraint(finger_ctrl.mobject, finger_placer_grp))

        for num_suffix in ["_1", "_2", "_3", "_end"]:
            armature_module.placers[key+num_suffix].mobject.getParent().setParent(finger_placer_grp)

        pm.parentConstraint(finger_ctrl.mobject, finger_placer_grp)



    #...Preliminary controls ------------------------------------------------------------------------------------------
    armature_module.ctrl_data = prelimCtrls.create_ctrl_data(side=armature_module.side)
    armature_module.create_prelim_ctrls()



    return armature_module
