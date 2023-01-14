# Title: IO_data_fields.py
# Author: Sam Leheny
# Contact: samleheny@live.com

# Description:


###########################
##### Import Commands #####
import pymel.core as pm
###########################
###########################




class IODataField:
    def __init__(
        self,
        IO_key,
        attr_name,
        attr_type,
        attr_value = None
    ):
        self.IO_key = IO_key
        self.attr_name = attr_name
        self.attr_type = attr_type
        self.attr_value = attr_value


    def create_attr(self, node):
        if self.attr_type == 'string':
            pm.addAttr(node, longName=self.attr_name, keyable=0, dataType=self.attr_type)
        else:
            pm.addAttr(node, longName=self.attr_name, keyable=0, attributeType=self.attr_type)


    def set_attr(self, node):
        if not self.attr_value:
            return
        if self.attr_type == 'string':
            pm.setAttr(f'{node}.{self.attr_name}', self.attr_value, type=self.attr_type, lock=1)
        else:
            pm.setAttr(f'{node}.{self.attr_name}', self.attr_value, lock=1)



########################################################################################################################
def get_dict(key):

    dict = {
        'armature': [
            IODataField('name', 'ArmatureName', 'string'),
            IODataField('prefab_key', 'ArmaturePrefabKey', 'string'),
            IODataField('symmetry_mode', 'SymmetryMode', 'string'),
            IODataField('driver_side', 'DriverSide', 'string'),
            IODataField('root_size', 'RootSize', 'float'),
            IODataField('armature_scale', 'ArmatureScale', 'float')
        ],
    }


    return dict[key]
