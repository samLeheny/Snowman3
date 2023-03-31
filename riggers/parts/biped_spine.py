# Title: biped_arm.py
# Author: Sam Leheny
# Contact: samleheny@live.com

# Description:


###########################
##### Import Commands #####
import importlib
import pymel.core as pm

import Snowman3.utilities.general_utils as gen
importlib.reload(gen)

import Snowman3.riggers.utilities.placer_utils as placer_utils
importlib.reload(placer_utils)
Placer = placer_utils.Placer
PlacerCreator = placer_utils.PlacerCreator
OrienterManager = placer_utils.OrienterManager

import Snowman3.riggers.parts.class_PartConstructor as class_PartConstructor
importlib.reload(class_PartConstructor)
PartConstructor = class_PartConstructor.PartConstructor

import Snowman3.riggers.utilities.control_utils as control_utils
importlib.reload(control_utils)
ControlCreator = control_utils.ControlCreator
SceneControlManager = control_utils.SceneControlManager

import Snowman3.dictionaries.colorCode as color_code
importlib.reload(color_code)
###########################
###########################


###########################
######## Variables ########
color_code = color_code.sided_ctrl_color
###########################
###########################



class BespokePartConstructor(PartConstructor):

    def __init__(
        self,
        part_name: str,
        side: str = None,
        segment_count: int = 6
    ):
        super().__init__(part_name, side)
        self.segment_count = segment_count
        self.jnt_count = segment_count + 1


    def create_placers(self):
        spine_length = 42.0
        spine_seg_length = spine_length / self.segment_count
        placers = []
        for i in range(self.jnt_count):
            n = i + 1
            has_vector_handles = True
            size = 1.25
            if i == range(self.jnt_count):
                has_vector_handles = False
                size = 0.8
            placer_creator = PlacerCreator(
                name=f'Spine{str(n)}',
                side=self.side,
                parent_part_name=self.part_name,
                position=(0, spine_seg_length * i, 0),
                size=size,
                vector_handle_positions=self.proportionalize_vector_handle_positions([[0, 1, 0], [0, 0, 1]], size),
                orientation=[[0, 1, 0], [0, 0, 1]],
                has_vector_handles=has_vector_handles
            )
            placers.append(placer_creator.create_placer())
        return placers



    def create_controls(self):
        ctrl_creators = [
            ControlCreator(
                name = 'IkChest',
                shape = 'circle',
                color = color_code[self.side],
                size = 14
            ),
            ControlCreator(
                name='IkWaist',
                shape='circle',
                color=color_code[self.side],
                size=14
            ),
            ControlCreator(
                name='IkPelvis',
                shape='circle',
                color=color_code[self.side],
                size=14
            )
        ]
        controls = [creator.create_control() for creator in ctrl_creators]
        return controls



    def get_connection_pairs(self):
        pairs = []
        for i in range(self.segment_count):
            n = i + 1
            pairs.append(
                (f'Spine{str(n+1)}', f'Spine{str(n)}')
            )
        return tuple(pairs)



    def build_rig_part(self, part):
        rig_part_container, transform_grp, no_transform_grp = self.create_rig_part_grps(part)

        scene_ctrl_managers = {}
        for ctrl in part.controls.values():
            scene_ctrl_managers[ctrl.name] = SceneControlManager(ctrl)

        scene_ctrls = {}
        for key, manager in scene_ctrl_managers.items():
            scene_ctrls[key] = manager.create_scene_control()

        for ctrl in scene_ctrls.values():
            ctrl.setParent(transform_grp)

        return rig_part_container
