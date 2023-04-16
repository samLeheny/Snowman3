# Title: placer_utils.py
# Author: Sam Leheny
# Contact: samleheny@live.com

# Description:


###########################
##### Import Commands #####
import importlib
import pymel.core as pm
from dataclasses import dataclass
from typing import Sequence

import Snowman3.utilities.general_utils as gen
importlib.reload(gen)

import Snowman3.utilities.rig_utils as rig
importlib.reload(rig)

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


########################################################################################################################
@dataclass
class Placer:
    name: str
    side: str = None
    position: Sequence = (0, 0, 0)
    size: float = 1.0
    has_vector_handles: bool = True
    vector_handle_positions: list[list, list] = ((0, 0, 1), (0, 1, 0))
    orientation: list[list, list] = ((0, 0, 1), (0, 1, 0))
    match_orienter: str = None
    data_name: str = None
    scene_name: str = None
    parent_part_name: str = None



########################################################################################################################
class PlacerCreator:
    def __init__(
        self,
        name: str,
        parent_part_name: str,
        position: tuple,
        side: str = None,
        size: float = None,
        has_vector_handles: bool = True,
        vector_handle_positions: list = None,
        orientation: list = None,
        match_orienter: str = None,
        scene_name: str = None,
        data_name: str = None,
    ):
        self.name = name
        self.data_name = data_name if data_name else name
        self.parent_part_name = parent_part_name
        self.position = position
        self.side = side
        self.size = size if size else 1.25
        self.has_vector_handles = has_vector_handles
        self.vector_handle_positions = self.initialize_vector_handle_positions(vector_handle_positions)
        self.orientation = orientation if orientation else [[1, 0, 0], [0, 1, 0]]
        self.match_orienter = match_orienter
        self.scene_name = scene_name if scene_name else f'{gen.side_tag(side)}{parent_part_name}_{name}_{placer_tag}'


    def initialize_vector_handle_positions(self, handle_vectors):
        if not handle_vectors:
            handle_vectors = [[5, 0, 0], [0, 0, -5]]
        aim_vector, up_vector = handle_vectors
        aim_side_mult = 1
        if self.side == 'R' and aim_vector[1:] == [0, 0]:
            aim_side_mult = -1
        aim_vector = [aim_vector[i] * aim_side_mult for i in range(3)]
        return [aim_vector, up_vector]


    def create_placer(self):
        placer = Placer(
            name = self.name,
            data_name = self.data_name,
            side = self.side,
            parent_part_name = self.parent_part_name,
            position = self.flip_position() if self.side == 'R' else self.position,
            size = self.size,
            vector_handle_positions = self.vector_handle_positions,
            orientation = self.orientation,
            match_orienter = self.match_orienter,
            scene_name = self.scene_name,
            has_vector_handles = self.has_vector_handles
        )
        return placer


    def flip_position(self):
        return -self.position[0], self.position[1], self.position[2]



########################################################################################################################
class PlacerManager:
    def __init__(
        self,
        placer
    ):
        self.placer = placer


    def data_from_placer(self):
        return vars(self.placer).copy()



