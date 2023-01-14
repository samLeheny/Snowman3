# Title: IO_data_fields.py
# Author: Sam Leheny
# Contact: samleheny@live.com

# Description:


###########################
##### Import Commands #####

###########################
###########################





########################################################################################################################
def get_dict(key):

    dict = {
        'armature':
            [('name', 'ArmatureName'),
            ('prefab_key', 'ArmaturePrefabKey'),
            ('symmetry_mode', 'SymmetryMode'),
            ('driver_side', 'DriverSide'),
            ('root_size', 'RootSize'),
            ('armature_scale', 'ArmatureScale')],
    }


    return dict[key]
