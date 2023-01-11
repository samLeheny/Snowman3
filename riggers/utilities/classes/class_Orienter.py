# Title: class_Orienter.py
# Author: Sam Leheny
# Contact: samleheny@live.com

# Description:


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
class Orienter:
    def __init__(
        self,
        name,
        side = None,
        size = None,
        parent = None,
        aim_vector = None,
        up_vector = None,
        match_to = None,
        placer = None,
    ):
        self.name = name
        self.side = side if side else None
        self.size = size if size else 1.0
        self.parent = parent if parent else None
        self.aim_vector = aim_vector if aim_vector else (1, 0, 0)
        self.up_vector = up_vector if up_vector else (0, 1, 0)
        self.match_to = match_to if match_to else None
        self.placer = placer
        self.mobject = None
        self.buffer = None
        self.side_tag = f'{side}_' if self.side else ""

        self.create()




    """
    --------- METHODS --------------------------------------------------------------------------------------------------
    --------------------------------------------------------------------------------------------------------------------
    create
    get_opposite_orienter
    match_to_obj
    aim_orient
    --------------------------------------------------------------------------------------------------------------------
    --------------------------------------------------------------------------------------------------------------------
    """


    ####################################################################################################################
    def create(self):

        self.mobject = rig_utils.orienter(name=self.name, side=self.side, scale=self.size)

        self.buffer = gen_utils.buffer_obj(self.mobject)
        gen_utils.convert_offset(self.mobject)

        self.buffer.setParent(self.parent) if self.parent else None
        gen_utils.zero_out(self.buffer)





    ####################################################################################################################
    def get_opposite_orienter(self):

        #...Check that orienter is sided
        if not self.side:
            print("Orienter '{0}' has not assigned side, and therefore, has no opposite orienter".format(self.mobject))
            return None

        #...Check that orienter's side is valid (left or right)
        if self.side not in (nom.leftSideTag, nom.rightSideTag):
            print(f'Side for orienter "{self.mobject}": {self.side}.'
                  f'Can only find opposite orienters if assigned side is "{nom.leftSideTag}" or "{nom.rightSideTag}"')
            return None

        #...Find and get opposite orienter
        opposite_orienter = gen_utils.get_opposite_side_obj(self.mobject)
        if not opposite_orienter:
            print(f'Unable to find opposite orienter for placer: "{self.mobject}"')
            return None

        return opposite_orienter





    ####################################################################################################################
    def match_to_obj(self, obj=None):

        if not obj: obj = self.match_to

        get_orienter_string = f'::{self.side_tag}{obj}_{nom.orienter}'
        string_check = pm.ls(get_orienter_string)
        driver_orienter = string_check[0] if string_check else None

        #...Match orienter
        pm.orientConstraint(driver_orienter, self.mobject)





    ####################################################################################################################
    def aim_orienter(self):

        if self.match_to:
            self.match_to_obj()
            return

        if self.placer.up_vector_handle:
            aim_target_obj = self.placer.aim_vector_handle.mobject
            up_target_obj = self.placer.up_vector_handle.mobject

            pm.aimConstraint(aim_target_obj, self.mobject, aimVector=self.aim_vector, upVector=self.up_vector,
                             worldUpType="object", worldUpObject=up_target_obj)
