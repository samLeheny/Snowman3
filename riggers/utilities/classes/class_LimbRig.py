# Title: class_LimbRig.py
# Author: Sam Leheny
# Contact: samleheny@live.com

# Description:


###########################
##### Import Commands #####
import importlib
import math
import pymel.core as pm

import Snowman3.utilities.general_utils as gen_utils
importlib.reload(gen_utils)

import Snowman3.utilities.rig_utils as rig_utils
importlib.reload(rig_utils)

import Snowman3.utilities.node_utils as node_utils
importlib.reload(node_utils)

import Snowman3.dictionaries.nameConventions as nameConventions
importlib.reload(nameConventions)
nom = nameConventions.create_dict()
###########################
###########################


###########################
######## Variables ########
default_socket_name = 'limbSocket'
default_pv_name = 'poleVector'
ctrl_colors = {"FK": 13, "IK": 6, "other": 17, "sub": (15, 4)}
roll_jnt_resolution = 5
prefab_inputs = {
        'plantigrade': {
            'default_seg_names' : ['upperlimb', 'lowerlimb', 'extrem'],
            'default_jnt_positions' : ((0, 0, 0), (1, 0, -0.5), (2, 0, 0), (2.5, 0, 0)),
            'dynamic_length_values' : (1, 1, 0, 0),
            'double_jnt_values' : (0, 0, 0, 0),
            'ik_indices' : {'start': 0, 'end': -2, 'mid': 1},
            'roller_segment_indices' : ((0, 1), (1, 2)),
            'tarsus_index': None
        },
        'plantigrade_doubleKnee': {
            'default_seg_names': ['upperlimb', 'joint', 'lowerlimb', 'extrem'],
            'default_jnt_positions': ((0, 0, 0), (0.9, 0, -0.5), (1.1, 0, -0.5), (2, 0, 0), (2.5, 0, 0)),
            'dynamic_length_values': (1, 0, 1, 0, 0),
            'double_jnt_values' : (0, 1, 0, 0, 0),
            'ik_indices' : {'start': 0, 'end': -2, 'mid': 1},
            'roller_segment_indices' : ((0, 1), (2, 3)),
            'tarsus_index': None
        },
        'digitigrade': {
            'default_seg_names': ['upperlimb', 'lowerlimb', 'tarsus', 'extrem'],
            'default_jnt_positions': ((0, 0, 0), (0.75, 0, -0.5), (1.5, 0, 0.25), (2, 0, 0), (2.5, 0, 0)),
            'dynamic_length_values': (1, 1, 1, 0, 0),
            'double_jnt_values' : (0, 0, 0, 0, 0),
            'ik_indices' : {'start': 0, 'end': -3, 'mid': 1},
            'roller_segment_indices' : ((0, 1), (1, 2)),
            'tarsus_index': 2
        },
        'digitigrade_doubleKnees': {
            'default_seg_names': ['upperlimb', 'frontKnee', 'lowerlimb', 'backKnee', 'tarsus', 'extrem'],
            'default_jnt_positions': ((0, 0, 0), (0.65, 0, -0.5), (0.85, 0, -0.5), (1.4, 0, 0.25), (1.6, 0, 0.25),
                                      (2, 0, 0), (2.5, 0, 0)),
            'dynamic_length_values': (1, 0, 1, 0, 1, 0, 0),
            'double_jnt_values' : (0, 1, 0, 1, 0, 0),
            'ik_indices' : {'start': 0, 'end': -3, 'mid': 1},
            'roller_segment_indices' : ((0, 1), (2, 3)),
            'tarsus_index': 4
        },
        'digitigrade_doubleFrontKnee': {
            'default_seg_names': ['upperlimb', 'frontKnee', 'lowerlimb', 'tarsus', 'extrem'],
            'default_jnt_positions': ((0, 0, 0), (0.65, 0, -0.5), (0.85, 0, -0.5), (1.5, 0, 0.25), (2, 0, 0),
                                      (2.5, 0, 0)),
            'dynamic_length_values': (1, 0, 1, 1, 0, 0),
            'double_jnt_values' : (0, 1, 0, 0, 0, 0),
            'ik_indices' : {'start': 0, 'end': -3, 'mid': 1},
            'roller_segment_indices' : ((0, 1), (2, 3)),
            'tarsus_index': 3
        },
    }
###########################
###########################





