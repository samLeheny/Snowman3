# Title: part_utils.py
# Author: Sam Leheny
# Contact: samleheny@live.com

# Description:


###########################
##### Import Commands #####
import importlib
from dataclasses import dataclass, field
import pymel.core as pm
from typing import Sequence

import Snowman3.utilities.general_utils as gen
importlib.reload(gen)

import Snowman3.utilities.rig_utils as rig
importlib.reload(rig)

import Snowman3.riggers.utilities.placer_utils as placer_utils
importlib.reload(placer_utils)
Placer = placer_utils.Placer
PlacerManager = placer_utils.PlacerManager
ScenePlacerManager = placer_utils.ScenePlacerManager

import Snowman3.riggers.utilities.control_utils as control_utils
importlib.reload(control_utils)
Control = control_utils.Control
ControlManager = control_utils.ControlManager

import Snowman3.dictionaries.colorCode as color_code
importlib.reload(color_code)

import Snowman3.riggers.utilities.metadata_utils as metadata_utils
importlib.reload(metadata_utils)
MetaDataAttr = metadata_utils.MetaDataAttr
###########################
###########################


###########################
######## Variables ########
part_tag = 'PART'
color_code = color_code.sided_ctrl_color
###########################
###########################



########################################################################################################################
@dataclass
class Part:
    name: str
    side: str = None
    handle_size: float = 1.2
    position: tuple = (0, 0, 0)
    rotation: tuple = (0, 0, 0)
    scale: float = 1,
    placers: dict = field(default_factory=dict)
    controls: dict = field(default_factory=dict)
    data_name: str = None
    scene_name: str = None
    prefab_key: str = None
    connectors: Sequence = field(default_factory=list)
    vector_handle_attachments: dict = field(default_factory=dict)
    construction_inputs: dict = field(default_factory=dict)



########################################################################################################################
class PartManager:
    def __init__(
        self,
        part
    ):
        self.part = part

    def data_from_part(self):
        data = vars(self.part).copy()

        data['placers'] = {}
        for key, placer in self.part.placers.items():
            manager = PlacerManager(placer)
            data['placers'][key] = manager.data_from_placer()

        data['controls'] = {}
        for key, control in self.part.controls.items():
            manager = ControlManager(control)
            data['controls'][key] = manager.data_from_control()

        return data


    def create_placers_from_data(self, placers_data=None):
        if not placers_data:
            placers_data = self.part.placers
        for key, data in placers_data.items():
            self.part.placers[key] = Placer(**data)


    def create_controls_from_data(self, controls_data=None):
        if not controls_data:
            controls_data = self.part.controls
        for key, data in controls_data.items():
            self.part.controls[key] = Control(**data)



