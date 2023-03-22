# Title: container_utils.py
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
PartManager = part_utils.PartManager
ScenePartManager = part_utils.ScenePartManager

import Snowman3.riggers.utilities.metadata_utils as metadata_utils
importlib.reload(metadata_utils)
MetaDataAttr = metadata_utils.MetaDataAttr
###########################
###########################


###########################
######## Variables ########
container_tag = 'CON'
###########################
###########################



########################################################################################################################
class Container:
    def __init__(
        self,
        name: str = None,
        side: str = None,
        data_name: str = None,
        scene_name: str = None,
        prefab_key: str = None,
        parts_prefix: str = '',
        parts = {}
    ):
        self.name = name
        self.side = side
        self.data_name = data_name if data_name else f'{gen.side_tag(side)}{name}'
        self.scene_name = scene_name if scene_name else f'{gen.side_tag(side)}{name}_{container_tag}'
        self.prefab_key = prefab_key
        self.parts = parts
        self.parts_prefix = parts_prefix



########################################################################################################################
class ContainerManager:
    def __init__(
        self,
        container
    ):
        self.container = container


    def data_from_container(self):
        data = {}
        for param, value in vars(self.container).items():
            data[param] = value
        data['parts'] = {}
        for key, part in self.container.parts.items():
            part_manager = PartManager(part)
            data['parts'][key] = part_manager.data_from_part()
        return data


    def opposite_container_data_name(self):
        if self.container.side not in ('L', 'R'):
            return None
        opposite_side_tags = {'L': 'R_', 'R': 'L_'}
        opposite_container_data_name = f'{opposite_side_tags[self.container.side]}{self.container.data_name[2:]}'
        return opposite_container_data_name


    def create_parts_from_data(self, parts_data):
        for key, data in parts_data.items():
            new_part = Part(**data)
            part_manager = PartManager(new_part)
            part_manager.create_placers_from_data(new_part.placers)
            self.container.parts[key] = part_manager.part



########################################################################################################################
class SceneContainerManager:
    def __init__(
        self,
        container
    ):
        self.container = container
        self.scene_container = None


    def create_scene_container(self):
        self.scene_container = pm.shadingNode('transform', name=self.container.scene_name, au=1)
        self.add_container_metadata()
        self.populate_scene_container(self.scene_container)
        if self.container.side == 'R':
            gen.flip(self.scene_container)


    def populate_scene_container(self, parts_parent=None):
        if not self.container.parts:
            return False
        for part in self.container.parts.values():
            part_manager = ScenePartManager(part)
            part_manager.create_scene_part(parts_parent)


    def add_container_metadata(self):
        metadata_attrs = (
            MetaDataAttr(long_name='ContainerTag', attribute_type='string', keyable=0, default_value_attr='name'),
            MetaDataAttr(long_name='Side', attribute_type='string', keyable=0, default_value_attr='side')
        )
        [attr.create(self.container, self.scene_container) for attr in metadata_attrs]