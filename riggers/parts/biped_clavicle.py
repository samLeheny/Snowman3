# Title: biped_clavicle.py
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

import Snowman3.dictionaries.nameConventions as nameConventions
importlib.reload(nameConventions)

import Snowman3.dictionaries.colorCode as color_code
importlib.reload(color_code)
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
            ['Clavicle', (0, 0, 0), [[1, 0, 0], [0, 0, 1]], [[1, 0, 0], [0, 0, 1]], 1.25, True, None],
            ['ClavicleEnd', (12, 0, 0), [[1, 0, 0], [0, 0, 1]], [[1, 0, 0], [0, 0, 1]], 0.8, False, 'Clavicle'],
        ]
        placers = []
        for p in data_packs:
            placer_creator = PlacerCreator(
                name=p[0],
                side=self.side,
                parent_part_name=self.part_name,
                position=p[1],
                size=p[4],
                vector_handle_positions=self.proportionalize_vector_handle_positions(p[2], p[4]),
                orientation=p[3],
                match_orienter=p[6],
                has_vector_handles=p[5]
            )
            placers.append(placer_creator.create_placer())
        return placers


    def create_controls(self):
        ctrl_creators = [
            ControlCreator(
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
        controls = [creator.create_control() for creator in ctrl_creators]
        return controls


    def get_connection_pairs(self):
        return (
            ('ClavicleEnd', 'Clavicle'),
        )


    def get_vector_handle_attachments(self):
        return{}



    def build_rig_part(self, part):
        rig_part_container, connector, transform_grp, no_transform_grp = self.create_rig_part_grps(part)
        orienters, scene_ctrls = self.get_scene_armature_nodes(part)

        clavicle_jnt = rig.joint(name='Clavicle', side=part.side, joint_type=nom.bindJnt, radius=1.0)
        clavicle_end_jnt = rig.joint(name='ClavicleEnd', side=part.side, joint_type=nom.bindJnt, radius=0.6)
        clavicle_end_jnt.setParent(clavicle_jnt)
        clavicle_jnt.setParent(scene_ctrls['Clavicle'])
        clavicle_ctrl_buffer = gen.buffer_obj(scene_ctrls['Clavicle'], parent=transform_grp)
        gen.zero_out(clavicle_ctrl_buffer)
        pm.matchTransform(clavicle_ctrl_buffer, orienters['Clavicle'])
        pm.matchTransform(clavicle_end_jnt, orienters['ClavicleEnd'])

        self.apply_all_control_transform_locks()

        pm.select(clear=1)
        return rig_part_container
