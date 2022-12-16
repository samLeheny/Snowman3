# Title: foot_setup.py
# Author: Sam Leheny
# Contact: samleheny@live.com

# Description: Builds setup module of biped biped_spine rig.


###########################
##### Import Commands #####
import importlib
import Snowman3.riggers.modules.foot_plantigrade.utilities.prelimCtrls as prelimCtrls
importlib.reload(prelimCtrls)
###########################
###########################


###########################
######## Variables ########

###########################
###########################





########################################################################################################################
def build(armature_module):


    # ...Position module
    armature_module.position_module()


    # ...Preliminary controls ------------------------------------------------------------------------------------------
    ctrls_dict = prelimCtrls.create_prelim_ctrls(side=armature_module.side,
                                                 is_driven_side=armature_module.is_driven_side)
    armature_module.create_prelim_ctrls()




    return armature_module
