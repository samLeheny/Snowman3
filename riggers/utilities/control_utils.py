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

import Snowman3.riggers.utilities.curve_utils as crv_utils
importlib.reload(crv_utils)
CurveConstruct = crv_utils.CurveConstruct

import Snowman3.dictionaries.colorCode as colorCode
###########################
###########################


###########################
######## Variables ########
CTRL_TAG = 'CTRL'
PREFAB_CTRL_SHAPES = prefab_curve_shapes.create_dict()
COLOR_CODE = colorCode.sided_ctrl_color
###########################
###########################



########################################################################################################################
class Control:
    def __init__(
        self,
        name: str,
        shape: str,
        color: Union[list, int],
        position: list,
        locks: dict = None,
        match_position: str = None,
        side: str = None,
        part_name: str = None
    ):
        self.name = name
        self.shape = shape
        self.color = color
        self.position = position
        self.locks = locks or {'v': 1}
        self.match_position = match_position
        self.side = side
        self.part_name = part_name
        self.data_name = self._create_data_name()
        self.scene_name = self._create_scene_name()


    @classmethod
    def create_from_data(cls, **kwargs):
        class_params = cls.__init__.__code__.co_varnames
        inst_inputs = {name: kwargs[name] for name in kwargs if name in class_params}
        return Control(**inst_inputs)


    def _create_scene_name(self):
        return f'{gen.side_tag(self.side)}{self.part_name}_{self.name}_{CTRL_TAG}'


    def _create_data_name(self):
        return f'{gen.side_tag(self.side)}{self.name}'


    def data_dict(self):
        return vars(self).copy()


    def format_data_to_part(self, part_key):
        self.part_name = part_key
        self.side = self.side
        self.scene_name = self._create_scene_name()
        self.data_name = self._create_data_name()


    def flip(self):
        if self.side not in ('L', 'R'):
            return False
        self.side = gen.opposite_side(self.side)
        self.color = COLOR_CODE[self.side]
        self.data_name = self._create_data_name()
        self.scene_name = self._create_scene_name()
        if self.position:
            self.position[0] = -self.position[0]



########################################################################################################################
class SceneControlManager:
    def __init__(
        self,
        control
    ):
        self.control = control
        self.scene_control = None


    def create_scene_control(self):
        self.create_scene_ctrl_obj()
        if self.control.match_position:
            self.snap_position()
        self.add_transform_lock_attributes()
        return self.scene_control


    def create_scene_ctrl_obj(self):
        curve_construct = CurveConstruct(self.control.scene_name, shape=self.control.shape, color=self.control.color)
        self.scene_control = curve_construct.create_scene_obj()
        return self.scene_control


    def snap_position(self):
        target_position_obj = self.control.match_position


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
    def __init__(self):
        pass

    @classmethod
    def compose_cvs(cls, shape, size, forward_direction, up_direction, shape_offset, prefabs_dict=PREFAB_CTRL_SHAPES):
        return gen.compose_curve_construct_cvs(
            curve_data=copy.deepcopy(prefabs_dict[shape]),
            scale=size,
            shape_offset=shape_offset,
            up_direction=up_direction,
            forward_direction=forward_direction)
