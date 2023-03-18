# Title: rig_module_utils.py
# Author: Sam Leheny
# Contact: samleheny@live.com

# Description:


###########################
##### Import Commands #####
import importlib
import pymel.core as pm

import Snowman3.riggers.utilities.module_utils as module_utils
importlib.reload(module_utils)
Module = module_utils.Module
###########################
###########################


###########################
######## Variables ########

###########################
###########################


class ModuleCreator:
    def __init__(
        self,
        module_data
    ):
        self.name = module_data.name
        self.side = module_data.side
        self.part_offset = module_data.part_offset if module_data.part_offset else (0, 0, 0)
        self.prefab_key = module_data.prefab_key
        self.parts_data = module_data.prefab_module_data.parts_data
        self.parts = {}
        self.parts_prefix = module_data.parts_prefix


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


    def create_module(self):
        module = Module(
            name=self.name,
            prefab_key=self.prefab_key,
            side=self.side,
            parts=self.assemble_parts(self.parts_data),
            parts_prefix = self.parts_prefix
        )
        return module



class ModuleData:
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
        self.prefab_module_data = prefab_module_inputs[prefab_key]
        self.parts_prefix = parts_prefix



class PrefabModuleData:
    def __init__(
        self,
        parts_data,
    ):
        self.parts_data = parts_data



prefab_module_inputs = {
    'root':
        PrefabModuleData(parts_data={'root': {'key': 'Root',
                                              'prefab_key': 'root'},
                                     'cog': {'key': 'Cog',
                                             'prefab_key': 'cog'}}),
    'biped_spine':
        PrefabModuleData(parts_data={'biped_spine': {'key': 'Spine',
                                                     'prefab_key': 'biped_spine'}}),
    'biped_neck':
        PrefabModuleData(parts_data={'biped_neck': {'key': 'Neck',
                                                    'prefab_key': 'biped_neck'}}),
    'biped_clavicle':
        PrefabModuleData(parts_data={'biped_clavicle': {'key': 'Clavicle',
                                                        'prefab_key': 'biped_clavicle'}}),
    'biped_arm':
        PrefabModuleData(parts_data={'biped_arm': {'key': 'Arm',
                                                   'prefab_key': 'biped_arm'}}),
    'biped_hand':
        PrefabModuleData(parts_data={'biped_hand': {'key': 'Hand',
                                                    'prefab_key': 'biped_hand'}}),
    'leg_plantigrade':
        PrefabModuleData(parts_data={'leg_plantigrade': {'key': 'Leg',
                                                         'prefab_key': 'leg_plantigrade'}}),
    'foot_plantigrade':
        PrefabModuleData(parts_data={'foot_plantigrade': {'key': 'Root',
                                                          'prefab_key': 'foot_plantigrade'}}),
}
