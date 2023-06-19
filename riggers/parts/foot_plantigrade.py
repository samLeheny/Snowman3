# Title: foot_plantigrade.py
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
        data_packs = [
            ['Tarsus', (0, 0, 0), [[0, 0, 1], [0, 1, 0]], [[1, 0, 0], [0, 0, 1]], 1.25, True, None],
            ['Ball', (0, -7.5, 11.8), [[0, 0, 1], [0, 1, 0]], [[1, 0, 0], [0, 0, 1]], 1.25, True, None],
            ['BallEnd', (0, -7.5, 16.73), [[0, 0, 1], [0, 1, 0]], [[1, 0, 0], [0, 0, 1]], 1.25, False, 'Ball'],
            ['SoleToe', (0, -10, 11.8), [[0, 0, 1], [0, 1, 0]], [[1, 0, 0], [0, 0, 1]], 0.6, False, 'Ball'],
            ['SoleToeEnd', (0, -10, 19), [[0, 0, 1], [0, 1, 0]], [[1, 0, 0], [0, 0, 1]], 0.6, False, 'Ball'],
            ['SoleInner', (-4.5, -10, 11.8), [[0, 0, 1], [0, 1, 0]], [[1, 0, 0], [0, 0, 1]], 0.6, False, 'Ball'],
            ['SoleOuter', (4.5, -10, 11.8), [[0, 0, 1], [0, 1, 0]], [[1, 0, 0], [0, 0, 1]], 0.6, False, 'Ball'],
            ['SoleHeel', (0, -10, -4), [[0, 0, 1], [0, 1, 0]], [[1, 0, 0], [0, 0, 1]], 0.6, False, 'Ball'],
            ['FootSettings', (6, 0, 0), [[0, 0, 1], [0, 1, 0]], [[0, 0, 1], [0, 1, 0]], 0.7, False, None],
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
        ctrls = [
            self.initialize_ctrl(
                name='FkToe',
                shape='toe',
                color=self.colors[0],
                size=9,
                up_direction=[0, 0, 1],
                forward_direction=[1, 0, 0],
                side=self.side
            ),
            self.initialize_ctrl(
                name='IkToe',
                shape='toe',
                color=self.colors[0],
                size=9,
                up_direction=[0, 0, 1],
                forward_direction=[1, 0, 0],
                side=self.side
            ),
            self.initialize_ctrl(
                name='FootSettings',
                shape='gear',
                color=color_code['settings'],
                size=0.6,
                locks={'v': 1, 't': [1, 1, 1], 'r': [1, 1, 1], 's': [1, 1, 1]},
                side=self.side
            ),
        ]
        return ctrls


    def get_connection_pairs(self):
        return (
            ('Ball', 'Tarsus'),
            ('BallEnd', 'Ball')
        )



    def build_rig_part(self, part):
        rig_part_container, transform_grp, no_transform_grp = self.create_rig_part_grps(part)
        orienters, scene_ctrls = self.get_scene_armature_nodes(part)

        for key, parent, orienter_key in (('FkToe', transform_grp, 'Ball'),
                                          ('IkToe', transform_grp, 'Ball'),
                                          ('FootSettings', transform_grp, 'FootSettings')):
            scene_ctrls[key].setParent(parent)
            buffer = gen.buffer_obj(scene_ctrls[key])
            gen.match_pos_ori(buffer, orienters[orienter_key])


        foot_attr_node = scene_ctrls['FootSettings']
        leg_attr_loc = pm.spaceLocator(name=f'{gen.side_tag(part.side)}leg_attr_LOC')
        leg_attr_loc.setParent(no_transform_grp)

        # ...Ensure a kinematic blend attribute is present on given control
        if not pm.attributeQuery("fkIk", node=leg_attr_loc, exists=1):
            pm.addAttr(leg_attr_loc, longName="fkIk", niceName="FK / IK", attributeType="float", minValue=0,
                       maxValue=10, defaultValue=10, keyable=1)
            kinematic_blend_mult = gen.create_attr_blend_nodes(attr="fkIk", node=leg_attr_loc)
            kinematic_blend_rev = gen.create_attr_blend_nodes(attr="fkIk", node=leg_attr_loc, reverse=True)

        kinematic_blend_mult = gen.get_attr_blend_nodes(attr="fkIk", node=leg_attr_loc, mult=True)
        kinematic_blend_rev = gen.get_attr_blend_nodes(attr="fkIk", node=leg_attr_loc, reverse=True)
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
        bind_chain_buffer = gen.buffer_obj(list(bind_jnts.values())[0], _parent=transform_grp)
        gen.zero_out(bind_chain_buffer)
        gen.match_pos_ori(bind_chain_buffer, orienters['Tarsus'])
        for i, key in enumerate(bind_jnt_keys):
            if i > 0:
                gen.match_pos_ori(bind_jnts[key], orienters[key])

        scene_ctrls['FootSettings'].getParent().setParent(bind_jnts['Tarsus'])

        # ...IK rig
        ik_foot_rig = self.ik_foot(part=part, parent=transform_grp, bind_jnt_keys=bind_jnt_keys,
                                   orienters=orienters, ctrls=scene_ctrls, foot_roll_ctrl=foot_attr_node)
        ik_grp = ik_foot_rig['ik_grp']
        ###rig_module.ik_chain_connector = ik_foot_rig["ik_chain_connector"]
        ik_jnts = ik_foot_rig['ik_jnts']
        foot_roll_jnts = ik_foot_rig['foot_roll_jnts']

        # ...FK rig
        fk_foot_rig = self.fk_foot(part, parent=transform_grp, ankle_orienter=orienters['Tarsus'],
                                   fk_toe_ctrl=scene_ctrls['FkToe'])

        # ...Blending --------------------------------------------------------------------------------------------------
        rotate_constraint = gen.matrix_constraint(objs=[fk_foot_rig["fk_foot_space"], ik_jnts['Tarsus'],
                                                        bind_jnts['Tarsus']], decompose=True, translate=False,
                                                  rotate=True, scale=True, shear=False)
        kinematic_blend_mult.connect(rotate_constraint["weights"][0])

        t_values = bind_jnts["Ball"].translate.get()
        rotate_constraint = gen.matrix_constraint(objs=[scene_ctrls["FkToe"], ik_jnts["Ball"], bind_jnts["Ball"]],
                                                  decompose=True, translate=False, rotate=True, scale=True, shear=False)
        kinematic_blend_mult.connect(rotate_constraint["weights"][0])
        bind_jnts["Ball"].translate.set(t_values)

        self.apply_all_control_transform_locks()

        return rig_part_container



    def ik_foot(self, part, parent=None, bind_jnt_keys=None, orienters=None, ctrls=None, foot_roll_ctrl=None):

        # ...IK joints -------------------------------------------------------------------------------------------------
        ik_grp = pm.group(name=f'{gen.side_tag(part.side)}ikConnector', em=1, p=parent)
        gen.zero_out(ik_grp)
        foot_pos = pm.xform(orienters['Tarsus'], q=1, worldSpace=1, rotatePivot=1)
        pm.move(foot_pos[0], foot_pos[1], foot_pos[2], ik_grp)

        ik_jnts = {}
        ik_jnt_keys = bind_jnt_keys
        prev_jnt = None
        for i, key in enumerate(ik_jnt_keys):
            jnt = ik_jnts[key] = rig.joint(name=f'Ik{key}', side=part.side, radius=1.0, joint_type='JNT')
            jnt.setParent(prev_jnt) if prev_jnt else None
            prev_jnt = jnt
        ik_chain_buffer = gen.buffer_obj(list(ik_jnts.values())[0], _parent=ik_grp)
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
        foot_roll_chain_buffer = gen.buffer_obj(list(foot_roll_jnts.values())[0], suffix='OFFSET', _parent=ik_grp)
        gen.zero_out(foot_roll_chain_buffer)
        pm.matchTransform(foot_roll_chain_buffer, ik_grp)
        for i, key in enumerate(foot_roll_keys):
            gen.match_pos_ori(foot_roll_jnts[key], orienters[key])
        gen.buffer_obj(foot_roll_jnts['SoleHeel'])
        gen.zero_out(foot_roll_jnts['SoleHeel'])

        ctrls['IkToe'].getParent().setParent(foot_roll_jnts['SoleToeEnd'])

        pm.parentConstraint(foot_roll_jnts['Tarsus'], ik_chain_buffer, mo=1)

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
        pm.connectAttr(f'{foot_roll_ctrl}.BallSpin', foot_roll_jnts['SoleToe'].rz)

        # ...Toe tip
        # ...Roll
        pushed_toe_total = nodes.addDoubleLinear(input1=total_angle, input2=ball_toe_total_delay.output)

        toe_remap = nodes.remapValue(inputValue=f'{foot_roll_ctrl}.FootRoll', inputMin=ball_toe_total_delay.output,
                                     inputMax=pushed_toe_total.output, outputMin=0, outputMax=total_angle,
                                     outValue=foot_roll_jnts["SoleToeEnd"].ry)

        nodes.addDoubleLinear(input1=toe_remap.outValue, input2=f'{foot_roll_ctrl}.ToeRoll',
                              output=foot_roll_jnts['SoleToeEnd'].ry, force=True)
        # ...Spin
        pm.connectAttr(f'{foot_roll_ctrl}.ToeSpin', foot_roll_jnts['SoleToeEnd'].rz)

        # ...Heel
        # ...Roll
        clamp = nodes.clamp(input=(f'{foot_roll_ctrl}.FootRoll', None, None), min=(-total_angle, 0, 0),
                            max=(0, 0, 0), output=(foot_roll_jnts['SoleHeel'].ry, None, None))

        nodes.addDoubleLinear(input1=clamp.output.outputR, input2=f'{foot_roll_ctrl}.HeelRoll',
                              output=foot_roll_jnts['SoleHeel'].ry, force=True)
        # ...Spin
        pm.connectAttr(f'{foot_roll_ctrl}.HeelSpin', foot_roll_jnts['SoleHeel'].rz)

        # ...Banking
        [pm.connectAttr(f'{foot_roll_ctrl}.Bank', foot_roll_jnts[key].rx) for key in ('SoleOuter', 'SoleInner')]
        pm.setAttr(f'{foot_roll_jnts["SoleOuter"]}.maxRotLimitEnable.maxRotZLimitEnable', 1)
        pm.setAttr(f'{foot_roll_jnts["SoleOuter"]}.maxRotLimit.maxRotZLimit', 0)
        pm.setAttr(f'{foot_roll_jnts["SoleInner"]}.minRotLimitEnable.minRotZLimitEnable', 1)
        pm.setAttr(f'{foot_roll_jnts["SoleInner"]}.minRotLimit.minRotZLimit', 0)

        # --------------------------------------------------------------------------------------------------------------
        pm.select(clear=1)
        return {'ik_grp': ik_grp,
                'ik_jnts': ik_jnts,
                'foot_roll_jnts': foot_roll_jnts}



    def fk_foot(self, part, parent=None, ankle_orienter=None, fk_toe_ctrl=None):
        fk_foot_space = pm.shadingNode('transform', name=f'{gen.side_tag(part.side)}FkFootSpace', au=1)
        fk_foot_space.setParent(parent)
        gen.match_pos_ori(fk_foot_space, ankle_orienter)
        fk_toe_ctrl.getParent().setParent(fk_foot_space)
        pm.select(clear=1)
        return {'fk_foot_space': fk_foot_space}
