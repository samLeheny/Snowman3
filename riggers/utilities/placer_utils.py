# Title: placer_utils.py
# Author: Sam Leheny
# Contact: samleheny@live.com

# Description:


###########################
##### Import Commands #####
import importlib
from dataclasses import dataclass

import Snowman3.utilities.general_utils as gen
importlib.reload(gen)

import Snowman3.riggers.utilities.metadata_utils as metadata_utils
importlib.reload(metadata_utils)
MetaDataAttr = metadata_utils.MetaDataAttr

import Snowman3.dictionaries.colorCode as color_code
importlib.reload(color_code)
###########################
###########################


###########################
######## Variables ########
placer_tag = 'PLC'
color_code = color_code.sided_ctrl_color
###########################
###########################


########################################################################################################################
@dataclass
class Placer:
    name: str
    side: str = None
    position: tuple[float, float, float] = (0, 0, 0)
    size: float = 1.0
    vector_handle_positions: list[list, list] = ((0, 0, 1), (0, 1, 0))
    orientation: list[list, list] = ((0, 0, 1), (0, 1, 0))
    data_name: str = None
    scene_name: str = None
    parent_part_name: str = None



########################################################################################################################
class PlacerCreator:
    def __init__(
        self,
        name: str,
        data_name: str,
        parent_part_name: str,
        position: tuple,
        side: str = None,
        size: float = None,
        vector_handle_positions: list = None,
        orientation: list = None,
        scene_name: str = None
    ):
        self.name = name
        self.data_name = data_name
        self.parent_part_name = parent_part_name
        self.position = position
        self.side = side
        self.size = size if size else 1.25
        self.vector_handle_positions = vector_handle_positions if vector_handle_positions else [[5, 0, 0], [0, 0, -5]]
        self.orientation = orientation if orientation else [[0, 0, 1], [1, 0, 0]]
        self.scene_name = scene_name if scene_name else f'{gen.side_tag(side)}{parent_part_name}_{name}_{placer_tag}'


    def create_placer(self):
        placer = Placer(
            name=self.name,
            data_name=self.data_name,
            side=self.side,
            parent_part_name=self.parent_part_name,
            position=self.flip_position() if self.side == 'R' else self.position,
            size=self.size,
            vector_handle_positions=self.vector_handle_positions,
            orientation=self.orientation,
            scene_name=self.scene_name
        )
        return placer


    def flip_position(self):
        return -self.position[0], self.position[1], self.position[2]



########################################################################################################################
class PlacerManager:
    def __init__(
        self,
        placer
    ):
        self.placer = placer


    def data_from_placer(self):
        data = {}
        for param, value in vars(self.placer).items():
            data[param] = value
        return data



########################################################################################################################
class ScenePlacerManager:
    def __init__(
        self,
        placer
    ):
        self.placer = placer
        self.scene_placer = None


    def create_scene_placer(self, parent=None):
        self.scene_placer = gen.prefab_curve_construct(prefab='sphere_placer', name=self.placer.scene_name,
                                                       scale=self.placer.size, side=self.placer.side)
        self.scene_placer.setParent(parent) if parent else None
        self.position_scene_placer()
        self.add_scene_placer_metadata()
        self.color_scene_placer()
        return self.scene_placer


    def position_scene_placer(self):
        self.scene_placer.translate.set(tuple(self.placer.position))


    def add_scene_placer_metadata(self):
        metadata_attrs = (
            MetaDataAttr(long_name='PlacerTag', attribute_type='string', keyable=0, default_value_attr='name'),
            MetaDataAttr(long_name='Side', attribute_type='string', keyable=0, default_value_attr='side'),
            MetaDataAttr(long_name='Size', attribute_type='string', keyable=0, default_value_attr='size'),
            MetaDataAttr(long_name='VectorHandleData', attribute_type='string', keyable=0,
                         default_value_attr='vector_handle_positions'),
            MetaDataAttr(long_name='Orientation', attribute_type='string', keyable=0, default_value_attr='orientation')
        )
        [attr.create(self.placer, self.scene_placer) for attr in metadata_attrs]


    def color_scene_placer(self, color=None):
        if not color:
            color = color_code[self.placer.side] if self.placer.side else color_code['M']
        gen.set_color(self.scene_placer, color)

