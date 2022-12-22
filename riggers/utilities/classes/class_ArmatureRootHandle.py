# Title: class_ArmatureRootHandle.py
# Author: Sam Leheny
# Contact: samleheny@live.com

# Description:


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
class ArmatureRootHandle:
    def __init__(
        self,
        name = None,
        root_size = None

    ):
        self.name = gen_utils.get_clean_name(name)
        self.mobject = None
        self.root_size = root_size if root_size else 1





    """
    --------- METHODS --------------------------------------------------------------------------------------------------
    --------------------------------------------------------------------------------------------------------------------
    create_mobject
    --------------------------------------------------------------------------------------------------------------------
    --------------------------------------------------------------------------------------------------------------------
    """





    ####################################################################################################################
    def create_mobject(self):

        # ...Compose object name
        obj_name = f'{self.name}_ARMATURE'

        # ...Create root object
        self.mobject = gen_utils.prefab_curve_construct(prefab = "COG",
                                                        name = obj_name,
                                                        color = [0.6, 0.6, 0.6],
                                                        up_direction = [0, 1, 0],
                                                        forward_direction = [0, 0, 1],
                                                        scale = self.root_size)
