# Title: piston.py
# Author: Sam Leheny
# Contact: samleheny@live.com

# Description:


###########################
##### Import Commands #####
import importlib
import pymel.core as pm

import Snowman3.utilities.general_utils as gen
importlib.reload(gen)

import Snowman3.utilities.rig_utils as rig
importlib.reload(rig)

import Snowman3.rigger.utilities.placer_utils as placer_utils
importlib.reload(placer_utils)
Placer = placer_utils.Placer
PlacerCreator = placer_utils.PlacerCreator
OrienterManager = placer_utils.OrienterManager

import Snowman3.rigger.utilities.control_utils as control_utils
importlib.reload(control_utils)
SceneControlManager = control_utils.SceneControlManager

import Snowman3.rigger.parts.class_PartConstructor as class_PartConstructor
importlib.reload(class_PartConstructor)
PartConstructor = class_PartConstructor.PartConstructor

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
    ):
        super().__init__(part_name, side)



    def create_placers(self):
        size = 1
        data_packs = [ ['Start', [0, 0, 0], True, None],
                       ['End', [0, 0, size*12], False, 'Start'] ]
        placers = [
            PlacerCreator(
                name=p[0],
                side=self.side,
                part_name=self.part_name,
                position=p[1],
                size=size,
                vector_handle_positions=self.proportionalize_vector_handle_positions([[0, 0, 1], [0, 1, 0]], 1),
                orientation=[[0, 0, 1], [0, 1, 0]],
                match_orienter=p[3],
                has_vector_handles=p[2]
            ).create_placer() for p in data_packs
        ]
        return placers


    def create_controls(self):
        size = 8
        shape = 'cube'
        color = self.colors[2]
        locks = {'s': [1, 1, 1], 'v': 1}
        return [
            self.initialize_ctrl(
                name='Start',
                shape=shape,
                color=color,
                locks=locks,
                size=size
            ),
            self.initialize_ctrl(
                name='End',
                shape=shape,
                color=color,
                locks=locks,
                size=size
            )
        ]



    def get_vector_handle_attachments(self):
        return {'Start': ['End', None]}



    def create_part_nodes_list(self):
        return ['Start', 'End']



    def get_connection_pairs(self):
        return [('End', 'Start')]



    def bespoke_build_rig_part(self, part, rig_part_container, transform_grp, no_transform_grp, orienters, scene_ctrls):

        part_keys = ['Start', 'End']
        radius_ratio = 8

        # ...Ctrls
        [scene_ctrls[k].setParent(transform_grp) for k in part_keys]
        offsets = {k: gen.buffer_obj(scene_ctrls[k]) for k in part_keys}

        # ...Orienters
        orienters = {}
        for k in part_keys:
            orienter_manager = OrienterManager(part.placers[k])
            orienters[k] = orienter_manager.get_orienter()
            gen.match_pos_ori(offsets[k], orienters[k])

        piston_length = gen.distance_between( obj_1=orienters['Start'], obj_2=orienters['End'] )

        # ...Jnts
        jnt_radius = piston_length / radius_ratio
        jnts = {}
        for k in part_keys:
            jnts[k] = rig.joint(name=f'{part.name}_{k}', side=part.side, joint_type='bind', radius=jnt_radius,
                                parent=scene_ctrls[k])
            gen.zero_out(jnts[k])

        for target_node, source_node, aim_vector in ([jnts['Start'], scene_ctrls['End'], (0, 0, 1)],
                                                     [jnts['End'], scene_ctrls['Start'], (0, 0, -1)]):
            pm.aimConstraint(source_node, target_node, aimVector=aim_vector, upVector=(0, 1, 0),
                             worldUpVector=(0, 1, 0), worldUpType='objectrotation', worldUpObject=source_node)

        # ...Part nodes
        for k in part_keys:
            self.part_nodes[k] = scene_ctrls[k]

        return rig_part_container
