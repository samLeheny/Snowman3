# Title: class_ControlData.py
# Author: Sam Leheny
# Contact: samleheny@live.com

# Description:


###########################
##### Import Commands #####
import importlib

import Snowman3.riggers.utilities.classes.class_PrelimControl as class_PrelimControl
importlib.reload(class_PrelimControl)
PrelimControl = class_PrelimControl.PrelimControl

import Snowman3.riggers.utilities.classes.class_AnimControl as class_AnimControl
importlib.reload(class_AnimControl)
AnimControl = class_AnimControl.AnimControl
###########################
###########################


###########################
######## Variables ########

###########################
###########################





########################################################################################################################
class ControlData:
    def __init__(
        self,
        name = None,
        shape = None,
        size = None,
        shape_offset = None,
        color = None,
        position = None,
        position_weights = None,
        orientation = None,
        locks = None,
        forward_direction = None,
        up_direction = None,
        is_driven_side = None,
        body_module = None,
        match_transform = None,
        module_ctrl = None,
        side = None,
    ):
        self.name = name
        self.shape = shape
        self.size = size if size else [1.0, 1.0, 1.0]
        self.shape_offset = shape_offset
        self.color = color
        self.position = position
        self.position_weights = position_weights
        self.orientation = orientation
        self.locks = locks if locks else {'v': 1}
        self.forward_direction = forward_direction if forward_direction else [0, 0, 1]
        self.up_direction = up_direction if up_direction else [0, 1, 0]
        self.is_driven_side = is_driven_side
        self.body_module = body_module
        self.match_transform = match_transform
        self.module_ctrl = module_ctrl
        self.side = side

        self.ctrl_obj = None
        self.shape_data = None





    ####################################################################################################################
    def create_prelim_ctrl(self):

        ctrl = PrelimControl(
            name = self.name,
            shape = self.shape,
            shape_offset = self.shape_offset,
            size = self.size,
            forward_direction = self.forward_direction,
            up_direction = self.up_direction,
            color = self.color,
            position = self.position,
            position_weights = self.position_weights,
            orientation = self.orientation,
            locks = self.locks,
            body_module = self.body_module,
            match_transform = self.match_transform,
            side = self.side,
            is_driven_side = self.is_driven_side,
            module_ctrl = self.module_ctrl
        )

        return ctrl





    ####################################################################################################################
    def create_anim_ctrl(self):

        ctrl = AnimControl(
            ctrl_name_tag = self.name,
            prelim_ctrl_name = self.name,
            side = self.side,
            match_transform = self.match_transform,
            module_ctrl = self.module_ctrl,
        )

        return ctrl
