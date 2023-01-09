# Title: fk_foot.py
# Author: Sam Leheny
# Contact: samleheny@live.com

# Description: Builds setup module of biped foot rig.


###########################
##### Import Commands #####
import importlib
import pymel.core as pm

import Snowman3.utilities.general_utils as gen_utils
importlib.reload(gen_utils)
###########################
###########################


###########################
######## Variables ########

###########################
###########################





########################################################################################################################
def build(side=None, parent=None, ankle_orienter=None, fk_toe_ctrl=None):


    side_tag = f'{side}_' if side else ''


    fk_foot_space = pm.shadingNode('transform', name=f'{side_tag}fkFoot_space', au=1)
    fk_foot_space.setParent(parent)
    pm.matchTransform(fk_foot_space, ankle_orienter)

    fk_toe_ctrl.setParent(fk_foot_space)



    # ------------------------------------------------------------------------------------------------------------------
    pm.select(clear=1)
    return {'fk_foot_space': fk_foot_space}
