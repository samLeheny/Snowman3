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
            ['FootFollowSpace', (12, -7.5, 0), [[1, 0, 0], [0, 0, -1]], [[1, 0, 0], [0, 0, 1]], 0.8, False, None,
                False, None],
            ['Thigh', (0, 0, 0), [[0, -1, 0], [0, 0, 1]], [[1, 0, 0], [0, 0, 1]], 1.25, True, None, False, None],
            ['Shin', (0, -45, 4.57), [[0, -1, 0], [0, 0, 1]], [[1, 0, 0], [0, 0, 1]], 1.25, True, None, False, None],
            ['ShinEnd', (0, -91, 0), [[0, -1, 0], [0, 0, 1]], [[1, 0, 0], [0, 0, 1]], 1.25, True, None, False, None],
            ['AnkleEnd', (0, -101, 0), [[0, -1, 0], [0, 0, 1]], [[1, 0, 0], [0, 0, 1]], 0.7, False, 'ShinEnd', False,
                None],
            ['IkKnee', (0, -45, 40), [[0, -1, 0], [0, 0, 1]], [[1, 0, 0], [0, 1, 0]], 1.25, False, None, True,
                ('Thigh', 'ShinEnd', 'Shin')],
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
        lengths = {'FkThigh': 42,
                   'FkShin': 42,
                   'FkFoot': 6.5}
        ctrl_creators = [
            ControlCreator(
                name='FkThigh',
                shape='body_section_tube',
                color=self.colors[0],
                size=[lengths['FkThigh'], 10, 10],
                up_direction = [1, 0, 0],
                forward_direction = [0, 0, 1],
                shape_offset=[lengths['FkThigh']/2, 0, 0],
                side=self.side
            ),
            ControlCreator(
                name='FkShin',
                shape='body_section_tube',
                color=self.colors[0],
                size=[lengths['FkShin'], 10, 10],
                up_direction = [1, 0, 0],
                forward_direction = [0, 0, 1],
                shape_offset=[lengths['FkShin']/2, 0, 0],
                side=self.side
            ),
            ControlCreator(
                name='FkFoot',
                shape='biped_foot',
                color=self.colors[0],
                size=[lengths['FkFoot'], 9.5, 6.5],
                up_direction = [-1, 0, 0],
                forward_direction = [0, 0, 1],
                shape_offset=[lengths['FkFoot']/2, 0, 0],
                side=self.side
            ),
            ControlCreator(
                name='IkFoot',
                shape='cylinder',
                color=self.colors[0],
                size=[7, 0.7, 7],
                side=self.side
            ),
            ControlCreator(
                name='IkKnee',
                shape='sphere',
                color=self.colors[0],
                size=2,
                side=self.side,
                locks={'r':[1, 1, 1], 's':[1, 1, 1]}
            ),
            ControlCreator(
                name='Hip',
                shape='tag_hexagon',
                color=self.colors[0],
                size=7.5,
                up_direction = [1, 0, 0],
                forward_direction = [0, 0, 1],
                side=self.side
            ),
            ControlCreator(
                name='IkFootFollow',
                shape='tetrahedron',
                color=self.colors[1],
                size=1.5,
                side=self.side
            ),
            ControlCreator(
                name='Knee',
                shape='circle',
                color=self.colors[0],
                up_direction = [1, 0, 0],
                size=7,
                side=self.side,
                locks={'s':[1, 1, 1]}
            )
        ]
        for limb_segment in ('Thigh', 'Shin'):
            for name_tag in ('Start', 'Mid', 'End'):
                ctrl_creators.append(
                    ControlCreator(
                        name=f'{limb_segment}Bend{name_tag}',
                        shape='circle',
                        color=self.colors[1],
                        up_direction=[1, 0, 0],
                        size=4.5,
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
                        size=3,
                        side=self.side
                    )
                )
        controls = [creator.create_control() for creator in ctrl_creators]
        return controls


    def get_connection_pairs(self):
        return (
            ('Shin', 'Thigh'),
            ('ShinEnd', 'Shin'),
            ('AnkleEnd', 'ShinEnd'),
            ('IkKnee', 'Shin'),
            ('Thigh', 'FootFollowSpace')
        )


    def get_vector_handle_attachments(self):
        return {
            'Thigh': ['Shin', 'IkKnee'],
            'Shin': ['ShinEnd', 'IkKnee'],
            'ShinEnd': ['AnkleEnd', None]
        }


    def build_rig_part(self, part):
        rig_part_container, connector, transform_grp, no_transform_grp = self.create_rig_part_grps(part)
        orienters, scene_ctrls = self.get_scene_armature_nodes(part)

        limb_rig = LimbRig(
            limb_name=part.name,
            side=part.side,
            prefab='plantigrade',
            segment_names=['Thigh', 'Shin', 'Foot'],
            socket_name='Hip',
            pv_name='Knee',
            orienters=[orienters[p] for p in ('Thigh', 'Shin', 'ShinEnd', 'AnkleEnd')],
            pv_position=pm.xform(orienters['IkKnee'], q=1, worldSpace=1, rotatePivot=1),
            tweak_scale_factor_node=connector
        )

        limb_len_sum_outputs = pm.listConnections(limb_rig.total_limb_len_sum.output, s=0, d=1, plugs=1)
        part_scale_mult = nodes.multDoubleLinear(input1=limb_rig.total_limb_len_sum.output, input2=connector.sy)
        [part_scale_mult.output.connect(plug, f=1) for plug in limb_len_sum_outputs]

        # ...Conform LimbRig's PV ctrl orientation to that of PV orienter
        pv_ctrl_buffer = limb_rig.ctrls['ik_pv'].getParent()
        world_pos = pm.xform(orienters['IkKnee'], q=1, worldSpace=1, rotatePivot=1)
        pm.delete(pm.orientConstraint(orienters['IkKnee'], pv_ctrl_buffer))

        self.reorient_ik_foot(ik_foot_ctrl=limb_rig.ctrls['ik_extrem'], side=part.side)

        # ...Move contents of limb rig into biped_leg rig module's groups
        [child.setParent(transform_grp) for child in limb_rig.grps['transform'].getChildren()]
        [child.setParent(no_transform_grp) for child in limb_rig.grps['noTransform'].getChildren()]

        #...Migrate Rig Scale attr over to new rig group
        rig_scale_attr_string = 'RigScale'
        gen.install_uniform_scale_attr(rig_part_container, rig_scale_attr_string)
        for plug in pm.listConnections(f'{limb_rig.grps["root"]}.{rig_scale_attr_string}', destination=1, plugs=1):
            pm.connectAttr(f'{rig_part_container}.{rig_scale_attr_string}', plug, force=1)
        for plug in pm.listConnections(f'{limb_rig.grps["root"]}.{rig_scale_attr_string}', source=1, plugs=1):
            pm.connectAttr(plug, f'{rig_part_container}.{rig_scale_attr_string}', force=1)
        pm.delete(limb_rig.grps['root'])

        ctrl_pairs = [('FkThigh', limb_rig.fk_ctrls[0]),
                      ('FkShin', limb_rig.fk_ctrls[1]),
                      ('FkFoot', limb_rig.fk_ctrls[2]),
                      ('IkFoot', limb_rig.ctrls['ik_extrem']),
                      ('IkKnee', limb_rig.ctrls['ik_pv']),
                      ('Hip', limb_rig.ctrls['socket']),
                      ('Knee', limb_rig.pin_ctrls[0])]
        for i, limb_segment in enumerate(('Thigh', 'Shin')):
            for j, name_tag in enumerate(('Start', 'Mid', 'End')):
                ctrl_pairs.append((f'{limb_segment}Bend{name_tag}', limb_rig.segments[i].bend_ctrls[j]))
            for j, ctrl_list in enumerate(limb_rig.tweak_ctrls[0]):
                ctrl_pairs.append((f'{limb_segment}Tweak{j+1}', limb_rig.tweak_ctrls[i][j]))

        for ctrl_str, limb_setup_ctrl in ctrl_pairs:
            scene_ctrls[ctrl_str] = self.migrate_control_to_new_node(scene_ctrls[ctrl_str], limb_setup_ctrl)

        ik_foot_follow_ctrl_buffer = gen.buffer_obj(scene_ctrls['IkFootFollow'], parent=transform_grp)
        pm.matchTransform(ik_foot_follow_ctrl_buffer, orienters['FootFollowSpace'])

        self.apply_all_control_transform_locks()

        pm.select(clear=1)
        return rig_part_container


    def reorient_ik_foot(self, ik_foot_ctrl, side):
        # ...Give IK foot control world orientation
        ctrl = ik_foot_ctrl

        ctrl_buffer = ctrl.getParent()
        # ...Temporarily moved shapes into a holder node (will move them back after reorientation)
        temp_shape_holder = pm.shadingNode('transform', name='TEMP_shape_holder', au=1)
        gen.copy_shapes(ctrl, temp_shape_holder, keep_original=True)
        [pm.delete(shape) for shape in ctrl.getShapes()]

        ori_offset = pm.shadingNode('transform', name=f'{gen.side_tag(side)}ikFoot_ori_OFFSET', au=1)
        ori_offset.setParent(ctrl_buffer)
        gen.zero_out(ori_offset)
        ori_offset.setParent(world=1)

        [child.setParent(ori_offset) for child in ctrl.getChildren()]

        par = ctrl_buffer.getParent()
        ctrl_buffer.setParent(world=1)

        if side == 'L':
            ctrl_buffer.rotate.set(0, 0, 0)
            ctrl_buffer.scale.set(1, 1, 1)
        elif side == 'R':
            ctrl_buffer.rotate.set(0, 180, 0)
            ctrl_buffer.scale.set(1, 1, -1)
        ctrl_buffer.setParent(par)

        ori_offset.setParent(ctrl)

        # ...Return shapes to control transform
        gen.copy_shapes(temp_shape_holder, ctrl, keep_original=False)