########################################################################################################################
class ScenePlacerManager:
    def __init__(
        self,
        placer
    ):
        self.placer = placer
        self.vector_handles = None
        self.scene_placer = None


    def create_scene_placer(self, parent=None):
        self.create_scene_obj(parent)
        self.position_scene_placer()
        self.add_scene_placer_metadata()
        self.color_scene_handle()
        self.add_attributes()
        self.lock_transforms()
        self.create_vector_handles() if self.placer.has_vector_handles else None
        self.create_orienter()
        return self.scene_placer


    def create_scene_obj(self, parent=None):
        self.scene_placer = gen.prefab_curve_construct(prefab='sphere_placer', name=self.placer.scene_name,
                                                       scale=self.placer.size)
        buffer_grp = pm.group(name=self.placer.scene_name.replace(placer_tag, 'BUFFER'), em=1, world=1)
        if parent:
            buffer_grp.setParent(parent)
            gen.zero_out(buffer_grp)
        self.scene_placer.setParent(buffer_grp)


    def position_scene_placer(self):
        self.scene_placer.translate.set(tuple(self.placer.position))


    def add_scene_placer_metadata(self):
        metadata_attrs = (
            MetaDataAttr(long_name='PlacerTag', attribute_type='string', keyable=0, default_value_attr='name'),
            MetaDataAttr(long_name='Side', attribute_type='string', keyable=0, default_value_attr='side'),
            MetaDataAttr(long_name='Size', attribute_type='string', keyable=0, default_value_attr='size'),
            MetaDataAttr(long_name='VectorHandleData', attribute_type='string', keyable=0,
                         default_value_attr='vector_handle_positions'),
            MetaDataAttr(long_name='Orientation', attribute_type='string', keyable=0, default_value_attr='orientation')
        )
        [attr.create(self.placer, self.scene_placer) for attr in metadata_attrs]


    def color_scene_handle(self, color=None):
        if not color:
            color = color_code[self.placer.side] if self.placer.side else color_code['M']
        gen.set_color(self.scene_placer, color)


    def create_vector_handles(self):
        aim_handle = VectorHandleManager(name=self.placer.name, vector='aim', side=self.placer.side,
                                         parent=self.scene_placer, placer=self.placer, size=self.placer.size * 0.4)
        up_handle = VectorHandleManager(name=self.placer.name, vector='up', side=self.placer.side,
                                        parent=self.scene_placer, placer=self.placer, size=self.placer.size * 0.4)
        for handle in (aim_handle, up_handle):
            handle.create_in_scene()
        self.vector_handles = (aim_handle, up_handle)


    def create_orienter(self):
        orienter = OrienterManager(placer=self.placer, parent=self.scene_placer)
        orienter.create_scene_orienter()
        orienter.constrain_orienter(vector_handles=self.vector_handles)


    def lock_transforms(self):
        lock_attrs = ('rotate', 'rx', 'ry', 'rz', 'scale', 'sx', 'sy', 'sz', 'visibility')
        for attr in lock_attrs:
            pm.setAttr(f'{self.scene_placer}.{attr}', keyable=0, lock=1)


    def add_attributes(self):
        gen.add_attr(obj=self.scene_placer, long_name='VectorHandles', attribute_type='bool', keyable=False,
                     channel_box=True)
        gen.add_attr(obj=self.scene_placer, long_name='Orienters', attribute_type='bool', keyable=False,
                     channel_box=True)




########################################################################################################################
class VectorHandleManager:
    def __init__(
        self,
        name: str,
        vector: str,
        position = None,
        size = None,
        side = None,
        parent = None,
        placer = None
    ):
        self.name = name
        self.scene_name = None
        self.vector = vector
        self.position = position if position else (0, 0, 0)
        self.size = size if size else 0.25
        self.side = side
        self.parent = parent
        self.placer = placer
        self.scene_handle = None
        self.vector_handles_size = 1


    def create_in_scene(self):
        self.create_scene_handle()
        self.scene_handle.setParent(self.parent) if self.parent else None
        self.set_position()
        self.create_connector_curve()


    def create_scene_handle(self):
        types = {'aim': ('AIM', 'cube', self.vector_handles_size * 0.7),
                 'up': ('UP', 'tetrahedron', self.vector_handles_size * 1.6)}
        vector_type, handle_shape, shape_scaler_factor = types[self.vector]
        self.scene_name = f'{gen.side_tag(self.placer.side)}{self.placer.parent_part_name}_{self.name}_{vector_type}'
        self.scene_handle = gen.prefab_curve_construct(prefab=handle_shape, name=self.scene_name,
                                                       scale=self.size * shape_scaler_factor)
        self.color_scene_handle()
        self.connect_attributes_to_placer()
        self.lock_transforms()


    def color_scene_handle(self, color=None):
        if not color:
            colors = {'L': color_code['L4'], 'R': color_code['R4'], 'M': color_code['M4']}
            color = colors[self.placer.side] if self.placer.side else colors['M']
        gen.set_color(self.scene_handle, color)


    def create_connector_curve(self):
        rig.connector_curve(name=f'{gen.side_tag(self.side)}{self.name}_{self.vector}', end_driver_1=self.parent,
                            end_driver_2=self.scene_handle, parent=self.scene_handle, override_display_type=1,
                            inheritsTransform=False, use_locators=False)


    def set_position(self):
        init_placement_vector = {'aim': self.placer.vector_handle_positions[0],
                                 'up': self.placer.vector_handle_positions[1]}
        self.scene_handle.translate.set(init_placement_vector[self.vector])


    def lock_transforms(self):
        lock_attrs = ('rotate', 'rx', 'ry', 'rz', 'scale', 'sx', 'sy', 'sz', 'visibility')
        for attr in lock_attrs:
            pm.setAttr(f'{self.scene_handle}.{attr}', keyable=0, lock=1)


    def connect_attributes_to_placer(self):
        pm.connectAttr(f'{self.parent}.VectorHandles', f'{self.scene_handle}.visibility')



