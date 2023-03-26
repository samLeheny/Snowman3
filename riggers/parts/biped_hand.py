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
###########################
###########################


###########################
######## Variables ########

###########################
###########################


class PlacersGetter:

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
        self.part_name = part_name
        self.side = side
        self.include_metacarpals = include_metacarpals
        self.finger_segment_count = finger_segment_count
        self.finger_jnt_count = finger_segment_count + 1
        self.thumb_segment_count = thumb_segment_count
        self.thumb_jnt_count = thumb_segment_count + 1
        self.finger_count = finger_count
        self.thumb_count = thumb_count



    def create_placers(self):
        placers = []
        placer_creator = PlacerCreator(
            name='Wrist',
            data_name='wrist',
            side=self.side,
            parent_part_name=self.part_name,
            position=(0, 0, 0),
            size=0.9,
            vector_handle_positions=[[0, 0, 5], [0, 5, 0]],
            orientation=[[0, 1, 0], [0, 0, 1]]
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

            if include_metacarpal:
                placer_x_positions.append(wrist_length)
                placer_names.append(f'{name}Meta')
            for j in range(self.finger_jnt_count):
                x_pos = wrist_length + (finger_seg_length * j)
                if include_metacarpal:
                    x_pos = x_pos + metacarpal_length
                placer_x_positions.append(x_pos)
                name_particle = f'Seg{j+1}'
                if j + 1 == self.finger_jnt_count:
                    name_particle = 'End'
                placer_names.append(f'{name}{name_particle}')

            for placer_name, placer_x_position in zip(placer_names, placer_x_positions):
                placer_creator = PlacerCreator(
                    name=placer_name,
                    data_name=placer_name,
                    side=self.side,
                    parent_part_name=self.part_name,
                    position=(placer_x_position, 0, z_position),
                    size=0.4,
                    vector_handle_positions=[[0, 0, 5], [0, 5, 0]],
                    orientation=[[0, 1, 0], [0, 0, 1]]
                )
                placers.append(placer_creator.create_placer())

        for i in range(self.finger_count):
            create_finger_placers(name=f'Finger{i+1}', z_position=(finger_spacing*i)-(palm_width/2),
                                  include_metacarpal=self.include_metacarpals)

        create_finger_placers(name=f'Thumb', z_position=((palm_width*1.6)/2), include_metacarpal=False)

        return placers



    def get_connection_pairs(self):
        return ()
