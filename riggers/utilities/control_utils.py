# Title: control_utils.py
# Author: Sam Leheny
# Contact: samleheny@live.com
import copy
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

import Snowman3.dictionaries.nurbsCurvePrefabs as prefab_curve_shapes
importlib.reload(prefab_curve_shapes)
###########################
###########################


###########################
######## Variables ########
control_tag = 'CTRL'
prefab_ctrl_shapes = prefab_curve_shapes.create_dict()
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
    match_position: str = None
    side: str = None
    scene_name: str = None



########################################################################################################################
class ControlCreator:
    def __init__(
        self,
        name: str,
        shape: str,
        color: Union[list, int],
        locks: dict = None,
        data_name: str = None,
        position: list = None,
        size: Union[list, float] = 1.0,
        forward_direction: list[float, float, float] = None,
        up_direction: list[float, float, float] = None,
        match_position: str = None,
        side: str = None,
        scene_name: str = None
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
        self.scene_name = scene_name if scene_name else f'{gen.side_tag(side)}{name}_{control_tag}'
        self.cv_data = self.compose_cvs()


    def compose_cvs(self, prefabs_dict=prefab_ctrl_shapes):
        prefab_curve_data = copy.deepcopy(prefabs_dict[self.shape])
        composed_cv_data = gen.compose_curve_construct_cvs(
            curve_data=prefab_curve_data, scale=self.size, shape_offset=None, up_direction=self.up_direction,
            forward_direction=self.forward_direction)
        return composed_cv_data


    def create_control(self):
        control = Control(
            name = self.name,
            data_name = self.data_name,
            shape = self.cv_data,
            color = self.color,
            position = self.position,
            locks = self.locks,
            match_position = self.match_position,
            side = self.side,
            scene_name = self.scene_name
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
        self.scene_control = gen.curve_construct(
            name=self.get_scene_name(),
            color=self.control.color,
            curves=self.control.shape
        )
        return self.scene_control


    def snap_position(self):
        target_position_obj = self.control.match_position


    def get_scene_name(self):
        return f'{gen.side_tag(self.control.side)}{self.control.name}_{control_tag}'