########################################################################################################################
class OrienterManager:
    def __init__(
        self,
        placer,
        parent = None,
    ):
        self.placer = placer
        self.parent = parent
        self.scene_orienter = None


    def create_scene_orienter(self):
        self.create_scene_obj()
        self.connect_attributes_to_placer()
        self.lock_transforms()


    def create_scene_obj(self):
        self.scene_orienter = rig.orienter(name=self.get_orienter_name(), scale=self.placer.size)
        offset = gen.buffer_obj(self.scene_orienter, parent=self.parent, suffix='OFFSET')
        buffer = gen.buffer_obj(self.scene_orienter)
        gen.zero_out(offset)
        if self.placer.side == 'R':
            gen.flip_obj(offset)
            self.flip_orienter_shape()
        return self.scene_orienter


    def flip_orienter_shape(self):
        self.scene_orienter.sz.set(-1)
        pm.makeIdentity(self.scene_orienter, apply=1)


    def constrain_orienter(self, vector_handles):
        if self.placer.match_orienter:
            self.constrain_to_neighboring_orienter()
        elif vector_handles:
            self.constrain_to_vector_handles(vector_handles)


    def constrain_to_vector_handles(self, vector_handles):
        aim_handle, up_handle = [handle.scene_handle for handle in vector_handles]
        aim_vector, up_vector = self.placer.orientation
        pm.aimConstraint(aim_handle, self.scene_orienter.getParent(), worldUpType='object', worldUpObject=up_handle,
                         aimVector=aim_vector, upVector=up_vector)


    def constrain_to_neighboring_orienter(self):
        neighboring_orienter_name = \
            f'{gen.side_tag(self.placer.side)}{self.placer.parent_part_name}_{self.placer.match_orienter}_ORI'
        neighboring_orienter = pm.PyNode(neighboring_orienter_name)
        pm.orientConstraint(neighboring_orienter, self.scene_orienter.getParent())


    def lock_transforms(self):
        lock_attrs = ('translate', 'tx', 'ty', 'tz', 'scale', 'sx', 'sy', 'sz', 'visibility')
        for attr in lock_attrs:
            pm.setAttr(f'{self.scene_orienter}.{attr}', keyable=0, lock=1)


    def connect_attributes_to_placer(self):
        pm.connectAttr(f'{self.parent}.Orienters', f'{self.scene_orienter}.visibility')


    def get_orienter_name(self):
        return f'{gen.side_tag(self.placer.side)}{self.placer.parent_part_name}_{self.placer.name}_ORI'


    def get_orienter(self):
        if not pm.objExists(self.get_orienter_name()):
            return None
        return pm.PyNode(self.get_orienter_name())
