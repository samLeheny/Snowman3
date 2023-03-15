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
        name: str,
        side: str = None,
        data_name: str = None,
        scene_name: str = None,
        prefab_key: str = None,
        parts = None
    ):
        self.name = name
        self.side = side
        self.data_name = data_name if data_name else f'{gen.side_tag(side)}{name}'
        self.scene_name = scene_name if scene_name else f'{gen.side_tag(side)}{name}_MODULE'
        self.prefab_key = prefab_key
        self.parts = parts if parts else {}

        self.get_parts_from_parts_data()



    def create_scene_module(self, parent=None):
        scene_module = pm.shadingNode('transform', name=self.scene_name, au=1)
        scene_module.setParent(parent) if parent else None
        self.add_module_metadata(scene_module)
        self.populate_scene_module(parts_parent=scene_module)
        return scene_module


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


    def impose_module_side_on_part(self, part):
        if not part.side:
            part.edit_side(self.side)


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
        return data


    def module_from_data(self, data):
        module = Module(**data)
        return module


    def update_module_from_scene(self):
        data = self.data_from_module()
        # ...Update module parts
        parts = data['parts']

        # ...Finish
        return True


    def mirror_module(self, driver_side='L'):
        for key, part_data in self.parts.items():
            part = part_utils.part_from_data(part_data)
            if part.side == driver_side:
                part_utils.mirror_part(part)


    def populate_prefab(self):
        dir_string = 'Snowman3.riggers.modules.{}.data.parts'
        prefab_parts = importlib.import_module(dir_string.format(self.prefab_key))
        importlib.reload(prefab_parts)
        part_list = prefab_parts.parts.values()
        for part in part_list:
            self.impose_module_side_on_part(part)
            self.add_part(part)
