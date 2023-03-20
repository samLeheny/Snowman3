# Title: module_utils.py
# Author: Sam Leheny
# Contact: samleheny@live.com

# Description:


###########################
##### Import Commands #####
import importlib
import pymel.core as pm

import Snowman3.utilities.general_utils as gen
importlib.reload(gen)

import Snowman3.riggers.utilities.part_utils as part_utils
importlib.reload(part_utils)
Part = part_utils.Part

import Snowman3.riggers.utilities.metadata_utils as metadata_utils
importlib.reload(metadata_utils)
MetaDataAttr = metadata_utils.MetaDataAttr
###########################
###########################


###########################
######## Variables ########
module_tag = 'MODULE'
###########################
###########################



class Module:
    def __init__(
        self,
        name: str = None,
        side: str = None,
        data_name: str = None,
        scene_name: str = None,
        prefab_key: str = None,
        parts_prefix: str = None,
        parts = None
    ):
        self.name = name
        self.side = side
        self.data_name = data_name if data_name else f'{gen.side_tag(side)}{name}'
        self.scene_name = scene_name if scene_name else f'{gen.side_tag(side)}{name}_MODULE'
        self.prefab_key = prefab_key
        self.parts = parts if parts else {}
        self.parts_prefix = parts_prefix if parts_prefix else ''

        self.get_parts_from_parts_data()


    def populate_scene_module(self, parts_parent=None):
        if not self.parts:
            return False
        for part in self.parts.values():
            part.create_scene_part(parent=parts_parent)


    def get_parts_from_parts_data(self):
        if not self.parts:
            return False
        if not type(list(self.parts.values())[0]) == dict:
            return False
        parts = {}
        for key, data in self.parts.items():
            parts[key] = Part(**data)
        self.parts = parts


    def get_scene_module(self):
        module_name = self.scene_name
        scene_module = pm.PyNode(module_name)
        return scene_module


    def add_module_metadata(self, scene_module):
        metadata_attrs = (
            MetaDataAttr(long_name='ModuleTag', attribute_type='string', keyable=0, default_value_attr_string='name'),
            MetaDataAttr(long_name='Side', attribute_type='string', keyable=0, default_value_attr_string='side')
        )
        [attr.create(self, scene_module) for attr in metadata_attrs]


    def add_part(self, part):
        if part.prefab_key:
            self.add_prefab_part(part)
        else:
            self.add_empty_part(part)
        return part


    def add_empty_part(self, part):
        self.parts[part.data_name] = part.data_from_part()

    def add_prefab_part(self, part):
        part.populate_prefab()
        self.parts[part.data_name] = part.data_from_part()


    def remove_part(self, part):
        pm.delete(part.get_part_handle())
        self.parts.pop(part.data_name)


    def add_placer(self, name, part, side=None):
        placer = part.add_placer(name, side)
        return placer


    def remove_placer(self, placer, part):
        part.remove_placer(placer)


    def data_from_module(self):
        data = {}
        for param, value in vars(self).items():
            data[param] = value

        data['parts'] = {}
        for key, part in self.parts.items():
            data['parts'][key] = part.data_from_part()
        return data


    def populate_prefab(self):
        print(self.parts)
        parts_holder = self.parts
        self.parts = {}
        for part in parts_holder.values():
            self.add_part(part)
