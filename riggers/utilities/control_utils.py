# Title: control_utils.py
# Author: Sam Leheny
# Contact: samleheny@live.com

# Description:


###########################
##### Import Commands #####
import importlib
import copy
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
PREFAB_CTRL_SHAPES = prefab_curve_shapes.create_dict()
###########################
###########################


########################################################################################################################
class Control:
    def __init__(
        self,
        name: str,
        data_name: str,
        shape: str,
        color: Union[list, int],
        position: list,
        locks: dict = None,
        match_position: str = None,
        shape_offset: list = None,
        side: str = None,
        scene_name: str = None,
        part_name: str = None
    ):
        self.name = name
        self.data_name = data_name
        self.shape = shape
        self.color = color
        self.position = position
        self.locks = locks if locks else {'v': 1}
        self.match_position = match_position
        self.shape_offset = shape_offset
        self.side = side
        self.scene_name = scene_name
        self.part_name = part_name


    @classmethod
    def create_in_part(cls, part_name, **data):
        ctrl = Control(**data)
        ctrl.part_name = part_name
        return ctrl


    def get_data_dict(self):
        return vars(self).copy()



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
        shape_offset: list[float, float, float] = None,
        match_position: str = None,
        side: str = None,
        scene_name: str = None,
        part_name: str = None
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
        self.shape_offset = shape_offset
        self.match_position = match_position
        self.side = side
        self.scene_name = scene_name if scene_name else f'{gen.side_tag(side)}{name}_{control_tag}'
        self.cv_data = self.compose_cvs()
        self.part_name = part_name


    def compose_cvs(self, prefabs_dict=PREFAB_CTRL_SHAPES):
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
            scene_name = self.scene_name,
            part_name = self.part_name
        )
        return control



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
        self.add_transform_lock_attributes()
        return self.scene_control


    def create_scene_obj(self):
        self.scene_control = gen.curve_construct(
            name=self.get_scene_name(),
            color=self.control.color,
            curves=self.control.shape,
            shape_offset=self.control.shape_offset
        )
        return self.scene_control


    def snap_position(self):
        target_position_obj = self.control.match_position


    def get_scene_name(self):
        return f'{gen.side_tag(self.control.side)}{self.control.part_name}_{self.control.name}_{control_tag}'


    def add_transform_lock_attributes(self):
        if not self.control.locks:
            return False
        # ...Fill in missing entries with zeroed lists
        for key in ('t', 'r', 's', 'v'):
            if key not in self.control.locks:
                self.control.locks[key] = [0, 0, 0] if key in ('t', 'r', 's') else 0
        # ...Add compound attr to ctrl
        pm.addAttr(self.scene_control, longName='LockAttrData', keyable=0, attributeType='compound', numberOfChildren=4)
        for key in ('t', 'r', 's', 'v'):
            pm.addAttr(self.scene_control, longName=f'LockAttrData{key.upper()}', keyable=0, dataType='string',
                       parent='LockAttrData')
        # ...Embed lock data values in new attrs
        for key in ('t', 'r', 's', 'v'):
            pm.setAttr(f'{self.scene_control}.LockAttrData{key.upper()}', str(self.control.locks[key]), type='string')



########################################################################################################################
class CurveShape:
    def __init__(
        self,
        shape: str,
        size: Union[list, float] = 1.0,
        forward_direction: list[float, float, float] = None,
        up_direction: list[float, float, float] = None,
        shape_offset: list[float, float, float] = None,
    ):
        self.shape = shape
        self.size = size
        self.forward_direction = forward_direction
        self.up_direction = up_direction
        self.shape_offset = shape_offset


    def compose_cvs(self, prefabs_dict=PREFAB_CTRL_SHAPES):
        prefab_curve_data = copy.deepcopy(prefabs_dict[self.shape])
        composed_cv_data = gen.compose_curve_construct_cvs(
            curve_data=prefab_curve_data,
            scale=self.size,
            shape_offset=self.shape_offset,
            up_direction=self.up_direction,
            forward_direction=self.forward_direction)
        return composed_cv_data
