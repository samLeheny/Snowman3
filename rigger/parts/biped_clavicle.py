# Title: biped_clavicle.py
# Author: Sam Leheny
# Contact: samleheny@live.com

# Description:


###########################
##### Import Commands #####

import Snowman3.utilities.general_utils as gen

import Snowman3.utilities.rig_utils as rig

import Snowman3.rigger.utilities.placer_utils as placer_utils
Placer = placer_utils.Placer
PlacerCreator = placer_utils.PlacerCreator
OrienterManager = placer_utils.OrienterManager

import Snowman3.rigger.parts.class_PartConstructor as class_PartConstructor
PartConstructor = class_PartConstructor.PartConstructor

import Snowman3.rigger.utilities.control_utils as control_utils
SceneControlManager = control_utils.SceneControlManager

import Snowman3.dictionaries.nameConventions as nameConventions

import Snowman3.dictionaries.colorCode as color_code
###########################
###########################


###########################
######## Variables ########
color_code = color_code.sided_ctrl_color
nom = nameConventions.create_dict()
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
        data_packs = [
            ['Clavicle', [0, 0, 0], [[1, 0, 0], [0, 0, 1]], [[1, 0, 0], [0, 0, 1]], 1.25, True, None],
            ['ClavicleEnd', [12, 0, 0], [[1, 0, 0], [0, 0, 1]], [[1, 0, 0], [0, 0, 1]], 0.8, False, 'Clavicle'],
        ]
        return [
            PlacerCreator(
                name=p[0],
                side=self.side,
                part_name=self.part_name,
                position=p[1],
                size=p[4],
                vector_handle_positions=self.proportionalize_vector_handle_positions(p[2], p[4]),
                orientation=p[3],
                match_orienter=p[6],
                has_vector_handles=p[5]
            ).create_placer() for p in data_packs
        ]


    def create_controls(self):
        ctrls = [
            self.initialize_ctrl(
                name='Clavicle',
                shape='biped_clavicle',
                color=color_code[self.side],
                size=9,
                forward_direction=[0, 0, 1],
                up_direction=[0, 1, 0],
                shape_offset=[5.4, 0, 0],
                side=self.side
            )
        ]
        return ctrls


    def get_connection_pairs(self):
        return (
            ('ClavicleEnd', 'Clavicle'),
        )


    def create_part_nodes_list(self):
        part_nodes = []
        for name in ('Clavicle', 'ClavicleEnd'):
            part_nodes.append(name)
        return part_nodes


    def get_vector_handle_attachments(self):
        return{}



    def bespoke_build_rig_part(self, part, rig_part_container, transform_grp, no_transform_grp, orienters, scene_ctrls):

        clavicle_jnt = rig.joint(name='Clavicle', side=part.side, joint_type=nom.bindJnt, radius=1.0)
        clavicle_end_jnt = rig.joint(name='ClavicleEnd', side=part.side, joint_type=nom.bindJnt, radius=0.6)
        clavicle_end_jnt.setParent(clavicle_jnt)
        clavicle_jnt.setParent(scene_ctrls['Clavicle'])
        clavicle_ctrl_buffer = gen.buffer_obj(scene_ctrls['Clavicle'], parent_=transform_grp)
        gen.zero_out(clavicle_ctrl_buffer)
        gen.match_pos_ori(clavicle_ctrl_buffer, orienters['Clavicle'])
        gen.match_pos_ori(clavicle_end_jnt, orienters['ClavicleEnd'])

        for key, node in (('Clavicle', clavicle_jnt),
                          ('ClavicleEnd', clavicle_end_jnt)):
            self.part_nodes[key] = node.nodeName()

        return rig_part_container
