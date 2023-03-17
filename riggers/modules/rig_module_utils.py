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


    def get_prefab_part(self, name, prefab_key):
        dir_string = f'Snowman3.riggers.parts.{prefab_key}'
        part_data = importlib.import_module(dir_string)
        importlib.reload(part_data)
        part = part_data.create_part(name, self.side, self.part_offset)
        return part


    def assemble_parts(self, parts_data):
        for key, part_data in parts_data.items():
            self.parts[key] = self.get_prefab_part(
                name = part_data['key'],
                prefab_key = part_data['prefab_key']
            )
        return self.parts


    def create_module(self):
        module = Module(
            name=self.name,
            prefab_key=self.prefab_key,
            side=self.side,
            parts=self.assemble_parts(self.parts_data)
        )
        return module



class ModuleData:
    def __init__(
        self,
        name: str,
        prefab_key: str,
        side: str,
        part_offset: tuple[float, float, float],
    ):
        self.name = name
        self.prefab_key = prefab_key
        self.side = side
        self.part_offset = part_offset
        self.prefab_module_data = PrefabModuleData(prefab_key)



class PrefabModuleData:
    def __init__(
        self,
        prefab_key: str,
    ):
        self.prefab_key = prefab_key,
        self.parts_data = self.get_parts_data(prefab_key)

    def get_parts_data(self, prefab_key):
        return prefab_module_inputs[prefab_key]['parts']



prefab_module_inputs = {
    'root': {
        'parts': {
            'root': {
                'key': 'root',
                'prefab_key': 'root'
            },
            'cog': {
                'key': 'cog',
                'prefab_key': 'cog'
            }
        }
    },
    'biped_spine': {
        'parts': {
            'biped_spine': {
                'key': 'spine',
                'prefab_key': 'biped_spine'
            }
        }
    },
    'biped_neck': {
        'parts': {
            'biped_neck': {
                'key': 'neck',
                'prefab_key': 'biped_neck'
            }
        }
    },
    'biped_clavicle': {
        'parts': {
            'biped_clavicle': {
                'key': 'clavicle',
                'prefab_key': 'biped_clavicle'
            }
        }
    },
    'biped_arm': {
        'parts': {
            'biped_arm': {
                'key': 'arm',
                'prefab_key': 'biped_arm'
            }
        }
    },
    'biped_hand': {
        'parts': {
            'biped_hand': {
                'key': 'hand',
                'prefab_key': 'biped_hand'
            }
        }
    },
    'leg_plantigrade': {
        'parts': {
            'leg_plantigrade': {
                'key': 'leg',
                'prefab_key': 'leg_plantigrade'
            }
        }
    },
    'foot_plantigrade': {
        'parts': {
            'foot_plantigrade': {
                'key': 'foot',
                'prefab_key': 'foot_plantigrade'
            }
        }
    }
}