########################################################################################################################
########################################################################################################################
class LimbRig:
    def __init__(
        self,
        limb_name,
        prefab,
        side = None,
        segment_names = None,
        jnt_positions = None,
        socket_name = None,
        pv_name = None
    ):
        self.roll_jnt_resolution = roll_jnt_resolution
        self.limb_name = limb_name
        self.prefab = prefab
        self.side = side
        self.side_tag = f'{self.side}_' if self.side else ""
        self.segments = []
        self.segment_count = None
        self.segment_names = segment_names
        self.jnt_positions = jnt_positions
        self.limb_ik_start_jnt_index = None
        self.limb_ik_end_jnt_index = None
        self.limb_ik_mid_jnt_index = None
        self.jnt_position_holders = []
        self.pv_position_holder = None
        self.grps = {}
        self.ctrls = {}
        self.ctrl_colors = ctrl_colors
        self.socket_name = socket_name if socket_name else default_socket_name
        self.pv_name = pv_name if pv_name else default_pv_name
        self.blend_jnt_chain_buffer = None
        self.fk_chain_buffer = None
        self.ik_jnt_chain_buffer = None
        self.ik_end_marker = None
        self.ik_handles, self.ik_solvers, self.ik_effectors = {}, {}, {}
        self.ik_display_crv = None
        self.ik_extrem_dist = None
        self.bend_ctrls = None
        self.bend_jnts = None
        self.roll_socket_target = None
        self.tweak_ctrls = []
        self.pv_vector = None

        self.build_prefab(self.prefab)





    ####################################################################################################################
    def build_prefab(self, prefab_key):
        """
        Builds the limb in scene based on prefab information provided
            (eg. plantigrade/digitigrade, single-kneed/double-kneed, etc.)
        Args:
            prefab_key (str): The key that corresponds to the pre-assembled dictionary of prefab inputs.
                [Should those dictionaries be stored here in the function??]
        """

        inputs = prefab_inputs[prefab_key]

        default_seg_names = inputs['default_seg_names']
        default_jnt_positions = inputs['default_jnt_positions']
        dynamic_length_values = inputs['dynamic_length_values']

        if not self.segment_names: self.segment_names = default_seg_names
        self.segment_names.append(f'{self.segment_names[-1]}End')
        if not self.jnt_positions: self.jnt_positions = default_jnt_positions

        for i, name in enumerate(self.segment_names):
            end_world_position = default_jnt_positions[i + 1] if i < len(default_seg_names) else None
            new_segment = LimbSegment(segment_name = name,
                                      side = self.side,
                                      index = i,
                                      start_world_position = default_jnt_positions[i],
                                      end_world_position = end_world_position,
                                      dynamic_length = dynamic_length_values[i],
                                      double_jnt_status = inputs['double_jnt_values'][i])
            self.segments.append(new_segment)

        self.segment_count = len(self.segments)
        self.limb_ik_start_jnt_index = inputs['ik_indices']['start']
        self.limb_ik_end_jnt_index = inputs['ik_indices']['end']
        self.limb_ik_mid_jnt_index = inputs['ik_indices']['mid']

        self.create_position_holders()
        self.get_pv_vector()
        self.create_rig_grps()
        self.create_rig_socket_ctrl()
        self.create_length_mult_nodes()
        self.blend_rig(index_pairs=inputs['roller_segment_indices'])
        self.fk_rig()
        self.ik_rig(tarsus_index=inputs['tarsus_index'], limb_ik_start_index=inputs['ik_indices']['start'],
                    limb_ik_end_index=inputs['ik_indices']['end'])
        self.setup_kinematic_blend()
        ### self.install_ribbon_systems()
        self.delete_position_holders()





    ####################################################################################################################
    def create_position_holders(self):
        """
        Accesses LimbRig instance's segment positions and places locators in those positions so subsequent methods can
            access said positions via those locator objects. Locators can be junked towards end of module script.
        """

        locs_grp = pm.group(name=f'{self.side_tag}position_holders_TEMP', world=1, em=1)

        # ...Create and position locs
        for i, pos in enumerate(self.jnt_positions):
            loc = pm.spaceLocator(name=f'{self.side_tag}position_holder_{str(i)}_{nom.locator}')
            loc.setParent(locs_grp)
            loc.translate.set(pos)
            loc.getShape().localScale.set(0.15, 0.15, 0.15)
            self.jnt_position_holders.append(loc)

        # ...Pole vector position holder
        self.create_pv_position_holder(locs_grp)

        # ...Orient locs
        for i in range(0, len(self.jnt_position_holders)):
            pm.delete(pm.aimConstraint(self.jnt_position_holders[i], self.jnt_position_holders[i-1],
                                       worldUpType='object', aimVector=(1, 0, 0), upVector=(0, 0, 1),
                                       worldUpObject=self.pv_position_holder))
        pm.delete(pm.orientConstraint(self.jnt_position_holders[-2], self.jnt_position_holders[-1]))

        # ...Mirror transforms if this is a right-sided limb
        if self.side == nom.rightSideTag:
            gen_utils.flip(locs_grp)





    ####################################################################################################################
    def delete_position_holders(self):
        """
        Remove temporary joint position holders from scene.
        """

        [pm.delete(loc) for loc in self.jnt_position_holders]
        pm.delete(self.pv_position_holder)





    ####################################################################################################################
    def create_pin_ctrl(self, name, target_jnt_index, limb_span_jnt_indices):
        """
        Creates a control that move's the position of a limb's joint. Positions the control at that joint and orients
            it to face the forward normal of that joint's immediate limb segments (points out and away from the limb.)
        Args:
            name (str): The string to use in control's name.
            target_jnt_index (int/ (int, int)): The index(s) of the joint for this control to be placed at. If two
                indices provided will place control at the midpoint between them.
            limb_span_jnt_indices ((int, int)): Two indices. One for the joint at the start end of the limb span whose
                center joint this control is for, and one for the other end (IN THAT ORDER!).
                eg: if this control is for a and elbow, provide indices for shoulder and wrist joints.
        Return:
            (mObj): The created control.
        """

        # ...Determine if a SINGLE jnt or a PAIR of jnts are referenced by the provided target index(s)
        multi_jnt_target = True if isinstance(target_jnt_index, (tuple, list)) else False


        # ...Get limb segments immediately before and after target_node, so we average their world orientations to
        # ...determine control's orientation
        limb_span_seg_1 = self.segments[limb_span_jnt_indices[0]]
        limb_span_seg_2 = self.segments[limb_span_jnt_indices[1] - 1]


        # ...Create control
        ctrl = rig_utils.control(
            ctrl_info={"shape": "circle",
                       "scale": [0.2, 0.2, 0.2],
                       "up_direction": [1, 0, 0],
                       "forward_direction": [0, 0, 1]},
            name=f'{name}Pin', ctrl_type=nom.animCtrl, side=self.side, color=self.ctrl_colors['other'])


        # ...Determine which blend joint to parent control under
        if multi_jnt_target:
            pos_offset_node_parent = self.segments[target_jnt_index[0]].blend_jnt
        else:
            pos_offset_node_parent = self.segments[target_jnt_index].blend_jnt


        # ...Create offset transform
        pos_offset_node = pm.shadingNode('transform', name=f'{self.side_tag}{name}_CTRL_OFFSET', au = 1)
        # ...Put offset node in final position and parent it within the blend joint chain
        pos_offset_node.setParent(pos_offset_node_parent)
        gen_utils.zero_out(pos_offset_node)
        # ...If two target joints were provided, position node between them
        if multi_jnt_target:
            target_segment_length = self.segments[target_jnt_index[0]].segment_length
            pos_offset_node.tx.set(target_segment_length / 2)


        # ...Put control under orientation buffer node
        buffer_node = gen_utils.buffer_obj(ctrl, parent=pos_offset_node)
        gen_utils.zero_out(buffer_node)
        # ...Orient buffer node by averaging world orientations of the two segments in immediate limb span
        pm.delete(pm.orientConstraint(limb_span_seg_1.blend_jnt, limb_span_seg_2.blend_jnt, buffer_node))


        return ctrl





    ####################################################################################################################
    def create_limb_pin_ctrls(self):

        self.ctrls['knee_pin'] = self.create_pin_ctrl(name='knee',
                                                      target_jnt_index=(1, 2),
                                                      limb_span_jnt_indices=(0, 3))
        self.ctrls['heel_pin'] = self.create_pin_ctrl(name='heel',
                                                      target_jnt_index=3,
                                                      limb_span_jnt_indices=(2, 4))





    ####################################################################################################################
    def create_pv_position_holder(self, parent):

        loc = self.pv_position_holder = pm.spaceLocator(name=f'{self.side_tag}position_holder_PV_{nom.locator}')
        loc.getShape().localScale.set(0.15, 0.15, 0.15)
        loc.setParent(parent)
        pm.delete(pm.pointConstraint(self.jnt_position_holders[self.limb_ik_start_jnt_index],
                                     self.jnt_position_holders[self.limb_ik_end_jnt_index], loc))
        pm.delete(pm.aimConstraint(self.jnt_position_holders[self.limb_ik_mid_jnt_index], loc, worldUpType='object',
                  worldUpObject=self.jnt_position_holders[0], aimVector=(0, 0, -1), upVector=(-1, 0, 0)))
        gen_utils.buffer_obj(loc)
        loc.tz.set(sum([seg.segment_length for seg in self.segments]) * -1)





    ####################################################################################################################
    def create_rig_grps(self):

        self.grps['root'] = pm.group(name=f'{self.side_tag}{self.limb_name}_RIG', world=1, em=1)

        self.grps['transform'] = pm.group(name="transform", p=self.grps['root'], em=1)

        self.grps['noTransform'] = pm.group(name="noTransform", p=self.grps['root'], em=1)
        self.grps['noTransform'].inheritsTransform.set(0, lock=1)

        if self.side == nom.rightSideTag:
            gen_utils.flip(self.grps['root'])
            gen_utils.flip(self.grps['noTransform'])

        # ...Rig Scale attribute
        pm.addAttr(self.grps['root'], longName="RigScale", minValue=0.001, defaultValue=1, keyable=0)

        pm.select(clear=1)





    ####################################################################################################################
    def create_rig_socket_ctrl(self):

        # ...Create controls
        ctrl = self.ctrls['socket'] = rig_utils.control(ctrl_info = {'shape': 'tag_hexagon',
                                                                     'scale': [0.2, 0.2, 0.2]},
                                                        name = f'{self.socket_name}Pin',
                                                        ctrl_type = nom.animCtrl,
                                                        side = self.side,
                                                        color = self.ctrl_colors['other'])

        # ...Position ctrl in scene and hierarchy
        ctrl.translate.set(self.jnt_positions[0])
        ctrl.setParent(self.grps['transform'])
        gen_utils.convert_offset(ctrl)
        gen_utils.buffer_obj(ctrl)

        # ...Rig Scale attribute
        pm.addAttr(ctrl, longName='LimbScale', minValue=0.001, defaultValue=1, keyable=1)
        [pm.connectAttr(f'{ctrl}.LimbScale', f'{ctrl}.{a}') for a in ('sx', 'sy', 'sz')]

        '''
        # ...Add settings attributes
        pm.addAttr(ctrl, longName="fkIk", niceName="FK / IK", attributeType="float", minValue=0, maxValue=10,
                   defaultValue=10, keyable=1)

        pm.addAttr(ctrl, longName="upperlimb_length", attributeType="float", minValue=0.001, defaultValue=1,
                   keyable=1)

        pm.addAttr(ctrl, longName="lowerlimb_length", attributeType="float", minValue=0.001, defaultValue=1,
                   keyable=1)

        pm.addAttr(ctrl, longName="stretchy_ik", attributeType="float", minValue=0, maxValue=10, defaultValue=10,
                   keyable=1)

        pm.addAttr(ctrl, longName="Volume", attributeType="float", minValue=0, maxValue=10, defaultValue=0,
                   keyable=1)

        pm.addAttr(ctrl, longName="squash_ik", attributeType="float", minValue=0, maxValue=10, defaultValue=0,
                   keyable=1)
        '''





    ####################################################################################################################
    def create_length_mult_nodes(self):

        for i, seg in enumerate(self.segments):
            if i == len(self.segments)-1:
                continue
            seg.create_length_mult_node(self.ctrls['socket']) if not seg.double_jnt else None





    ####################################################################################################################
    def blend_rig(self, index_pairs):


        pm.addAttr(self.ctrls['socket'], longName='Volume', attributeType='float', minValue=0, maxValue=10,
                   defaultValue=0, keyable=1)

        # ...Blend skeleton
        self.create_blend_jnts()
        # ...Limb pin controls
        self.create_limb_pin_ctrls()


        # ...Rollers
        '''lowerlimb_roller = self.install_rollers(
            start_node = self.segments[index_pairs[1][0]].blend_jnt,
            end_node = self.segments[index_pairs[1][1]].blend_jnt,
            seg_name = self.segments[index_pairs[1][0]].segment_name,
            start_rot_match = self.segments[index_pairs[1][0]].blend_jnt,
            end_rot_match = self.segments[index_pairs[1][1]].blend_jnt,
            ctrl_mid_influ = True,
            populate_ctrls = (1, 1, 1),
            ctrl_color = self.ctrl_colors['other'],
            side = self.side,
            parent = self.grps['noTransform']
        )
        for ctrl_tag in ('start_ctrl', 'mid_ctrl', 'end_ctrl'):
            self.segments[index_pairs[1][0]].bend_ctrls.append(lowerlimb_roller[ctrl_tag])
        for jnt_tag in ('start_jnt', 'mid_jnt', 'end_jnt'):
            self.segments[index_pairs[1][0]].bend_jnts.append(lowerlimb_roller[jnt_tag])

        self.ctrls['mid_limb_pin'] = lowerlimb_roller['start_ctrl']
        self.ctrls['lowerlimb_bend_mid'] = lowerlimb_roller['mid_ctrl']
        self.ctrls['lowerlimb_bend_end'] = lowerlimb_roller['end_ctrl']

        upperlimb_roller = self.install_rollers(
            start_node = self.segments[index_pairs[0][0]].blend_jnt,
            end_node = self.segments[index_pairs[0][1]].blend_jnt,
            seg_name = self.segments[index_pairs[0][0]].segment_name,
            start_rot_match = self.ctrls['socket'],
            end_rot_match = lowerlimb_roller['start_ctrl'],
            populate_ctrls = (1, 1, 0),
            ctrl_color = self.ctrl_colors['other'],
            side = self.side,
            parent = self.grps['noTransform']
            )
        for ctrl_tag in ('start_ctrl', 'mid_ctrl'):
            self.segments[index_pairs[0][0]].bend_ctrls.append(upperlimb_roller[ctrl_tag])
        for jnt_tag in ('start_jnt', 'mid_jnt', 'end_jnt'):
            self.segments[index_pairs[0][0]].bend_jnts.append(upperlimb_roller[jnt_tag])

        self.roll_socket_target = upperlimb_roller["roll_socket_target"]

        self.ctrls['upperlimb_bend_start'] = upperlimb_roller['start_ctrl']
        self.ctrls['upperlimb_bend_mid'] = upperlimb_roller['mid_ctrl']


        # ...Bend ctrls vis
        bend_ctrl_vis_attr_string = 'BendCtrls'
        if not pm.attributeQuery(bend_ctrl_vis_attr_string, node=self.ctrls['socket'], exists=1):
            pm.addAttr(self.ctrls['socket'], longName=bend_ctrl_vis_attr_string, attributeType='enum', keyable=0,
                       enumName='Off:On')
            pm.setAttr(f'{self.ctrls["socket"]}.{bend_ctrl_vis_attr_string}', channelBox=1)

        for ctrl in (upperlimb_roller['start_ctrl'], upperlimb_roller['mid_ctrl'],
                     lowerlimb_roller['mid_ctrl'], lowerlimb_roller['end_ctrl']):
            pm.connectAttr(f'{self.ctrls["socket"]}.{bend_ctrl_vis_attr_string}', ctrl.visibility)'''


        '''self.install_ribbon(
            start_node=upperlimb_roller['start_jnt'],
            end_node=upperlimb_roller['end_jnt'],
            bend_jnts=(upperlimb_roller['start_jnt'], upperlimb_roller['mid_jnt'], upperlimb_roller['end_jnt']),
            length_ends=(self.ctrls['socket'], self.ctrls['mid_limb_pin']),
            segment=self.segments[index_pairs[0][0]]
        )

        self.install_ribbon(
            start_node=lowerlimb_roller['start_jnt'],
            end_node=lowerlimb_roller['end_jnt'],
            bend_jnts=(lowerlimb_roller['start_jnt'], lowerlimb_roller['mid_jnt'], lowerlimb_roller['end_jnt']),
            length_ends=(self.ctrls['mid_limb_pin'], self.segments[index_pairs[1][1]].blend_jnt),
            segment=self.segments[index_pairs[1][0]]
        )'''





    ####################################################################################################################
    def install_rollers(self, start_node, end_node, seg_name, start_rot_match, end_rot_match, jnt_radius=0.3,
                        ctrl_mid_influ=False, populate_ctrls=(1, 1, 1), roll_axis=(1, 0, 0), up_axis=(0, 1, 0),
                        ctrl_color=0, side=None, parent=None):

        rollers = rig_utils.limb_rollers(
            start_node = start_node,
            end_node = end_node,
            roller_name = seg_name,
            start_rot_match = start_rot_match,
            end_rot_match = end_rot_match,
            jnt_radius = jnt_radius,
            populate_ctrls = populate_ctrls,
            ctrl_mid_influ = ctrl_mid_influ,
            roll_axis = roll_axis,
            up_axis = up_axis,
            ctrl_color = ctrl_color,
            side = side,
            parent = parent
        )


        # --------------------------------------------------------------------------------------------------------------
        return rollers





    ####################################################################################################################
    def create_blend_jnts(self):

        pm.select(clear=1)

        # ...Create joints ---------------------------------------------------------------------------------------------
        for i, seg in enumerate(self.segments):
            blend_jnt = seg.blend_jnt = rig_utils.joint(name=f'{seg.segment_name}_blend', side=self.side,
                                                        joint_type=nom.nonBindJnt, radius=0.1)
            if i > 0:
                blend_jnt.setParent(self.segments[i - 1].blend_jnt)


        # ...Wrap top of chain in a buffer group -----------------------------------------------------------------------
        self.blend_jnt_chain_buffer = gen_utils.buffer_obj(self.segments[0].blend_jnt)
        if self.side == nom.rightSideTag:
            gen_utils.flip(self.blend_jnt_chain_buffer)


        # Position Jnts ------------------------------------------------------------------------------------------------
        for i, seg in enumerate(self.segments):
            if i == 0: continue
            seg.blend_jnt.tx.set(self.segments[i - 1].segment_length)


        # Orient Jnts --------------------------------------------------------------------------------------------------
        nodes_to_orient = [seg.blend_jnt for seg in self.segments]
        nodes_to_orient[0] = self.blend_jnt_chain_buffer
        nodes_to_orient.remove(nodes_to_orient[-1])
        for i, node in enumerate(nodes_to_orient):
            pm.delete(pm.aimConstraint(self.jnt_position_holders[i+1], node, worldUpType="scene", aimVector=(1, 0, 0),
                                       upVector=(0, -1, 0), worldUpVector=(0, 1, 0)))

        self.segments[-1].blend_jnt.rotate.set(0, 0 ,0)
        self.segments[-1].blend_jnt.scale.set(1, 1, 1)


        # ...Clean joint rotations -------------------------------------------------------------------------------------
        for i, seg in enumerate(self.segments):
            if i == 0: continue
            seg.blend_jnt.jointOrient.set(seg.blend_jnt.rotate.get() + seg.blend_jnt.jointOrient.get())
            seg.blend_jnt.rotate.set(0, 0, 0)


        self.blend_jnt_chain_buffer.setParent(self.ctrls['socket'])


        rot = self.blend_jnt_chain_buffer.rotate.get()
        gen_utils.matrix_constraint(objs=[self.ctrls['socket'], self.blend_jnt_chain_buffer], decompose=True,
                                    translate=True, rotate=False, scale=False, shear=False)
        self.blend_jnt_chain_buffer.rotate.set(rot)



        # --------------------------------------------------------------------------------------------------------------
        pm.select(clear=1)





    ####################################################################################################################
    def fk_rig(self):

        i = 0
        jnt_parent = None
        for n, seg in enumerate(self.segments):
            if n == self.segment_count-1:
                continue

            fk_ctrl = None

            if not seg.double_jnt:
                # ...Single-jointed FK ctrl
                # ...Create and parent control
                parent = self.segments[n-1].fk_jnt_cap
                fk_ctrl = seg.fk_ctrl = rig_utils.control(ctrl_info={
                    'shape': 'cube',
                    'scale': [seg.segment_length / 2 * 0.93,
                              seg.segment_length / 2 * (0.93 * 0.25),
                              seg.segment_length / 2 * (0.93 * 0.25)],
                    'offset': [seg.segment_length / 2, 0, 0]},
                    name=f'{seg.segment_name}_FK',
                    ctrl_type=nom.animCtrl,
                    side=self.side,
                    parent=parent,
                    color=self.ctrl_colors['FK']
                )
                jnt_parent = fk_ctrl

            if  seg.double_jnt:
                jnt_parent = self.segments[n-1].fk_jnt_cap
            jnt = seg.fk_jnt = rig_utils.joint(name=f'{seg.segment_name}_fk', side=self.side, joint_type=nom.nonBindJnt,
                                               radius=0.08, color=2, parent=jnt_parent)
            cap_jnt = seg.fk_jnt_cap = rig_utils.joint(name=f'{seg.segment_name}_fkCap', side=self.side,
                                                       joint_type=nom.nonBindJnt, radius=0.04, color=2, parent=jnt)
            cap_jnt.tx.set(seg.segment_length)

            # ...Position control
            seg_start_node = jnt if seg.double_jnt else fk_ctrl
            orig_parent = seg_start_node.getParent()
            seg_start_node.setParent(seg.blend_jnt)
            gen_utils.zero_out(seg_start_node)
            seg_start_node.setParent(orig_parent) if orig_parent else seg_start_node.setParent(world=1)
            gen_utils.convert_offset(seg_start_node) if not seg.double_jnt else None


            if self.segments[n-1].double_jnt:
                node_utils.multiplyDivide(input1=fk_ctrl.rotate, input2=(0.5, 0.5, 0.5),
                                          output=self.segments[n-1].fk_jnt.rotate)
                node_utils.multiplyDivide(input1=fk_ctrl.rotate, input2=(-0.5, -0.5, -0.5),
                                          output=self.segments[n-1].fk_jnt_cap.rotate)


        # ...Wrap top of ctrl chain in buffer group --------------------------------------------------------------------
        gen_utils.convert_offset(self.segments[i].fk_ctrl, reverse=True)
        self.fk_chain_buffer = gen_utils.buffer_obj(self.segments[0].fk_ctrl, parent=self.ctrls['socket'])
        self.fk_chain_buffer.setParent(self.ctrls['socket'])

        # ...Connect FK segment lengths to settings attributes ---------------------------------------------------------
        for i, seg in enumerate(self.segments):
            if i == len(self.segments)-1:
                continue
            if seg.length_mult_node:
                pm.listConnections(seg.length_mult_node.input2, s=1, d=0, plugs=1)[0].connect(seg.fk_jnt.sx)

        # --------------------------------------------------------------------------------------------------------------
        pm.select(clear=1)





    ####################################################################################################################
    def ik_rig(self, limb_ik_start_index, limb_ik_end_index, tarsus_index=None):

        self.create_ik_jnt_chain()
        self.create_ik_ctrls(tarsus_index=tarsus_index)
        self.install_limb_ik_solver(limb_ik_start_index, limb_ik_end_index)
        self.install_extrem_ik_solver()
        if tarsus_index:
            self.install_tarsus_ik_solver(tarsus_index=tarsus_index)

        stretchy_indices = []
        compensate_seg_indices = []
        positive_limb_ik_end_index = self.segments.index(self.segments[limb_ik_end_index])
        ik_indices = range(limb_ik_start_index, positive_limb_ik_end_index)
        for i, seg in enumerate(self.segments):
            if i in ik_indices:
                if seg.double_jnt:
                    compensate_seg_indices.append(i)
                else:
                    stretchy_indices.append(i)

        self.stretchy_ik(subject_indices=stretchy_indices, compensate_seg_indices=compensate_seg_indices,
                         ik_end_index=positive_limb_ik_end_index)





    ####################################################################################################################
    def create_ik_jnt_chain(self):

        # ...Create joints ---------------------------------------------------------------------------------------------
        for seg in self.segments:
            jnt = seg.ik_jnt = rig_utils.joint(name=f'{seg.segment_name}_ik', side=self.side, joint_type=nom.nonBindJnt,
                                               radius=0.08, color=2)

            constraint_target = seg.ik_constraint_target = pm.shadingNode('transform',
                                                                          name=f'{seg.segment_name}_ik_target', au=1)
            constraint_target.setParent(jnt)
            gen_utils.zero_out(constraint_target)

            pm.select(clear=1)


        # ...Parent joints into a chain --------------------------------------------------------------------------------
        for i, seg in enumerate(self.segments):
            if i == 0:
                continue
            seg.ik_jnt.setParent(self.segments[i-1].ik_jnt)

        # ...Wrap top of chain in a buffer group -----------------------------------------------------------------------
        self.ik_jnt_chain_buffer = gen_utils.buffer_obj(self.segments[0].ik_jnt, parent=self.ctrls['socket'])

        # ...Position and orient joints --------------------------------------------------------------------------------
        match_nodes = [seg.ik_jnt for seg in self.segments]
        match_nodes[0] = self.ik_jnt_chain_buffer
        for i, node in enumerate(match_nodes):
            pm.delete(pm.parentConstraint(self.segments[i].blend_jnt, node))
            node.scale.set(1, 1, 1)

        # Orient Jnts --------------------------------------------------------------------------------------------------
        for i, node in enumerate(match_nodes):
            if i == self.segment_count - 1:
                continue
            pm.delete(pm.aimConstraint(self.jnt_position_holders[i + 1], node, worldUpType='object',
                                       aimVector=(1, 0, 0), upVector=(0, 0, 1), worldUpObject=self.pv_position_holder))
        self.segments[-1].ik_jnt.rotate.set(0, 0, 0)
        self.segments[-1].ik_jnt.scale.set(1, 1, 1)

        # ...Clean joint rotations -------------------------------------------------------------------------------------
        for seg in self.segments:
            seg.ik_jnt.jointOrient.set(seg.ik_jnt.rotate.get() + seg.ik_jnt.jointOrient.get())
            seg.ik_jnt.rotate.set(0, 0, 0)

        # ...Connect IK joint lengths to settings attributes -----------------------------------------------------------
        for i, seg in enumerate(self.segments):
            if seg.length_mult_node:
                seg.length_mult_node.output.connect(self.segments[i+1].ik_jnt.tx)

        # --------------------------------------------------------------------------------------------------------------
        pm.select(clear=1)





    ####################################################################################################################
    def get_pv_vector(self):
        # ...Pole vector vector ----------------------------------------------------------------------------------------
        self.pv_vector = gen_utils.vector_between(obj_1=self.jnt_position_holders[1],
                                                  obj_2=self.pv_position_holder)





    ####################################################################################################################
    def create_ik_ctrls(self, tarsus_index=None):

        # ...Create controls -------------------------------------------------------------------------------------------
        self.ctrls['ik_extrem'] = rig_utils.control(ctrl_info = {'shape': 'circle',
                                                                 'scale': [0.25, 0.25, 0.25],
                                                                 'up_direction': [1, 0, 0]},
                                                    name = f'{self.segments[-1].segment_name}_IK',
                                                    ctrl_type = nom.animCtrl,
                                                    side = self.side,
                                                    color = self.ctrl_colors['IK'])
        extrem_buffer = gen_utils.buffer_obj(self.ctrls['ik_extrem'], parent=self.grps['transform'])


        self.ctrls['ik_pv'] = rig_utils.control(ctrl_info = {'shape': 'sphere',
                                                             'scale': [0.1, 0.1, 0.1]},
                                                name = f'{self.pv_name}_IK',
                                                ctrl_type = nom.animCtrl,
                                                side = self.side,
                                                color = self.ctrl_colors["IK"])
        pv_buffer = gen_utils.buffer_obj(self.ctrls['ik_pv'], parent=self.grps['transform'])


        tarsus_buffer = None
        if tarsus_index:
            self.ctrls['ik_tarsus'] = rig_utils.control(ctrl_info={
                'shape': 'sphere',
                'scale': [self.segments[-2].segment_length/4,
                          self.segments[-2].segment_length/4,
                          self.segments[-2].segment_length/4]},
                name=f'{self.segments[-2].segment_name}_IK',
                ctrl_type=nom.animCtrl,
                side=self.side,
                color=self.ctrl_colors['IK'])
            tarsus_buffer = gen_utils.buffer_obj(self.ctrls['ik_tarsus'], parent=self.ctrls['ik_extrem'])


        # ...Position controls -----------------------------------------------------------------------------------------
        extrem_buffer.setParent(self.segments[-2].ik_jnt)
        gen_utils.zero_out(extrem_buffer)
        extrem_buffer.setParent(self.grps['transform'])

        gen_utils.zero_out(pv_buffer)
        pm.delete(pm.parentConstraint(self.segments[0].blend_jnt, self.segments[-2].blend_jnt, pv_buffer))
        extrem_dist = gen_utils.distance_between(position_1=self.segments[0].start_world_position,
                                                 position_2=self.segments[-2].start_world_position)
        pv_buffer.tz.set(pv_buffer.tz.get() + (-extrem_dist) * 0.8)

        if tarsus_index:
            tarsus_buffer.setParent(self.segments[-2].blend_jnt)
            gen_utils.zero_out(tarsus_buffer)
            tarsus_buffer.setParent(self.ctrls['ik_extrem'])

        # ...Drive IK extrem scale via socket ctrl's Limb Scale attr
        [pm.connectAttr(f'{self.ctrls["socket"]}.LimbScale',
                        f'{self.ctrls["ik_extrem"]}.{a}') for a in ('sx', 'sy', 'sz')]






    ####################################################################################################################
    def install_limb_ik_solver(self, start_jnt_index, end_effector_index):

        ik_handle, ik_eff = pm.ikHandle(name=f'{self.side_tag}{self.limb_name}_{nom.ikHandle}',
                                        startJoint=self.segments[start_jnt_index].ik_jnt,
                                        endEffector=self.segments[end_effector_index].ik_jnt, solver="ikRPsolver")
        ik_eff.rename(f'{self.side_tag}ik_{self.limb_name}_{nom.effector}')

        self.ik_end_marker = pm.spaceLocator(name=f'{self.side_tag}{self.limb_name}_ikEndMarker_{nom.locator}')
        self.ik_end_marker.getShape().localScale.set(0.2, 0.2, 0.2)
        self.ik_end_marker.setParent(self.segments[end_effector_index].ik_jnt)
        gen_utils.zero_out(self.ik_end_marker)
        if 'ik_tarsus' in self.ctrls:
            self.ik_end_marker.setParent(self.ctrls['ik_tarsus'])
        else:
            self.ik_end_marker.setParent(self.ctrls['ik_extrem'])
        self.ik_end_marker.rotate.set(0, 0, 0)
        ik_handle.setParent(self.ik_end_marker)
        gen_utils.zero_out(ik_handle)

        self.ik_handles["limb"], self.ik_effectors["limb"] = ik_handle, ik_eff

        self.ik_solvers["limb"] = pm.listConnections(f'{ik_handle}.ikSolver', source=True)[0]

        pm.poleVectorConstraint(self.ctrls["ik_pv"], self.ik_handles["limb"])


        # ...Display curve ---------------------------------------------------------------------------------------------
        self.ik_display_crv = rig_utils.connector_curve(name=f'{self.side_tag}ik_{self.segment_names[-2]}',
                                                        end_driver_1=self.segments[1].ik_jnt,
                                                        end_driver_2=self.ctrls['ik_pv'],
                                                        override_display_type=1, line_width=-1.0,
                                                        parent=self.grps['transform'])[0]

        if self.side == nom.rightSideTag:
            [pm.setAttr(f'{self.ik_display_crv}.{a}', lock=0) for a in gen_utils.all_transform_attrs]
            gen_utils.flip(self.ik_display_crv)
            [pm.setAttr(f'{self.ik_display_crv}.{a}', lock=1) for a in gen_utils.all_transform_attrs]


        # --------------------------------------------------------------------------------------------------------------
        pm.select(clear=1)





    ####################################################################################################################
    def install_extrem_ik_solver(self):

        # ...Create solver
        [self.ik_handles["extrem"], self.ik_effectors["extrem"]] = pm.ikHandle(
            name=f'{self.side_tag}{self.segments[-2].segment_name}_{nom.ikHandle}',
            startJoint=self.segments[-2].ik_jnt,
            endEffector=self.segments[-1].ik_jnt, solver="ikSCsolver")

        # ...Rename effector
        self.ik_effectors["extrem"].rename(
            f'{self.side_tag}ik_{self.segments[-2].segment_name}_{nom.effector}')

        self.ik_handles["extrem"].setParent(self.ctrls["ik_extrem"])





    ####################################################################################################################
    def install_tarsus_ik_solver(self, tarsus_index):

        # ...Create solver
        [self.ik_handles["tarsus"], self.ik_effectors["tarsus"]] = pm.ikHandle(
            name=f'{self.side_tag}{self.segments[tarsus_index].segment_name}_{nom.ikHandle}',
            startJoint=self.segments[tarsus_index].ik_jnt,
            endEffector=self.segments[tarsus_index+1].ik_jnt, solver="ikSCsolver")

        # ...Rename effector
        self.ik_effectors["extrem"].rename(
            f'{self.side_tag}ik_{self.segments[tarsus_index].segment_name}_{nom.effector}')

        self.ik_handles["tarsus"].setParent(self.ctrls["ik_extrem"])





    ####################################################################################################################
    def stretchy_ik(self, ik_end_index, squash=True, soft_ik=True, subject_indices=(0, 1), compensate_seg_indices=None):

        pm.addAttr(self.ctrls['socket'], longName='stretchy_ik', attributeType='float', minValue=0, maxValue=10,
                   defaultValue=10, keyable=1)
        pm.addAttr(self.ctrls['socket'], longName='squash_ik', attributeType='float', minValue=0, maxValue=10,
                   defaultValue=0, keyable=1)

        total_limb_len_sum = self.get_length_sum(ik_end_index)


        ik_extrem_dist = self.ik_extrem_dist = node_utils.distanceBetween(
            inMatrix1=self.ctrls['socket'].worldMatrix,
            inMatrix2=self.ik_end_marker.worldMatrix)

        scaled_extrem_dist = node_utils.floatMath(floatA=ik_extrem_dist.distance,
                                                  floatB=f'{self.grps["root"]}.RigScale', operation=3)

        if not compensate_seg_indices:
            extrem_dist_output = scaled_extrem_dist.outFloat
            len_total_output = total_limb_len_sum.output
        else:
            len_compensate = sum(
                [gen_utils.distance_between(obj_1=self.segments[i].ik_jnt,
                                            obj_2=self.segments[i+1].ik_jnt) for i in compensate_seg_indices])
            extrem_dist_output = node_utils.floatMath(floatA=scaled_extrem_dist.outFloat, floatB=len_compensate,
                                                      operation=1).outFloat
            len_total_output = node_utils.floatMath(floatA=total_limb_len_sum.output, floatB=len_compensate,
                                                    operation=1).outFloat


        limb_straigtness_div = node_utils.floatMath(floatA=extrem_dist_output,
                                                    floatB=len_total_output, operation=3)

        straight_condition = node_utils.condition(colorIfTrue=(limb_straigtness_div.outFloat, 0, 0),
                                                  colorIfFalse=(1, 1, 1), operation=2,
                                                  firstTerm=scaled_extrem_dist.outFloat,
                                                  secondTerm=total_limb_len_sum.output)

        [straight_condition.outColor.outColorR.connect(self.segments[i].ik_jnt.sx) for i in subject_indices]

        # ...Make stretch optional -------------------------------------------------------------------------------------
        stretch_option_remap = node_utils.remapValue(inputValue=f'{self.ctrls["socket"]}.stretchy_ik',
                                                     outputMin=1, inputMax=10,
                                                     outputMax=straight_condition.outColor.outColorR,)
        [stretch_option_remap.outValue.connect(self.segments[i].ik_jnt.sx, force=1) for i in subject_indices]


        # ...Squash option ---------------------------------------------------------------------------------------------
        if squash:
            node_utils.remapValue(inputValue=f'{self.ctrls["socket"]}.squash_ik', inputMax=10, outputMin=1,
                                  outputMax=limb_straigtness_div.outFloat,
                                  outValue=straight_condition.colorIfFalse.colorIfFalseR)


        # ...Include Soft IK effect ------------------------------------------------------------------------------------
        if soft_ik:
            pm.addAttr(self.ctrls['socket'], longName='soft_ik', niceName='Soft IK', attributeType=float,
                       minValue=0, maxValue=10, defaultValue=0, keyable=1)

            num_space_div = node_utils.floatMath(floatA=100, floatB=total_limb_len_sum.output, operation=3)

            ratio_mult = node_utils.multDoubleLinear(input1=num_space_div.outFloat, input2=ik_extrem_dist.distance)

            anim_crv = self.soft_ik_curve(input=ratio_mult.output)

            soft_ik_weight_remap = node_utils.remapValue(inputValue=f'{self.ctrls["socket"]}.soft_ik',
                                                         outputMax=anim_crv.output, inputMax=10, outputMin=1)

            soft_ik_weight_mult = node_utils.multDoubleLinear(input1=stretch_option_remap.outValue,
                                                              input2=soft_ik_weight_remap.outValue)
            [soft_ik_weight_mult.output.connect(self.segments[i].ik_jnt.sx, force=1) for i in subject_indices]






    ####################################################################################################################
    def get_length_sum(self, ik_end_index):

        # ...Combine initial two lengths in first sum
        first_sum = node_utils.addDoubleLinear(input1=self.segments[0].segment_length,
                                               input2=self.segments[1].segment_length)
        prev_sum, final_sum = first_sum, first_sum

        # ...Add each sum as input to the next until all lengths have been added together
        for i in range(2, ik_end_index):
            new_sum = node_utils.addDoubleLinear(input1=prev_sum.output,
                                                 input2=self.segments[i].segment_length)
            prev_sum, final_sum = new_sum, new_sum

        return final_sum





    ####################################################################################################################
    def soft_ik_curve(self, input=None, output=None):

        # ...Create anim curve node
        anim_curve = pm.shadingNode('animCurveUU', name=f'{self.side_tag}_anim_crv_softIk_{self.limb_name}', au=1)
        # ...Shape its curve
        if input:
            pm.connectAttr(input, anim_curve + '.input')
        pm.setKeyframe(anim_curve, float=10, value=1)
        pm.setKeyframe(anim_curve, float=77.5, value=0.91)
        pm.setKeyframe(anim_curve, float=100, value=1)

        pm.keyTangent(anim_curve, index=(0, 0), lock=False, edit=True)
        pm.keyTangent(anim_curve, index=(0, 0), weightedTangents=True, edit=True)
        pm.keyTangent(anim_curve, index=(0, 0), outAngle=0, edit=True)
        pm.keyTangent(anim_curve, index=(0, 0), outWeight=544.42547, edit=True)

        pm.keyTangent(anim_curve, index=(1, 1), lock=False, edit=True)
        pm.keyTangent(anim_curve, index=(1, 1), weightedTangents=True, edit=True)
        pm.keyTangent(anim_curve, index=(1, 1), inAngle=0, edit=True)
        pm.keyTangent(anim_curve, index=(1, 1), inWeight=396.596271, edit=True)
        pm.keyTangent(anim_curve, index=(1, 1), outAngle=0, edit=True)
        pm.keyTangent(anim_curve, index=(1, 1), outWeight=300, edit=True)

        pm.keyTangent(anim_curve, index=(2, 2), lock=False, edit=True)
        pm.keyTangent(anim_curve, index=(2, 2), weightedTangents=True, edit=True)
        pm.keyTangent(anim_curve, index=(2, 2), inAngle=0.023, edit=True)
        pm.keyTangent(anim_curve, index=(2, 2), inWeight=40.000005, edit=True)

        if output:
            pm.connectAttr(anim_curve + '.output', output)


        return anim_curve






    ####################################################################################################################
    def setup_kinematic_blend(self):
        """
        Setup limb blending between FK and IK rigs.
        """

        pm.addAttr(self.ctrls['socket'], longName="fkIk", niceName="FK / IK", attributeType="float", minValue=0,
                   maxValue=10, defaultValue=10, keyable=1)

        # ...Outfit blend attribute with mult nodes to get to 0-to-1 space from a 0-to-10 attr input
        blend_driver_plugs = gen_utils.create_attr_blend_nodes(attr='fkIk', node=self.ctrls['socket'], reverse=True)


        for i, seg in enumerate(self.segments):
            if i == len(self.segments)-1:
                continue
            constraint = pm.orientConstraint(seg.fk_jnt, seg.ik_jnt, seg.blend_jnt)

            weights = pm.orientConstraint(constraint, query=1, weightAliasList=1)
            pm.connectAttr(blend_driver_plugs.rev.outputX, weights[0])
            pm.connectAttr(blend_driver_plugs.multOutput, weights[1])

            seg.blend_jnt.jointOrient.set(0, 0, 0)


        # ...Blend joint scale
        self.kinematic_blend_jnt_lengths(blend_driver_plugs)


        # ...FK/IK controls visibility
        for seg in self.segments:
            if seg.fk_ctrl:
                blend_driver_plugs.rev.outputX.connect(seg.fk_ctrl.visibility)

        for key in ['ik_extrem', 'ik_pv', 'ik_tarsus']:
            if key in self.ctrls:
                blend_driver_plugs.mult.output.connect(self.ctrls[key].visibility)
        blend_driver_plugs.mult.output.connect(self.ik_display_crv.getShape().visibility)





    ####################################################################################################################
    def kinematic_blend_jnt_lengths(self, blend_driver_plugs):

        # ...Joint scale
        self.kinematic_blend_jnt_scale(blend_driver_plugs)
        # ...Joint cap translation
        self.kinematic_blend_jnt_cap_translate(blend_driver_plugs)





    ####################################################################################################################
    def kinematic_blend_jnt_scale(self, blend_driver_plugs):

        for i, seg in enumerate(self.segments):
            if seg.dynamic_length:
                # ...Create blend node
                blend = pm.shadingNode("blendTwoAttr", au=1)
                # ...Blend inputs
                self.segments[i].fk_jnt.sx.connect(blend.input[0])
                self.segments[i].ik_jnt.sx.connect(blend.input[1])
                # ...Drive blend
                pm.connectAttr(blend_driver_plugs.multOutput, blend.attributesBlender)
                # ...Output blend
                blend.output.connect(self.segments[i].blend_jnt.sx)





    ####################################################################################################################
    def kinematic_blend_jnt_cap_translate(self, blend_driver_plugs):

        for i, seg in enumerate(self.segments):
            if seg.dynamic_length:
                # ...Create blend node
                blend = pm.shadingNode("blendTwoAttr", au=1)
                # ...Blend inputs
                self.segments[i].fk_jnt.getChildren()[0].tx.connect(blend.input[0])
                self.segments[i+1].ik_jnt.tx.connect(blend.input[1])
                # ...Drive blend
                pm.connectAttr(blend_driver_plugs.multOutput, blend.attributesBlender)
                # ...Output blend
                blend.output.connect(self.segments[i+1].blend_jnt.tx)





    ####################################################################################################################
    def install_ribbon(self, start_node, end_node, bend_jnts, segment, length_ends):

        ctrl_size = 0.7
        tweak_color = 1

        ribbon_up_vector = (0, 0, -1)
        if self.side == nom.rightSideTag:
            ribbon_up_vector = (0, 0, 1)

        # ...Create ribbons
        segment_ribbon = rig_utils.ribbon_plane(name=self.segments[0].segment_name,
                                                start_obj=start_node,
                                                end_obj=end_node,
                                                up_obj=self.pv_position_holder,
                                                density=self.roll_jnt_resolution,
                                                side=self.side,
                                                up_vector=ribbon_up_vector)
        segment_ribbon["nurbsStrip"].setParent(self.grps['noTransform'])
        segment_ribbon["nurbsStrip"].scale.set(1, 1, 1)

        # ...Skin ribbons
        pm.select(bend_jnts[0], bend_jnts[1], bend_jnts[2], replace=1)
        pm.select(segment_ribbon["nurbsStrip"], add=1)
        pm.skinCluster(maximumInfluences=1, toSelectedBones=1)

        # ...Tweak ctrls
        if self.side == nom.leftSideTag:
            tweak_color = self.ctrl_colors["sub"][0]
        elif self.side == nom.rightSideTag:
            tweak_color = self.ctrl_colors["sub"][1]

        upperlimb_tweak_ctrls = rig_utils.ribbon_tweak_ctrls(ribbon = segment_ribbon["nurbsStrip"],
                                                             ctrl_name = segment.segment_name,
                                                             length_ends = length_ends,
                                                             length_attr = segment.length_mult_node.output,
                                                             attr_ctrl = self.ctrls['socket'],
                                                             side = self.side,
                                                             ctrl_color = tweak_color,
                                                             ctrl_resolution = 5,
                                                             parent = self.grps['noTransform'],
                                                             ctrl_size=ctrl_size)
        self.tweak_ctrls.append(upperlimb_tweak_ctrls)










