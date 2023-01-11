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
class LimbRig:
    def __init__(
        self,
        limb_name,
        side = None,
        segment_count = None,
        jnt_positions = None,
        segment_names = None,
        socket_name = None,
        pv_name = None,
        prefab = None
    ):
        self.limb_name = limb_name
        self.side = side
        self.side_tag = f'{self.side}_' if self.side else ""
        self.segment_count = segment_count
        self.jnt_positions = jnt_positions
        self.segment_names = segment_names
        self.jnt_names = list(self.segment_names[:]) + [f'{self.segment_names[-1]}End']
        self.socket_name = socket_name if socket_name else default_socket_name
        self.ctrl_colors = ctrl_colors
        self.pv_name = pv_name if pv_name else default_pv_name
        self.prefab = prefab

        self.grps = {}
        self.ctrls = {}
        self.segment_lengths = None
        self.length_mult_nodes = []
        self.blend_jnts = []
        self.blend_jnt_chain_buffer = None
        self.position_holders = []
        self.pv_position_holder = None
        self.fk_ctrls = []
        self.fk_jnt_caps = []
        self.fk_jnts = []
        self.fk_constraint_targets = []
        self.fk_ctrl_chain_buffer = None
        self.ik_jnts = []
        self.ik_constraint_targets = []
        self.ik_jnt_chain_buffer = None
        self.ik_handles = {}
        self.ik_effectors = {}
        self.ik_solvers = {}
        self.ik_display_crv = None
        self.ik_extrem_dist = None
        self.all_seg_length_nodes = []
        self.ik_end_marker = None

        self.build_prefab(self.prefab)





    ####################################################################################################################
    def build_prefab(self, prefab_key):

        prefab_methods = {
            "plantigrade" : self.build_prefab_plantigrade,
            "plantigrade_doubleKnee" : self.build_prefab_plantigrade_doubleKnee,
            "digitigrade" : self.build_prefab_digitigrade,
            "digitigrade_doubleKnees" : self.build_prefab_digitigrade_doubleKnees,
            "digitigrade_doubleFrontKnee" : self.build_prefab_digitigrade_doubleFrontKnee,
        }

        prefab_methods[prefab_key]()





    ####################################################################################################################
    def build_prefab_plantigrade(self):

        default_seg_names = ('upperlimb', 'lowerlimb', 'extrem')
        default_jnt_positions = ((0, 0, 0), (1, 0, -0.5), (2, 0, 0), (2.5, 0, 0))

        self.segment_count = len(default_seg_names)
        if not self.segment_names: self.segment_names = default_seg_names
        if not self.jnt_positions: self.jnt_positions = default_jnt_positions
        self.segment_lengths = self.get_segment_lengths()

        self.create_position_holders(start_socket_index=0, end_socket_index=-2, up_vector_index=1)
        self.create_rig_grps()
        self.create_rig_socket_ctrl()
        self.collect_all_segment_nodes(main_seg_indices=(0, 1))
        self.blend_rig()
        self.fk_rig(('s', 's', 's'))
        self.ik_rig(dyn_length_jnts=(0, 1), ik_jnt_indices=(0, 2), extrem_jnt_indices=(2, 3))
        self.setup_kinematic_blend(dyn_len_jnt_indices=(0, 1))





    ####################################################################################################################
    def build_prefab_plantigrade_doubleKnee(self):

        default_seg_names = ('upperlimb', 'joint', 'lowerlimb', 'extrem')
        default_jnt_positions = ((0, 0, 0), (0.9, 0, -0.5), (1.1, 0, -0.5), (2, 0, 0), (2.5, 0, 0))

        self.segment_count = len(default_seg_names)
        if not self.segment_names: self.segment_names = default_seg_names
        if not self.jnt_positions: self.jnt_positions = default_jnt_positions
        self.segment_lengths = self.get_segment_lengths()

        self.create_position_holders(start_socket_index=0, end_socket_index=-2, up_vector_index=1)
        self.create_rig_grps()
        self.create_rig_socket_ctrl()
        self.collect_all_segment_nodes(main_seg_indices=(0, 2))
        self.blend_rig()
        self.fk_rig(('s', 'd', 's'))
        self.ik_rig(dyn_length_jnts=(0, 2), ik_jnt_indices=(0, 3), extrem_jnt_indices=(3, 4),
                    compensate_seg_indices=(1,))
        self.setup_kinematic_blend(dyn_len_jnt_indices=(0, 2))





    ####################################################################################################################
    def build_prefab_digitigrade(self):

        default_seg_names = ('upperlimb', 'lowerlimb', 'tarsus', 'extrem')
        default_jnt_positions = ((0, 0, 0), (0.75, 0, -0.5), (1.5, 0, 0.25), (2, 0, 0), (2.5, 0, 0))

        self.segment_count = len(default_seg_names)
        if not self.segment_names: self.segment_names = default_seg_names
        if not self.jnt_positions: self.jnt_positions = default_jnt_positions
        self.segment_lengths = self.get_segment_lengths()

        self.create_position_holders(start_socket_index=0, end_socket_index=-3, up_vector_index=1)
        self.create_rig_grps()
        self.create_rig_socket_ctrl()
        self.collect_all_segment_nodes(main_seg_indices=(0, 1, 2))
        self.blend_rig()
        self.fk_rig(('s', 's', 's', 's'))
        self.ik_rig(dyn_length_jnts=(0, 1), ik_jnt_indices=(0, 2), extrem_jnt_indices=(3, 4), tarsus_indices=(-3, -2))
        self.setup_kinematic_blend(dyn_len_jnt_indices=(0, 1, 2))





    ####################################################################################################################
    def build_prefab_digitigrade_doubleKnees(self):

        default_seg_names = ('upperlimb', 'frontKnee', 'lowerlimb', 'backKnee', 'tarsus', 'extrem')
        default_jnt_positions = ((0, 0, 0), (0.65, 0, -0.5), (0.85, 0, -0.5), (1.4, 0, 0.25), (1.6, 0, 0.25), (2, 0, 0),
                                 (2.5, 0, 0))

        self.segment_count = len(default_seg_names)
        if not self.segment_names: self.segment_names = default_seg_names
        if not self.jnt_positions: self.jnt_positions = default_jnt_positions
        self.segment_lengths = self.get_segment_lengths()

        self.create_position_holders(start_socket_index=0, end_socket_index=-4, up_vector_index=1)
        self.create_rig_grps()
        self.create_rig_socket_ctrl()
        self.collect_all_segment_nodes(main_seg_indices=(0, 2, 4))
        self.blend_rig()
        self.fk_rig(('s', 'd', 'd', 's'))
        self.ik_rig(dyn_length_jnts=(0, 2), ik_jnt_indices=(0, 3), extrem_jnt_indices=(5, 6), tarsus_indices=(-3, -2),
                    compensate_seg_indices=(1,))
        self.setup_kinematic_blend(dyn_len_jnt_indices=(0, 2, 4))





    ####################################################################################################################
    def build_prefab_digitigrade_doubleFrontKnee(self):

        default_seg_names = ('upperlimb', 'frontKnee', 'lowerlimb', 'tarsus', 'extrem')
        default_jnt_positions = ((0, 0, 0), (0.65, 0, -0.5), (0.85, 0, -0.5), (1.5, 0, 0.25), (2, 0, 0), (2.5, 0, 0))

        self.segment_count = len(default_seg_names)
        if not self.segment_names: self.segment_names = default_seg_names
        if not self.jnt_positions: self.jnt_positions = default_jnt_positions
        self.segment_lengths = self.get_segment_lengths()

        self.create_position_holders(start_socket_index=0, end_socket_index=-3, up_vector_index=1)
        self.create_rig_grps()
        self.create_rig_socket_ctrl()
        self.collect_all_segment_nodes(main_seg_indices=(0, 2, 3))
        self.blend_rig()
        self.fk_rig(('s', 'd', 's', 's'))
        self.ik_rig(dyn_length_jnts=(0, 2), ik_jnt_indices=(0, 3), extrem_jnt_indices=(4, 5), tarsus_indices=(-3, -2),
                    compensate_seg_indices=(1,))
        self.setup_kinematic_blend(dyn_len_jnt_indices=(0, 2, 3))





    ####################################################################################################################
    def create_position_holders(self, start_socket_index, end_socket_index, up_vector_index):

        locs_grp = pm.group(name=f'{self.side_tag}position_holders_TEMP', world=1, em=1)

        #...Create and position locs
        for i, pos in enumerate(self.jnt_positions):
            loc = pm.spaceLocator(name=f'{self.side_tag}position_holder_{str(i)}_{nom.locator}')
            loc.setParent(locs_grp)
            loc.translate.set(pos)
            loc.getShape().localScale.set(0.15, 0.15, 0.15)
            self.position_holders.append(loc)

        #...Pole vector position holder
        self.create_pv_position_holder(locs_grp, start_socket_index=start_socket_index,
                                       end_socket_index=end_socket_index, up_vector_index=up_vector_index)

        #...Orient locs
        for i in range(0, len(self.position_holders)):
            pm.delete(pm.aimConstraint(self.position_holders[i], self.position_holders[i-1], worldUpType='object',
                                       aimVector=(1, 0, 0), upVector=(0, 0, -1), worldUpObject=self.pv_position_holder))
        pm.delete(pm.orientConstraint(self.position_holders[-2], self.position_holders[-1]))

        #...Mirror transforms if this is a right-sided limb
        if self.side == nom.rightSideTag:
            gen_utils.flip(locs_grp)





    ####################################################################################################################
    def create_pv_position_holder(self, parent, start_socket_index, end_socket_index, up_vector_index):

        loc = self.pv_position_holder = pm.spaceLocator(name=f'{self.side_tag}position_holder_PV_{nom.locator}')
        loc.getShape().localScale.set(0.15, 0.15, 0.15)
        loc.setParent(parent)
        pm.delete(pm.pointConstraint(self.position_holders[start_socket_index],
                                     self.position_holders[end_socket_index], loc))
        pm.delete(pm.aimConstraint(self.position_holders[up_vector_index], loc, worldUpType='object',
                  worldUpObject=self.position_holders[0], aimVector=(0, 0, -1), upVector=(-1, 0, 0)))
        gen_utils.buffer_obj(loc)
        loc.tz.set(sum(self.segment_lengths)*-1)
    
    
    
    

    ####################################################################################################################
    def make_jnt_names(self):

        jnt_names = list(self.segment_names)
        jnt_names.append(f'{jnt_names[-1]}End')
        return jnt_names





    ####################################################################################################################
    def create_rig_grps(self):

        self.grps['root'] = pm.group(name=f'{self.side_tag}{self.limb_name}_RIG', world=1, em=1)

        self.grps['transform'] = pm.group(name="transform", p=self.grps['root'], em=1)

        self.grps['noTransform'] = pm.group(name="noTransform", p=self.grps['root'], em=1)
        self.grps['noTransform'].inheritsTransform.set(0, lock=1)

        if self.side == nom.rightSideTag:
            gen_utils.flip(self.grps['root'])
            gen_utils.flip(self.grps['noTransform'])

        #...Rig Scale attribute
        pm.addAttr(self.grps['root'], longName="RigScale", minValue=0.001, defaultValue=1, keyable=0)

        pm.select(clear=1)





    ####################################################################################################################
    def create_rig_socket_ctrl(self):

        #...Create controls
        ctrl = self.ctrls['socket'] = rig_utils.control(ctrl_info = {'shape': 'tag_hexagon',
                                                                     'scale': [0.2, 0.2, 0.2]},
                                                        name = f'{self.socket_name}Pin',
                                                        ctrl_type = nom.animCtrl,
                                                        side = self.side,
                                                        color = self.ctrl_colors['other'])

        #...Position ctrl in scene and hierarchy
        ctrl.translate.set(self.jnt_positions[0])
        ctrl.setParent(self.grps['transform'])
        gen_utils.convert_offset(ctrl)
        gen_utils.buffer_obj(ctrl)

        #...Rig Scale attribute
        pm.addAttr(ctrl, longName='LimbScale', minValue=0.001, defaultValue=1, keyable=1)
        [pm.connectAttr(f'{ctrl}.LimbScale', f'{ctrl}.{a}') for a in ('sx', 'sy', 'sz')]

        '''
        #...Add settings attributes
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
    def get_segment_lengths(self):

        return [gen_utils.distance_between(position_1=self.jnt_positions[i], position_2=self.jnt_positions[i + 1])
                for i in range(self.segment_count)]





    ####################################################################################################################
    def collect_all_segment_nodes(self, main_seg_indices):

        for i in range(self.segment_count):

            if i in main_seg_indices:
                mult = self.install_limb_length_attrs(i)
                self.all_seg_length_nodes.append(mult.output)
            else:
                value_holder = node_utils.floatConstant(inFloat=self.segment_lengths[i])
                self.all_seg_length_nodes.append(value_holder.outFloat)





    ####################################################################################################################
    def install_limb_length_attrs(self, seg_index):

        length_attr_name = f'{self.segment_names[seg_index]}Len'
        pm.addAttr(self.ctrls['socket'], longName=length_attr_name, attributeType="float",
                   minValue=0.001, defaultValue=1, keyable=1)

        mult = node_utils.multDoubleLinear(input1=self.segment_lengths[seg_index],
                                           input2=f'{self.ctrls["socket"]}.{length_attr_name}')
        self.length_mult_nodes.append(mult)

        return mult





    ####################################################################################################################
    def blend_rig(self):

        #...Blend skeleton
        self.create_blend_jnts()

        #...Rollers
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


        #...Bend ctrls vis
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

        #...Create joints ---------------------------------------------------------------------------------------------
        for i in range(self.segment_count + 1):
            jnt = rig_utils.joint(name=f'{self.jnt_names[i]}_blend', side=self.side, joint_type=nom.nonBindJnt,
                                  radius=0.1)
            self.blend_jnts.append(jnt)
            jnt.setParent(self.blend_jnts[i-1]) if i > 0 else None


        #...Wrap top of chain in a buffer group -----------------------------------------------------------------------
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


        #...Clean joint rotations -------------------------------------------------------------------------------------
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





    ####################################################################################################################
    def fk_rig(self, fk_jnt_types):

        i = 0
        for n, x in enumerate(fk_jnt_types):

            jnt_i = i
            if fk_jnt_types[n] in ('single', 's'):
                jnt_i = i
            elif fk_jnt_types[n] in ('double', 'd'):
                jnt_i = i + 1
            #...Single-jointed FK ctrl
            #...Create and parent control
            parent = self.fk_jnt_caps[n-1] if n > 0 else None
            fk_ctrl = rig_utils.control(ctrl_info={'shape': 'cube',
                                                   'scale': [self.segment_lengths[jnt_i] / 2 * 0.93,
                                                             self.segment_lengths[jnt_i] / 2 * (0.93 * 0.25),
                                                             self.segment_lengths[jnt_i] / 2 * (0.93 * 0.25)],
                                                   'offset': [self.segment_lengths[jnt_i] / 2, 0, 0]},
                                        name=f'{self.segment_names[jnt_i]}_FK',
                                        ctrl_type=nom.animCtrl,
                                        side=self.side,
                                        parent=parent,
                                        color=self.ctrl_colors['FK'])
            self.ctrls[f'{self.segment_names[jnt_i]}_FK'] = fk_ctrl
            self.fk_ctrls.append(fk_ctrl)

            jnt = rig_utils.joint(name=f'{self.segment_names[jnt_i]}_fk', side=self.side, joint_type=nom.nonBindJnt,
                                  radius=0.08, color=2, parent=fk_ctrl)
            self.fk_jnts.append(jnt)
            cap_jnt = rig_utils.joint(name=f'{self.segment_names[jnt_i]}_fkCap', side=self.side,
                                      joint_type=nom.nonBindJnt, radius=0.04, color=2, parent=jnt)
            self.fk_jnt_caps.append(cap_jnt)
            cap_jnt.tx.set(self.segment_lengths[jnt_i])


            fk_ctrl.setParent(self.blend_jnts[jnt_i])
            gen_utils.zero_out(fk_ctrl)
            fk_ctrl.setParent(parent) if parent else fk_ctrl.setParent(world=1)


            if fk_jnt_types[n] in ('double', 'd'):
                roller_1 = pm.shadingNode('transform', name=f'{self.side_tag}{self.jnt_names[i]}_roller', au=1)
                roller_1.setParent(self.blend_jnts[i])
                gen_utils.zero_out(roller_1)
                roller_1.setParent(parent)

                roller_2 = pm.shadingNode('transform', name=f'{self.side_tag}{self.jnt_names[i + 1]}_roller', au=1)
                roller_2.setParent(self.blend_jnts[jnt_i])
                gen_utils.zero_out(roller_2)
                roller_2.setParent(roller_1)

                fk_ctrl.setParent(roller_2)
                [gen_utils.convert_offset(r) for r in (roller_1, roller_2)]

                node_utils.multiplyDivide(input1=fk_ctrl.rotate, input2=(0.5, 0.5, 0.5), output=roller_1.rotate)
                node_utils.multiplyDivide(input1=fk_ctrl.rotate, input2=(-0.5, -0.5, -0.5), output=roller_2.rotate)

            #...Position control

            #...Add relevant items into FK constraint targets list
            if fk_jnt_types[n] in ('double', 'd'):
                self.fk_constraint_targets.append(roller_1)
            self.fk_constraint_targets.append(jnt)

            if fk_jnt_types[n] in ('single', 's'):
                i += 1
            elif fk_jnt_types[n] in ('double', 'd'):
                i += 2


        #...Wrap top of ctrl chain in buffer group --------------------------------------------------------------------
        self.fk_ctrl_chain_buffer = gen_utils.buffer_obj(self.fk_ctrls[0], parent=self.ctrls['socket'])
        self.fk_ctrl_chain_buffer.setParent(self.blend_jnts[0])
        gen_utils.zero_out(self.fk_ctrl_chain_buffer)
        self.fk_ctrl_chain_buffer.setParent(self.ctrls['socket'])

        #...Connect FK segment lengths to settings attributes ---------------------------------------------------------
        for mult, jnt in zip(self.length_mult_nodes, self.fk_jnts):
            pm.listConnections(mult.input2, s=1, d=0, plugs=1)[0].connect(jnt.sx)

        # --------------------------------------------------------------------------------------------------------------
        pm.select(clear=1)





    ####################################################################################################################
    def ik_rig(self, dyn_length_jnts, ik_jnt_indices, extrem_jnt_indices, tarsus_indices=None,
               compensate_seg_indices=None):
        """
        Runs in sequence the class methods relating to IK rig creation.
        Args:
            dyn_length_jnts: The indices of those joints whose lengths will be controlled via attributes.
            ik_jnt_indices: The indices of the first and last joints to be influenced by the limb IK solver.
            extrem_jnt_indices: The indices of the first and last joints that compose the limb extremity
                (hand/foot,etc.)
            tarsus_indices: The indices of the first and last joints that compose the limb tarsus segment (usually just
                in the case of digitigrade limbs)
            compensate_seg_indices: The indices of those joints who are influenced by the limb IK solver but whose
                lengths are static. (And so the stretch IK network will need to compensate by an amount equal to the
                sum of their lengths.)
        """

        self.create_ik_jnt_chain(dyn_length_jnts)
        self.create_ik_ctrls(tarsus_indices=tarsus_indices)
        self.install_limb_ik_solver(ik_jnt_indices[0], ik_jnt_indices[1])
        self.install_extrem_ik_solver(extrem_jnt_indices)
        if tarsus_indices:
            self.install_tarsus_ik_solver(tarsus_indices=tarsus_indices)
        self.stretchy_ik(subject_indices=dyn_length_jnts, compensate_seg_indices=compensate_seg_indices,
                         ik_end_index=ik_jnt_indices[-1])





    ####################################################################################################################
    def create_ik_jnt_chain(self, length_jnts):

        #...Create joints ---------------------------------------------------------------------------------------------
        for i in range(self.segment_count+1):
            jnt = rig_utils.joint(name=f'{self.jnt_names[i]}_ik', side=self.side, joint_type=nom.nonBindJnt,
                                  radius=0.08, color=2)

            constraint_target = pm.shadingNode('transform', name=f'{self.jnt_names[i]}_ik_target', au=1)
            constraint_target.setParent(jnt)
            gen_utils.zero_out(constraint_target)

            self.ik_jnts.append(jnt)
            self.ik_constraint_targets.append(constraint_target)


        #...Parent joints into a chain --------------------------------------------------------------------------------
        for i in range(1, self.segment_count+1):
            self.ik_jnts[i].setParent(self.ik_jnts[i - 1])

        #...Wrap top of chain in a buffer group -----------------------------------------------------------------------
        self.ik_jnt_chain_buffer = gen_utils.buffer_obj(self.ik_jnts[0], parent=self.ctrls['socket'])

        #...Position and orient joints --------------------------------------------------------------------------------
        match_nodes = self.ik_jnts[:]
        match_nodes[0] = self.ik_jnt_chain_buffer
        match_nodes.remove(match_nodes[-1])
        for i, node in enumerate(match_nodes):
            pm.delete(pm.parentConstraint(self.blend_jnts[i], node))
            node.scale.set(1, 1, 1)

        # Position Jnts ------------------------------------------------------------------------------------------------
        for i in range(1, self.segment_count+1):
            self.ik_jnts[i].tx.set(self.segment_lengths[i - 1])

        # Orient Jnts --------------------------------------------------------------------------------------------------
        for i, node in enumerate(match_nodes):
            pm.delete(pm.aimConstraint(self.position_holders[i + 1], node, worldUpType='object',
                                       aimVector=(1, 0, 0), upVector=(0, 0, -1), worldUpObject=self.pv_position_holder))
        self.ik_jnts[-1].rotate.set(0, 0, 0)
        self.ik_jnts[-1].scale.set(1, 1, 1)

        #...Clean joint rotations -------------------------------------------------------------------------------------
        for i in range(1, self.segment_count+1):
            self.ik_jnts[i].jointOrient.set(self.ik_jnts[i].rotate.get() + self.ik_jnts[i].jointOrient.get())
            self.ik_jnts[i].rotate.set(0, 0, 0)

        #...Connect IK joint lengths to settings attributes -----------------------------------------------------------
        for i, j in enumerate(length_jnts):
            self.length_mult_nodes[i].output.connect(self.ik_jnts[j+1].tx)

        # --------------------------------------------------------------------------------------------------------------
        pm.select(clear=1)





    ####################################################################################################################
    def create_ik_ctrls(self, tarsus_indices=None):

        #...Create controls -------------------------------------------------------------------------------------------
        self.ctrls['ik_extrem'] = rig_utils.control(ctrl_info = {'shape': 'circle',
                                                                 'scale': [0.25, 0.25, 0.25],
                                                                 'up_direction': [1, 0, 0]},
                                                    name = f'{self.segment_names[-1]}_IK',
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
        if tarsus_indices:
            self.ctrls['ik_tarsus'] = rig_utils.control(ctrl_info={
                'shape': 'sphere',
                'scale': [self.segment_lengths[-2]/4,
                          self.segment_lengths[-2]/4,
                          self.segment_lengths[-2]/4]},
                name=f'{self.segment_names[-2]}_IK',
                ctrl_type=nom.animCtrl,
                side=self.side,
                color=self.ctrl_colors['IK'])
            tarsus_buffer = gen_utils.buffer_obj(self.ctrls['ik_tarsus'], parent=self.ctrls['ik_extrem'])


        #...Position controls -----------------------------------------------------------------------------------------
        extrem_buffer.setParent(self.ik_jnts[-2])
        gen_utils.zero_out(extrem_buffer)
        extrem_buffer.setParent(self.grps['transform'])

        gen_utils.zero_out(pv_buffer)
        pm.delete(pm.parentConstraint(self.blend_jnts[0], self.blend_jnts[-2], pv_buffer))
        extrem_dist = gen_utils.distance_between(position_1=self.jnt_positions[0],
                                                 position_2=self.jnt_positions[-2])
        pv_buffer.tz.set(pv_buffer.tz.get() + (-extrem_dist) * 0.8)

        if tarsus_indices:
            tarsus_buffer.setParent(self.blend_jnts[-2])
            gen_utils.zero_out(tarsus_buffer)
            tarsus_buffer.setParent(self.ctrls["ik_extrem"])

        #...Drive IK extrem scale via socket ctrl's Limb Scale attr
        [pm.connectAttr(f'{self.ctrls["socket"]}.LimbScale',
                        f'{self.ctrls["ik_extrem"]}.{a}') for a in ('sx', 'sy', 'sz')]






    ####################################################################################################################
    def install_limb_ik_solver(self, start_jnt_index, end_effector_index):

        ik_handle, ik_eff = pm.ikHandle(name=f'{self.side_tag}{self.limb_name}_{nom.ikHandle}',
                                        startJoint=self.ik_jnts[start_jnt_index],
                                        endEffector=self.ik_jnts[end_effector_index], solver="ikRPsolver")
        ik_eff.rename(f'{self.side_tag}ik_{self.limb_name}_{nom.effector}')

        self.ik_end_marker = pm.spaceLocator(name=f'{self.side_tag}{self.limb_name}_ikEndMarker_{nom.locator}')
        self.ik_end_marker.getShape().localScale.set(0.2, 0.2, 0.2)
        self.ik_end_marker.setParent(self.ik_jnts[end_effector_index])
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


        #...Display curve ---------------------------------------------------------------------------------------------
        self.ik_display_crv = rig_utils.connector_curve(name=f'{self.side_tag}ik_{self.segment_names[-2]}',
                                                        end_driver_1=self.ik_jnts[1], end_driver_2=self.ctrls["ik_pv"],
                                                        override_display_type=1, line_width=-1.0,
                                                        parent=self.grps['transform'])[0]

        if self.side == nom.rightSideTag:
            [pm.setAttr(f'{self.ik_display_crv}.{a}', lock=0) for a in gen_utils.all_transform_attrs]
            gen_utils.flip(self.ik_display_crv)
            [pm.setAttr(f'{self.ik_display_crv}.{a}', lock=1) for a in gen_utils.all_transform_attrs]


        # --------------------------------------------------------------------------------------------------------------
        pm.select(clear=1)





    ####################################################################################################################
    def install_extrem_ik_solver(self, extrem_jnt_indices):

        #...Create solver
        [self.ik_handles["extrem"], self.ik_effectors["extrem"]] = pm.ikHandle(
            name=f'{self.side_tag}{self.segment_names[extrem_jnt_indices[0]]}_{nom.ikHandle}',
            startJoint=self.ik_jnts[extrem_jnt_indices[0]],
            endEffector=self.ik_jnts[extrem_jnt_indices[1]], solver="ikSCsolver")

        #...Rename effector
        self.ik_effectors["extrem"].rename(
            f'{self.side_tag}ik_{self.segment_names[extrem_jnt_indices[0]]}_{nom.effector}')

        self.ik_handles["extrem"].setParent(self.ctrls["ik_extrem"])





    ####################################################################################################################
    def install_tarsus_ik_solver(self, tarsus_indices):

        #...Create solver
        [self.ik_handles["tarsus"], self.ik_effectors["tarsus"]] = pm.ikHandle(
            name=f'{self.side_tag}{self.segment_names[tarsus_indices[0]]}_{nom.ikHandle}',
            startJoint=self.ik_jnts[tarsus_indices[0]],
            endEffector=self.ik_jnts[tarsus_indices[1]], solver="ikSCsolver")

        #...Rename effector
        self.ik_effectors["extrem"].rename(f'{self.side_tag}ik_{self.segment_names[tarsus_indices[0]]}_{nom.effector}')

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
            len_compensate = sum([gen_utils.distance_between(obj_1=self.ik_jnts[i],
                                                             obj_2=self.ik_jnts[i+1]) for i in compensate_seg_indices])
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

        [straight_condition.outColor.outColorR.connect(self.ik_jnts[i].sx) for i in subject_indices]

        #...Make stretch optional -------------------------------------------------------------------------------------
        stretch_option_remap = node_utils.remapValue(inputValue=f'{self.ctrls["socket"]}.stretchy_ik',
                                                     outputMin=1, inputMax=10,
                                                     outputMax=straight_condition.outColor.outColorR,)
        [stretch_option_remap.outValue.connect(self.ik_jnts[i].sx, force=1) for i in subject_indices]


        #...Squash option ---------------------------------------------------------------------------------------------
        if squash:
            squash_remap = node_utils.remapValue(inputValue=f'{self.ctrls["socket"]}.squash_ik',
                                                 inputMax=10, outputMin=1, outputMax=limb_straigtness_div.outFloat,
                                                 outValue=straight_condition.colorIfFalse.colorIfFalseR)


        #...Include Soft IK effect ------------------------------------------------------------------------------------
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
            [soft_ik_weight_mult.output.connect(self.ik_jnts[i].sx, force=1) for i in subject_indices]






    ####################################################################################################################
    def get_length_sum(self, ik_end_index):

        #...Combine initial two lengths in first sum
        first_sum = node_utils.addDoubleLinear(input1=self.all_seg_length_nodes[0],
                                               input2=self.all_seg_length_nodes[1])
        prev_sum, final_sum = first_sum, first_sum

        #...Add each sum as input to the next until all lengths have been added together
        for i in range(2, ik_end_index):
            new_sum = node_utils.addDoubleLinear(input1=prev_sum.output,
                                                 input2=self.all_seg_length_nodes[i])
            prev_sum, final_sum = new_sum, new_sum

        return final_sum





    ####################################################################################################################
    def soft_ik_curve(self, input=None, output=None):

        #...Create anim curve node
        anim_curve = pm.shadingNode('animCurveUU', name=f'{self.side_tag}_anim_crv_softIk_{self.limb_name}', au=1)
        #...Shape its curve
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
    def setup_kinematic_blend(self, dyn_len_jnt_indices):
        """
        Setup limb blending between FK and IK rigs.
        """

        pm.addAttr(self.ctrls['socket'], longName="fkIk", niceName="FK / IK", attributeType="float", minValue=0,
                   maxValue=10, defaultValue=10, keyable=1)

        #...Outfit blend attribute with mult nodes to get to 0-to-1 space from a 0-to-10 attr input
        blend_driver_plugs = gen_utils.create_attr_blend_nodes(attr='fkIk', node=self.ctrls['socket'], reverse=True)


        for fk_ctrl, ik_target, blend_jnt in zip(self.fk_constraint_targets, self.ik_constraint_targets,
                                                 self.blend_jnts):
            constraint = pm.orientConstraint(fk_ctrl, ik_target, blend_jnt)

            weights = pm.orientConstraint(constraint, query=1, weightAliasList=1)
            pm.connectAttr(blend_driver_plugs.rev.outputX, weights[0])
            pm.connectAttr(blend_driver_plugs.multOutput, weights[1])

            blend_jnt.jointOrient.set(0, 0, 0)


        #...Blend joint scale
        self.kinematic_blend_jnt_lengths(blend_driver_plugs, dyn_len_jnt_indices)


        #...FK/IK controls visibility
        for ctrl in self.fk_ctrls:
            blend_driver_plugs.rev.outputX.connect(ctrl.visibility)

        for key in ['ik_extrem', 'ik_pv', 'ik_tarsus']:
            if key in self.ctrls:
                blend_driver_plugs.mult.output.connect(self.ctrls[key].visibility)
        blend_driver_plugs.mult.output.connect(self.ik_display_crv.getShape().visibility)





    ####################################################################################################################
    def kinematic_blend_jnt_lengths(self, blend_driver_plugs, dyn_len_jnt_indices):

        #...Joint scale
        self.kinematic_blend_jnt_scale(blend_driver_plugs, dyn_len_jnt_indices)
        #...Joint cap translation
        self.kinematic_blend_jnt_cap_translate(blend_driver_plugs, dyn_len_jnt_indices)





    ####################################################################################################################
    def kinematic_blend_jnt_scale(self, blend_driver_plugs, dyn_len_jnt_indices):

        for i in dyn_len_jnt_indices:

            #...Create blend node
            blend = pm.shadingNode("blendTwoAttr", au=1)
            #...Blend inputs
            self.fk_constraint_targets[i].sx.connect(blend.input[0])
            self.ik_jnts[i].sx.connect(blend.input[1])
            #...Drive blend
            pm.connectAttr(blend_driver_plugs.multOutput, blend.attributesBlender)
            #...Output blend
            blend.output.connect(self.blend_jnts[i].sx)





    ####################################################################################################################
    def kinematic_blend_jnt_cap_translate(self, blend_driver_plugs, dyn_len_jnt_indices):

        for i in dyn_len_jnt_indices:

            #...Create blend node
            blend = pm.shadingNode("blendTwoAttr", au=1)
            #...Blend inputs
            self.fk_constraint_targets[i].getChildren()[0].tx.connect(blend.input[0])
            self.ik_jnts[i+1].tx.connect(blend.input[1])
            #...Drive blend
            pm.connectAttr(blend_driver_plugs.multOutput, blend.attributesBlender)
            #...Output blend
            blend.output.connect(self.blend_jnts[i+1].tx)
