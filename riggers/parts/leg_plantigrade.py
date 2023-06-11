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

import Snowman3.utilities.rig_utils as rig
importlib.reload(rig)

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
            ['Tarsus', (0, -91, 0), [[0, -1, 0], [0, 0, 1]], [[1, 0, 0], [0, 0, 1]], 1.25, True, None, False, None],
            ['AnkleEnd', (0, -101, 0), [[0, -1, 0], [0, 0, 1]], [[1, 0, 0], [0, 0, 1]], 1.25, False, 'Tarsus',
                False, None],
            ['Ball', (0, -98.5, 11.8), [[0, -1, 0], [0, 0, 1]], [[1, 0, 0], [0, 0, 1]], 1.25, True, None, False, None],
            ['BallEnd', (0, -98.5, 16.73), [[0, -1, 0], [0, 0, 1]], [[1, 0, 0], [0, 0, 1]], 1.25, False, 'Ball', False,
             None],
            ['IkKnee', (0, -45, 40), [[0, -1, 0], [0, 0, 1]], [[1, 0, 0], [0, 1, 0]], 1.25, False, None, True,
                ('Thigh', 'Tarsus', 'Shin')],
            ['SoleToe', (0, -101, 11.8), [[0, 0, 1], [0, 1, 0]], [[1, 0, 0], [0, 0, 1]], 0.6, False, 'Ball', False,
                None],
            ['SoleToeEnd', (0, -101, 19), [[0, 0, 1], [0, 1, 0]], [[1, 0, 0], [0, 0, 1]], 0.6, False, 'Ball', False,
                None],
            ['SoleInner', (-4.5, -101, 11.8), [[0, 0, 1], [0, 1, 0]], [[1, 0, 0], [0, 0, 1]], 0.6, False, 'Ball', False,
                None],
            ['SoleOuter', (4.5, -101, 11.8), [[0, 0, 1], [0, 1, 0]], [[1, 0, 0], [0, 0, 1]], 0.6, False, 'Ball', False,
                None],
            ['SoleHeel', (0, -101, -4), [[0, 0, 1], [0, 1, 0]], [[1, 0, 0], [0, 0, 1]], 0.6, False, 'Ball', False,
             None],
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
            ),
            ControlCreator(
                name='FkToe',
                shape='toe',
                color=self.colors[0],
                size=9,
                up_direction=[-1, 0, 0],
                forward_direction=[0, 0, 1],
                side=self.side
            ),
            ControlCreator(
                name='IkToe',
                shape='toe',
                color=self.colors[0],
                size=9,
                up_direction=[-1, 0, 0],
                forward_direction=[0, 0, 1],
                side=self.side
            ),
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
            ('Tarsus', 'Shin'),
            ('AnkleEnd', 'Tarsus'),
            ('Ball', 'Tarsus'),
            ('BallEnd', 'Ball'),
            ('IkKnee', 'Shin'),
            ('Thigh', 'FootFollowSpace'),
        )


    def create_part_nodes_list(self):
        part_nodes = []
        for name in ('Thigh', 'Shin', 'Ankle', 'AnkleEnd', 'Tarsus', 'Ball', 'BallEnd'):
            part_nodes.append(name)
        return part_nodes


    def get_vector_handle_attachments(self):
        return {
            'Thigh': ['Shin', 'IkKnee'],
            'Shin': ['Tarsus', 'IkKnee'],
            'Tarsus': ['AnkleEnd', None]
        }


    def bespoke_build_rig_part(self, part, rig_part_container, transform_grp, no_transform_grp, orienters, scene_ctrls):

        limb_rig = LimbRig(
            limb_name=part.name,
            side=part.side,
            prefab='plantigrade',
            segment_names=['Thigh', 'Shin', 'Ankle'],
            socket_name='Hip',
            pv_name='Knee',
            orienters=[orienters[p] for p in ('Thigh', 'Shin', 'Tarsus', 'AnkleEnd')],
            pv_position=pm.xform(orienters['IkKnee'], q=1, worldSpace=1, rotatePivot=1),
            tweak_scale_factor_node=rig_part_container
        )

        limb_len_sum_outputs = pm.listConnections(limb_rig.total_limb_len_sum.output, s=0, d=1, plugs=1)
        world_scale_matrix = nodes.decomposeMatrix(inputMatrix=rig_part_container.worldMatrix)
        part_scale_mult = nodes.multDoubleLinear(input1=limb_rig.total_limb_len_sum.output,
                                                 input2=world_scale_matrix.outputScale.outputScaleX)
        [part_scale_mult.output.connect(plug, f=1) for plug in limb_len_sum_outputs]

        # ...Conform LimbRig's PV ctrl orientation to that of PV orienter
        pv_ctrl_buffer = limb_rig.ctrls['ik_pv'].getParent()
        world_pos = pm.xform(orienters['IkKnee'], q=1, worldSpace=1, rotatePivot=1)
        pm.delete(pm.orientConstraint(orienters['IkKnee'], pv_ctrl_buffer))

        self.reorient_ik_foot(ik_foot_ctrl=limb_rig.ctrls['ik_extrem'], side=part.side)

        # ...Move contents of limb rig into biped_leg rig module's groups
        [child.setParent(transform_grp) for child in limb_rig.grps['transform'].getChildren()]
        [child.setParent(no_transform_grp) for child in limb_rig.grps['noTransform'].getChildren()]

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
        gen.match_pos_ori(ik_foot_follow_ctrl_buffer, orienters['FootFollowSpace'])

        ###
        for key, parent, orienter_key in (('FkToe', transform_grp, 'Ball'),
                                          ('IkToe', transform_grp, 'Ball')):
            scene_ctrls[key].setParent(parent)
            buffer = gen.buffer_obj(scene_ctrls[key])
            gen.match_pos_ori(buffer, orienters[orienter_key])

        foot_attr_node = scene_ctrls['IkFoot']
        kinematic_blend_mult = gen.create_attr_blend_nodes(attr="fkIk", node=scene_ctrls['Hip'])
        kinematic_blend_rev = gen.create_attr_blend_nodes(attr="fkIk", node=scene_ctrls['Hip'], reverse=True)

        kinematic_blend_mult = gen.get_attr_blend_nodes(attr="fkIk", node=scene_ctrls['Hip'], mult=True)
        kinematic_blend_rev = gen.get_attr_blend_nodes(attr="fkIk", node=scene_ctrls['Hip'], reverse=True)
        kinematic_blend_mult.connect(scene_ctrls["IkToe"].visibility)
        kinematic_blend_rev.connect(scene_ctrls["FkToe"].visibility)

        # ...Bind joints -----------------------------------------------------------------------------------------------
        bind_jnts = {}
        bind_jnt_keys = ('Tarsus', 'Ball', 'BallEnd')
        prev_jnt = None
        for i, key in enumerate(bind_jnt_keys):
            jnt = bind_jnts[key] = rig.joint(name=key, side=part.side, radius=0.5, joint_type='BIND')
            jnt.setParent(prev_jnt) if prev_jnt else None
            prev_jnt = jnt
        bind_chain_buffer = gen.buffer_obj(list(bind_jnts.values())[0], parent=limb_rig.blend_jnts[-2])
        gen.zero_out(bind_chain_buffer)
        gen.match_pos_ori(bind_chain_buffer, orienters['Tarsus'])
        for i, key in enumerate(bind_jnt_keys):
            if i > 0:
                gen.match_pos_ori(bind_jnts[key], orienters[key])

        # ...IK rig
        ik_foot_rig = self.ik_foot(part=part, parent=limb_rig.ik_jnts[-2], bind_jnt_keys=bind_jnt_keys,
                                   orienters=orienters, ctrls=scene_ctrls, foot_roll_ctrl=foot_attr_node)
        ik_jnts = ik_foot_rig['ik_jnts']
        foot_roll_jnts = ik_foot_rig['foot_roll_jnts']
        ik_foot_rig['foot_roll_root_node'].setParent(scene_ctrls['IkFoot'])
        limb_rig.ik_handles['limb'].setParent(foot_roll_jnts['Tarsus'])

        # ...FK rig
        fk_foot_rig = self.fk_foot(part, parent=scene_ctrls['FkFoot'], ankle_orienter=orienters['Tarsus'],
                                   fk_toe_ctrl=scene_ctrls['FkToe'])

        # ...Blending
        rotate_constraint = gen.matrix_constraint(objs=[fk_foot_rig["fk_foot_space"], ik_jnts['Tarsus'],
                                                        bind_jnts['Tarsus']], decompose=True, translate=False,
                                                  rotate=True, scale=True, shear=False)
        kinematic_blend_mult.connect(rotate_constraint["weights"][0])

        t_values = bind_jnts["Ball"].translate.get()
        rotate_constraint = gen.matrix_constraint(objs=[scene_ctrls["FkToe"], ik_jnts["Ball"], bind_jnts["Ball"]],
                                                  decompose=True, translate=False, rotate=True, scale=True, shear=False)
        kinematic_blend_mult.connect(rotate_constraint["weights"][0])
        bind_jnts["Ball"].translate.set(t_values)

        limb_rig.ik_handles['extrem'].getParent().setParent(foot_roll_jnts['Tarsus'])

        for key, node in (('Thigh', limb_rig.blend_jnts[0]),
                          ('Shin', limb_rig.blend_jnts[1]),
                          ('Ankle', limb_rig.blend_jnts[-2]),
                          ('AnkleEnd', limb_rig.blend_jnts[-1]),
                          ('IkPoleVector', scene_ctrls['IkKnee'])):
            self.part_nodes[key] = node.nodeName()

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



    def ik_foot(self, part, parent, bind_jnt_keys, orienters, ctrls, foot_roll_ctrl):

        # ...IK joints -------------------------------------------------------------------------------------------------
        '''ik_grp = pm.group(name=f'{gen.side_tag(part.side)}ikConnector', em=1, p=parent)
        gen.zero_out(ik_grp)
        foot_pos = pm.xform(orienters['Tarsus'], q=1, worldSpace=1, rotatePivot=1)
        pm.move(foot_pos[0], foot_pos[1], foot_pos[2], ik_grp)'''

        ik_jnts = {}
        ik_jnt_keys = bind_jnt_keys
        prev_jnt = None
        for i, key in enumerate(ik_jnt_keys):
            jnt = ik_jnts[key] = rig.joint(name=f'Ik{key}', side=part.side, radius=1.0, joint_type='JNT')
            jnt.setParent(prev_jnt) if prev_jnt else None
            prev_jnt = jnt
        ik_chain_buffer = gen.buffer_obj(list(ik_jnts.values())[0], parent=parent)
        gen.zero_out(ik_chain_buffer)
        gen.match_pos_ori(ik_chain_buffer, orienters['Tarsus'])
        for i, key in enumerate(ik_jnt_keys):
            if i > 0:
                gen.match_pos_ori(ik_jnts[key], orienters[key])


        # ...Foot roll jnts---------------------------------------------------------------------------------------------
        foot_roll_jnts = {}
        foot_roll_keys = ('SoleHeel', 'SoleToe', 'SoleOuter', 'SoleInner', 'SoleToeEnd', 'Ball', 'Tarsus')
        prev_jnt = None
        for i, key in enumerate(foot_roll_keys):
            jnt = foot_roll_jnts[key] = rig.joint(name=f'FootRoll{key}', side=part.side, radius=1.5, joint_type='JNT')
            jnt.setParent(prev_jnt) if prev_jnt else None
            prev_jnt = jnt
        foot_roll_chain_buffer = gen.buffer_obj(list(foot_roll_jnts.values())[0], suffix='OFFSET', parent=parent)
        gen.zero_out(foot_roll_chain_buffer)
        #pm.matchTransform(foot_roll_chain_buffer, parent)
        for i, key in enumerate(foot_roll_keys):
            gen.match_pos_ori(foot_roll_jnts[key], orienters[key])
        gen.buffer_obj(foot_roll_jnts['SoleHeel'])
        #gen.zero_out(foot_roll_jnts['SoleHeel'])

        ctrls['IkToe'].getParent().setParent(foot_roll_jnts['SoleToeEnd'])

        pm.orientConstraint(foot_roll_jnts['Tarsus'], ik_chain_buffer, mo=1)

        # ...IK handles ------------------------------------------------------------------------------------------------
        ik_handles = {}
        ik_effectors = {}

        for tag, jnts, parent in (("Tarsus", (ik_jnts["Tarsus"], ik_jnts["Ball"]), foot_roll_jnts["Ball"]),
                                  ("Toe", (ik_jnts["Ball"], ik_jnts["BallEnd"]), ctrls["IkToe"])):
            ik_handles[tag], ik_effectors[tag] = pm.ikHandle(name=f'{gen.side_tag(part.side)}{tag}_IKH',
                                                             startJoint=jnts[0], endEffector=jnts[1],
                                                             solver='ikSCsolver')
            ik_effectors[tag].rename(f'{gen.side_tag(part.side)}ik_{tag}_EFF')
            ik_handles[tag].setParent(parent)

        # ...Foot roll attributes --------------------------------------------------------------------------------------
        for attr_name, attr_type in (("FootRoll", "float"),
                                     ("BallRoll", "float"),
                                     ("ToeRoll", "float"),
                                     ("HeelRoll", "float"),
                                     ("Bank", "doubleAngle"),
                                     ("HeelSpin", "doubleAngle"),
                                     ("BallSpin", "doubleAngle"),
                                     ("ToeSpin", "doubleAngle")):
            pm.addAttr(foot_roll_ctrl, longName=attr_name, attributeType=attr_type, defaultValue=0, keyable=1)

        ball_roll_delay_attr_string = "BallDelay"
        pm.addAttr(foot_roll_ctrl, longName=ball_roll_delay_attr_string, attributeType="float",
                   defaultValue=0, keyable=1)

        toe_roll_start_attr_string = "ToeRollStart"
        pm.addAttr(foot_roll_ctrl, longName=toe_roll_start_attr_string, attributeType="float", defaultValue=15,
                   minValue=0, keyable=1)

        total_angle = 180

        # ...Ball
        # ...Roll
        ball_toe_total_delay = nodes.addDoubleLinear(input1=f'{foot_roll_ctrl}.BallDelay',
                                                     input2=f'{foot_roll_ctrl}.ToeRollStart')

        pushed_ball_return = nodes.addDoubleLinear(input1=ball_toe_total_delay.output,
                                                   input2=f'{foot_roll_ctrl}.ToeRollStart')

        ball_remap_A = nodes.remapValue(inputValue=f'{foot_roll_ctrl}.FootRoll',
                                        inputMin=f'{foot_roll_ctrl}.BallDelay',
                                        inputMax=ball_toe_total_delay.output, outputMin=0,
                                        outputMax=f'{foot_roll_ctrl}.ToeRollStart')

        ball_remap_B = nodes.remapValue(inputValue=f'{foot_roll_ctrl}.FootRoll',
                                        inputMin=ball_toe_total_delay.output,
                                        inputMax=pushed_ball_return.output,
                                        outputMin=f'{foot_roll_ctrl}.ToeRollStart', outputMax=0)

        ball_con = nodes.condition(firstTerm=f'{foot_roll_ctrl}.FootRoll',
                                   secondTerm=ball_toe_total_delay.output,
                                   colorIfTrue=(ball_remap_B.outValue, 0, 0),
                                   colorIfFalse=(ball_remap_A.outValue, 1, 1),
                                   operation='greater or equal',
                                   outColor=(foot_roll_jnts['Ball'].ry, None, None))

        nodes.addDoubleLinear(input1=ball_con.outColor.outColorR, input2=f'{foot_roll_ctrl}.BallRoll',
                              output=foot_roll_jnts['Ball'].ry, force=True)

        # ...Spin
        pm.connectAttr(f'{foot_roll_ctrl}.BallSpin', foot_roll_jnts['SoleToe'].rx)

        # ...Toe tip
        # ...Roll
        pushed_toe_total = nodes.addDoubleLinear(input1=total_angle, input2=ball_toe_total_delay.output)

        toe_remap = nodes.remapValue(inputValue=f'{foot_roll_ctrl}.FootRoll', inputMin=ball_toe_total_delay.output,
                                     inputMax=pushed_toe_total.output, outputMin=0, outputMax=total_angle,
                                     outValue=foot_roll_jnts["SoleToeEnd"].ry)

        nodes.addDoubleLinear(input1=toe_remap.outValue, input2=f'{foot_roll_ctrl}.ToeRoll',
                              output=foot_roll_jnts['SoleToeEnd'].ry, force=True)
        # ...Spin
        pm.connectAttr(f'{foot_roll_ctrl}.ToeSpin', foot_roll_jnts['SoleToeEnd'].rx)

        # ...Heel
        # ...Roll
        clamp = nodes.clamp(input=(f'{foot_roll_ctrl}.FootRoll', None, None), min=(-total_angle, 0, 0),
                            max=(0, 0, 0), output=(foot_roll_jnts['SoleHeel'].ry, None, None))

        nodes.addDoubleLinear(input1=clamp.output.outputR, input2=f'{foot_roll_ctrl}.HeelRoll',
                              output=foot_roll_jnts['SoleHeel'].ry, force=True)
        # ...Spin
        pm.connectAttr(f'{foot_roll_ctrl}.HeelSpin', foot_roll_jnts['SoleHeel'].rx)

        # ...Banking
        [pm.connectAttr(f'{foot_roll_ctrl}.Bank', foot_roll_jnts[key].rz) for key in ('SoleOuter', 'SoleInner')]
        pm.setAttr(f'{foot_roll_jnts["SoleOuter"]}.maxRotLimitEnable.maxRotZLimitEnable', 1)
        pm.setAttr(f'{foot_roll_jnts["SoleOuter"]}.maxRotLimit.maxRotZLimit', 0)
        pm.setAttr(f'{foot_roll_jnts["SoleInner"]}.minRotLimitEnable.minRotZLimitEnable', 1)
        pm.setAttr(f'{foot_roll_jnts["SoleInner"]}.minRotLimit.minRotZLimit', 0)

        # ------------------------------------------------------------------------------------------------------------------
        pm.select(clear=1)
        return {'ik_jnts': ik_jnts,
                'foot_roll_jnts': foot_roll_jnts,
                'foot_roll_root_node': foot_roll_chain_buffer}



    def fk_foot(self, part, parent=None, ankle_orienter=None, fk_toe_ctrl=None):
        fk_foot_space = pm.shadingNode('transform', name=f'{gen.side_tag(part.side)}FkFootSpace', au=1)
        fk_foot_space.setParent(parent)
        gen.match_pos_ori(fk_foot_space, ankle_orienter)
        fk_toe_ctrl.getParent().setParent(fk_foot_space)
        pm.select(clear=1)
        return {'fk_foot_space': fk_foot_space}
