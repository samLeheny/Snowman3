# Title: placer_utils.py
# Author: Sam Leheny
# Contact: samleheny@live.com

# Description:


###########################
##### Import Commands #####
import importlib
import pymel.core as pm

import Snowman3.utilities.general_utils as gen
importlib.reload(gen)

import Snowman3.riggers.utilities.metadata_utils as metadata_utils
importlib.reload(metadata_utils)
MetaDataAttr = metadata_utils.MetaDataAttr

import Snowman3.dictionaries.colorCode as color_code
importlib.reload(color_code)
###########################
###########################


###########################
######## Variables ########
placer_tag = 'PLC'
color_code = color_code.sided_ctrl_color
###########################
###########################


class Placer:
    def __init__(
        self,
        name: str,
        side: str = None,
        position: tuple[float, float, float] = None,
        size: float = None,
        vector_handle_positions: tuple[tuple, tuple] = None,
        orientation: tuple[tuple, tuple] = None,
        data_name: str = None,
        scene_name: str = None,
    ):
        self.name = name
        self.side = side
        self.position = position if position else (0, 0, 0)
        self.size = size if size else 1.0
        self.vector_handle_positions = vector_handle_positions if vector_handle_positions else ((0, 0, 1), (0, 1, 0))
        self.orientation = orientation if orientation else ((0, 0, 1), (0, 1, 0))
        self.data_name = data_name if data_name else f'{gen.side_tag(side)}{name}'
        self.scene_name = scene_name


metadata_attrs = (
    MetaDataAttr(long_name='PlacerTag', attribute_type='string', keyable=0, default_value_attr_string='name'),
    MetaDataAttr(long_name='Side', attribute_type='string', keyable=0, default_value_attr_string='side'),
    MetaDataAttr(long_name='Size', attribute_type='string', keyable=0, default_value_attr_string='size'),
    MetaDataAttr(long_name='VectorHandleData', attribute_type='string', keyable=0,
                 default_value_attr_string='vector_handle_positions'),
    MetaDataAttr(long_name='Orientation', attribute_type='string', keyable=0, default_value_attr_string='orientation')
)


########################################################################################################################
def add_placer_metadata(module, scene_placer):
    [attr.create(module, scene_placer) for attr in metadata_attrs]


####################################################################################################################
def create_scene_placer(placer, parent=None):
    scene_placer = gen.prefab_curve_construct(prefab='sphere_placer', name=placer.scene_name, scale=placer.size,
                                              side=placer.side)
    scene_placer.setParent(parent) if parent else None
    position_placer(placer, scene_placer)
    add_placer_metadata(placer, scene_placer)
    color_placer(placer)
    return scene_placer


####################################################################################################################
def position_placer(placer, scene_placer):
    scene_placer.translate.set(tuple(placer.position))


########################################################################################################################
def data_from_placer(placer):
    data = {}
    for param, value in vars(placer).items():
        data[param] = value
    return data


########################################################################################################################
def placer_from_data(data):
    placer = Placer(**data)
    return placer


########################################################################################################################
def get_scene_placer(placer):
    if not pm.objExists(placer.scene_name):
        print(f"Placer: '{placer.scene_name}' not found in scene")
        return False
    return pm.PyNode(placer.scene_name)


########################################################################################################################
def color_placer(placer, color=None):
    if not color:
        color = color_code[placer.side]
    gen.set_color(get_scene_placer(placer), color)


########################################################################################################################
def mirror_placer(placer):
    scene_placer = get_scene_placer(placer)
    opposite_scene_placer = get_opposite_scene_placer(scene_placer)
    # ...Mirror position
    pm.setAttr(f'{opposite_scene_placer}.tx', pm.getAttr(f'{scene_placer}.tx') * -1)
    [pm.setAttr(f'{opposite_scene_placer}.{a}', pm.getAttr(f'{scene_placer}.{a}')) for a in ('ty', 'tz')]
    # ...Match handle size
    pm.setAttr(f'{opposite_scene_placer}.Size', pm.getAttr(f'{scene_placer}.Size'))


########################################################################################################################
def get_opposite_scene_placer(scene_placer):
    sided_prefixes = {'L_': 'R_', 'R_': 'L_'}
    this_prefix = None
    opposite_scene_placer = None
    for prefix in sided_prefixes.keys():
        if str(scene_placer).startswith(prefix):
            this_prefix = prefix
    if this_prefix:
        opposite_scene_placer = pm.PyNode(str(scene_placer).replace(this_prefix, sided_prefixes[this_prefix]))
    return opposite_scene_placer
