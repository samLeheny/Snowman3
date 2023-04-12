# Title: biped_arm.py
# Author: Sam Leheny
# Contact: samleheny@live.com

# Description:


###########################
##### Import Commands #####
import importlib
import pymel.core as pm
from dataclasses import dataclass

import Snowman3.utilities.general_utils as gen
importlib.reload(gen)

import Snowman3.utilities.rig_utils as rig
importlib.reload(rig)

import Snowman3.riggers.utilities.placer_utils as placer_utils
importlib.reload(placer_utils)
Placer = placer_utils.Placer
PlacerCreator = placer_utils.PlacerCreator

import Snowman3.riggers.utilities.control_utils as control_utils
importlib.reload(control_utils)
ControlCreator = control_utils.ControlCreator
SceneControlManager = control_utils.SceneControlManager

import Snowman3.riggers.parts.class_PartConstructor as class_PartConstructor
importlib.reload(class_PartConstructor)
PartConstructor = class_PartConstructor.PartConstructor
###########################
###########################


###########################
######## Variables ########

###########################
###########################


class BespokePartConstructor(PartConstructor):

    def __init__(
        self,
        part_name: str,
        side: str = None,
        include_metacarpals: bool = True,
        finger_segment_count: int = 3,
        thumb_segment_count: int = 3,
        finger_count: int = 4,
        thumb_count: int = 1
    ):
        super().__init__(part_name, side)
        self.include_metacarpals = include_metacarpals
        self.finger_segment_count = finger_segment_count
        self.finger_jnt_count = finger_segment_count + 1
        self.thumb_segment_count = thumb_segment_count
        self.thumb_jnt_count = thumb_segment_count + 1
        self.finger_count = finger_count
        self.thumb_count = thumb_count


    def get_digit_name(self, number, digit_count):
        finger_names = (('Index', 'Pinky'),
                        ('Index', 'Middle', 'Pinky'),
                        ('Index', 'Middle', 'Ring', 'Pinky'))
        code = None
        if 1 < self.finger_count < 5:
            code = finger_names[digit_count - 2]
        if code:
            return f'{code[number-1]}Finger'
        else:
            return f'Finger{number}'



    def create_placers(self):
        placers = []

        size = 0.9
        wrist_length = 2.5
        finger_length = 6.73
        metacarpal_length = finger_length if self.include_metacarpals else 0
        finger_seg_length = finger_length / self.finger_segment_count
        palm_width = metacarpal_length * 0.8
        finger_spacing = palm_width / (self.finger_count - 1)

        placer_creators = [
            PlacerCreator(
                name='Wrist',
                side=self.side,
                parent_part_name=self.part_name,
                position=(0, 0, 0),
                size=size,
                vector_handle_positions=self.proportionalize_vector_handle_positions([[1, 0, 0], [0, 1, 0]], size),
                orientation=[[1, 0, 0], [0, 1, 0]],
                has_vector_handles=True
            ),
            PlacerCreator(
                name='QuickPoseFingers',
                side=self.side,
                parent_part_name=self.part_name,
                position=(wrist_length+(metacarpal_length/2), metacarpal_length, 0),
                size=size*0.7,
                vector_handle_positions=self.proportionalize_vector_handle_positions([[1, 0, 0], [0, 1, 0]], size),
                orientation=[[1, 0, 0], [0, 1, 0]],
                has_vector_handles=True
            )
        ]
        placers = [creator.create_placer() for creator in placer_creators]

        def create_finger_placers(name, z_position, include_metacarpal):
            placer_x_positions = []
            placer_names = []
            has_placer_handles = []
            match_orienters = []

            vector_handle_positions = [[1, 0, 0], [0, 1, 0]]
            if name == 'Thumb':
                vector_handle_positions = [[1, 0, 0], [0, 0, 1]]
            if include_metacarpal:
                placer_names.append(f'{name}Meta')
                placer_x_positions.append(wrist_length)
                has_placer_handles.append(True)
                match_orienters.append(None)
            for j in range(self.finger_jnt_count):
                has_vector_handles_status = True
                x_pos = wrist_length + (finger_seg_length * j)
                if include_metacarpal:
                    x_pos = x_pos + metacarpal_length
                placer_x_positions.append(x_pos)
                name_particle = f'Seg{j+1}'
                match_orienter = None
                if j + 1 == self.finger_jnt_count:
                    has_vector_handles_status = False
                    name_particle = 'End'
                    match_orienter = placer_names[-1]
                placer_names.append(f'{name}{name_particle}')
                has_placer_handles.append(has_vector_handles_status)
                match_orienters.append(match_orienter)

            for p in zip(placer_names, placer_x_positions, has_placer_handles, match_orienters):
                size = 0.4
                placer_creator = PlacerCreator(
                    name=p[0],
                    side=self.side,
                    parent_part_name=self.part_name,
                    position=(p[1], 0, z_position),
                    size=size,
                    vector_handle_positions=self.proportionalize_vector_handle_positions(vector_handle_positions, size),
                    orientation=[[1, 0, 0], [0, 0, 1]],
                    match_orienter=p[3],
                    has_vector_handles=p[2]
                )
                placers.append(placer_creator.create_placer())

        for i in range(self.finger_count):
            create_finger_placers(
                name=self.get_digit_name(i + 1, self.finger_count), z_position=(-finger_spacing * i) + (palm_width / 2),
                include_metacarpal=self.include_metacarpals)

        create_finger_placers(name='Thumb', z_position=((palm_width*1.6)/2), include_metacarpal=False)

        return placers



    def create_controls(self):
        ctrl_creators = [
            ControlCreator(
                name='PalmFlex',
                shape='hand_bend',
                color=self.colors[0],
                size=1,
                up_direction=[0, -1, 0],
                side=self.side
            ),
            ControlCreator(
                name='QuickPoseFingers',
                shape='smooth_tetrahedron',
                color=self.colors[1],
                size=1,
                side=self.side
            )
        ]
        def create_digit_ctrls(digit_name, segment_count, include_metacarpals):
            if include_metacarpals:
                ctrl_creators.append(
                    ControlCreator(
                        name=f'{digit_name}Meta',
                        shape='cube',
                        color=self.colors[0],
                        size=0.4,
                        side=self.side
                    )
                )
            for j in range(segment_count):
                ctrl_creators.append(
                    ControlCreator(
                        name=f'{digit_name}Seg{j+1}',
                        shape='cube',
                        color=self.colors[0],
                        size=0.55,
                        side=self.side
                    )
                )
        for i in range(self.finger_count):
            digit_name = self.get_digit_name(i, self.finger_count)
            create_digit_ctrls(digit_name, self.finger_segment_count, self.include_metacarpals)
        create_digit_ctrls('Thumb', self.thumb_segment_count, False)
        controls = [creator.create_control() for creator in ctrl_creators]
        return controls




    def get_connection_pairs(self):
        pairs = []
        for i in range(self.finger_count):
            finger_name = self.get_digit_name(i + 1, self.finger_count)
            finger_pairs = []
            segs = [f'{finger_name}Seg{s+1}' for s in range(self.finger_segment_count)]
            segs.append(f'{finger_name}End')
            if self.include_metacarpals:
                segs.insert(0, f'{finger_name}Meta')
            for j in range(self.finger_segment_count+1):
                finger_pairs.append([segs[j], segs[j+1]])
            finger_pairs.insert(0, ['Wrist', segs[0]])
            for pair in finger_pairs:
                pairs.append(pair)

        for i in range(self.thumb_count):
            thumb_name = 'Thumb'
            thumb_pairs = []
            segs = [f"{thumb_name}{'Seg'}{s+1}" for s in range(self.thumb_segment_count)]
            segs.append(f"{thumb_name}{'End'}")
            for j in range(self.thumb_segment_count):
                thumb_pairs.append([segs[j], segs[j+1]])
            thumb_pairs.insert(0, ['Wrist', segs[0]])
            for pair in thumb_pairs:
                pairs.append(pair)

        return pairs



    def get_vector_handle_attachments(self):
        attachments = {}

        def create_segment_tags_list(digit_number, segment_count, digit_type):
            tags = []
            finger_names = {'thumb': 'Thumb',
                            'finger': self.get_digit_name(digit_number + 1, self.finger_count)}
            finger_name = finger_names[digit_type]
            if self.include_metacarpals and digit_type == 'finger':
                tags.append(f'{finger_name}Meta')
            for seg_num in range(segment_count + 1):
                seg_name_tag = f'Seg{seg_num + 1}'
                if seg_num == segment_count:
                    seg_name_tag = 'End'
                placer_key = f'{finger_name}{seg_name_tag}'
                tags.append(placer_key)
            return tags

        def process_digit(digit_number, segment_count, digit_type):
            segment_tags = create_segment_tags_list(digit_number, segment_count, digit_type)
            for i in range(len(segment_tags)-1):
                attachments[segment_tags[i]] = [segment_tags[i + 1], None]

        for f in range(self.finger_count):
            process_digit(f, self.finger_segment_count, 'finger')
        for t in range(self.thumb_count):
            process_digit(t, self.thumb_segment_count, 'thumb')

        return attachments



    def build_rig_part(self, part):
        rig_part_container, connector, transform_grp, no_transform_grp = self.create_rig_part_grps(part)
        orienters, scene_ctrls = self.get_scene_armature_nodes(part)

        pm.matchTransform(scene_ctrls['QuickPoseFingers'], orienters['QuickPoseFingers'])
        if self.include_metacarpals:
            last_finger_name = self.get_digit_name(self.finger_count, self.finger_count)
            pm.matchTransform(scene_ctrls['PalmFlex'], orienters[f'{last_finger_name}Meta'])

        fingers = []

        @dataclass
        class fingerHierarchy:
            segments = []
            metacarpal = None
            index: int = None
            name: str = None

        @dataclass
        class fingerSegment:
            ctrl = None
            jnt = None
            curl_buffer = None
            spread_buffer = None
            index: int = None
            name: str = None

        for a in range(self.finger_count):
            finger_name = self.get_digit_name(a, self.finger_count)
            new_finger = fingerHierarchy(index=a+1, name=finger_name)
            if self.include_metacarpals:
                segment_name = f'{finger_name}Meta'
                new_finger.metacarpal = fingerSegment(index=0, name=segment_name)
            for b in range(self.finger_segment_count):
                segment_name = f'{finger_name}Seg{b+1}'
                new_segment = fingerSegment(index=b+1, name=segment_name)
                new_finger.segments.append(new_segment)


        segment_joints = {}
        def install_joints(digit_name, segment_count, include_metacarpals):
            if include_metacarpals:
                jnt = rig.joint(name=f'{digit_name}Meta', side=part.side, parent=scene_ctrls[f'{digit_name}Meta'])
                segment_joints[f'{digit_name}Meta'] = jnt
                gen.zero_out(jnt)
            for s in range(segment_count):
                jnt = rig.joint(name=f'{digit_name}Seg{s+1}', side=part.side,
                                parent=scene_ctrls[f'{digit_name}Seg{s+1}'])
                segment_joints[f'{digit_name}Seg{s+1}'] = jnt
                gen.zero_out(jnt)
        for i in range(self.finger_count):
            digit_name = self.get_digit_name(i, self.finger_count)
            install_joints(digit_name, self.finger_segment_count, self.include_metacarpals)


        def position_digit_ctrls(digit_name, segment_count, include_metacarpals):
            if include_metacarpals:
                pm.matchTransform(scene_ctrls[f'{digit_name}Meta'], orienters[f'{digit_name}Meta'])
            for j in range(segment_count):
                pm.matchTransform(scene_ctrls[f'{digit_name}Seg{j+1}'], orienters[f'{digit_name}Seg{j+1}'])
        for i in range(self.finger_count):
            digit_name = self.get_digit_name(i, self.finger_count)
            position_digit_ctrls(digit_name, self.finger_segment_count, self.include_metacarpals)
        position_digit_ctrls('Thumb', self.thumb_segment_count, False)


        def digit_hierarchy(digit_name, segment_count, include_metacarpals):
            prev_seg_jnt = None
            if include_metacarpals:
                this_seg_ctrl = scene_ctrls[f'{digit_name}Meta']
                metacarpal_buffer = gen.buffer_obj(this_seg_ctrl)
                prev_seg_jnt = segment_joints[f'{digit_name}Meta']
            for j in range(segment_count):
                this_seg_ctrl = scene_ctrls[f'{digit_name}Seg{j+1}']
                curl_buffer = gen.buffer_obj(this_seg_ctrl, 'ROLL')
                curl_buffer.setParent(prev_seg_jnt) if prev_seg_jnt else None
                prev_seg_jnt = segment_joints[f'{digit_name}Seg{j+1}']
                if j == 0:
                    spread_buffer = gen.buffer_obj(this_seg_ctrl, 'SPREAD')
        for i in range(self.finger_count):
            digit_name = self.get_digit_name(i, self.finger_count)
            digit_hierarchy(digit_name, self.finger_segment_count, self.include_metacarpals)


        return rig_part_container
