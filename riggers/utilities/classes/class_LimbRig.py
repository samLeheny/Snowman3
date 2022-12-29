# Title: class_LimbRig.py
# Author: Sam Leheny
# Contact: samleheny@live.com

# Description:


###########################
##### Import Commands #####
import importlib
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
###########################
###########################





########################################################################################################################
########################################################################################################################
class LimbRig:
    def __init__(
        self,
        limb_name,
        side = None,
        segment_names = None,
        jnt_positions = None,
        socket_name = None,
        pv_name = None
    ):
        self.limb_name = limb_name
        self.side = side
        self.side_tag = f'{self.side}_' if self.side else ""
        self.segments = None
        self.segment_count = None
        self.segment_names = segment_names
        self.jnt_positions = jnt_positions
        self.limb_ik_start_jnt_index = None
        self.limb_ik_end_jnt_index = None
        self.limb_ik_mid_jnt_index = None
        self.jnt_position_holders = None
        self.pv_position_holder = None
        self.grps = {}
        self.ctrls = {}
        self.ctrl_colors = ctrl_colors
        self.socket_name = socket_name if socket_name else default_socket_name
        self.pv_name = pv_name if pv_name else default_pv_name





    ####################################################################################################################
    def build_prefab(self, prefab_key):
        prefab_methods = {
            "plantigrade": self.build_prefab_plantigrade,
            #"plantigrade_doubleKnee": self.build_prefab_plantigrade_doubleKnee,
            #"digitigrade": self.build_prefab_digitigrade,
            #"digitigrade_doubleKnees": self.build_prefab_digitigrade_doubleKnees,
            #"digitigrade_doubleFrontKnee": self.build_prefab_digitigrade_doubleFrontKnee,
        }

        prefab_methods[prefab_key]()





    ####################################################################################################################
    def build_prefab_plantigrade(self):

        default_seg_names = ('upperlimb', 'lowerlimb', 'extrem')
        default_jnt_positions = ((0, 0, 0), (1, 0, -0.5), (2, 0, 0), (2.5, 0, 0))

        if not self.segment_names: self.segment_names = default_seg_names
        if not self.jnt_positions: self.jnt_positions = default_jnt_positions

        for i, name in enumerate(default_seg_names):
            new_segment = LimbSegment(segment_name = name,
                                      side = self.side,
                                      start_world_position = default_jnt_positions[i],
                                      end_world_position = default_jnt_positions[i + 1])
            self.segments.append(new_segment)

        self.segment_count = len(self.segments)
        self.limb_ik_start_jnt_index = 0
        self.limb_ik_end_jnt_index = -2
        self.limb_ik_mid_jnt_index = 1

        self.create_position_holders()
        self.create_rig_grps()
        self.create_rig_socket_ctrl()
        self.create_length_mult_nodes()
        ### self.collect_all_segment_nodes(main_seg_indices=(0, 1))
        self.blend_rig()
        self.fk_rig(('s', 's', 's'))
        self.ik_rig(dyn_length_jnts=(0, 1), ik_jnt_indices=(0, 2), extrem_jnt_indices=(2, 3))
        self.setup_kinematic_blend(dyn_len_jnt_indices=(0, 1))





    ####################################################################################################################
    def create_position_holders(self):

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
                                       worldUpType='object', aimVector=(1, 0, 0), upVector=(0, 0, -1),
                                       worldUpObject=self.pv_position_holder))
        pm.delete(pm.orientConstraint(self.jnt_position_holders[-2], self.jnt_position_holders[-1]))

        # ...Mirror transforms if this is a right-sided limb
        if self.side == nom.rightSideTag:
            gen_utils.flip(locs_grp)





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
        loc.tx.set(sum([seg.segment_lengths for seg in self.segments.values()]) * -1)
        ### loc.tz.set(sum(self.segment_lengths)*-1)





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

        [seg.create_length_mult_node(self.ctrls['socket']) if seg.dynamic_length else None for seg in self.segments]





    ####################################################################################################################
    def blend_rig(self):

        # ...Blend skeleton
        self.create_blend_jnts()

        # ...Rollers
        '''lowerlimb_roller = self.install_rollers(start_node = self.blend_jnts[1],
                                                end_node = self.blend_jnts[2],
                                                seg_name = self.seg_names[1],
                                                start_rot_match = self.blend_jnts[0],
                                                end_rot_match = self.blend_jnts[2],
                                                ctrl_mid_influ = True,
                                                populate_ctrls = (1, 1, 1),
                                                ctrl_color = self.ctrl_colors["other"],
                                                side = self.side,
                                                parent = self.no_transform_grp)

        upperlimb_roller = self.install_rollers(start_node = self.blend_jnts[0],
                                                end_node = self.blend_jnts[1],
                                                seg_name = self.seg_names[0],
                                                start_rot_match = self.ctrls["rig_socket"],
                                                end_rot_match = lowerlimb_roller["start_ctrl"],
                                                populate_ctrls = (1, 1, 0),
                                                ctrl_color = self.ctrl_colors["other"],
                                                side = self.side,
                                                parent = self.no_transform_grp)

        self.bend_ctrls = (upperlimb_roller["start_ctrl"], upperlimb_roller["mid_ctrl"], lowerlimb_roller["start_ctrl"],
                           lowerlimb_roller["mid_ctrl"], lowerlimb_roller["end_ctrl"])
        self.bend_jnts = (upperlimb_roller["start_jnt"], upperlimb_roller["mid_jnt"], upperlimb_roller["end_jnt"],
                          lowerlimb_roller["start_jnt"], lowerlimb_roller["mid_jnt"], lowerlimb_roller["end_jnt"])

        self.roll_socket_target = upperlimb_roller["roll_socket_target"]



        self.ctrls["upperlimb_bend_start"] = self.bend_ctrls[0]
        self.ctrls["upperlimb_bend_mid"] = self.bend_ctrls[1]
        self.ctrls["mid_limb_pin"] = self.bend_ctrls[2]
        self.ctrls["lowerlimb_bend_mid"] = self.bend_ctrls[3]
        self.ctrls["lowerlimb_bend_end"] = self.bend_ctrls[4]


        # ...Bend ctrls vis
        bend_ctrl_vis_attr_string = "BendCtrls"
        if not pm.attributeQuery(bend_ctrl_vis_attr_string, node=self.ctrls["rig_socket"], exists=1):
            pm.addAttr(self.ctrls["rig_socket"], longName=bend_ctrl_vis_attr_string, attributeType="enum", keyable=0,
                       enumName="Off:On")
            pm.setAttr(self.ctrls["rig_socket"] + '.' + bend_ctrl_vis_attr_string, channelBox=1)

        for ctrl in (upperlimb_roller["start_ctrl"], upperlimb_roller["mid_ctrl"],
                     lowerlimb_roller["mid_ctrl"], lowerlimb_roller["end_ctrl"]):
            pm.connectAttr(self.ctrls["rig_socket"] + "." + bend_ctrl_vis_attr_string, ctrl.visibility)'''





    ####################################################################################################################
    def create_blend_jnts(self):

        pm.select(clear=1)

        # ...Create joints ---------------------------------------------------------------------------------------------

        for i in range(self.segment_count + 1):
            jnt = rig_utils.joint(name=f'{self.jnt_names[i]}_blend', side=self.side, joint_type=nom.nonBindJnt,
                                  radius=0.1)
            self.blend_jnts.append(jnt)
            jnt.setParent(self.blend_jnts[i-1]) if i > 0 else None


        # ...Wrap top of chain in a buffer group -----------------------------------------------------------------------
        self.blend_jnt_chain_buffer = gen_utils.buffer_obj(self.blend_jnts[0])
        if self.side == nom.rightSideTag:
            gen_utils.flip(self.blend_jnt_chain_buffer)


        # Position Jnts ------------------------------------------------------------------------------------------------
        for i in range(1, self.segment_count + 1):
            self.blend_jnts[i].tx.set(self.segment_lengths[i-1])


        # Orient Jnts --------------------------------------------------------------------------------------------------
        nodes_to_orient = self.blend_jnts[:]
        nodes_to_orient[0] = self.blend_jnt_chain_buffer
        nodes_to_orient.remove(nodes_to_orient[-1])
        for i, node in enumerate(nodes_to_orient):
            pm.delete(pm.aimConstraint(self.position_holders[i+1], node, worldUpType="scene", aimVector=(1, 0, 0),
                                       upVector=(0, 1, 0), worldUpVector=(0, 1, 0)))

        self.blend_jnts[-1].rotate.set(0, 0, 0)
        self.blend_jnts[-1].scale.set(1, 1, 1)


        # ...Clean joint rotations -------------------------------------------------------------------------------------
        for i in range(1, self.segment_count + 1):
            self.blend_jnts[i].jointOrient.set(self.blend_jnts[i].rotate.get() + self.blend_jnts[i].jointOrient.get())
            self.blend_jnts[i].rotate.set(0, 0, 0)


        self.blend_jnt_chain_buffer.setParent(self.ctrls['socket'])


        rot = self.blend_jnt_chain_buffer.rotate.get()
        gen_utils.matrix_constraint(objs=[self.ctrls['socket'], self.blend_jnt_chain_buffer], decompose=True,
                                    translate=True, rotate=False, scale=False, shear=False)
        self.blend_jnt_chain_buffer.rotate.set(rot)



        # --------------------------------------------------------------------------------------------------------------
        pm.select(clear=1)









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
        dynamic_length = None
    ):
        self.segment_name = segment_name
        self.index = index
        self.side = side
        self.side_tag = f'{self.side}_' if self.side else ""
        self.start_world_position = start_world_position
        self.end_world_position = end_world_position
        self.dynamic_length = dynamic_length if dynamic_length else False

        self.segment_length = self.record_length()
        self.length_mult_node = None







    ####################################################################################################################
    def record_length(self):

        return gen_utils.distance_between(position_1=self.start_world_position, position_2=self.end_world_position)

    ####################################################################################################################
    def create_length_mult_node(self, ctrl):

        length_attr_name = f'{self.segment_name[self.index]}Len'
        pm.addAttr(ctrl, longName=length_attr_name, attributeType="float", minValue=0.001, defaultValue=1, keyable=1)
        return node_utils.multDoubleLinear(input1=self.segment_length, input2=f'{ctrl}.{length_attr_name}')
