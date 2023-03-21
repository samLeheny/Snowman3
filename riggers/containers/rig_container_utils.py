# Title: rig_container_utils.py
# Author: Sam Leheny
# Contact: samleheny@live.com

# Description:


###########################
##### Import Commands #####
import importlib
import pymel.core as pm

import Snowman3.riggers.utilities.container_utils as container_utils
importlib.reload(container_utils)
Container = container_utils.Container
###########################
###########################


###########################
######## Variables ########

###########################
###########################


class ContainerCreator:
    def __init__(
        self,
        container_data
    ):
        self.name = container_data.name
        self.side = container_data.side
        self.part_offset = container_data.part_offset if container_data.part_offset else (0, 0, 0)
        self.prefab_key = container_data.prefab_key
        self.parts_data = container_data.prefab_container_data.parts_data if \
            container_data.prefab_container_data else {}
        self.parts = {}
        self.parts_prefix = container_data.parts_prefix


    def get_prefab_part(self, name, prefab_key, parts_prefix):
        dir_string = f'Snowman3.riggers.parts.{prefab_key}'
        part_data = importlib.import_module(dir_string)
        importlib.reload(part_data)
        part = part_data.create_part(f'{parts_prefix}{name}', self.side, self.part_offset)
        return part


    def assemble_parts(self, parts_data):
        for key, part_data in parts_data.items():
            self.parts[key] = self.get_prefab_part(
                name = part_data['key'],
                prefab_key = part_data['prefab_key'],
                parts_prefix = self.parts_prefix
            )
        return self.parts


    def create_container(self):
        container = Container(
            name=self.name,
            prefab_key=self.prefab_key,
            side=self.side,
            parts=self.assemble_parts(self.parts_data),
            parts_prefix = self.parts_prefix
        )
        return container



class ContainerData:
    def __init__(
        self,
        name: str,
        prefab_key: str,
        side: str,
        part_offset: tuple[float, float, float],
        parts_prefix: str = '',
    ):
        self.name = name
        self.prefab_key = prefab_key
        self.side = side
        self.part_offset = part_offset
        self.prefab_container_data = prefab_container_inputs[prefab_key] if prefab_key else None
        self.parts_prefix = parts_prefix



class PrefabContainerData:
    def __init__(
        self,
        parts_data,
    ):
        self.parts_data = parts_data



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
