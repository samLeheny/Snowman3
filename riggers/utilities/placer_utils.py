# Title: placer_utils.py
# Author: Sam Leheny
# Contact: samleheny@live.com

# Description:


###########################
##### Import Commands #####
import importlib

import Snowman3.utilities.general_utils as gen
importlib.reload(gen)
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
        side = None,
        position = None,
        size = None,
        vector_handle_positions = None,
        orientation = None
    ):
        self.name = name
        self.side = side
        self.position = position if position else (0, 0, 0)
        self.size = size if size else 1.0
        self.vector_handle_positions = vector_handle_positions
        self.orientation = orientation
        self.has_vector_handles = True if vector_handle_positions else False



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



####################################################################################################################
def add_placer_metadata(placer, scene_placer):
    # ...Placer tag
    gen.add_attr(scene_placer, long_name="PlacerTag", attribute_type="string", keyable=0, default_value=placer.name)
    # ...Side
    side_attr_input = placer.side if placer.side else "None"
    gen.add_attr(scene_placer, long_name="Side", attribute_type="string", keyable=0, default_value=side_attr_input)
    # ...Size
    gen.add_attr(scene_placer, long_name="Size", attribute_type="float", keyable=0,
                 default_value=float(placer.size))
    # ...Vector handle positions
    gen.add_attr(scene_placer, long_name="VectorHandleData", attribute_type="string", keyable=0,
                 default_value=str(placer.vector_handle_positions))
    # ...Orientation
    gen.add_attr(scene_placer, long_name="Orientation", attribute_type="string", keyable=0,
                 default_value=str(placer.orientation))
