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
        self.data_name = data_name if data_name else f'{gen.side_tag(side)}{name}'
        self.scene_name = scene_name if scene_name else f'{gen.side_tag(side)}{name}_{part_tag}'
        self.prefab_key = prefab_key

        self.get_placers_from_placers_data()



    def data_from_part(self):
        data = {}
        for param, value in vars(self).items():
            data[param] = value
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


    def get_part_handle(self):
        if not pm.objExists(self.scene_name):
            return False
        part_handle = pm.PyNode(self.scene_name)
        return part_handle


    def add_placer(self, placer):
        self.placers[placer.data_name] = placer.data_from_placer()
        return placer


    def remove_placer(self, placer):
        pm.delete(placer.get_scene_placer())
        self.placers.pop(placer.data_name)


    def part_from_data(self, data):
        part = Part(**data)
        return part


    def update_part_from_scene(self):
        part_handle = self.get_part_handle()
        # ...Update position
        self.position = list(part_handle.translate.get())
        # ...Update handle size
        self.handle_size = pm.getAttr(f'{part_handle}.HandleSize')


    def mirror_part(self):
        part_handle = self.get_part_handle()
        opposite_part_handle = self.get_opposite_part_handle()
        # ...Mirror position
        pm.setAttr(f'{opposite_part_handle}.tx', pm.getAttr(f'{part_handle}.tx') * -1)
        [pm.setAttr(f'{opposite_part_handle}.{a}', pm.getAttr(f'{part_handle}.{a}')) for a in ('ty', 'tz')]
        # ...Match handle size
        pm.setAttr(f'{opposite_part_handle}.HandleSize', pm.getAttr(f'{part_handle}.HandleSize'))


    def get_opposite_part_handle(self, part_handle):
        sided_prefixes = {'L_': 'R_', 'R_': 'L_'}
        this_prefix = None
        opposite_part_handle = None
        for prefix in sided_prefixes.keys():
            if str(part_handle).startswith(prefix):
                this_prefix = prefix
        if this_prefix:
            opposite_part_handle = pm.PyNode(str(part_handle).replace(this_prefix, sided_prefixes[this_prefix]))
        return opposite_part_handle


    def get_scene_part(self):
        scene_part = pm.PyNode(self.scene_name)
        return scene_part


    def color_part_handle(self, handle, color=None):
        if not color:
            if not self.side:
                color = color_code['M']
            else:
                color = color_code[self.side]
        gen.set_color(handle, color)


    def populate_prefab(self):
        placers_holder = self.placers
        self.placers = {}
        for placer in placers_holder.values():
            if not placer.parent_part_name:
                placer.edit_parent_part_name(self.name)
            self.add_placer(placer)


    def edit_side(self, new_side):
        self.side = new_side
        self.data_name = f'{gen.side_tag(self.side)}{self.name}'
        self.scene_name = f'{gen.side_tag(self.side)}{self.name}_{part_tag}'
