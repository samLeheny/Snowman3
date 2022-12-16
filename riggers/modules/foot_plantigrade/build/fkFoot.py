# Title: fk_foot.py
# Author: Sam Leheny
# Contact: samleheny@live.com

# Description: Builds setup module of biped foot rig.


###########################
##### Import Commands #####
import pymel.core as pm

import Snowman.utilities.general_utils as gen_utils
reload(gen_utils)
###########################
###########################


###########################
######## Variables ########

###########################
###########################





########################################################################################################################
def build(side=None, parent=None, ankle_orienter=None, fk_toe_ctrl=None):


    side_tag = "{}_".format(side) if side else ""


    fk_foot_loc = pm.spaceLocator(name="{}fkFoot_space".format(side_tag))
    fk_foot_loc.setParent(parent)
    pm.matchTransform(fk_foot_loc, ankle_orienter)

    fk_toe_ctrl.setParent(fk_foot_loc)

    fk_root_input = pm.spaceLocator(name="{}fkFoot_input".format(side_tag))
    fk_root_input.setParent(fk_foot_loc)
    pm.matchTransform(fk_root_input, fk_foot_loc)
    fk_root_input.setParent(world=1)
    gen_utils.matrix_constraint(objs=[fk_root_input, fk_foot_loc], translate=True, rotate=True, scale=False,
                                shear=False, decompose=True)



    # ------------------------------------------------------------------------------------------------------------------
    pm.select(clear=1)
    return {"fk_root_input": fk_root_input,
            "fk_foot_loc": fk_foot_loc}
