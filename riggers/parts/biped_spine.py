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
        ctrl_creators = []
        ik_ctrl_creators = [
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
        ctrl_creators += ik_ctrl_creators
        fk_ctrl_creators = [
            ControlCreator(
                name='FkSpine1',
                shape='directional_circle',
                color=color_code['M2'],
                size=12,
            ),
            ControlCreator(
                name='FkSpine2',
                shape='directional_circle',
                color=color_code['M2'],
                size=12,
            ),
            ControlCreator(
                name='FkSpine3',
                shape='directional_circle',
                color=color_code['M2'],
                size=12,
            )
        ]
        ctrl_creators += fk_ctrl_creators
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



    def find_mid_value(self, count):
        even_count = False
        if count % 2 == 0:
            even_count = True
        if even_count:
            return int(count / 2), int((count / 2) + 1)
        else:
            return int(((count - 1) / 2) + 1)



    def build_rig_part(self, part):
        segment_count = part.construction_inputs['segment_count']
        rig_part_container, transform_grp, no_transform_grp = self.create_rig_part_grps(part)

        scene_ctrl_managers = {}
        for ctrl in part.controls.values():
            scene_ctrl_managers[ctrl.name] = SceneControlManager(ctrl)

        scene_ctrls = {}
        for key, manager in scene_ctrl_managers.items():
            scene_ctrls[key] = manager.create_scene_control()

        for ctrl in scene_ctrls.values():
            ctrl.setParent(transform_grp)

        def snap_ctrl_to_orienter(ctrl_key, orienter_key):
            orienter_manager = OrienterManager(part.placers[orienter_key])
            orienter = orienter_manager.get_orienter()
            pm.matchTransform(scene_ctrls[ctrl_key], orienter)
        snap_ctrl_to_orienter('IkPelvis', f'Spine{1}')
        snap_ctrl_to_orienter('IkChest', f'Spine{segment_count + 1}')
        spine_mid_num = self.find_mid_value(self.jnt_count)
        if isinstance(spine_mid_num, int):
            snap_ctrl_to_orienter('IkWaist', f'Spine{spine_mid_num}')
        else:
            spine_mid_num_pair = spine_mid_num
            orienter_managers = [OrienterManager(part.placers[f'Spine{str(num)}']) for num in spine_mid_num_pair]
            orienters = [manager.get_orienter() for manager in orienter_managers]
            pm.delete(pm.parentConstraint(orienters[0], orienters[1], scene_ctrls['IkWaist']))

        orienters = []
        for i in range(7):
            key = f'Spine{i+1}'
            orienter_manager = OrienterManager(part.placers[key])
            orienters.append(orienter_manager.get_orienter())
        segment_lengths = [gen.distance_between(orienters[i], orienters[i+1]) for i in range(len(orienters)-1)]
        total_spine_length = sum(segment_lengths)
        top_fk_ctrl_position = 0.855
        fk_ctrl_count = 3
        fk_ctrl_placement_mults = [(top_fk_ctrl_position/fk_ctrl_count)*i for i in range(1, (fk_ctrl_count+1))]
        fk_ctrl_placement = [total_spine_length * mult for mult in fk_ctrl_placement_mults]
        spine_length_increments = []
        for i, length in enumerate(segment_lengths):
            if i == 0:
                spine_length_increments.append(length)
            else:
                spine_length_increments.append(spine_length_increments[i-1] + length)
        pairs = []
        pair_values = []
        for placement in fk_ctrl_placement:
            for i, increment in enumerate(spine_length_increments):
                if increment > placement:
                    pairs.append((i-1, i))
                    pair_values.append((spine_length_increments[i-1], increment))
                    break
        print(fk_ctrl_placement)
        #print(spine_length_increments)
        #print(pairs)
        print(pair_values)

        return rig_part_container
