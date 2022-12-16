# Title: class_SetupControl.py
# Author: Sam Leheny
# Contact: samleheny@live.com

# Description:


###########################
##### Import Commands #####
import pymel.core as pm

import Snowman.utilities.general_utils as gen_utils
reload(gen_utils)

import Snowman.utilities.rig_utils as rig_utils
reload(rig_utils)

import Snowman.dictionaries.nameConventions as nameConventions
reload(nameConventions)
nom = nameConventions.create_dict()
###########################
###########################


###########################
######## Variables ########

###########################
###########################





########################################################################################################################
class SetupControl:
    def __init__(
        self,
        name = None,
        shape = "cube",
        locks = None,
        scale = None,
        side = None,
        color = None,
        parent = None
    ):
        self.name = name
        self.shape = shape
        self.locks = locks
        self.scale = scale if scale else [5.0, 5.0, 4.58]
        self.side = side
        self.color = color if color else 1
        self.parent = parent,
        self.mobject = None





    ####################################################################################################################
    def create(self):


        if not self.locks: self.locks = {"v": 1}
        if not self.scale: self.scale = [5.0, 5.0, 4.58]


        # ...Assemble data with which to build controls
        ctrl_data = {"name": self.name,
                     "shape": self.shape,
                     "color": self.color,
                     "locks": self.locks,
                     "scale": self.scale}

        # ...Create control
        ctrl = self.mobject = rig_utils.control(ctrl_info=ctrl_data, ctrl_type="setup_ctrl", side=self.side,
                                                parent=self.parent)


        return ctrl





    ####################################################################################################################
    def dull_color(self, gray_out=True, hide=False):

        for shape in self.mobject.getShapes():
            shape.overrideEnabled.set(1)
            shape.overrideDisplayType.set(1)
            if hide:
                shape.visibility.set(0)





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