# Title: placer_utils.py
# Author: Sam Leheny
# Contact: samleheny@live.com

# Description:


###########################
##### Import Commands #####
import importlib

import Snowman3.utilities.general_utils as gen
importlib.reload(gen)

import Snowman3.riggers.utilities.metadata_utils as metadata_utils
importlib.reload(metadata_utils)
MetaDataAttr = metadata_utils.MetaDataAttr
###########################
###########################


###########################
######## Variables ########
placer_tag = 'PLC'
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
    scene_placer = gen.prefab_curve_construct(prefab='sphere_placer', name=get_placer_name(placer),
                                              scale=placer.size, side=placer.side)
    scene_placer.setParent(parent) if parent else None
    position_placer(placer, scene_placer)
    add_placer_metadata(placer, scene_placer)
    return scene_placer


####################################################################################################################
def get_placer_name(placer):
    side_tag = f'{placer.side}_' if placer.side else ''
    placer_name = f'{side_tag}{placer.name}_{placer_tag}'
    return placer_name


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
def color_placer(placer, color=None):