########################################################################################################################
class ScenePartManager:
    def __init__(
        self,
        part
    ):
        self.part = part
        self.scene_part = None


    def create_scene_part(self):
        self.create_part_handle()
        self.position_part(self.scene_part)
        self.add_part_metadata()
        self.populate_scene_part(self.scene_part)
        self.create_placer_connectors()
        self.attach_all_vector_handles()
        return self.scene_part


    def create_part_handle(self):
        self.scene_part = gen.prefab_curve_construct(prefab='cube', name=self.part.scene_name,
                                                     scale=self.part.handle_size)
        self.color_part_handle()
        self.lock_transforms()
        self.add_attributes()


    def color_part_handle(self, color=None):
        if not color:
            if not self.part.side:
                color = color_code['M']
            else:
                color = color_code[self.part.side]
        gen.set_color(self.scene_part, color)


    def position_part(self, handle):
        handle.translate.set(tuple(self.part.position))
        handle.rotate.set(tuple(self.part.rotation))
        handle.scale.set(self.part.scale, self.part.scale, self.part.scale)


    def add_part_metadata(self):
        metadata_attrs = (
            MetaDataAttr(long_name='PartTag', attribute_type='string', keyable=0, default_value_attr='name'),
            MetaDataAttr(long_name='Side', attribute_type='string', keyable=0, default_value_attr='side'),
            MetaDataAttr(long_name='HandleSize', attribute_type='float', keyable=0, default_value_attr='handle_size')
        )
        [attr.create(self.part, self.scene_part) for attr in metadata_attrs]
        pm.setAttr(f'{self.scene_part}.HandleSize', channelBox=1)
        pm.setAttr(f'{self.scene_part}.HandleSize', self.scene_part.sx.get())
        for a in ('sx', 'sy', 'sz'):
            pm.connectAttr(f'{self.scene_part}.HandleSize', f'{self.scene_part}.{a}')
            pm.setAttr(f'{self.scene_part}.{a}', keyable=0)


    def populate_scene_part(self, placers_parent=None):
        if not self.part.placers:
            return False
        for placer in self.part.placers.values():
            placer_manager = ScenePlacerManager(placer)
            placer_manager.create_scene_placer(parent=placers_parent)
            self.connect_placer_attributes(placer_manager.scene_placer)


    def create_placer_connectors(self):
        connectors_grp = pm.group(name='connector_curves', empty=1, parent=self.scene_part)
        for pair in self.part.connectors:
            source_scene_placer = pm.PyNode(self.part.placers[pair[0]].scene_name)
            target_scene_placer = pm.PyNode(self.part.placers[pair[1]].scene_name)
            connector = rig.connector_curve(name=f'{gen.side_tag(self.part.side)}{self.part.name}',
                                            end_driver_1=source_scene_placer, end_driver_2=target_scene_placer,
                                            override_display_type=2, parent=connectors_grp, inheritsTransform=False)


    def attach_all_vector_handles(self):
        attachment_sets = self.part.vector_handle_attachments
        if not attachment_sets:
            return False
        for placer_key, targets in attachment_sets.items():
            placer = self.part.placers[placer_key]
            if not placer.has_vector_handles:
                return False
            self.attach_vector_handles(placer, targets[0], 'aim')
            self.attach_vector_handles(placer, targets[1], 'up')


    def attach_vector_handles(self, placer, target_key, vector):
        if not target_key:
            return False
        target_placer = self.part.placers[target_key]
        target_scene_placer = pm.PyNode(target_placer.scene_name)
        handle_particles = {'aim': 'AIM', 'up': 'UP'}
        scene_vector_handle = pm.PyNode(
            f"{gen.side_tag(self.part.side)}{self.part.name}_{placer.name}_{handle_particles[vector]}")
        pm.pointConstraint(target_scene_placer, scene_vector_handle)


    def lock_transforms(self):
        lock_attrs = ('visibility',)
        for attr in lock_attrs:
            pm.setAttr(f'{self.scene_part}.{attr}', keyable=0, lock=1)


    def add_attributes(self):
        gen.add_attr(obj=self.scene_part, long_name='VectorHandles', attribute_type='bool', keyable=False,
                     channel_box=True)
        gen.add_attr(obj=self.scene_part, long_name='Orienters', attribute_type='bool', keyable=False,
                     channel_box=True)


    def connect_placer_attributes(self, scene_placer):
        for attr in ('VectorHandles', 'Orienters'):
            pm.connectAttr(f'{self.scene_part}.{attr}', f'{scene_placer}.{attr}')



########################################################################################################################
class PartCreator:
    def __init__(
        self,
        name: str,
        prefab_key: str,
        side: str = None,
        position: tuple[float, float, float] = (0, 0, 0),
        rotation: tuple[float, float, float] = (0, 0, 0),
        scale: float = 1,
        construction_inputs: dict = None
    ):
        self.name = name
        self.prefab_key = prefab_key
        self.side = side
        self.position = position
        self.rotation = rotation
        self.scale = scale
        self.construction_inputs = construction_inputs
        self.part_constructor = self.construct_part_constructor()


    def construct_part_constructor(self):
        dir_string = f"Snowman3.riggers.parts.{self.prefab_key}"
        getter = importlib.import_module(dir_string)
        importlib.reload(getter)
        BespokePartConstructor = getter.BespokePartConstructor
        args = self.construction_inputs if self.construction_inputs else {}
        for key, value in (('part_name', self.name), ('side', self.side)):
            args[key] = value
        part_constructor = BespokePartConstructor(**args)
        return part_constructor


    def get_placers(self):
        placers_dict = {}
        for placer in self.part_constructor.create_placers():
            placers_dict[placer.data_name] = placer
        return placers_dict


    def get_controls(self):
        ctrls_dict = {}
        for ctrl in self.part_constructor.create_controls():
            ctrls_dict[ctrl.data_name] = ctrl
        return ctrls_dict


    def create_part(self):
        position = self.position
        rotation = self.rotation
        scale = self.scale
        scene_name = f'{gen.side_tag(self.side)}{self.name}_{part_tag}'
        connectors = self.part_constructor.get_connection_pairs()
        vector_handle_attachments = self.part_constructor.get_vector_handle_attachments()
        part = Part(name = self.name,
                    prefab_key = self.prefab_key,
                    side = self.side,
                    position = position,
                    rotation = rotation,
                    scale = scale,
                    handle_size = 1.0,
                    data_name = f'{gen.side_tag(self.side)}{self.name}',
                    scene_name = scene_name,
                    placers = self.get_placers(),
                    controls = self.get_controls(),
                    connectors = connectors,
                    vector_handle_attachments=vector_handle_attachments,
                    construction_inputs = self.construction_inputs)
        return part
