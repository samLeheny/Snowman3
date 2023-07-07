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
SceneControlManager = control_utils.SceneControlManager

import Snowman3.riggers.utilities.class_LimbRig as class_LimbRig
importlib.reload(class_LimbRig)
LimbRig = class_LimbRig.LimbRig
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
        limb_type: str = 'plantigrade_doubleKnee'
    ):
        super().__init__(part_name, side)
        self.limb_type = limb_type



    def create_placers(self):
        data_packs = [
            ['HandFollowSpace', [6, 9.5, 0], [[1, 0, 0], [0, 0, -1]], [[1, 0, 0], [0, 0, 1]], 0.8, False, None, False,
                None],
            ['Upperarm', [0, 0, 0], [[1, 0, 0], [0, 0, -1]], [[1, 0, 0], [0, 0, -1]], 1.25, True, None, False, None],
            ['ForearmEnd', [52.64, 0, 0], [[1, 0, 0], [0, 1, 0]], [[1, 0, 0], [0, 1, 0]], 1.25, True, None, False,
                None],
            ['WristEnd', [59, 0, 0], [[1, 0, 0], [0, 1, 0]], [[1, 0, 0], [0, 1, 0]], 0.7, False, 'ForearmEnd', False,
                None],
            ['IkElbow', [26.94, 0, -35], [[1, 0, 0], [0, 1, 0]], [[1, 0, 0], [0, 0, 1]], 1.25, False, None, True,
                ('Upperarm', 'ForearmEnd', 'Forearm')]
        ]
        forearm_position = [26.94, 0, -2.97]
        forearm_index = 2
        if self.limb_type == 'plantigrade':
            pass
        elif self.limb_type == 'plantigrade_doubleKnee':
            forearm_position = [29.94, 0, -2.97]
            forearm_index = 3
            data_packs.insert(2, ['Elbow', [23.94, 0, -2.97], [[1, 0, 0], [0, 0, -1]], [[1, 0, 0], [0, 0, -1]], 1.25,
                                  True, None, False, None])
        data_packs.insert(forearm_index, ['Forearm', forearm_position, [[1, 0, 0], [0, 0, -1]], [[1, 0, 0], [0, 0, -1]],
                                          1.25, True, None, False, None])
        placers = []
        for p in data_packs:
            placer_creator = PlacerCreator(
                name=p[0],
                side=self.side,
                part_name=self.part_name,
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
        ctrls = [
            self.initialize_ctrl(
                name='FkUpperarm',
                shape='body_section_tube',
                color=self.colors[0],
                size=[lengths['FkUpperarm'], 6.5, 6.5],
                up_direction = [1, 0, 0],
                forward_direction = [0, 0, 1],
                shape_offset=[lengths['FkUpperarm']/2, 0, 0],
                side=self.side
            ),
            self.initialize_ctrl(
                name='FkForearm',
                shape='body_section_tube',
                color=self.colors[0],
                size=[lengths['FkForearm'], 6.5, 6.5],
                up_direction = [1, 0, 0],
                forward_direction = [0, 0, 1],
                shape_offset=[lengths['FkForearm']/2, 0, 0],
                side=self.side
            ),
            self.initialize_ctrl(
                name='FkHand',
                shape='body_section_tube',
                color=self.colors[0],
                size=[lengths['FkHand'], 4, 8],
                up_direction = [1, 0, 0],
                forward_direction = [0, 0, 1],
                shape_offset=[lengths['FkHand']/2, 0, 0],
                side=self.side
            ),
            self.initialize_ctrl(
                name='IkHand',
                shape='cylinder',
                color=self.colors[0],
                size=[0.7, 7, 7],
                up_direction = [1, 0, 0],
                forward_direction = [0, 0, 1],
                side=self.side
            ),
            self.initialize_ctrl(
                name='IkElbow',
                shape='sphere',
                color=self.colors[0],
                size=[2, 2, 2],
                side=self.side,
                locks={'r':[1, 1, 1], 's':[1, 1, 1]}
            ),
            self.initialize_ctrl(
                name='Shoulder',
                shape='tag_hexagon',
                color=self.colors[0],
                size=[6, 6, 6],
                up_direction = [0, 1, 0],
                forward_direction = [0, 0, 1],
                side=self.side
            ),
            self.initialize_ctrl(
                name='IkHandFollow',
                shape='tetrahedron',
                color=self.colors[1],
                size=[1.5, 1.5, 1.5],
                side=self.side
            ),
            self.initialize_ctrl(
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
                ctrls.append(
                    self.initialize_ctrl(
                        name=f'{limb_segment}Bend{name_tag}',
                        shape='circle',
                        color=self.colors[1],
                        up_direction=[1, 0, 0],
                        size=3.5,
                        side=self.side
                    )
                )
            for i in range(5):
                ctrls.append(
                    self.initialize_ctrl(
                        name=f'{limb_segment}Tweak{i+1}',
                        shape='square',
                        color=self.colors[2],
                        up_direction=[1, 0, 0],
                        size=2,
                        side=self.side
                    )
                )
        return ctrls



    def get_connection_pairs(self):
        pairs = [
            ('ForearmEnd', 'Forearm'),
            ('WristEnd', 'ForearmEnd'),
            ('IkElbow', 'Forearm'),
            ('Upperarm', 'HandFollowSpace')
        ]
        if self.limb_type == 'plantigrade':
            pairs.append(('Forearm', 'Upperarm'))
        elif self.limb_type == 'plantigrade_doubleKnee':
            [pairs.append(new_pair) for new_pair in (('Elbow', 'Upperarm'), ('Forearm', 'Elbow'))]
        return pairs



    def create_part_nodes_list(self):
        part_nodes = ['Upperarm', 'Forearm', 'Wrist', 'WristEnd', 'IkPoleVector']
        if self.limb_type == 'plantigrade_doubleKnee':
            part_nodes.insert(1, 'Elbow')
        return part_nodes



    def get_vector_handle_attachments(self):
        attachments = {'Forearm': ['ForearmEnd', 'IkElbow'],
                       'ForearmEnd': ['WristEnd', None]}
        if self.limb_type == 'plantigrade':
            attachments['Upperarm'] = ['Forearm', 'IkElbow']
        elif self.limb_type == 'plantigrade_doubleKnee':
            attachments['Upperarm'] = ['Elbow', 'IkElbow']
            attachments['Elbow'] = ['Forearm', 'IkElbow']
        return attachments



    def bespoke_build_rig_part(self, part, rig_part_container, transform_grp, no_transform_grp, orienters, scene_ctrls):

        limb_rig = LimbRig(
            limb_name=part.name,
            side=part.side,
            prefab=self.limb_type,
            segment_names=self.get_segment_names(),
            socket_name='Shoulder',
            pv_name='Elbow',
            orienters=[orienters[p] for p in self.get_orienter_keys()],
            pv_position=pm.xform(orienters['IkElbow'], q=1, worldSpace=1, rotatePivot=1),
            tweak_scale_factor_node=rig_part_container
        )

        self.connect_limb_default_world_length(limb_rig, rig_part_container)
        self.conform_pv_ctrl_orientation(limb_rig.ctrls['ik_pv'], orienters['IkElbow'])
        # ...Move contents of limb rig into biped_arm rig module's groups
        [child.setParent(transform_grp) for child in limb_rig.grps['transform'].getChildren()]
        [child.setParent(no_transform_grp) for child in limb_rig.grps['noTransform'].getChildren()]
        pm.delete(limb_rig.grps['root'])

        self.finalize_ctrl_shapes(limb_rig, scene_ctrls)

        ik_hand_follow_ctrl_buffer = gen.buffer_obj(scene_ctrls['IkHandFollow'], parent_=transform_grp)[0]
        gen.match_pos_ori(ik_hand_follow_ctrl_buffer, orienters['HandFollowSpace'])

        self.update_part_nodes(limb_rig, scene_ctrls)

        return rig_part_container



    def get_segment_names(self):
        segment_names = ['Upperarm', 'Forearm', 'Wrist']
        if self.limb_type == 'plantigrade_doubleKnee':
            segment_names.insert(1, 'Elbow')
        return segment_names



    def get_orienter_keys(self):
        orienter_keys = ['Upperarm', 'Forearm', 'ForearmEnd', 'WristEnd']
        if self.limb_type == 'plantigrade_doubleKnee':
            orienter_keys.insert(1, 'Elbow')
        return orienter_keys



    def connect_limb_default_world_length(self, limb_rig, rig_part_container):
        limb_len_sum_input_plugs = pm.listConnections(limb_rig.total_limb_len_sum.output, s=0, d=1, plugs=1)
        rig_part_world_scale_matrix = nodes.decomposeMatrix(inputMatrix=rig_part_container.worldMatrix)
        part_scale_mult = nodes.multDoubleLinear(input1=limb_rig.total_limb_len_sum.output,
                                                 input2=rig_part_world_scale_matrix.outputScale.outputScaleX)
        [part_scale_mult.output.connect(plug, f=1) for plug in limb_len_sum_input_plugs]



    def conform_pv_ctrl_orientation(self, ik_ctrl, ik_orienter):
        pv_ctrl_buffer = ik_ctrl.getParent()
        world_pos = pm.xform(ik_orienter, q=1, worldSpace=1, rotatePivot=1)
        pm.delete(pm.orientConstraint(ik_orienter, pv_ctrl_buffer))



    def finalize_ctrl_shapes(self, limb_rig, scene_ctrls):
        ctrl_pairs = [('FkUpperarm', limb_rig.fk_ctrls[0]),
                      ('FkForearm', limb_rig.fk_ctrls[1]),
                      ('FkHand', limb_rig.fk_ctrls[2]),
                      ('IkHand', limb_rig.ctrls['ik_extrem']),
                      ('IkElbow', limb_rig.ctrls['ik_pv']),
                      ('Shoulder', limb_rig.ctrls['socket']),
                      ('Elbow', limb_rig.pin_ctrls[0])]

        ribbon_ctrl_set_indices = (0, 1)
        ribbon_segment_names = ('Upperarm', 'Forearm')
        ribbon_segment_indices = (0, 1)
        if self.limb_type == 'plantigrade_doubleKnee':
            ribbon_segment_indices = (0, 2)

        for i, limb_segment, tweak_i in zip(ribbon_segment_indices, ribbon_segment_names, ribbon_ctrl_set_indices):
            for j, name_tag in enumerate(('Start', 'Mid', 'End')):
                ctrl_pairs.append( (f'{limb_segment}Bend{name_tag}',
                                    limb_rig.segments[i].bend_ctrls[j]) )
            for j, ctrl_list in enumerate(limb_rig.tweak_ctrls[0]):
                ctrl_pairs.append( (f'{limb_segment}Tweak{j + 1}',
                                    limb_rig.tweak_ctrls[tweak_i][j]) )

        for ctrl_str, limb_setup_ctrl in ctrl_pairs:
            scene_ctrls[ctrl_str] = self.migrate_control_to_new_node(scene_ctrls[ctrl_str], limb_setup_ctrl)



    def update_part_nodes(self, limb_rig, scene_ctrls):
        pairings = [('Upperarm', limb_rig.blend_jnts[0]),
                    ('Wrist', limb_rig.blend_jnts[-2]),
                    ('WristEnd', limb_rig.blend_jnts[-1]),
                    ('IkPoleVector', scene_ctrls['IkElbow'])]
        if self.limb_type == 'plantigrade_doubleKnee':
            pairings.append(('Elbow', limb_rig.blend_jnts[1]))
            pairings.append(('Forearm', limb_rig.blend_jnts[2]))
        else:
            pairings.append(('Forearm', limb_rig.blend_jnts[1]))
        for key, node in pairings:
            self.part_nodes[key] = node.nodeName()
