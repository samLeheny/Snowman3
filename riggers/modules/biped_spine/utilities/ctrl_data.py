# Title: spineControls.py
# Author: Sam Leheny
# Contact: samleheny@live.com

# Description:


###########################
##### Import Commands #####
import importlib

import Snowman3.riggers.utilities.classes.class_ControlData as class_ControlData
importlib.reload(class_ControlData)
ControlData = class_ControlData.ControlData

import Snowman3.dictionaries.nurbsCurvePrefabs as nurbs_curve_prefabs
importlib.reload(nurbs_curve_prefabs)
curve_prefabs = nurbs_curve_prefabs.create_dict()

import Snowman3.dictionaries.nameConventions as nameConventions
importlib.reload(nameConventions)
nom = nameConventions.create_dict()

import Snowman3.riggers.dictionaries.control_colors as ctrl_colors_dict
importlib.reload(ctrl_colors_dict)
ctrl_colors = ctrl_colors_dict.create_dict()
###########################
###########################


###########################
######## Variables ########

###########################
###########################



def create_ctrl_data(side=None, is_driven_side=None, module_ctrl=None):

    ctrl_data = {
        'ik_chest': ControlData(
            name = 'ik_chest',
            shape = 'circle',
            size = [14, 14, 14],
            shape_offset = [0, -3, 0],
            color = ctrl_colors[nom.midSideTag],
            orientation = {'aim_vector': ('y', (0, 1, 0)),
                             'up_vector': ('z', (0, 0, 1))},
            locks = {'v': 1},
            module_ctrl = module_ctrl
        ),


        'ik_waist': ControlData(
            name = 'ik_waist',
            shape = 'circle',
            size = [14, 14, 14],
            color = ctrl_colors[nom.midSideTag],
            orientation = {'aim_vector': ('y', (0, 1, 0)),
                             'up_vector': ('z', (0, 0, 1))},
            locks = {'v': 1},
            module_ctrl = module_ctrl
        ),


        'ik_pelvis': ControlData(
            name = 'ik_pelvis',
            shape = 'circle',
            shape_offset = [0, -2, 0],
            size = [14, 14, 14],
            color = ctrl_colors[nom.midSideTag],
            orientation = {'aim_vector': ('y', (0, 1, 0)),
                             'up_vector': ('z', (0, 0, 1))},
            locks = {'v': 1},
            module_ctrl = module_ctrl
        ),


        'fk_spine_1': ControlData(
            name = 'fk_spine_1',
            shape = 'directional_circle',
            size = [12, 12, 12],
            color = ctrl_colors[nom.midSideTag2],
            orientation = {'aim_vector': ('y', (0, 1, 0)),
                             'up_vector': ('z', (0, 0, 1))},
            locks = {'v': 1},
            up_direction = [0, -1, 0],
            module_ctrl = module_ctrl
        ),


        'fk_spine_2': ControlData(
            name = 'fk_spine_2',
            shape = 'directional_circle',
            size = [12, 12, 12],
            shape_offset = [0, 2, 0],
            color = ctrl_colors[nom.midSideTag2],
            orientation = {'aim_vector': ('y', (0, 1, 0)),
                             'up_vector': ('z', (0, 0, 1))},
            locks = {'v': 1},
            up_direction = [0, -1, 0],
            module_ctrl = module_ctrl
        ),


        'fk_spine_3': ControlData(
            name = 'fk_spine_3',
            shape = 'directional_circle',
            size = [12, 12, 12],
            shape_offset = [0, -3, 0],
            color = ctrl_colors[nom.midSideTag2],
            orientation = {'aim_vector': ('y', (0, 1, 0)),
                             'up_vector': ('z', (0, 0, 1))},
            locks = {'v': 1},
            up_direction = [0, -1, 0],
            module_ctrl = module_ctrl
        ),


        'fk_hips': ControlData(
            name = 'fk_hips',
            shape = 'directional_circle',
            shape_offset = [0, -5, 0],
            size = [12, 12, 12],
            color = ctrl_colors[nom.midSideTag2],
            orientation = {'aim_vector': ('y', (0, 1, 0)),
                             'up_vector': ('z', (0, 0, 1))},
            locks = {'v': 1},
            module_ctrl = module_ctrl
        ),


        'spine_tweak_1': ControlData(
            name = 'spine_tweak_1',
            shape = 'square',
            size = [12, 12, 12],
            color = ctrl_colors[nom.midSideTag3],
            up_direction = [0, 0, 1],
            forward_direction = [0, 1, 0],
            orientation = {'aim_vector': ('y', (0, 1, 0)),
                             'up_vector': ('z', (0, 0, 1))},
            locks = {'v': 1},
            module_ctrl = module_ctrl
        ),


        'spine_tweak_2': ControlData(
            name = 'spine_tweak_2',
            shape = 'square',
            size = [12, 12, 12],
            color = ctrl_colors[nom.midSideTag3],
            up_direction = [0, 0, 1],
            forward_direction = [0, 1, 0],
            orientation = {'aim_vector': ('y', (0, 1, 0)),
                             'up_vector': ('z', (0, 0, 1))},
            locks = {'v': 1},
            module_ctrl = module_ctrl
        ),


        'spine_tweak_3': ControlData(
            name = 'spine_tweak_3',
            shape = 'square',
            size = [12, 12, 12],
            color = ctrl_colors[nom.midSideTag3],
            up_direction = [0, 0, 1],
            forward_direction = [0, 1, 0],
            orientation = {'aim_vector': ('y', (0, 1, 0)),
                             'up_vector': ('z', (0, 0, 1))},
            locks = {'v': 1},
            module_ctrl = module_ctrl
        ),


        'spine_tweak_4': ControlData(
            name = 'spine_tweak_4',
            shape = 'square',
            size = [12, 12, 12],
            color = ctrl_colors[nom.midSideTag3],
            up_direction = [0, 0, 1],
            forward_direction = [0, 1, 0],
            orientation = {'aim_vector': ('y', (0, 1, 0)),
                             'up_vector': ('z', (0, 0, 1))},
            locks = {'v': 1},
            module_ctrl = module_ctrl
        ),


        'spine_tweak_5': ControlData(
            name = 'spine_tweak_5',
            shape = 'square',
            size = [12, 12, 12],
            color = ctrl_colors[nom.midSideTag3],
            up_direction = [0, 0, 1],
            forward_direction = [0, 1, 0],
            orientation = {'aim_vector': ('y', (0, 1, 0)),
                             'up_vector': ('z', (0, 0, 1))},
            locks = {'v': 1},
            module_ctrl = module_ctrl
        ),


        'spine_tweak_6': ControlData(
            name = 'spine_tweak_6',
            shape = 'square',
            size = [12, 12, 12],
            color = ctrl_colors[nom.midSideTag3],
            up_direction = [0, 0, 1],
            forward_direction = [0, 1, 0],
            orientation = {'aim_vector': ('y', (0, 1, 0)),
                             'up_vector': ('z', (0, 0, 1))},
            locks = {'v': 1},
            module_ctrl = module_ctrl
        ),


        'spine_tweak_7': ControlData(
            name = 'spine_tweak_7',
            shape = 'square',
            size = [12, 12, 12],
            color = ctrl_colors[nom.midSideTag3],
            up_direction = [0, 0, 1],
            forward_direction = [0, 1, 0],
            orientation = {'aim_vector': ('y', (0, 1, 0)),
                             'up_vector': ('z', (0, 0, 1))},
            locks = {'v': 1},
            module_ctrl = module_ctrl
        ),


        'settings': ControlData(
            name = 'spine_settings',
            shape = 'gear',
            size = [1, 1, 1],
            position = ('spine_1',),
            shape_offset = [18.5, 8, 0],
            color = ctrl_colors['settings'],
            locks = {'v': 1, 't': [1, 1, 1], 'r': [1, 1, 1], 's': [1, 1, 1]},
            module_ctrl = module_ctrl
        )
    }

    return ctrl_data