########################################################################################################################
########################################################################################################################
class LimbSegment:
    def __init__(
        self,
        segment_name,
        index,
        start_world_position,
        end_world_position,
        side = None,
        dynamic_length = None,
        double_jnt_status = None
    ):
        self.segment_name = segment_name
        self.index = index
        self.side = side
        self.side_tag = f'{self.side}_' if self.side else ""
        self.start_world_position = start_world_position
        self.end_world_position = end_world_position
        self.dynamic_length = dynamic_length if dynamic_length else False
        self.double_jnt = double_jnt_status
        self.fk_ctrl = None
        self.fk_jnt_cap = None
        self.bend_jnts = []
        self.bend_ctrls = []

        self.segment_length = self.record_length()
        self.length_mult_node = None







    ####################################################################################################################
    def record_length(self):
        if not self.end_world_position:
            return 0
        return gen_utils.distance_between(position_1=self.start_world_position, position_2=self.end_world_position)

    ####################################################################################################################
    def create_length_mult_node(self, ctrl):

        length_attr_name = f'{self.segment_name}Len'
        pm.addAttr(ctrl, longName=length_attr_name, attributeType="float", minValue=0.001, defaultValue=1, keyable=1)
        self.length_mult_node = node_utils.multDoubleLinear(input1=self.segment_length,
                                                            input2=f'{ctrl}.{length_attr_name}')
