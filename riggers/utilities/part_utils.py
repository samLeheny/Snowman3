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

import Snowman3.riggers.utilities.placer_utils as placer_utils
importlib.reload(placer_utils)
Placer = placer_utils.Placer
PlacerManager = placer_utils.PlacerManager
ScenePlacerManager = placer_utils.ScenePlacerManager

import Snowman3.dictionaries.colorCode as color_code
importlib.reload(color_code)

import Snowman3.riggers.utilities.metadata_utils as metadata_utils
importlib.reload(metadata_utils)
MetaDataAttr = metadata_utils.MetaDataAttr
###########################
###########################


###########################
######## Variables ########
part_tag = 'PART'
color_code = color_code.sided_ctrl_color
###########################
###########################



########################################################################################################################
class Part:
    def __init__(
        self,
        name: str,
        side: str = None,
        handle_size: float = 1.0,
        position: tuple[float, float, float] = (0, 0, 0),
        placers: dict = {},
        data_name: str = None,
        scene_name: str = None,
        prefab_key: str = None
    ):
        self.name = name
        self.side = side
        self.handle_size = handle_size
        self.position = position
        self.placers = placers
        self.data_name = data_name if data_name else prefab_key
        self.scene_name = scene_name if scene_name else f'{gen.side_tag(side)}{name}_{part_tag}'
        self.prefab_key = prefab_key



########################################################################################################################
class PartManager:
    def __init__(
        self,
        part
    ):
        self.part = part


    def data_from_part(self):
        data = {}
        for param, value in vars(self.part).items():
            data[param] = value
        data['placers'] = {}
        for key, placer, in self.part.placers.items():
            placer_manager = PlacerManager(placer)
            data['placers'][key] = placer_manager.data_from_placer()
        return data


    def create_placers_from_data(self, placers_data):
        for key, data in placers_data.items():
            self.part.placers[key] = Placer(**data)



########################################################################################################################
class ScenePartManager:
    def __init__(
        self,
        part
    ):
        self.part = part
        self.scene_part = None


    def create_scene_part(self, parent=None):
        self.create_part_handle()
        self.position_part(self.scene_part)
        self.scene_part.setParent(parent) if parent else None
        self.add_part_metadata()
        self.populate_scene_part(self.scene_part)
        self.zero_out_part_rotation()
        return self.scene_part


    def create_part_handle(self):
        self.scene_part = gen.prefab_curve_construct(prefab='cube', name=self.part.scene_name,
                                                     scale=self.part.handle_size, side=self.part.side)
        self.color_part_handle()


    def color_part_handle(self, color=None):
        if not color:
            if not self.part.side:
                color = color_code['M']
            else:
                color = color_code[self.part.side]
        gen.set_color(self.scene_part, color)


    def position_part(self, handle):
        handle.translate.set(tuple(self.part.position))


    def add_part_metadata(self):
        metadata_attrs = (
            MetaDataAttr(long_name='PartTag', attribute_type='string', keyable=0, default_value_attr='name'),
            MetaDataAttr(long_name='Side', attribute_type='string', keyable=0, default_value_attr='side'),
            MetaDataAttr(long_name='HandleSize', attribute_type='float', keyable=0, default_value_attr='handle_size')
        )
        [attr.create(self.part, self.scene_part) for attr in metadata_attrs]
        pm.setAttr(f'{self.scene_part}.HandleSize', channelBox=1)
        for a in ('sx', 'sy', 'sz'):
            pm.connectAttr(f'{self.scene_part}.HandleSize', f'{self.scene_part}.{a}')
            pm.setAttr(f'{self.scene_part}.{a}', keyable=0)


    def populate_scene_part(self, placers_parent=None):
        if not self.part.placers:
            return False
        for placer in self.part.placers.values():
            placer_manager = ScenePlacerManager(placer)
            placer_manager.create_scene_placer(parent=placers_parent)


    def zero_out_part_rotation(self):
        self.scene_part.rotate.set(0, 0, 0)
