# Title: space_blends_IO.py
# Author: Sam Leheny
# Contact: samleheny@live.com

# Description:


###########################
##### Import Commands #####
import importlib

import Snowman3.riggers.utilities.classes.class_SpaceBlend as class_spaceBlend
importlib.reload(class_spaceBlend)
SpaceBlend = class_spaceBlend.SpaceBlend

import Snowman3.riggers.IO.data_IO as classDataIO
importlib.reload(classDataIO)
DataIO = classDataIO.DataIO
###########################
###########################

###########################
######## Variables ########
default_file_name = 'space_blends.json'
###########################
###########################





########################################################################################################################
class SpaceBlendsDataIO( DataIO ):
    def __init__(
        self,
        data = None,
        space_blends = None,
        dirpath = None,
        file_name = default_file_name
    ):
        super().__init__(data=data, dirpath=dirpath, file_name=file_name)
        self.space_blends = space_blends



    ####################################################################################################################
    def prep_data_for_export(self):

        self.data = []
        for blend in self.space_blends:
            self.data.append(blend.get_data_list())



    ####################################################################################################################
    def save(self):
        self.prep_data_for_export() if not self.data else None
        self.save_data_to_file(self.data)



    ####################################################################################################################
    def create_blends_from_data(self, data):

        blends = []

        for blend_dict in data:

            params = ('target', 'source', 'source_name', 'attr_node', 'global_space_parent', 'translate', 'rotate',
                      'scale', 'attr_name', 'name', 'type', 'default_value', 'side', 'reverse')

            for param in params:
                if not param in blend_dict: blend_dict[param] = None

            blends.append(SpaceBlend(
                target = blend_dict['target'],
                source = blend_dict['source'],
                source_name = blend_dict['source_name'],
                attr_node = blend_dict['attr_node'],
                global_space_parent = blend_dict['global_space_parent'],
                translate = blend_dict['translate'],
                rotate = blend_dict['rotate'],
                scale = blend_dict['scale'],
                attr_name = blend_dict['attr_name'],
                name = blend_dict['name'],
                type = blend_dict['type'],
                default_value = blend_dict['default_value'],
                side = blend_dict['side'],
                reverse = blend_dict['reverse']
            ))

        return blends
