# Title: part_utils.py
# Author: Sam Leheny
# Contact: samleheny@live.com

# Description:


###########################
##### Import Commands #####
import importlib
import pymel.core as pm

import Snowman3.utilities.general_utils as gen
importlib.reload(gen)

import Snowman3.dictionaries.colorCode as color_code
importlib.reload(color_code)

import Snowman3.riggers.utilities.placer_utils as placer_utils
importlib.reload(placer_utils)
Placer = placer_utils.Placer
###########################
###########################


###########################
######## Variables ########
part_tag = 'PART'
color_code = color_code.sided_ctrl_color
###########################
###########################



class Part:
    def __init__(
        self,
        name: str,
        side: str = None,
        handle_size: float = None,
        position = None,
        placers = None,
        data_name: str = None,
        scene_name: str = None,
        prefab_key: str = None
    ):
        self.name = name
        self.side = side
        self.handle_size = handle_size if handle_size else 1.0
        self.position = position if position else [0, 0, 0]
        self.placers = placers if placers else {}
        self.data_name = data_name if data_name else prefab_key
        self.scene_name = scene_name if scene_name else f'{gen.side_tag(side)}{name}_{part_tag}'
        self.prefab_key = prefab_key

        self.get_placers_from_placers_data()



    def data_from_part(self):
        data = {}
        for param, value in vars(self).items():
            data[param] = value
        data['placers'] = {}
        for key, placer, in self.placers.items():
            data['placers'][key] = placer.data_from_placer()
        return data



    def get_placers_from_placers_data(self):
        if not self.placers:
            return False
        if not type(list(self.placers.values())[0]) == dict:
            return False
        placers = {}
        for key, data in self.placers.items():
            placers[key] = Placer(**data)
        self.placers = placers



    def create_scene_part(self, parent=None):
        scene_part = self.create_part_handle()
        self.position_part(scene_part)
        scene_part.setParent(parent) if parent else None
        self.add_part_metadata(scene_part)
        self.populate_scene_part(scene_part)
        return scene_part



    def create_part_handle(self):
        handle = gen.prefab_curve_construct(prefab='cube', name=self.scene_name, scale=self.handle_size, side=self.side)
        self.color_part_handle(handle)
        return handle



    def populate_scene_part(self, placers_parent=None):
        if not self.placers:
            return False
        for placer in self.placers.values():
            placer.create_scene_placer(parent=placers_parent)



    def position_part(self, handle):
        handle.translate.set(tuple(self.position))



    def add_part_metadata(self, scene_part):
        # ...Placer tag
        gen.add_attr(scene_part, long_name='PartTag', attribute_type='string', keyable=0, default_value=self.name)
        # ...Side
        side_attr_input = self.side if self.side else 'None'
        gen.add_attr(scene_part, long_name='Side', attribute_type='string', keyable=0, default_value=side_attr_input)
        # ...Handle size
        gen.add_attr(scene_part, long_name='HandleSize', attribute_type='float', keyable=0,
                     default_value=self.handle_size)
        pm.setAttr(f'{scene_part}.HandleSize', channelBox=1)
        for a in ('sx', 'sy', 'sz'):
            pm.connectAttr(f'{scene_part}.HandleSize', f'{scene_part}.{a}')
            pm.setAttr(f'{scene_part}.{a}', keyable=0)



    def color_part_handle(self, handle, color=None):
        if not color:
            if not self.side:
                color = color_code['M']
            else:
                color = color_code[self.side]
        gen.set_color(handle, color)
