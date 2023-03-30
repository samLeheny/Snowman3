# Title: biped_arm.py
# Author: Sam Leheny
# Contact: samleheny@live.com

# Description:


###########################
##### Import Commands #####
import importlib

import Snowman3.riggers.utilities.placer_utils as placer_utils
importlib.reload(placer_utils)
Placer = placer_utils.Placer
PlacerCreator = placer_utils.PlacerCreator

import Snowman3.riggers.parts.class_PartConstructor as class_PartConstructor
importlib.reload(class_PartConstructor)
PartConstructor = class_PartConstructor.PartConstructor

import Snowman3.riggers.utilities.part_utils as part_utils
importlib.reload(part_utils)
SceneRigPartManager = part_utils.SceneRigPartManager
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
        placer_creator = PlacerCreator(
            name='Wrist',
            data_name='wrist',
            side=self.side,
            parent_part_name=self.part_name,
            position=(0, 0, 0),
            size=size,
            vector_handle_positions=self.proportionalize_vector_handle_positions([[1, 0, 0], [0, 1, 0]], size),
            orientation=[[0, 0, 1], [0, 1, 0]],
            has_vector_handles=True
        )
        placers.append(placer_creator.create_placer())

        wrist_length = 2.5
        finger_length = 6.73
        metacarpal_length = 0
        if self.include_metacarpals:
            metacarpal_length = finger_length
        finger_seg_length = finger_length / self.finger_segment_count
        palm_width = metacarpal_length * 0.8
        finger_spacing = palm_width / (self.finger_count - 1)

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
                    data_name=p[0],
                    side=self.side,
                    parent_part_name=self.part_name,
                    position=(p[1], 0, z_position),
                    size=size,
                    vector_handle_positions=self.proportionalize_vector_handle_positions(vector_handle_positions, size),
                    orientation=[[0, 0, 1], [1, 0, 0]],
                    match_orienter=p[3],
                    has_vector_handles=p[2]
                )
                placers.append(placer_creator.create_placer())

        for i in range(self.finger_count):
            create_finger_placers(
                name=self.get_digit_name(i + 1, self.finger_count), z_position=(finger_spacing * i) - (palm_width / 2),
                include_metacarpal=self.include_metacarpals)

        create_finger_placers(name='Thumb', z_position=((palm_width*1.6)/2), include_metacarpal=False)

        return placers



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
            finger_pairs.insert(0, ['wrist', segs[0]])
            for pair in finger_pairs:
                pairs.append(pair)

        for i in range(self.thumb_count):
            thumb_name = 'Thumb'
            thumb_pairs = []
            segs = [f"{thumb_name}{'Seg'}{s+1}" for s in range(self.thumb_segment_count)]
            segs.append(f"{thumb_name}{'End'}")
            for j in range(self.thumb_segment_count):
                thumb_pairs.append([segs[j], segs[j+1]])
            thumb_pairs.insert(0, ['wrist', segs[0]])
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
        rig_part_manager = SceneRigPartManager(part)
        rig_part = rig_part_manager.create_scene_rig_part()
