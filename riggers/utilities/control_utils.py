# Title: control_utils.py
# Author: Sam Leheny
# Contact: samleheny@live.com

# Description:


###########################
##### Import Commands #####
import importlib
import pymel.core as pm
from dataclasses import dataclass, field
from typing import Union

import Snowman3.utilities.general_utils as gen
importlib.reload(gen)

import Snowman3.utilities.rig_utils as rig
importlib.reload(rig)
###########################
###########################


###########################
######## Variables ########
control_tag = 'CTRL'
###########################
###########################


########################################################################################################################
@dataclass
class Control:
    name: str
    data_name: str
    shape: str
    color: Union[list, int]
    position: list
    locks: dict = field(default_factory=lambda: {'v': 1})
    size: Union[list, float] = 1.0
    forward_direction: list[float, float, float] = field(default_factory=lambda: [0, 0, 1])
    up_direction: list[float, float, float] = field(default_factory=lambda: [0, 1, 0])
    match_position: str = None
    side: str = None



########################################################################################################################
class ControlCreator:
    def __init__(
        self,
        name: str,
        shape: str,
        color: Union[list, int],
        locks: dict,
        data_name: str = None,
        position: list = None,
        size: Union[list, float] = 1.0,
        forward_direction: list[float, float, float] = None,
        up_direction: list[float, float, float] = None,
        match_position: str = None,
        side: str = None
    ):
        self.name = name
        self.data_name = data_name if data_name else name
        self.shape = shape
        self.color = color
        self.position = position if position else [0, 0, 0]
        self.locks = locks if locks else {'v': 1}
        self.size = size
        self.forward_direction = forward_direction if forward_direction else [0, 0, 1]
        self.up_direction = up_direction if up_direction else [0, 1, 0]
        self.match_position = match_position
        self.side = side


    def create_control(self):
        control = Control(
            name = self.name,
            data_name = self.data_name,
            shape = self.shape,
            color = self.color,
            position = self.position,
            locks = self.locks,
            size = self.size,
            forward_direction = self.forward_direction,
            up_direction = self.up_direction,
            match_position = self.match_position,
            side = self.side
        )
        return control



########################################################################################################################
class ControlManager:
    def __init__(
        self,
        control
    ):
        self.control = control


    def data_from_control(self):
        return vars(self.control).copy()



########################################################################################################################
class SceneControlManager:
    def __init__(
        self,
        control
    ):
        self.control = control
        self.scene_control = None


    def create_scene_control(self):
        self.create_scene_obj()
        if self.control.match_position:
            self.snap_position()
        return self.scene_control


    def create_scene_obj(self):
        self.scene_control = gen.prefab_curve_construct(
            name=self.get_scene_name(),
            prefab=self.control.shape,
            forward_direction=self.control.forward_direction,
            up_direction=self.control.up_direction,
            side=self.control.side,
            color=self.control.color,
            scale=self.control.size
        )
        return self.scene_control


    def snap_position(self):
        target_position_obj = self.control.match_position


    def get_scene_name(self):
        return f'{gen.side_tag(self.control.side)}{self.control.name}_{control_tag}'
