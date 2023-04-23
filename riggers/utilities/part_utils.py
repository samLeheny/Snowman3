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

import Snowman3.utilities.attribute_utils as attr_utils
importlib.reload(attr_utils)

import Snowman3.utilities.rig_utils as rig
importlib.reload(rig)

import Snowman3.utilities.node_utils as nodes
importlib.reload(nodes)

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
    handle_size: float = 1.6
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
        self.part_handle = None
        self.misc_grp = None
        self.no_transform_misc_grp = None
        self.transform_misc_grp = None
        self.placers_grp = None


    def create_scene_part(self):
        self.create_part_handle()
        self.position_part(self.part_handle)
        self.add_part_metadata()
        self.populate_scene_part()
        self.create_placer_connectors()
        self.attach_all_vector_handles()
        return self.part_handle


    def create_part_handle(self):
        self.part_handle = gen.prefab_curve_construct(prefab='cube', name=self.part.scene_name,
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
        gen.set_color(self.part_handle, color)


    def position_part(self, handle):
        handle.translate.set(tuple(self.part.position))
        handle.rotate.set(tuple(self.part.rotation))
        handle.scale.set(self.part.scale, self.part.scale, self.part.scale)


    def add_part_metadata(self):
        metadata_attrs = (
            MetaDataAttr(long_name='PartTag', attribute_type='string', keyable=0, default_value_attr='name'),
            MetaDataAttr(long_name='Side', attribute_type='string', keyable=0, default_value_attr='side'),
            MetaDataAttr(long_name='HandleSize', attribute_type='float', keyable=1, default_value_attr='handle_size')
        )
        [attr.create(self.part, self.part_handle) for attr in metadata_attrs]
        pm.setAttr(f'{self.part_handle}.HandleSize', channelBox=1)
        pm.setAttr(f'{self.part_handle}.HandleSize', self.part_handle.sx.get())
        for a in ('sx', 'sy', 'sz'):
            pm.connectAttr(f'{self.part_handle}.HandleSize', f'{self.part_handle}.{a}')
            pm.setAttr(f'{self.part_handle}.{a}', keyable=0)


    def populate_scene_part(self):
        self.add_misc_grp()
        self.add_placers_grp()
        if not self.part.placers:
            return False
        scene_placers = {}
        for placer in self.part.placers.values():
            placer_manager = ScenePlacerManager(placer)
            scene_placers[placer.name] = placer_manager.create_scene_placer(parent=self.placers_grp)
            self.connect_placer_attributes(placer_manager.scene_placer)
        self.perform_pole_vector_setups(scene_placers)


    def add_misc_grp(self):
        grp_names = 'Misc', 'MiscTransform', 'MiscNoTransform'
        self.misc_grp = pm.group(name=grp_names[0], em=1, p=self.part_handle)
        self.misc_grp.visibility.set(0, lock=1)
        self.transform_misc_grp = pm.group(name=grp_names[1], em=1, p=self.misc_grp)
        self.no_transform_misc_grp = pm.group(name=grp_names[2], em=1, p=self.misc_grp)
        self.no_transform_misc_grp.inheritsTransform.set(0, lock=1)


    def add_placers_grp(self):
        grp_name = 'Placers'
        self.placers_grp = pm.group(name=grp_name, em=1, p=self.part_handle)


    def perform_pole_vector_setups(self, scene_placers):
        for key, placer in self.part.placers.items():
            if placer.is_pole_vector:
                self.pole_vector_setup(key, scene_placers)


    def pole_vector_setup(self, placer_key, scene_placers):
        pole_vector_placer = self.part.placers[placer_key]
        pole_vector_scene_placer = scene_placers[placer_key]
        ik_limb_nodes = [None, None, None]
        for key, scene_placer in scene_placers.items():
            for i, node in enumerate(ik_limb_nodes):
                if key == pole_vector_placer.pole_vector_partners[i]:
                    ik_limb_nodes[i] = scene_placer
        start_node, end_node, mid_node = ik_limb_nodes

        mid_limb_loc = pm.spaceLocator(
            name=f'{gen.side_tag(pole_vector_placer.side)}{pole_vector_placer.name}_MidLimb_{"LOC"}')
        constraint = pm.pointConstraint(start_node, end_node, mid_limb_loc)
        constraint_weights = pm.pointConstraint(constraint, q=1, weightAliasList=1)

        limb_segment_1_length = nodes.distanceBetween(inMatrix1=start_node.worldMatrix[0],
                                                      inMatrix2=mid_node.worldMatrix[0])
        limb_segment_2_length = nodes.distanceBetween(inMatrix1=mid_node.worldMatrix[0],
                                                      inMatrix2=end_node.worldMatrix[0])
        total_limb_distance = nodes.distanceBetween(inMatrix1=start_node.worldMatrix[0],
                                                    inMatrix2=end_node.worldMatrix[0])
        segment_length_ratio = nodes.floatMath(operation=3, floatA=limb_segment_1_length.distance,
                                               floatB=total_limb_distance.distance, outFloat=constraint_weights[1])
        reciprocal_segment_length_ratio = nodes.floatMath(operation=3, floatA=limb_segment_2_length.distance,
                                                          floatB=total_limb_distance.distance,
                                                          outFloat=constraint_weights[0])

        pm.aimConstraint(mid_node, mid_limb_loc, aimVector=(0, 0, 1), upVector=(1, 0, 0), worldUpType='object',
                         worldUpObject=end_node)

        pole_vector_joint_loc = pm.spaceLocator(
            name=f'{gen.side_tag(pole_vector_placer.side)}{pole_vector_placer.name}_PvJoint_{"LOC"}')
        pm.pointConstraint(mid_node, pole_vector_joint_loc)
        pm.orientConstraint(mid_limb_loc, pole_vector_joint_loc)

        pole_vector_position_loc = pm.spaceLocator(
            name=f'{gen.side_tag(pole_vector_placer.side)}{pole_vector_placer.name}_PvPos_{"LOC"}')
        pole_vector_position_loc.setParent(pole_vector_joint_loc)
        gen.zero_out(pole_vector_position_loc)
        pole_vector_distance = gen.distance_between(obj_1=mid_node, obj_2=pole_vector_scene_placer)
        pole_vector_position_loc.tz.set(pole_vector_distance)
        pm.pointConstraint(pole_vector_position_loc, pole_vector_scene_placer)

        attr_utils.add_attr(pole_vector_scene_placer, long_name='Distance', attribute_type='float', keyable=True,
                            channel_box=True, min_value=0.001, default_value=pole_vector_distance)
        pm.connectAttr(f'{pole_vector_scene_placer}.{"Distance"}', pole_vector_position_loc.tz)
        for attr in ('translate', 'tx', 'ty', 'tz'):
            pm.setAttr(f'{pole_vector_scene_placer}.{attr}', keyable=0)
            pm.setAttr(f'{pole_vector_scene_placer}.{attr}', lock=1)

        for node in (pole_vector_joint_loc, mid_limb_loc):
            node.setParent(self.no_transform_misc_grp)


    def create_placer_connectors(self):
        grp_name = 'ConnectorCurves'
        connectors_grp = pm.group(name=grp_name, empty=1, parent=self.part_handle)
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
            pm.setAttr(f'{self.part_handle}.{attr}', keyable=0, lock=1)


    def add_attributes(self):
        attr_utils.add_attr(obj=self.part_handle, long_name='VectorHandles', attribute_type='bool', keyable=True,
                            channel_box=True)
        attr_utils.add_attr(obj=self.part_handle, long_name='Orienters', attribute_type='bool', keyable=True,
                            channel_box=True)


    def connect_placer_attributes(self, scene_placer):
        for attr in ('VectorHandles', 'Orienters'):
            pm.connectAttr(f'{self.part_handle}.{attr}', f'{scene_placer}.{attr}')



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
        part = Part(
            name = self.name,
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
            vector_handle_attachments = vector_handle_attachments,
            construction_inputs = self.construction_inputs
        )
        return part
