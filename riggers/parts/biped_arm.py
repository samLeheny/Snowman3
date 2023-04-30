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

import Snowman3.utilities.node_utils as nodes
importlib.reload(nodes)

import Snowman3.riggers.utilities.placer_utils as placer_utils
importlib.reload(placer_utils)
Placer = placer_utils.Placer
PlacerCreator = placer_utils.PlacerCreator

import Snowman3.riggers.parts.class_PartConstructor as class_PartConstructor
importlib.reload(class_PartConstructor)
PartConstructor = class_PartConstructor.PartConstructor

import Snowman3.riggers.utilities.control_utils as control_utils
importlib.reload(control_utils)
ControlCreator = control_utils.ControlCreator
SceneControlManager = control_utils.SceneControlManager

import Snowman3.dictionaries.colorCode as color_code
importlib.reload(color_code)

import Snowman3.riggers.utilities.class_LimbRig as class_LimbRig
importlib.reload(class_LimbRig)
LimbRig = class_LimbRig.LimbRig
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
        data_packs = [
            ['HandFollowSpace', (6, 9.5, 0), [[1, 0, 0], [0, 0, -1]], [[1, 0, 0], [0, 0, 1]], 0.8, False, None, False,
                None],
            ['Upperarm', (0, 0, 0), [[1, 0, 0], [0, 0, -1]], [[1, 0, 0], [0, 0, -1]], 1.25, True, None, False, None],
            ['Forearm', (26.94, 0, -2.97), [[1, 0, 0], [0, 0, -1]], [[1, 0, 0], [0, 0, -1]], 1.25, True, None, False,
                None],
            ['ForearmEnd', (52.64, 0, 0), [[1, 0, 0], [0, 1, 0]], [[1, 0, 0], [0, 1, 0]], 1.25, True, None, False,
                None],
            ['WristEnd', (59, 0, 0), [[1, 0, 0], [0, 1, 0]], [[1, 0, 0], [0, 1, 0]], 0.7, False, 'ForearmEnd', False,
                None],
            ['IkElbow', (26.94, 0, -35), [[1, 0, 0], [0, 1, 0]], [[1, 0, 0], [0, 0, 1]], 1.25, False, None, True,
                ('Upperarm', 'ForearmEnd', 'Forearm')]
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
                has_vector_handles=p[5],
                is_pole_vector=p[7],
                pole_vector_partners=p[8]
            )
            placers.append(placer_creator.create_placer())
        return placers



    def create_controls(self):
        lengths = {'FkUpperarm': 25,
                   'FkForearm': 25,
                   'FkHand': 6.5}
        ctrl_creators = [
            ControlCreator(
                name='FkUpperarm',
                shape="body_section_tube",
                color=self.colors[0],
                size=[lengths['FkUpperarm'], 6.5, 6.5],
                up_direction = [1, 0, 0],
                forward_direction = [0, 0, 1],
                shape_offset=[lengths['FkUpperarm']/2, 0, 0],
                side=self.side
            ),
            ControlCreator(
                name='FkForearm',
                shape="body_section_tube",
                color=self.colors[0],
                size=[lengths['FkForearm'], 6.5, 6.5],
                up_direction = [1, 0, 0],
                forward_direction = [0, 0, 1],
                shape_offset=[lengths['FkForearm']/2, 0, 0],
                side=self.side
            ),
            ControlCreator(
                name='FkHand',
                shape="body_section_tube",
                color=self.colors[0],
                size=[lengths['FkHand'], 4, 8],
                up_direction = [1, 0, 0],
                forward_direction = [0, 0, 1],
                shape_offset=[lengths['FkHand']/2, 0, 0],
                side=self.side
            ),
            ControlCreator(
                name='IkHand',
                shape="cylinder",
                color=self.colors[0],
                size=[0.7, 7, 7],
                up_direction = [1, 0, 0],
                forward_direction = [0, 0, 1],
                side=self.side
            ),
            ControlCreator(
                name='IkElbow',
                shape="sphere",
                color=self.colors[0],
                size=[2, 2, 2],
                side=self.side,
                locks={'r':[1, 1, 1], 's':[1, 1, 1]}
            ),
            ControlCreator(
                name='Shoulder',
                shape='tag_hexagon',
                color=self.colors[0],
                size=[6, 6, 6],
                up_direction = [0, 1, 0],
                forward_direction = [0, 0, 1],
                side=self.side
            ),
            ControlCreator(
                name='IkHandFollow',
                shape='tetrahedron',
                color=self.colors[1],
                size=[1.5, 1.5, 1.5],
                side=self.side
            ),
            ControlCreator(
                name='Elbow',
                shape='circle',
                color=self.colors[0],
                up_direction = [1, 0, 0],
                size=4.5,
                side=self.side,
                locks={'s':[1, 1, 1]}
            )
        ]
        for limb_segment in ('Upperarm', 'Forearm'):
            for name_tag in ('Start', 'Mid', 'End'):
                ctrl_creators.append(
                    ControlCreator(
                        name=f'{limb_segment}Bend{name_tag}',
                        shape='circle',
                        color=self.colors[1],
                        up_direction=[1, 0, 0],
                        size=3.5,
                        side=self.side
                    )
                )
            for i in range(5):
                ctrl_creators.append(
                    ControlCreator(
                        name=f'{limb_segment}Tweak{i+1}',
                        shape='square',
                        color=self.colors[2],
                        up_direction=[1, 0, 0],
                        size=2,
                        side=self.side
                    )
                )
        controls = [creator.create_control() for creator in ctrl_creators]
        return controls


    def get_connection_pairs(self):
        return (
            ('Forearm', 'Upperarm'),
            ('ForearmEnd', 'Forearm'),
            ('WristEnd', 'ForearmEnd'),
            ('IkElbow', 'Forearm'),
            ('Upperarm', 'HandFollowSpace')
        )


    def create_part_nodes_list(self):
        part_nodes = []
        for name in ('Upperarm', 'Forearm', 'Wrist', 'WristEnd', 'IkPoleVector'):
            part_nodes.append(name)
        return part_nodes



    def get_vector_handle_attachments(self):
        return{
            'Upperarm': ['Forearm', 'IkElbow'],
            'Forearm': ['ForearmEnd', 'IkElbow'],
            'ForearmEnd': ['WristEnd', None]
        }




    def bespoke_build_rig_part(self, part, rig_part_container, transform_grp, no_transform_grp, orienters, scene_ctrls):

        limb_rig = LimbRig(
            limb_name=part.name,
            side=part.side,
            prefab='plantigrade',
            segment_names=['Upperarm', 'Forearm', 'Wrist'],
            socket_name='Shoulder',
            pv_name='Elbow',
            orienters=[orienters[p] for p in ('Upperarm', 'Forearm', 'ForearmEnd', 'WristEnd')],
            pv_position=pm.xform(orienters['IkElbow'], q=1, worldSpace=1, rotatePivot=1),
            tweak_scale_factor_node=rig_part_container
        )

        limb_len_sum_outputs = pm.listConnections(limb_rig.total_limb_len_sum.output, s=0, d=1, plugs=1)
        world_scale_matrix = nodes.decomposeMatrix(inputMatrix=rig_part_container.worldMatrix)
        part_scale_mult = nodes.multDoubleLinear(input1=limb_rig.total_limb_len_sum.output,
                                                 input2=world_scale_matrix.outputScale.outputScaleX)
        [part_scale_mult.output.connect(plug, f=1) for plug in limb_len_sum_outputs]

        # ...Conform LimbRig's PV ctrl orientation to that of PV orienter
        pv_ctrl_buffer = limb_rig.ctrls['ik_pv'].getParent()
        world_pos = pm.xform(orienters['IkElbow'], q=1, worldSpace=1, rotatePivot=1)
        pm.delete(pm.orientConstraint(orienters['IkElbow'], pv_ctrl_buffer))

        # ...Move contents of limb rig into biped_arm rig module's groups
        [child.setParent(transform_grp) for child in limb_rig.grps['transform'].getChildren()]
        [child.setParent(no_transform_grp) for child in limb_rig.grps['noTransform'].getChildren()]


        pm.delete(limb_rig.grps['root'])

        ctrl_pairs = [('FkUpperarm', limb_rig.fk_ctrls[0]),
                      ('FkForearm', limb_rig.fk_ctrls[1]),
                      ('FkHand', limb_rig.fk_ctrls[2]),
                      ('IkHand', limb_rig.ctrls['ik_extrem']),
                      ('IkElbow', limb_rig.ctrls['ik_pv']),
                      ('Shoulder', limb_rig.ctrls['socket']),
                      ('Elbow', limb_rig.pin_ctrls[0])]
        for i, limb_segment in enumerate(('Upperarm', 'Forearm')):
            for j, name_tag in enumerate(('Start', 'Mid', 'End')):
                ctrl_pairs.append((f'{limb_segment}Bend{name_tag}', limb_rig.segments[i].bend_ctrls[j]))
            for j, ctrl_list in enumerate(limb_rig.tweak_ctrls[0]):
                ctrl_pairs.append((f'{limb_segment}Tweak{j+1}', limb_rig.tweak_ctrls[i][j]))

        for ctrl_str, limb_setup_ctrl in ctrl_pairs:
            scene_ctrls[ctrl_str] = self.migrate_control_to_new_node(scene_ctrls[ctrl_str], limb_setup_ctrl)

        ik_hand_follow_ctrl_buffer = gen.buffer_obj(scene_ctrls['IkHandFollow'], parent=transform_grp)
        gen.match_pos_ori(ik_hand_follow_ctrl_buffer, orienters['HandFollowSpace'])

        for key, node in (('Upperarm', limb_rig.blend_jnts[0]),
                          ('Forearm', limb_rig.blend_jnts[1]),
                          ('Wrist', limb_rig.blend_jnts[-2]),
                          ('WristEnd', limb_rig.blend_jnts[-1]),
                          ('IkPoleVector', scene_ctrls['IkElbow'])):
            self.part_nodes[key] = node.nodeName()

        return rig_part_container
