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

import Snowman3.utilities.node_utils as nodes
importlib.reload(nodes)

import Snowman3.riggers.utilities.placer_utils as placer_utils
importlib.reload(placer_utils)
Placer = placer_utils.Placer
PlacerCreator = placer_utils.PlacerCreator

import Snowman3.riggers.utilities.control_utils as control_utils
importlib.reload(control_utils)
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


    def get_digit_name(self, number, digit_count, digit_type):
        if digit_type == 'finger':
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
        elif digit_type == 'thumb':
            if digit_count < 2:
                return 'Thumb'
            else:
                return f'Thumb{number}'



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
                part_name=self.part_name,
                position=[0, 0, 0],
                size=size,
                vector_handle_positions=self.proportionalize_vector_handle_positions([[1, 0, 0], [0, 1, 0]], size),
                orientation=[[1, 0, 0], [0, 1, 0]],
                has_vector_handles=True
            ),
            PlacerCreator(
                name='QuickPoseFingers',
                side=self.side,
                part_name=self.part_name,
                position=[wrist_length+(metacarpal_length/2), metacarpal_length, 0],
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
                    part_name=self.part_name,
                    position=[p[1], 0, z_position],
                    size=size,
                    vector_handle_positions=self.proportionalize_vector_handle_positions(vector_handle_positions, size),
                    orientation=[[1, 0, 0], [0, 0, 1]],
                    match_orienter=p[3],
                    has_vector_handles=p[2]
                )
                placers.append(placer_creator.create_placer())

        for i in range(self.finger_count):
            create_finger_placers(
                name=self.get_digit_name(i + 1, self.finger_count, 'finger'), z_position=(-finger_spacing * i) + (palm_width / 2),
                include_metacarpal=self.include_metacarpals)

        create_finger_placers(name='Thumb', z_position=((palm_width*1.6)/2), include_metacarpal=False)

        return placers



    def create_controls(self):
        ctrls = [
            self.initialize_ctrl(
                name='Wrist',
                shape='circle',
                up_direction=[1, 0, 0],
                color=self.colors[0],
                size=4,
                side=self.side
            ),
            self.initialize_ctrl(
                name='PalmFlex',
                shape='hand_bend',
                color=self.colors[0],
                size=1,
                up_direction=[0, -1, 0],
                side=self.side,
                locks={'t':[1, 1, 1], 's':[1, 1, 1]}
            ),
            self.initialize_ctrl(
                name='QuickPoseFingers',
                shape='smooth_tetrahedron',
                color=self.colors[1],
                size=1,
                side=self.side,
                locks={'t': [1, 1, 0], 'r': [0, 1, 0], 's':[1, 1, 0]}
            )
        ]
        def create_digit_ctrls(digit_name, segment_count, include_metacarpals):
            if include_metacarpals:
                ctrls.append(
                    self.initialize_ctrl(
                        name=f'{digit_name}Meta',
                        shape='cube',
                        color=self.colors[0],
                        size=0.4,
                        side=self.side
                    )
                )
            for j in range(segment_count):
                ctrls.append(
                    self.initialize_ctrl(
                        name=f'{digit_name}Seg{j+1}',
                        shape='cube',
                        color=self.colors[0],
                        size=0.55,
                        side=self.side
                    )
                )
        for i in range(self.finger_count):
            digit_name = self.get_digit_name(i+1, self.finger_count, 'finger')
            create_digit_ctrls(digit_name, self.finger_segment_count, self.include_metacarpals)
        create_digit_ctrls('Thumb', self.thumb_segment_count, False)
        return ctrls




    def get_connection_pairs(self):
        pairs = [('Wrist', 'QuickPoseFingers')]
        for i in range(self.finger_count):
            finger_name = self.get_digit_name(i + 1, self.finger_count, 'finger')
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



    def create_part_nodes_list(self):
        part_nodes = ['Wrist']
        for i in range(self.finger_count):
            digit_name = self.get_digit_name(i+1, self.finger_count, 'finger')
            if self.include_metacarpals:
                part_nodes.append(f'{digit_name}Meta')
            for j in range(self.finger_segment_count):
                part_nodes.append(f'{digit_name}Seg{j+1}')
        for i in range(self.thumb_count):
            digit_name = self.get_digit_name(i+1, self.thumb_count, 'thumb')
            for j in range(self.thumb_segment_count):
                part_nodes.append(f'{digit_name}Seg{j+1}')
        return part_nodes



    def get_vector_handle_attachments(self):
        attachments = {}

        def create_segment_tags_list(digit_number, segment_count, digit_type):
            tags = []
            finger_names = {'thumb': 'Thumb',
                            'finger': self.get_digit_name(digit_number + 1, self.finger_count, 'finger')}
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



    def bespoke_build_rig_part(self, part, rig_part_container, transform_grp, no_transform_grp, orienters, scene_ctrls):

        wrist_jnt = rig.joint(name='Wrist', radius=0.7, side=part.side, parent=scene_ctrls['Wrist'])
        wrist_buffer = gen.buffer_obj(scene_ctrls['Wrist'], parent_=transform_grp)[0]
        gen.match_pos_ori(wrist_buffer, orienters['Wrist'])

        quick_pose_buffer = gen.buffer_obj(scene_ctrls['QuickPoseFingers'], parent_=scene_ctrls['Wrist'])[0]
        gen.zero_out(quick_pose_buffer)

        gen.match_pos_ori(quick_pose_buffer, orienters['QuickPoseFingers'])
        fingers_curl_weight = -1.25
        fingers_curl_mult_node = nodes.animBlendNodeAdditiveDA(inputA=scene_ctrls['QuickPoseFingers'].rz,
                                                               weightA=fingers_curl_weight)
        fingers_fan_mult_node = nodes.addDoubleLinear(input1=scene_ctrls['QuickPoseFingers'].sz, input2=-1)
        fingers_shift_weight = -0.1
        fingers_shift_mult_node = nodes.unitConversion(input=scene_ctrls['QuickPoseFingers'].tz,
                                                       conversionFactor=fingers_shift_weight)

        if self.include_metacarpals:
            palm_flex_buffer = gen.buffer_obj(scene_ctrls['PalmFlex'], parent_=scene_ctrls['Wrist'])[0]
            gen.zero_out(palm_flex_buffer)
            last_finger_name = self.get_digit_name(self.finger_count, self.finger_count, 'finger')
            gen.match_pos_ori(palm_flex_buffer, orienters[f'{last_finger_name}Meta'])


        @dataclass
        class Finger:
            segments = []
            metacarpal = None
            index: int = None
            name: str = None

        @dataclass
        class FingerSegment:
            ctrl = None
            jnt = None
            buffer = None
            curl_buffer = None
            spread_buffer = None
            parent_segment = None
            index: int = None
            name: str = None

        def create_digit_list(digit_count, segment_count, include_metacarpals, finger_type):
            digits = []
            for a in range(digit_count):
                digit_name = self.get_digit_name(a+1, digit_count, finger_type)
                new_finger = Finger(index=a+1, name=digit_name)
                previous_segment = None
                if include_metacarpals:
                    segment_name = f'{digit_name}Meta'
                    new_finger.metacarpal = FingerSegment(index=0, name=segment_name)
                    new_finger.metacarpal.ctrl = scene_ctrls[segment_name]
                    previous_segment = new_finger.metacarpal
                segments = []
                for b in range(segment_count):
                    segment_name = f'{digit_name}Seg{b+1}'
                    new_segment = FingerSegment(index=b+1, name=segment_name)
                    if previous_segment:
                        new_segment.parent_segment = previous_segment
                    new_segment.ctrl = scene_ctrls[segment_name]
                    segments.append(new_segment)
                    previous_segment = new_segment
                new_finger.segments = segments
                digits.append(new_finger)
            return digits

        fingers = create_digit_list(self.finger_count, self.finger_segment_count, self.include_metacarpals, 'finger')
        thumbs = create_digit_list(self.thumb_count, self.thumb_segment_count, False, 'thumb')



        def install_joints(digit):
            if digit.metacarpal:
                digit.metacarpal.jnt = jnt = rig.joint(name=digit.metacarpal.name, side=part.side,
                                                       parent=digit.metacarpal.ctrl, radius=0.45)
                gen.zero_out(jnt)
                digit.metacarpal.ctrl.setParent(wrist_jnt)
            for segment in digit.segments:
                segment.jnt = jnt = rig.joint(name=segment.name, side=part.side, parent=segment.ctrl, radius=0.45)
                gen.zero_out(jnt)
                if segment.parent_segment:
                    segment.ctrl.setParent(segment.parent_segment.jnt)
                elif not digit.metacarpal:
                    segment.ctrl.setParent(wrist_jnt)


        def position_ctrls(digit):
            if digit.metacarpal:
                gen.match_pos_ori(digit.metacarpal.ctrl, orienters[digit.metacarpal.name])
            for seg in digit.segments:
                gen.match_pos_ori(seg.ctrl, orienters[seg.name])


        def install_buffer_nodes(digit):
            if digit.metacarpal:
                digit.metacarpal.buffer = gen.buffer_obj(digit.metacarpal.ctrl)[0]
            for seg in digit.segments:
                seg.buffer = gen.buffer_obj(seg.ctrl)[0]
                seg.curl_buffer = gen.buffer_obj(seg.ctrl, suffix='ROLL')[0]
                if seg.index == 1:
                    seg.spread_buffer = gen.buffer_obj(seg.ctrl, suffix='SPREAD')[0]


        def parent_finger(digit):
            finger_root_seg = digit.metacarpal if digit.metacarpal else digit.segments[0]
            finger_root_seg.buffer.setParent(wrist_jnt)


        def connect_curling(finger):
            for seg in finger.segments:
                fingers_curl_mult_node.output.connect(seg.curl_buffer.ry)


        def connect_spreading(finger):
            seg = finger.segments[0]
            max_spread_weight = 1.25
            weight = -((((max_spread_weight * 2) / (self.finger_count - 1)) * (finger.index - 1)) - max_spread_weight)
            mult_node = nodes.animBlendNodeAdditiveDA(inputA=scene_ctrls['QuickPoseFingers'].rx,
                                                      output=seg.spread_buffer.ry, weightA=weight)


        def connect_fanning(finger):
            seg = finger.segments[0]
            max_fan_weight = 50
            weight = (((max_fan_weight*2)/(self.finger_count - 1)) * (finger.index - 1)) - max_fan_weight
            mult_node = nodes.multDoubleLinear(input1=fingers_fan_mult_node.output, input2=weight,
                                               output=seg.spread_buffer.rz)


        def connect_shifting(finger):
            seg = finger.segments[0]
            fingers_shift_mult_node.output.connect(seg.curl_buffer.rz)


        def connect_palm_flexing(finger, finger_count):

            middle_index = finger_count / 2
            if (finger.index - middle_index) < 0.001:
                return False
            metacarpal_flex_weight = (1 / middle_index ** 2) * (finger.index - middle_index) ** 2
            mult_node = nodes.animBlendNodeAdditiveRotation(inputA=scene_ctrls['PalmFlex'].rotate,
                                                            weightA=metacarpal_flex_weight,
                                                            output=finger.metacarpal.ctrl.rotate)

        for digit in fingers + thumbs:
            install_joints(digit)
            position_ctrls(digit)
            install_buffer_nodes(digit)
            parent_finger(digit)

        for finger in fingers:
            connect_curling(finger)
            connect_spreading(finger)
            connect_fanning(finger)
            connect_shifting(finger)
            if self.include_metacarpals:
                connect_palm_flexing(finger, self.finger_count)

        part_nodes = {'Wrist': wrist_jnt}
        for i in range(self.finger_count):
            digit_name = self.get_digit_name(i + 1, self.finger_count, 'finger')
            if self.include_metacarpals:
                key = f'{digit_name}Meta'
                part_nodes[key] = scene_ctrls[key]
            for j in range(self.finger_segment_count):
                key = f'{digit_name}Seg{j + 1}'
                part_nodes[key] = scene_ctrls[key]
        for i in range(self.thumb_count):
            digit_name = self.get_digit_name(i + 1, self.thumb_count, 'thumb')
            for j in range(self.thumb_segment_count):
                key = f'{digit_name}Seg{j + 1}'
                part_nodes[key] = scene_ctrls[key]
        self.part_nodes = part_nodes

        return rig_part_container
