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
        self.fk_ctrl_caps = []
        self.fk_ctrl_chain_buffer = None
        self.ik_jnts = []
        self.ik_constraint_targets = []
        self.ik_jnt_chain_buffer = None
        self.ik_handles = {}
        self.ik_effectors = {}
        self.ik_solvers = {}
        self.ik_display_crv = None

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

        self.segment_count = 3
        if not self.segment_names: self.segment_names = default_seg_names
        if not self.jnt_positions: self.jnt_positions = default_jnt_positions
        self.segment_lengths = self.get_segment_lengths()

        self.create_position_holders(start_socket_index=0, end_socket_index=-2, up_vector_index=1)
        self.create_rig_grps()
        self.create_rig_socket_ctrl()
        self.install_limb_length_attrs((0, 1))
        self.blend_rig()
        self.fk_rig(('s', 's', 's'))
        self.ik_rig((0, 1), limb_indices=(0, 2), extrem_indices=(2, 3))





    ####################################################################################################################
    def build_prefab_plantigrade_doubleKnee(self):

        default_seg_names = ('upperlimb', 'joint', 'lowerlimb', 'extrem')
        default_jnt_positions = ((0, 0, 0), (0.9, 0, -0.5), (1.1, 0, -0.5), (2, 0, 0), (2.5, 0, 0))

        self.segment_count = 4
        if not self.segment_names: self.segment_names = default_seg_names
        if not self.jnt_positions: self.jnt_positions = default_jnt_positions
        self.segment_lengths = self.get_segment_lengths()

        self.create_position_holders(start_socket_index=0, end_socket_index=-2, up_vector_index=1)
        self.create_rig_grps()
        self.create_rig_socket_ctrl()
        self.install_limb_length_attrs((0, 2))
        self.blend_rig()
        self.fk_rig(('s', 'd', 's'))
        self.ik_rig((0, 2), limb_indices=(0, 3), extrem_indices=(3, 4))





    ####################################################################################################################
    def build_prefab_digitigrade(self):

        default_seg_names = ('upperlimb', 'lowerlimb', 'tarsus', 'extrem')
        default_jnt_positions = ((0, 0, 0), (0.75, 0, -0.5), (1.5, 0, 0.25), (2, 0, 0), (2.5, 0, 0))

        self.segment_count = 4
        if not self.segment_names: self.segment_names = default_seg_names
        if not self.jnt_positions: self.jnt_positions = default_jnt_positions
        self.segment_lengths = self.get_segment_lengths()

        self.create_position_holders(start_socket_index=0, end_socket_index=-3, up_vector_index=1)
        self.create_rig_grps()
        self.create_rig_socket_ctrl()
        self.install_limb_length_attrs((0, 1, 2))
        self.blend_rig()
        self.fk_rig(('s', 's', 's', 's'))
        self.ik_rig((0, 1, 2), limb_indices=(0, 2), extrem_indices=(3, 4), tarsus_indices=(-3, -2))





    ####################################################################################################################
    def build_prefab_digitigrade_doubleKnees(self):

        default_seg_names = ('upperlimb', 'frontKnee', 'lowerlimb', 'backKnee', 'tarsus', 'extrem')
        default_jnt_positions = ((0, 0, 0), (0.65, 0, -0.5), (0.85, 0, -0.5), (1.4, 0, 0.25), (1.6, 0, 0.25), (2, 0, 0),
                                 (2.5, 0, 0))

        self.segment_count = 6
        if not self.segment_names: self.segment_names = default_seg_names
        if not self.jnt_positions: self.jnt_positions = default_jnt_positions
        self.segment_lengths = self.get_segment_lengths()

        self.create_position_holders(start_socket_index=0, end_socket_index=-4, up_vector_index=1)
        self.create_rig_grps()
        self.create_rig_socket_ctrl()
        self.install_limb_length_attrs((0, 2, 4))
        self.blend_rig()
        self.fk_rig(('s', 'd', 'd', 's'))
        self.ik_rig((0, 2, 4), limb_indices=(0, 3), extrem_indices=(5, 6), tarsus_indices=(-3, -2))





    ####################################################################################################################
    def build_prefab_digitigrade_doubleFrontKnee(self):

        default_seg_names = ('upperlimb', 'frontKnee', 'lowerlimb', 'tarsus', 'extrem')
        default_jnt_positions = ((0, 0, 0), (0.65, 0, -0.5), (0.85, 0, -0.5), (1.5, 0, 0.25), (2, 0, 0), (2.5, 0, 0))

        self.segment_count = 5
        if not self.segment_names: self.segment_names = default_seg_names
        if not self.jnt_positions: self.jnt_positions = default_jnt_positions
        self.segment_lengths = self.get_segment_lengths()

        self.create_position_holders(start_socket_index=0, end_socket_index=-3, up_vector_index=1)
        self.create_rig_grps()
        self.create_rig_socket_ctrl()
        self.install_limb_length_attrs((0, 2, 3))
        self.blend_rig()
        self.fk_rig(('s', 'd', 's', 's'))
        self.ik_rig((0, 2, 3), limb_indices=(0, 3), extrem_indices=(4, 5), tarsus_indices=(-3, -2))





    ####################################################################################################################
    def create_position_holders(self, start_socket_index, end_socket_index, up_vector_index):

        locs_grp = pm.group(name=f'{self.side_tag}position_holders_TEMP', world=1, em=1)

        # ...Create and position locs
        for i, pos in enumerate(self.jnt_positions):
            loc = pm.spaceLocator(name=f'{self.side_tag}position_holder_{str(i)}_{nom.locator}')
            loc.setParent(locs_grp)
            loc.translate.set(pos)
            loc.getShape().localScale.set(0.15, 0.15, 0.15)
            self.position_holders.append(loc)

        # ...Pole vector position holder
        self.create_pv_position_holder(locs_grp, start_socket_index=start_socket_index,
                                       end_socket_index=end_socket_index, up_vector_index=up_vector_index)

        # ...Orient locs
        for i in range(0, len(self.position_holders)):
            pm.delete(pm.aimConstraint(self.position_holders[i], self.position_holders[i-1], worldUpType='object',
                                       aimVector=(1, 0, 0), upVector=(0, 0, -1), worldUpObject=self.pv_position_holder))
        pm.delete(pm.orientConstraint(self.position_holders[-2], self.position_holders[-1]))

        # ...Mirror transforms if this is a right-sided limb
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
    '''def process_jnt_positions(self, init_jnt_positions_arg):

        # ...If use provided custom positions, make sure they provided the correct number corresponding to segment_count
        if init_jnt_positions_arg:

            count = len(init_jnt_positions_arg)
            if not count == self.segment_count + 1:
                print(f'Received {count} joint position vectors but a segment count of {self.segment_count}. '
                      f'Number of provided joint positions must be exactly 1 more than the provided segment count.')
                return False

            return init_jnt_positions_arg

        # ...If no custom positions input provided, get default positions from dictionary based on segment_count
        if str(self.segment_count) not in limb_defaults:
            print(f'Cannot provide default joint positions for a limb of Segment Count: {self.segment_count}')
            return False

        return limb_defaults[str(self.segment_count)][0]





    ####################################################################################################################
    def process_segment_names(self, init_seg_names_arg):

        if init_seg_names_arg:

            count = len(init_seg_names_arg)
            if not count == self.segment_count:
                print(f'Received {count} segment names but a segment count of {self.segment_count}. '
                      f'The number of segment names provided must be equal to the provided segment count.')
                return False

            return init_seg_names_arg

        if str(self.segment_count) not in limb_defaults:
            print(f'Cannot provide default segment names for a limb of Segment Count: {self.segment_count}')
            return False

        return limb_defaults[str(self.segment_count)][1]'''
    
    
    
    

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
    def get_segment_lengths(self):

        return [gen_utils.distance_between(position_1=self.jnt_positions[i], position_2=self.jnt_positions[i + 1])
                for i in range(self.segment_count)]





    ####################################################################################################################
    def install_limb_length_attrs(self, indices):

        for i in indices:

            length_attr_name = f'{self.segment_names[i]}Len'
            pm.addAttr(self.ctrls['socket'], longName=length_attr_name, attributeType="float",
                       minValue=0.001, defaultValue=1, keyable=1)

            self.length_mult_nodes.append(
                node_utils.multDoubleLinear(input1=self.segment_lengths[i],
                                            input2=f'{self.ctrls["socket"]}.{length_attr_name}'))

        '''
        if self.fk_ctrl_caps:
            upperlimb_len_mult.output.connect(self.fk_ctrl_caps[0].tx)
            lowerlimb_len_mult.output.connect(self.fk_ctrl_caps[1].tx)
        '''





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
            print(node)
            print(self.position_holders[i+1])
            print("")
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





    ####################################################################################################################
    def fk_rig(self, fk_jnt_types):

        n = 0
        i = 0
        for n, x in enumerate(fk_jnt_types):

            jnt_i = i
            if fk_jnt_types[n] in ('single', 's'):
                jnt_i = i
            elif fk_jnt_types[n] in ('double', 'd'):
                jnt_i = i + 1
            # ...Single-jointed FK ctrl
            # ...Create and parent control
            par = self.fk_ctrl_caps[n-1] if n > 0 else None
            fk_ctrl = rig_utils.control(ctrl_info={'shape': 'cube',
                                                   'scale': [self.segment_lengths[jnt_i] / 2 * 0.93,
                                                             self.segment_lengths[jnt_i] / 2 * (0.93 * 0.25),
                                                             self.segment_lengths[jnt_i] / 2 * (0.93 * 0.25)],
                                                   'offset': [self.segment_lengths[jnt_i] / 2, 0, 0]},
                                        name=f'{self.segment_names[jnt_i]}_FK',
                                        ctrl_type=nom.animCtrl,
                                        side=self.side,
                                        parent=par,
                                        color=self.ctrl_colors['FK'])
            self.ctrls[f'{self.segment_names[jnt_i]}_FK'] = fk_ctrl
            self.fk_ctrls.append(fk_ctrl)

            # ...Position control
            fk_ctrl.setParent(self.blend_jnts[jnt_i])
            gen_utils.zero_out(fk_ctrl)
            fk_ctrl.setParent(par) if par else fk_ctrl.setParent(world=1)

            # ...
            if i < self.segment_count - 1:
                cap = pm.createNode("transform", name=f'{self.side_tag}{self.segment_names[jnt_i]}_FK_ctrl_CAP')
                cap.setParent(fk_ctrl)
                gen_utils.zero_out(cap)
                pm.delete(pm.pointConstraint(self.blend_jnts[jnt_i + 1], cap))
                self.fk_ctrl_caps.append(cap)

                if fk_jnt_types[n] in ('double', 'd'):
                    roller_1 = pm.shadingNode('transform', name=f'{self.side_tag}{self.jnt_names[i]}_roller', au=1)
                    roller_1.setParent(self.blend_jnts[i])
                    gen_utils.zero_out(roller_1)
                    roller_1.setParent(par)

                    roller_2 = pm.shadingNode('transform', name=f'{self.side_tag}{self.jnt_names[i+1]}_roller', au=1)
                    roller_2.setParent(self.blend_jnts[jnt_i])
                    gen_utils.zero_out(roller_2)
                    roller_2.setParent(roller_1)

                    fk_ctrl.setParent(roller_2)
                    [gen_utils.convert_offset(r) for r in (roller_1, roller_2)]

                    node_utils.multiplyDivide(input1=fk_ctrl.rotate, input2=(0.5, 0.5, 0.5), output=roller_1.rotate)
                    node_utils.multiplyDivide(input1=fk_ctrl.rotate, input2=(-0.5, -0.5, -0.5), output=roller_2.rotate)

            # ...Move unclean transforms into offsetParentMatrix
            # ...(exclude first ctrl, it'll have a buffer grp instead)
            if fk_jnt_types[n] in ('single', 's'):
                if i > 0:
                    gen_utils.convert_offset(fk_ctrl)


            if fk_jnt_types[n] in ('single', 's'):
                i += 1
            elif fk_jnt_types[n] in ('double', 'd'):
                i += 2


        # ...Wrap top of ctrl chain in buffer group --------------------------------------------------------------------
        self.fk_ctrl_chain_buffer = gen_utils.buffer_obj(self.fk_ctrls[0], parent=self.ctrls['socket'])
        self.fk_ctrl_chain_buffer.setParent(self.blend_jnts[0])
        gen_utils.zero_out(self.fk_ctrl_chain_buffer)
        self.fk_ctrl_chain_buffer.setParent(self.ctrls['socket'])

        # ...Connect FK segment lengths to settings attributes ---------------------------------------------------------
        [mult.output.connect(cap.tx) for mult, cap in zip(self.length_mult_nodes, self.fk_ctrl_caps)]

        # --------------------------------------------------------------------------------------------------------------
        pm.select(clear=1)





    ####################################################################################################################
    def ik_rig(self, length_jnts, limb_indices, extrem_indices, tarsus_indices=None):

        self.create_ik_jnt_chain(length_jnts)
        self.create_ik_ctrls(tarsus_indices=tarsus_indices)
        self.install_limb_ik_solver(limb_indices[0], limb_indices[1])
        self.install_extrem_ik_solver(extrem_indices)
        if tarsus_indices:
            self.install_tarsus_ik_solver(tarsus_indices=tarsus_indices)
        '''self.stretchy_ik()'''





    ####################################################################################################################
    def create_ik_jnt_chain(self, length_jnts):

        # ...Create joints ---------------------------------------------------------------------------------------------
        for i in range(self.segment_count+1):
            jnt = rig_utils.joint(name=f'{self.jnt_names[i]}_ik', side=self.side, joint_type=nom.nonBindJnt,
                                  radius=0.08, color=2)

            constraint_target = pm.shadingNode('transform', name=f'{self.jnt_names[i]}_ik_target', au=1)
            constraint_target.setParent(jnt)
            gen_utils.zero_out(constraint_target)

            self.ik_jnts.append(jnt)
            self.ik_constraint_targets.append(constraint_target)


        # ...Parent joints into a chain --------------------------------------------------------------------------------
        for i in range(1, self.segment_count+1):
            self.ik_jnts[i].setParent(self.ik_jnts[i - 1])

        # ...Wrap top of chain in a buffer group -----------------------------------------------------------------------
        self.ik_jnt_chain_buffer = gen_utils.buffer_obj(self.ik_jnts[0], parent=self.ctrls['socket'])

        # ...Position and orient joints --------------------------------------------------------------------------------
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

        # ...Clean joint rotations -------------------------------------------------------------------------------------
        for i in range(1, self.segment_count+1):
            self.ik_jnts[i].jointOrient.set(self.ik_jnts[i].rotate.get() + self.ik_jnts[i].jointOrient.get())
            self.ik_jnts[i].rotate.set(0, 0, 0)

        # ...Connect IK joint lengths to settings attributes -----------------------------------------------------------
        for i, j in enumerate(length_jnts):
            self.length_mult_nodes[i].output.connect(self.ik_jnts[j+1].tx)

        # --------------------------------------------------------------------------------------------------------------
        pm.select(clear=1)





    ####################################################################################################################
    def create_ik_ctrls(self, tarsus_indices=None):

        # ...Create controls -------------------------------------------------------------------------------------------
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
                'shape': 'cube',
                'scale': [self.segment_lengths[-2] / 2 * 0.93,
                          self.segment_lengths[-2] / 2 * (0.93 * 0.25),
                          self.segment_lengths[-2] / 2 * (0.93 * 0.25)],
                'offset': [self.segment_lengths[-2] / 2, 0, 0]},
                name=f'{self.segment_names[-2]}_IK',
                ctrl_type=nom.animCtrl,
                side=self.side,
                color=self.ctrl_colors['IK'])
            tarsus_buffer = gen_utils.buffer_obj(self.ctrls['ik_tarsus'], parent=self.ctrls['ik_extrem'])


        # ...Position controls -----------------------------------------------------------------------------------------
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






    ####################################################################################################################
    def install_limb_ik_solver(self, start_jnt_index, end_effector_index):

        ik_handle, ik_eff = pm.ikHandle(name=f'{self.side_tag}{self.limb_name}_{nom.ikHandle}',
                                        startJoint=self.ik_jnts[start_jnt_index],
                                        endEffector=self.ik_jnts[end_effector_index], solver="ikRPsolver")
        ik_eff.rename(f'{self.side_tag}ik_{self.limb_name}_{nom.effector}')
        ik_handle.setParent(self.ik_jnts[end_effector_index])
        gen_utils.zero_out(ik_handle)
        if 'ik_tarsus' in self.ctrls:
            ik_handle.setParent(self.ctrls['ik_tarsus'])
        else:
            ik_handle.setParent(self.ctrls['ik_extrem'])
        ik_handle.rotate.set(0, 0, 0)

        self.ik_handles["limb"], self.ik_effectors["limb"] = ik_handle, ik_eff

        self.ik_solvers["limb"] = pm.listConnections(f'{ik_handle}.ikSolver', source=True)[0]

        pm.poleVectorConstraint(self.ctrls["ik_pv"], self.ik_handles["limb"])


        # ...Display curve ---------------------------------------------------------------------------------------------
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
    def install_extrem_ik_solver(self, extrem_indices):

        # ...Create solver
        [self.ik_handles["extrem"], self.ik_effectors["extrem"]] = pm.ikHandle(
            name=f'{self.side_tag}{self.segment_names[extrem_indices[0]]}_{nom.ikHandle}',
            startJoint=self.ik_jnts[extrem_indices[0]],
            endEffector=self.ik_jnts[extrem_indices[1]], solver="ikSCsolver")

        # ...Rename effector
        self.ik_effectors["extrem"].rename(f'{self.side_tag}ik_{self.segment_names[extrem_indices[0]]}_{nom.effector}')

        self.ik_handles["extrem"].setParent(self.ctrls["ik_extrem"])





    ####################################################################################################################
    def install_tarsus_ik_solver(self, tarsus_indices):

        # ...Create solver
        [self.ik_handles["tarsus"], self.ik_effectors["tarsus"]] = pm.ikHandle(
            name=f'{self.side_tag}{self.segment_names[tarsus_indices[0]]}_{nom.ikHandle}',
            startJoint=self.ik_jnts[tarsus_indices[0]],
            endEffector=self.ik_jnts[tarsus_indices[1]], solver="ikSCsolver")

        # ...Rename effector
        self.ik_effectors["extrem"].rename(f'{self.side_tag}ik_{self.segment_names[tarsus_indices[0]]}_{nom.effector}')

        self.ik_handles["tarsus"].setParent(self.ctrls["ik_extrem"])
