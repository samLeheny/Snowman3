# Title: container_utils.py
# Author: Sam Leheny
# Contact: samleheny@live.com

# Description:


###########################
##### Import Commands #####
import importlib
from dataclasses import dataclass
import pymel.core as pm

import Snowman3.utilities.general_utils as gen
importlib.reload(gen)

import Snowman3.riggers.utilities.part_utils as part_utils
importlib.reload(part_utils)
Part = part_utils.Part
PartCreator = part_utils.PartCreator
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
@dataclass
class Container:
    name: str
    side: str
    data_name: str
    scene_name: str
    prefab_key: str
    parts_prefix: str
    parts: dict



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



########################################################################################################################
class ContainerCreator:
    def __init__(
        self,
        container_data
    ):
        self.name = container_data.name
        self.side = container_data.side
        self.part_offset = container_data.part_offset if container_data.part_offset else (0, 0, 0)
        self.prefab_key = container_data.prefab_key
        self.parts = {}
        self.parts_prefix = container_data.parts_prefix


    def get_prefab_part(self, name, prefab_key, parts_prefix):
        part_creator = PartCreator(name=f'{parts_prefix}{name}', prefab_key=prefab_key,  side=self.side,
                                   part_offset=self.part_offset)
        return part_creator.create_part()


    def assemble_parts(self):
        if not self.prefab_key:
            return self.parts
        container_inputs = prefab_container_inputs[self.prefab_key]
        prefab_parts_data = container_inputs.parts_data
        for key, part_data in prefab_parts_data.items():
            self.parts[key] = self.get_prefab_part(
                name = part_data['key'],
                prefab_key = part_data['prefab_key'],
                parts_prefix = self.parts_prefix
            )
        return self.parts


    def create_container(self):
        data_name = f'{gen.side_tag(self.side)}{self.name}'
        scene_name = f'{gen.side_tag(self.side)}{self.name}_{container_tag}'
        parts = self.assemble_parts()
        container = Container(
            name = self.name,
            prefab_key = self.prefab_key,
            side = self.side,
            parts_prefix = self.parts_prefix,
            parts = parts,
            data_name = data_name,
            scene_name = scene_name
        )
        return container


@dataclass()
class ContainerData:
    name: str
    prefab_key: str
    side: str
    part_offset: tuple[float, float, float]
    parts_prefix: str = ''


@dataclass()
class PrefabContainerData:
    parts_data: dict



prefab_container_inputs = {
    'root':
        PrefabContainerData(parts_data={'root': {'key': 'Root',
                                                 'prefab_key': 'root'},
                                        'cog': {'key': 'Cog',
                                                'prefab_key': 'cog'}}),
    'biped_spine':
        PrefabContainerData(parts_data={'biped_spine': {'key': 'Spine',
                                                        'prefab_key': 'biped_spine'}}),
    'biped_neck':
        PrefabContainerData(parts_data={'biped_neck': {'key': 'Neck',
                                                       'prefab_key': 'biped_neck'}}),
    'biped_clavicle':
        PrefabContainerData(parts_data={'biped_clavicle': {'key': 'Clavicle',
                                                           'prefab_key': 'biped_clavicle'}}),
    'biped_arm':
        PrefabContainerData(parts_data={'biped_arm': {'key': 'Arm',
                                                      'prefab_key': 'biped_arm'}}),
    'biped_hand':
        PrefabContainerData(parts_data={'biped_hand': {'key': 'Hand',
                                                       'prefab_key': 'biped_hand'}}),
    'leg_plantigrade':
        PrefabContainerData(parts_data={'leg_plantigrade': {'key': 'Leg',
                                                            'prefab_key': 'leg_plantigrade'}}),
    'foot_plantigrade':
        PrefabContainerData(parts_data={'foot_plantigrade': {'key': 'Root',
                                                             'prefab_key': 'foot_plantigrade'}}),
}
