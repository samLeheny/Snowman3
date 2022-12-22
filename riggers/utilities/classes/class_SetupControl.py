# Title: class_SetupControl.py
# Author: Sam Leheny
# Contact: samleheny@live.com

# Description:


###########################
##### Import Commands #####
import importlib
import pymel.core as pm

import Snowman3.utilities.general_utils as gen_utils
import Snowman3.utilities.rig_utils as rig_utils
import Snowman3.riggers.utilities.armature_utils as amtr_utils
importlib.reload(gen_utils)
importlib.reload(rig_utils)
importlib.reload(amtr_utils)

import Snowman3.dictionaries.nameConventions as nameConventions
importlib.reload(nameConventions)
nom = nameConventions.create_dict()
###########################
###########################


###########################
######## Variables ########
default_shape = "cube"
###########################
###########################





########################################################################################################################
class SetupControl:
    def __init__(
        self,
        name = None,
        shape = None,
        locks = None,
        scale = None,
        side = None,
        color = None,
        parent = None
    ):
        self.name = name
        self.shape = shape if shape else default_shape
        self.locks = locks if locks else {"v": 1}
        self.scale = scale if scale else [5.0, 5.0, 4.58]
        self.side = side
        self.color = color if color else 1
        self.parent = parent
        self.mobject = None




    """
    --------- METHODS --------------------------------------------------------------------------------------------------
    --------------------------------------------------------------------------------------------------------------------
    create
    dull_color
    make_benign
    setup_symmetry
    --------------------------------------------------------------------------------------------------------------------
    --------------------------------------------------------------------------------------------------------------------
    """




    ####################################################################################################################
    def create(self):

        # ...Assemble data with which to build controls
        ctrl_data = {"name": self.name,
                     "shape": self.shape,
                     "color": self.color,
                     "locks": self.locks,
                     "scale": self.scale}

        # ...Create control
        self.mobject = rig_utils.control(ctrl_info=ctrl_data, ctrl_type="setup_ctrl", side=self.side,
                                         parent=self.parent)





    ####################################################################################################################
    def dull_color(self, hide=False):

        for shape in self.mobject.getShapes():
            shape.overrideEnabled.set(1)
            shape.overrideDisplayType.set(1)
            shape.visibility.set(0) if hide else None





    ####################################################################################################################
    def make_benign(self, hide=True):

        if hide:
            # ...Hide ctrl shape
            for shape in self.mobject.getShapes():
                shape.visibility.set(0, lock=1) if not shape.visibility.get(lock=1) else None

        # ...Lock attributes
        [pm.setAttr(self.mobject + "." + attr, lock=1, keyable=0) for attr in gen_utils.keyable_attrs]

        # ...Dull ctrl color
        self.dull_color()





    ####################################################################################################################
    def setup_symmetry(self):

        amtr_utils.connect_pair(self.mobject, attrs=("tx", "ty", "tz", "rx", "ry", "rz", "sx", "sy", "sz",
                                                     "ModuleScale"))
