# Title: placer_utils.py
# Author: Sam Leheny
# Contact: samleheny@live.com

# Description:


###########################
##### Import Commands #####
import importlib
import pymel.core as pm

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


class Placer:
    def __init__(
        self,
        name: str,
        side: str = None,
        position: tuple[float, float, float] = None,
        size: float = None,
        vector_handle_positions: list[list, list] = None,
        orientation: list[list, list] = None,
        data_name: str = None,
        scene_name: str = None,
    ):
        self.name = name
        self.side = side
        self.position = position if position else (0, 0, 0)
        self.size = size if size else 1.0
        self.vector_handle_positions = vector_handle_positions if vector_handle_positions else ((0, 0, 1), (0, 1, 0))
        self.orientation = orientation if orientation else ((0, 0, 1), (0, 1, 0))
        self.data_name = data_name if data_name else f'{gen.side_tag(side)}{name}'
        self.scene_name = scene_name



    def create_scene_placer(self, parent=None):
        scene_placer = gen.prefab_curve_construct(prefab='sphere_placer', name=self.scene_name, scale=self.size,
                                                  side=self.side)
        scene_placer.setParent(parent) if parent else None
        self.position_placer(scene_placer)
        self.add_placer_metadata(scene_placer)
        self.color_placer()
        return scene_placer


    def position_placer(self, scene_placer):
        scene_placer.translate.set(tuple(self.position))


    def add_placer_metadata(self, scene_placer):
        metadata_attrs = (
            MetaDataAttr(long_name='PlacerTag', attribute_type='string', keyable=0, default_value_attr_string='name'),
            MetaDataAttr(long_name='Side', attribute_type='string', keyable=0, default_value_attr_string='side'),
            MetaDataAttr(long_name='Size', attribute_type='string', keyable=0, default_value_attr_string='size'),
            MetaDataAttr(long_name='VectorHandleData', attribute_type='string', keyable=0,
                         default_value_attr_string='vector_handle_positions'),
            MetaDataAttr(long_name='Orientation', attribute_type='string', keyable=0,
                         default_value_attr_string='orientation')
        )
        [attr.create(self, scene_placer) for attr in metadata_attrs]


    def color_placer(self, color=None):
        if not color:
            if not self.side:
                color = color_code['M']
            else:
                color = color_code[self.side]
        gen.set_color(self.get_scene_placer(), color)


    def get_scene_placer(self):
        if not pm.objExists(self.scene_name):
            print(f"Placer: '{self.scene_name}' not found in scene")
            return False
        return pm.PyNode(self.scene_name)


    def data_from_placer(self):
        data = {}
        for param, value in vars(self).items():
            data[param] = value
        return data


    def placer_from_data(self, data):
        placer = Placer(**data)
        return placer


    def mirror_placer(self):
        scene_placer = self.get_scene_placer()
        opposite_scene_placer = self.get_opposite_scene_placer(scene_placer)
        # ...Mirror position
        pm.setAttr(f'{opposite_scene_placer}.tx', pm.getAttr(f'{scene_placer}.tx') * -1)
        [pm.setAttr(f'{opposite_scene_placer}.{a}', pm.getAttr(f'{scene_placer}.{a}')) for a in ('ty', 'tz')]
        # ...Match handle size
        pm.setAttr(f'{opposite_scene_placer}.Size', pm.getAttr(f'{scene_placer}.Size'))


    def get_opposite_scene_placer(self, scene_placer):
        sided_prefixes = {'L_': 'R_', 'R_': 'L_'}
        this_prefix = None
        opposite_scene_placer = None
        for prefix in sided_prefixes.keys():
            if str(scene_placer).startswith(prefix):
                this_prefix = prefix
        if this_prefix:
            opposite_scene_placer = pm.PyNode(str(scene_placer).replace(this_prefix, sided_prefixes[this_prefix]))
        return opposite_scene_placer
