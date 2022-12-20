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
default_point_positions = ((0, 0, 0), (6, 0, -1), (12, 0, 0), (14, 0, 0))
default_point_names = ("upperlimb", "lowerlimb", "extrem", "extremEnd") # Changing these will break a lot of shit
ctrl_colors = {"FK": 13, "IK": 6, "other": 17, "sub": (15, 4)}
ctrl_length_ratios = (0.25, 0.25, 0.65)
###########################
###########################





########################################################################################################################
class LimbRig:
    def __init__(
        self,
        limb_name,
        side = None,
        segment_names = None,
        socket_name = None,
        midlimb_name = None,
        final_pose_nodes = None,
        include_extrem_fk_rot = False
    ):
        self.limb_name = limb_name
        self.side = side
        self.side_tag = "{}_".format(side) if side else ""
        self.seg_keys = default_point_names
        self.seg_names = segment_names if segment_names else default_point_names
        self.ctrl_colors = ctrl_colors
        self.point_count = len(default_point_names)
        self.seg_count = self.point_count - 1
        self.default_point_positions = default_point_positions
        self.blend_jnts = None
        self.blend_jnt_chain_buffer = None
        self.seg_lengths = None
        self.final_seg_lengths = None
        self.ctrls = {}
        self.tweak_ctrls = []
        self.fk_ctrls = None
        self.fk_ctrl_caps = None
        self.fk_ctrl_chain_buffer = None
        self.ctrl_len_ratios = ctrl_length_ratios
        self.ik_jnts = None
        self.ik_jnt_chain_buffer = None
        self.ik_constraint_targets = None
        self.ik_handles = {}
        self.ik_effectors = {}
        self.ik_solvers = {}
        self.final_pose_nodes = final_pose_nodes
        self.include_extrem_fk_rot = include_extrem_fk_rot
        self.socket_name = socket_name if socket_name else "limb"
        self.pv_name = midlimb_name if midlimb_name else "midlimb"
        self.root_grp = None
        self.transform_grp = None
        self.no_transform_grp = None
        self.limb_length_mults = []
        self.seg_resolution = 5
        self.bend_ctrls = None
        self.bend_jnts = None
        self.stretch_rig_grps = {}
        self.ik_display_crv = {}
        self.position_holders = []
        self.roll_socket_target = None
        self.ik_hand_rot_loc = None
        self.ik_extrem_dist = None


        # Get segment lengths
        len_list = []
        for i in range(self.point_count - 1):
            len_list.append(gen_utils.distance_between(position_1=self.default_point_positions[i],
                                                       position_2=self.default_point_positions[i + 1]))

        self.seg_lengths = tuple(len_list)


        # ...Rig creation ----------------------------------------------------------------------------------------------
        self.create_position_holders()
        self.create_rig_grps()
        self.create_rig_socket_ctrl()
        self.install_limb_length_attrs()
        self.blend_rig()
        self.fk_rig()
        self.ik_rig()
        self.setup_kinematic_blend()
        self.install_ribbon_systems()
        if self.final_pose_nodes:
            self.move_to_final_pose()
        pm.delete(self.position_holders[0].getParent())



    ####################################################################################################################
    ########### ------------------------------    TABLE OF CONTENTS    ----------------------------------- #############
    ####################################################################################################################
    '''
    create_position_holders
    create_rig_grps
    create_rig_socket_ctrl
    create_blend_jnts
    create_ik_jnt_chain
    create_ik_ctrls
    install_extrem_ik_solver
    install_limb_ik_solver
    install_ik_extrem_rot_ctrl
    setup_kinematic_blend
    install_rollers
    install_limb_length_attrs
    soft_ik_curve
    stretchy_ik
    blend_rig
    fk_rig
    ik_rig
    ribbon_tweak_ctrls
    install_ribbon_systems
    resize_tweak_ctrls
    move_to_final_pose
    '''
    ####################################################################################################################
    ####################################################################################################################
    ####################################################################################################################



    ####################################################################################################################
    def create_position_holders(self):

        locs_grp = pm.group(name="{}position_holders_TEMP".format(self.side_tag))

        i = 0

        for pos in default_point_positions:

            loc = pm.spaceLocator(name="{}position_holder_{}_{}".format(self.side_tag, str(i), nom.locator))
            loc.setParent(locs_grp)
            loc.translate.set(pos)
            self.position_holders.append(loc)
            i += 1

        pm.delete(pm.aimConstraint(self.position_holders[1], self.position_holders[0], worldUpType="scene",
                                   aimVector=(1, 0, 0), upVector=(0, 1, 0), worldUpVector=(0, 1, 0)))
        pm.delete(pm.aimConstraint(self.position_holders[2], self.position_holders[1], worldUpType="scene",
                                   aimVector=(1, 0, 0), upVector=(0, 1, 0), worldUpVector=(0, 1, 0)))
        pm.delete(pm.aimConstraint(self.position_holders[3], self.position_holders[2], worldUpType="scene",
                                   aimVector=(1, 0, 0), upVector=(0, 1, 0), worldUpVector=(0, 1, 0)))
        pm.delete(pm.orientConstraint(self.position_holders[2], self.position_holders[3]))


        if self.side == nom.rightSideTag:
            gen_utils.flip(locs_grp)





    ####################################################################################################################
    def create_rig_grps(self):

        self.root_grp = pm.group(name="{}{}_RIG".format(self.side_tag, self.limb_name), world=1, em=1)
        pm.addAttr(self.root_grp, longName="rigScale", minValue=0.001, defaultValue=1, keyable=0)

        self.transform_grp = pm.group(name="transform", p=self.root_grp, em=1)

        self.no_transform_grp = pm.group(name="noTransform", p=self.root_grp, em=1)
        self.no_transform_grp.inheritsTransform.set(0, lock=1)

        if self.side == nom.rightSideTag:
            gen_utils.flip(self.root_grp)
            gen_utils.flip(self.no_transform_grp)


        # ...Rig Scale attribute ---------------------------------------------------------------------------------------
        pm.addAttr(self.root_grp, longName="RigScale", minValue=0.001, defaultValue=1, keyable=0)


        pm.select(clear=1)





    ####################################################################################################################
    def create_rig_socket_ctrl(self):

        # ...Create controls -------------------------------------------------------------------------------------------
        ctrl = self.ctrls["rig_socket"] = rig_utils.control(ctrl_info={"shape": "tag_hexagon",
                                                                       "scale": [2, 2, 2]},
                                                            name="{}Pin".format(self.socket_name),
                                                            ctrl_type=nom.animCtrl,
                                                            side=self.side,
                                                            color=self.ctrl_colors["other"])

        ctrl.translate.set(self.default_point_positions[0])
        ctrl.setParent(self.transform_grp)
        gen_utils.zero_out(ctrl)
        gen_utils.convert_offset(ctrl)

        gen_utils.buffer_obj(ctrl)


        # ...Rig Scale attribute ---------------------------------------------------------------------------------------
        pm.addAttr(ctrl, longName="LimbScale", minValue=0.001, defaultValue=1, keyable=1)
        [pm.connectAttr(ctrl + "." + "LimbScale", ctrl + "." + a) for a in ("sx", "sy", "sz")]


        # ...Add settings attributes -----------------------------------------------------------------------------------
        pm.addAttr(ctrl, longName="fkIk", niceName="FK / IK", attributeType="float", minValue=0, maxValue=10,
                   defaultValue=10, keyable=1)

        pm.addAttr(ctrl, longName="upperlimb_length", attributeType="float", minValue=0.001, defaultValue=1, keyable=1)

        pm.addAttr(ctrl, longName="lowerlimb_length", attributeType="float", minValue=0.001, defaultValue=1, keyable=1)

        pm.addAttr(ctrl, longName="stretchy_ik", attributeType="float", minValue=0, maxValue=10, defaultValue=10,
                   keyable=1)

        pm.addAttr(ctrl, longName="Volume", attributeType="float", minValue=0, maxValue=10, defaultValue=0, keyable=1)

        pm.addAttr(ctrl, longName="squash_ik", attributeType="float", minValue=0, maxValue=10, defaultValue=0,
                   keyable=1)


        # --------------------------------------------------------------------------------------------------------------
        return ctrl





    ####################################################################################################################
    def create_blend_jnts(self):
        """
            Create, position, and arrange into hierarchy the limb segment transform objects that will be blended between
                the FK and IK rigs.
            Return:
                (tuple): The created segment transforms, in order.
        """

        pm.select(clear=1)

        # ...Create joints ---------------------------------------------------------------------------------------------
        blend_jnts_list = []

        for i in range(self.point_count):
            jnt = rig_utils.joint(name="{}_blend".format(self.seg_names[i]), side=self.side, joint_type=nom.nonBindJnt,
                                  radius=0.5)
            blend_jnts_list.append(jnt)

            if i > 0:
                jnt.setParent(blend_jnts_list[i-1])

        self.blend_jnts = blend_jnts_list


        # ...Wrap top of chain in a buffer group -----------------------------------------------------------------------
        self.blend_jnt_chain_buffer = gen_utils.buffer_obj(self.blend_jnts[0])

        if self.side == nom.rightSideTag:
            gen_utils.flip(self.blend_jnt_chain_buffer)



        # Position Jnts ------------------------------------------------------------------------------------------------
        for i in range(1, len(self.blend_jnts)):
            self.blend_jnts[i].tx.set(self.seg_lengths[i-1])


        # Orient Jnts --------------------------------------------------------------------------------------------------
        i = 0
        for node in (self.blend_jnt_chain_buffer, self.blend_jnts[1], self.blend_jnts[2]):
            pm.delete(pm.aimConstraint(self.position_holders[i+1], node, worldUpType="scene",
                                       aimVector=(1, 0, 0), upVector=(0, 1, 0), worldUpVector=(0, 1, 0)))
            i += 1
        self.blend_jnts[-1].rotate.set(0, 0, 0)
        self.blend_jnts[-1].scale.set(1, 1, 1)


        # ...Clean joint rotations -------------------------------------------------------------------------------------
        for i in range(1, self.point_count):
            self.blend_jnts[i].jointOrient.set(self.blend_jnts[i].rotate.get() + self.blend_jnts[i].jointOrient.get())
            self.blend_jnts[i].rotate.set(0, 0, 0)



        self.blend_jnt_chain_buffer.setParent(self.ctrls["rig_socket"])



        rot = self.blend_jnt_chain_buffer.rotate.get()
        gen_utils.matrix_constraint(objs=[self.ctrls["rig_socket"], self.blend_jnt_chain_buffer], decompose=True,
                                    translate=True, rotate=False, scale=False, shear=False)
        self.blend_jnt_chain_buffer.rotate.set(rot)



        # --------------------------------------------------------------------------------------------------------------
        pm.select(clear=1)
        return self.blend_jnts





    ####################################################################################################################
    def create_ik_jnt_chain(self):
        """
            Create, position, and arrange hierarchy of IK rig joint chain.
            Return:
                (tuple, mObj):
                    IK joints, in order.
                    First joint buffer group.
        """

        # ...Create joints ---------------------------------------------------------------------------------------------
        ik_jnts_list = []
        ik_constraint_target_list = []

        for i in range(self.point_count):

            jnt = rig_utils.joint(name="{}_ik".format(self.seg_names[i]), side=self.side, joint_type=nom.nonBindJnt,
                                  radius=0.75, color=2)

            constraint_target = pm.shadingNode("transform", name="{}_ik_target".format(self.seg_names[i]), au=1)
            constraint_target.setParent(jnt)
            gen_utils.zero_out(constraint_target)

            ik_jnts_list.append(jnt)
            ik_constraint_target_list.append(constraint_target)

        self.ik_jnts = ik_jnts_list
        self.ik_constraint_targets = ik_constraint_target_list


        # ...Parent joints into a chain --------------------------------------------------------------------------------
        for i in range(1, self.point_count):
            self.ik_jnts[i].setParent(self.ik_jnts[i - 1])


        # ...Wrap top of chain in a buffer group -----------------------------------------------------------------------
        self.ik_jnt_chain_buffer = gen_utils.buffer_obj(self.ik_jnts[0], parent=self.ctrls["rig_socket"])


        # ...Position and orient joints --------------------------------------------------------------------------------
        i = 0
        for node in (self.ik_jnt_chain_buffer, self.ik_jnts[1], self.ik_jnts[2]):
            pm.delete(pm.parentConstraint(self.blend_jnts[i], node))
            node.scale.set(1, 1, 1)


        # Position Jnts ------------------------------------------------------------------------------------------------
        for i in range(1, len(self.ik_jnts)):
            self.ik_jnts[i].tx.set(self.seg_lengths[i - 1])

        # Orient Jnts --------------------------------------------------------------------------------------------------
        i = 0
        for node in (self.ik_jnt_chain_buffer, self.ik_jnts[1], self.ik_jnts[2]):
            pm.delete(pm.aimConstraint(self.position_holders[i + 1], node, worldUpType="scene",
                                       aimVector=(1, 0, 0), upVector=(0, 1, 0), worldUpVector=(0, 1, 0)))
            i += 1
        self.ik_jnts[-1].rotate.set(0, 0, 0)
        self.ik_jnts[-1].scale.set(1, 1, 1)


        # ...Clean joint rotations -------------------------------------------------------------------------------------
        for i in range(1, self.point_count):
            self.ik_jnts[i].jointOrient.set( self.ik_jnts[i].rotate.get() + self.ik_jnts[i].jointOrient.get() )
            self.ik_jnts[i].rotate.set(0, 0, 0)


        # ...Connect IK joint lengths to settings attributes -----------------------------------------------------------
        if self.limb_length_mults:
            self.limb_length_mults[0].output.connect(self.ik_jnts[1].tx)
            self.limb_length_mults[1].output.connect(self.ik_jnts[2].tx)


        # --------------------------------------------------------------------------------------------------------------
        pm.select(clear=1)
        return self.ik_jnts, self.ik_jnt_chain_buffer, self.ik_constraint_targets





    ####################################################################################################################
    def create_ik_ctrls(self):
        """
            Creates controls for IK rig, positions them, and connects IK skeleton.
            Returns:
                (tuple): (IK extrem ctrl, IK pole vector ctrl)
        """

        # ...Create controls -------------------------------------------------------------------------------------------
        self.ctrls["ik_extrem"] = rig_utils.control(ctrl_info = {"shape": "circle",
                                                                 "scale": [2, 2, 2],
                                                                 "up_direction": [1, 0, 0]},
                                                    name = "{}_IK".format(self.seg_names[2]),
                                                    ctrl_type = nom.animCtrl,
                                                    side = self.side,
                                                    color = self.ctrl_colors["IK"])
        extrem_buffer = gen_utils.buffer_obj(self.ctrls["ik_extrem"], parent=self.transform_grp)


        self.ctrls["ik_pv"] = rig_utils.control(ctrl_info = {"shape": "sphere",
                                                             "scale": [0.7, 0.7, 0.7]},
                                                name = "{}_IK".format(self.pv_name),
                                                ctrl_type = nom.animCtrl,
                                                side = self.side,
                                                color = self.ctrl_colors["IK"])
        pv_buffer = gen_utils.buffer_obj(self.ctrls["ik_pv"], parent=self.transform_grp)



        # ...Position controls -----------------------------------------------------------------------------------------
        extrem_buffer.setParent(self.ik_jnts[2])
        gen_utils.zero_out(extrem_buffer)
        extrem_buffer.setParent(self.transform_grp)

        gen_utils.zero_out(pv_buffer)
        pm.delete(pm.pointConstraint(self.blend_jnts[1], pv_buffer))
        extrem_dist = gen_utils.distance_between(position_1=self.default_point_positions[0],
                                                 position_2=self.default_point_positions[2])
        pv_buffer.tz.set(pv_buffer.tz.get() + (-extrem_dist) * 0.8)





    ####################################################################################################################
    def install_extrem_ik_solver(self):

        # ...Create solver
        [self.ik_handles["extrem"], self.ik_effectors["extrem"]] = pm.ikHandle(
            name="{}{}_{}".format(self.side_tag, self.seg_names[2], nom.ikHandle), startJoint=self.ik_jnts[2],
            endEffector=self.ik_jnts[3], solver="ikSCsolver")

        # ...Rename effector
        self.ik_effectors["extrem"].rename('{}ik_{}_{}'.format(self.side_tag, self.seg_names[2], nom.effector))


        self.ik_handles["extrem"].setParent(self.ctrls["ik_extrem"])





    ####################################################################################################################
    def install_limb_ik_solver(self):
        """
            Setup Rotation Plane IK solver for limb and parent it under IK extrem control
            Return:
                (tuple):
                    IK handle
                    IK effector
                    IK solver
        """

        ik_handle, ik_eff = pm.ikHandle(name="{}{}_{}".format(self.side_tag, self.limb_name, nom.ikHandle),
                                        startJoint=self.ik_jnts[0], endEffector=self.ik_jnts[2], solver="ikRPsolver")
        ik_eff.rename('{}ik_{}_{}'.format(self.side_tag, self.limb_name, nom.effector))
        ik_handle.setParent(self.ctrls["ik_extrem"])
        gen_utils.zero_out(ik_handle)

        self.ik_handles["limb"], self.ik_effectors["limb"] = ik_handle, ik_eff

        self.ik_solvers["limb"] = pm.listConnections(ik_handle + '.ikSolver', source=True)[0]

        pm.poleVectorConstraint(self.ctrls["ik_pv"], self.ik_handles["limb"])


        # ...Display curve ---------------------------------------------------------------------------------------------
        self.ik_display_crv = rig_utils.connector_curve(name="{}ik_{}".format(self.side_tag, self.seg_names[2]),
                                                        end_driver_1=self.ik_jnts[1], end_driver_2=self.ctrls["ik_pv"],
                                                        override_display_type=1, line_width=-1.0,
                                                        parent=self.no_transform_grp)[0]

        if self.side == nom.rightSideTag:
            [pm.setAttr(self.ik_display_crv+'.'+a, lock=0) for a in gen_utils.all_transform_attrs]
            gen_utils.flip(self.ik_display_crv)
            [pm.setAttr(self.ik_display_crv+'.'+a, lock=1) for a in gen_utils.all_transform_attrs]


        # --------------------------------------------------------------------------------------------------------------
        pm.select(clear=1)
        return ik_handle, ik_eff, self.ik_solvers["limb"]
    
    
    
    

    ####################################################################################################################
    def install_ik_extrem_rot_ctrl(self):


        # ...Create control
        self.ctrls["ik_extrem_rot"] = rig_utils.control(ctrl_info={"shape": "cube",
                                                                   "scale": [3, 2, 2],
                                                                   "offset": [1.5, 0, 0]},
                                                        name="{}Rot_IK".format(self.seg_names[2]),
                                                        ctrl_type=nom.animCtrl,
                                                        side=self.side,
                                                        color=self.ctrl_colors["IK"])
        extrem_rot_buffer = gen_utils.buffer_obj(self.ctrls["ik_extrem_rot"], parent=self.ctrls["ik_extrem"])



        self.ik_hand_rot_loc = pm.spaceLocator(name="{}{}_ikRot_{}".format(self.side, self.seg_names[2], nom.locator))
        self.ik_hand_rot_loc.setParent(self.ctrls["ik_extrem"])
        gen_utils.zero_out(self.ik_hand_rot_loc)
        pm.delete(pm.orientConstraint(self.ik_jnts[1], self.ik_hand_rot_loc))

        gen_utils.zero_out(extrem_rot_buffer)
        extrem_rot_buffer.setParent(self.ik_hand_rot_loc)
        gen_utils.matrix_constraint(objs=[self.ik_jnts[1], self.ik_hand_rot_loc], decompose=True,
                                    translate=False, rotate=True, scale=False, shear=False)



        offset = pm.group(name="{}{}_IKH_OFFSET".format(self.side_tag, self.seg_names[2]), em=1,
                          parent=self.ctrls["ik_extrem"])
        gen_utils.zero_out(offset)
        self.ik_handles["extrem"].setParent(offset)
        constraint = gen_utils.matrix_constraint(objs=[self.ctrls["ik_extrem"], self.ctrls["ik_extrem_rot"],
                                                       offset], decompose=True, translate=False, rotate=True,
                                                 scale=False, shear=False)
        attr_string = "ik_{}_fk".format(self.seg_names[2])
        pm.addAttr(self.ctrls["rig_socket"], longName=attr_string, minValue=0, maxValue=10, defaultValue=0, keyable=1)
        blend = gen_utils.create_attr_blend_nodes(attr=attr_string, node=self.ctrls["rig_socket"], reverse=False)
        pm.connectAttr(blend.multOutput, constraint["weights"][0])



        blend_plugs = gen_utils.create_attr_blend_nodes(attr="fkIk", node=self.ctrls["rig_socket"], reverse=True)
        blend_plugs.mult.output.connect(self.ctrls["ik_extrem_rot"].visibility)






    ####################################################################################################################
    def setup_kinematic_blend(self):
        """
            Setup limb blending between FK and IK rigs.
        """

        # ...Outfit blend attribute with mult nodes to get to 0-to-1 space from a 0-to-10 attr input -------------------
        blend_plugs = gen_utils.create_attr_blend_nodes(attr="fkIk", node=self.ctrls["rig_socket"], reverse=True)

        for fk_ctrl, ik_target, blend_jnt in zip(self.fk_ctrls, self.ik_constraint_targets, self.blend_jnts):
            constraint = pm.orientConstraint(fk_ctrl, ik_target, blend_jnt)
            weights = pm.orientConstraint(constraint, query=1, weightAliasList=1)
            pm.connectAttr(blend_plugs.rev.outputX, weights[0])
            pm.connectAttr(blend_plugs.multOutput, weights[1])

            blend_jnt.jointOrient.set(0, 0, 0)


        for i in range(2):
            blend = pm.shadingNode("blendTwoAttr", au=1)
            self.fk_ctrls[i].getParent().sx.connect(blend.input[0])
            self.ik_jnts[i].sx.connect(blend.input[1])
            pm.connectAttr(blend_plugs.multOutput, blend.attributesBlender)
            blend.output.connect(self.blend_jnts[i].sx)


        # FK/IK controls visibility
        for ctrl in self.fk_ctrls:
            blend_plugs.rev.outputX.connect(ctrl.visibility)

        ik_ctrls = [self.ctrls["ik_extrem"], self.ctrls["ik_pv"]]
        for ctrl in ik_ctrls:
            blend_plugs.mult.output.connect(ctrl.visibility)
        blend_plugs.mult.output.connect(self.ik_display_crv.getShape().visibility)





    ####################################################################################################################
    def install_rollers(self, start_node, end_node, seg_name, start_rot_match, end_rot_match, jnt_radius=0.3,
                        ctrl_mid_influ=False, populate_ctrls=(1, 1, 1), roll_axis=(1, 0, 0), up_axis=(0, 1, 0),
                        ctrl_color=0, side=None, parent=None):
        """

        """

        rollers = rig_utils.limb_rollers(start_node = start_node,
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
                                         parent = parent)


        # --------------------------------------------------------------------------------------------------------------
        return rollers





    ####################################################################################################################
    def install_limb_length_attrs(self):

        upperlimb_len_mult = node_utils.multDoubleLinear(input1=self.seg_lengths[0],
                                                         input2=self.ctrls["rig_socket"] + "." + "upperlimb_length")
        lowerlimb_len_mult = node_utils.multDoubleLinear(input1=self.seg_lengths[1],
                                                         input2=self.ctrls["rig_socket"] + "." + "lowerlimb_length")

        self.limb_length_mults.append(upperlimb_len_mult)
        self.limb_length_mults.append(lowerlimb_len_mult)

        if self.fk_ctrl_caps:
            upperlimb_len_mult.output.connect(self.fk_ctrl_caps[0].tx)
            lowerlimb_len_mult.output.connect(self.fk_ctrl_caps[1].tx)





    ####################################################################################################################
    def soft_ik_curve(self, input=None, output=None):

        # Create anim curve node
        anim_curve = pm.shadingNode('animCurveUU', name='{}_anim_crv_softIk_{}'.format(self.side_tag, self.limb_name),
                                    au=1)
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


        # --------------------------------------------------------------------------------------------------------------
        return anim_curve





    ####################################################################################################################
    def stretchy_ik(self, soft_ik=True, squash=True):
        """

        """

        if not self.limb_length_mults:
            self.install_limb_length_attrs()


        total_limb_len_sum = node_utils.addDoubleLinear(input1=self.limb_length_mults[0].output,
                                                        input2=self.limb_length_mults[1].output)

        ik_extrem_dist = self.ik_extrem_dist = node_utils.distanceBetween(
            inMatrix1=self.ctrls["rig_socket"].worldMatrix,
            inMatrix2=self.ctrls["ik_extrem"].worldMatrix)

        scaled_extrem_dist = node_utils.floatMath(floatA=ik_extrem_dist.distance,
                                                  floatB=self.root_grp + "." + "RigScale", operation=3)

        limb_straigtness_div = node_utils.floatMath(floatA=scaled_extrem_dist.outFloat,
                                                    floatB=total_limb_len_sum.output, operation=3)

        straight_condition = node_utils.condition(colorIfTrue=(limb_straigtness_div.outFloat, 0, 0),
                                                  colorIfFalse=(1, 1, 1), operation=2,
                                                  firstTerm=scaled_extrem_dist.outFloat,
                                                  secondTerm=total_limb_len_sum.output)

        [straight_condition.outColor.outColorR.connect(self.ik_jnts[i].scaleX) for i in (0, 1)]

        # ...Make stretch optional -------------------------------------------------------------------------------------
        stretch_option_remap = node_utils.remapValue(inputValue=self.ctrls["rig_socket"] + "." + "stretchy_ik",
                                                     outputMin=10, inputMax=10,
                                                     outputMax=straight_condition.outColor.outColorR,)
        [stretch_option_remap.outValue.connect(self.ik_jnts[i].scaleX, force=1) for i in (0, 1)]


        # ...Squash option ---------------------------------------------------------------------------------------------
        if squash:
            squash_remap = node_utils.remapValue(inputValue=self.ctrls["rig_socket"] + "." + "squash_ik",
                                                 inputMax=10, outputMin=1, outputMax=limb_straigtness_div.outFloat,
                                                 outValue=straight_condition.colorIfFalse.colorIfFalseR)



        # ...Include Soft IK effect ------------------------------------------------------------------------------------
        if soft_ik:
            pm.addAttr(self.ctrls["rig_socket"], longName="soft_ik", niceName="Soft IK", attributeType=float, minValue=0,
                       maxValue=10, defaultValue=0, keyable=1)

            num_space_div = node_utils.floatMath(floatA=100, floatB=total_limb_len_sum.output, operation=3)

            ratio_mult = node_utils.multDoubleLinear(input1=num_space_div.outFloat, input2=ik_extrem_dist.distance)

            anim_crv = self.soft_ik_curve(input=ratio_mult.output)

            soft_ik_weight_remap = node_utils.remapValue(inputValue=self.ctrls["rig_socket"] + "." + "soft_ik",
                                                         outputMax=anim_crv.output, inputMax=10, outputMin=1)

            soft_ik_weight_mult = node_utils.multDoubleLinear(input1=stretch_option_remap.outValue,
                                                              input2=soft_ik_weight_remap.outValue)
            [soft_ik_weight_mult.output.connect(self.ik_jnts[i].scaleX, force=1) for i in (0, 1)]





    ####################################################################################################################
    def blend_rig(self):

        # ...Blend skeleton
        self.create_blend_jnts()

        # ...Rollers
        lowerlimb_roller = self.install_rollers(start_node = self.blend_jnts[1],
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
            pm.connectAttr(self.ctrls["rig_socket"] + "." + bend_ctrl_vis_attr_string, ctrl.visibility)





    ####################################################################################################################
    def fk_rig(self):
        """
            Creates, positions, and arranges hierarchy of FK control chain
            Returns:
                (tuple, mObj):
                    FK controls, in order.
                    First control buffer group.
                    FK control caps, in order.
        """

        fk_ctrls_list = []
        fk_ctrl_caps = []

        for i in range(self.seg_count):

            # ...Create and parent control
            par = fk_ctrl_caps[i - 1] if i > 0 else None
            fk_ctrl = rig_utils.control(ctrl_info={"shape": "cube",
                                                   "scale": [self.seg_lengths[i] / 2 * 0.93,
                                                             self.seg_lengths[i] / 2 * self.ctrl_len_ratios[i],
                                                             self.seg_lengths[i] / 2 * self.ctrl_len_ratios[i]],
                                                   "offset": [self.seg_lengths[i] / 2, 0, 0]},
                                        name="{}_FK".format(self.seg_names[i]),
                                        ctrl_type=nom.animCtrl,
                                        side=self.side,
                                        parent=par,
                                        color=self.ctrl_colors["FK"])
            self.ctrls["{}_FK".format(self.seg_keys[i])] = fk_ctrl
            fk_ctrls_list.append(fk_ctrl)

            # ...Position control
            fk_ctrl.setParent(self.blend_jnts[i])
            gen_utils.zero_out(fk_ctrl)
            fk_ctrl.setParent(par) if par else fk_ctrl.setParent(world=1)

            # ...
            if i < self.seg_count - 1:
                cap = pm.createNode("transform", name="{}{}_FK_ctrl_CAP".format(self.side_tag, self.seg_names[i]))
                cap.setParent(fk_ctrl)
                gen_utils.zero_out(cap)
                pm.delete(pm.pointConstraint(self.blend_jnts[i + 1], cap))
                fk_ctrl_caps.append(cap)

            # ...Move unclean transforms into offsetParentMatrix (exclude first ctrl, it'll have a buffer grp instead)
            if i > 0:
                gen_utils.convert_offset(fk_ctrl)

        self.fk_ctrls = tuple(fk_ctrls_list)
        self.fk_ctrl_caps = tuple(fk_ctrl_caps)

        # ...Wrap top of ctrl chain in buffer group --------------------------------------------------------------------
        self.fk_ctrl_chain_buffer = gen_utils.buffer_obj(self.fk_ctrls[0], parent=self.ctrls["rig_socket"])
        self.fk_ctrl_chain_buffer.setParent(self.blend_jnts[0])
        gen_utils.zero_out(self.fk_ctrl_chain_buffer)
        self.fk_ctrl_chain_buffer.setParent(self.ctrls["rig_socket"])

        # ...Connect FK segment lengths to settings attributes ---------------------------------------------------------
        if self.limb_length_mults:
            self.limb_length_mults[0].output.connect(self.fk_ctrl_caps[0].tx)
            self.limb_length_mults[1].output.connect(self.fk_ctrl_caps[1].tx)

        # --------------------------------------------------------------------------------------------------------------
        pm.select(clear=1)
        return self.fk_ctrls, self.fk_ctrl_chain_buffer, self.fk_ctrl_caps





    ####################################################################################################################
    def ik_rig(self):

        self.create_ik_jnt_chain()
        self.create_ik_ctrls()
        self.install_limb_ik_solver()
        self.install_extrem_ik_solver()
        self.stretchy_ik()
        if self.include_extrem_fk_rot:
            self.install_ik_extrem_rot_ctrl()





    ####################################################################################################################
    def install_ribbon_systems(self):


        ctrl_size = 0.7

        ribbon_up_vector = (0, 0, -1)
        if self.side == nom.rightSideTag:
            ribbon_up_vector = (0, 0, 1)

        # ...Create ribbons
        upper_limb_ribbon = rig_utils.ribbon_plane(name=self.seg_names[0], start_obj=self.bend_jnts[0],
                                                   end_obj=self.bend_jnts[2], up_obj=self.ctrls["ik_pv"],
                                                   density=self.seg_resolution, side=self.side,
                                                   up_vector=ribbon_up_vector)
        upper_limb_ribbon["nurbsStrip"].setParent(self.no_transform_grp)
        upper_limb_ribbon["nurbsStrip"].scale.set(1, 1, 1)

        lower_limb_ribbon = rig_utils.ribbon_plane(name=self.seg_names[1], start_obj=self.bend_jnts[3],
                                                   end_obj=self.bend_jnts[5], up_obj=self.ctrls["ik_pv"],
                                                   density=self.seg_resolution, side=self.side,
                                                   up_vector=ribbon_up_vector)
        lower_limb_ribbon["nurbsStrip"].setParent(self.no_transform_grp)
        lower_limb_ribbon["nurbsStrip"].scale.set(1, 1, 1)


        # ...Skin ribbons
        pm.select(self.bend_jnts[0], self.bend_jnts[1], self.bend_jnts[2], replace=1)
        pm.select(upper_limb_ribbon["nurbsStrip"], add=1)
        pm.skinCluster(maximumInfluences=1, toSelectedBones=1)

        pm.select(self.bend_jnts[3], self.bend_jnts[4], self.bend_jnts[5], replace=1)
        pm.select(lower_limb_ribbon["nurbsStrip"], add=1)
        pm.skinCluster(maximumInfluences=1, toSelectedBones=1)


        # ...Tweak ctrls
        tweak_color = 1
        if self.side == nom.leftSideTag:
            tweak_color = self.ctrl_colors["sub"][0]
        elif self.side == nom.rightSideTag:
            tweak_color = self.ctrl_colors["sub"][1]

        upperlimb_tweak_ctrls = rig_utils.ribbon_tweak_ctrls(ribbon = upper_limb_ribbon["nurbsStrip"],
                                                             ctrl_name = self.seg_names[0],
                                                             length_ends = (self.ctrls["rig_socket"],
                                                                            self.ctrls["mid_limb_pin"]),
                                                             length_attr = self.limb_length_mults[0].output,
                                                             attr_ctrl = self.ctrls["rig_socket"],
                                                             side = self.side,
                                                             ctrl_color = tweak_color,
                                                             ctrl_resolution = 5,
                                                             parent = self.no_transform_grp,
                                                             ctrl_size=ctrl_size)
        self.tweak_ctrls.append(upperlimb_tweak_ctrls)

        lowerlimb_tweak_ctrls = rig_utils.ribbon_tweak_ctrls(ribbon = lower_limb_ribbon["nurbsStrip"],
                                                             ctrl_name = self.seg_names[1],
                                                             length_ends = (self.ctrls["mid_limb_pin"],
                                                                            self.blend_jnts[2]),
                                                             length_attr = self.limb_length_mults[1].output,
                                                             attr_ctrl = self.ctrls["rig_socket"],
                                                             side = self.side,
                                                             ctrl_color = tweak_color,
                                                             ctrl_resolution = 5,
                                                             parent = self.no_transform_grp,
                                                             ctrl_size=ctrl_size)
        self.tweak_ctrls.append(lowerlimb_tweak_ctrls)





    ####################################################################################################################
    def resize_tweak_controls(self):

        old_seg_lengths, new_seg_lengths = self.seg_lengths, self.final_seg_lengths

        for i in range(self.seg_count-1):

            upscale_mult = new_seg_lengths[i] / old_seg_lengths[i]

            for ctrl in self.tweak_ctrls[i]:

                gen_utils.scale_obj_shape(ctrl, scale=(upscale_mult, upscale_mult, upscale_mult))





    ####################################################################################################################
    def move_to_final_pose(self):
        """

        """

        # ...Get segment lengths according to final pose node positions ------------------------------------------------
        self.final_seg_lengths = (
            gen_utils.distance_between(obj_1=self.final_pose_nodes[0], obj_2=self.final_pose_nodes[1]),
            gen_utils.distance_between(obj_1=self.final_pose_nodes[1], obj_2=self.final_pose_nodes[2]),
            gen_utils.distance_between(obj_1=self.final_pose_nodes[2], obj_2=self.final_pose_nodes[3]),
        )


        # ...Update places in rig where final default lengths are hardcoded --------------------------------------------
        self.limb_length_mults[0].input1.set(self.final_seg_lengths[0])
        self.limb_length_mults[1].input1.set(self.final_seg_lengths[1])



        # ...Match upper limb ------------------------------------------------------------------------------------------
        # ...Rig socket control
        pm.delete(pm.pointConstraint(self.final_pose_nodes[0], self.ctrls["rig_socket"].getParent()))

        # ...FK upper limb
        pm.delete(pm.aimConstraint(self.final_pose_nodes[1], self.fk_ctrls[0].getParent(), worldUpType="objectrotation",
                                   aimVector=(1, 0, 0), worldUpVector=(0, 1, 0), upVector=(0, 1, 0),
                                   worldUpObject=self.final_pose_nodes[1]))

        pm.delete(pm.orientConstraint(self.ctrls["upperlimb_FK"], self.roll_socket_target))


        # ...Match lower limb ------------------------------------------------------------------------------------------
        # ...FK lower limb
        gen_utils.convert_offset(self.fk_ctrls[1], reverse=True)
        pm.delete(pm.aimConstraint(self.final_pose_nodes[2], self.fk_ctrls[1], worldUpType="objectrotation",
                                   aimVector=(1, 0, 0), worldUpVector=(0, 1, 0), upVector=(0, 1, 0),
                                   worldUpObject=self.final_pose_nodes[2]))
        gen_utils.convert_offset(self.fk_ctrls[1])


        # ...Match extremity -------------------------------------------------------------------------------------------
        # ...FK extremity
        gen_utils.convert_offset(self.fk_ctrls[2], reverse=True)
        pm.delete(pm.aimConstraint(self.final_pose_nodes[3], self.fk_ctrls[2], worldUpType="objectrotation",
                                   aimVector=(1, 0, 0), worldUpVector=(0, 1, 0), upVector=(0, 1, 0),
                                   worldUpObject=self.final_pose_nodes[3]))
        gen_utils.convert_offset(self.fk_ctrls[2])
        # ...IK extremity
        pm.delete(pm.parentConstraint(self.final_pose_nodes[2], self.ctrls["ik_extrem"].getParent()))
        # ...IK pole vector
        pm.delete(pm.pointConstraint(self.final_pose_nodes[4], self.ctrls["ik_pv"].getParent()))

        if self.include_extrem_fk_rot:
            pm.delete(pm.orientConstraint(self.ctrls["ik_extrem"], self.ctrls["ik_extrem_rot"].getParent()))

        self.ik_handles["extrem"].tx.set(gen_utils.distance_between(obj_1=self.final_pose_nodes[2],
                                                                    obj_2=self.final_pose_nodes[3]))


        # ...Match extremity end ---------------------------------------------------------------------------------------
        [jnt.tx.set(self.final_seg_lengths[2]) for jnt in (self.ik_jnts[3], self.blend_jnts[3])]


        # ...
        self.blend_jnts[1].tx.set(self.ik_jnts[1].tx.get())
        self.blend_jnts[2].tx.set(self.ik_jnts[2].tx.get())
        self.blend_jnts[3].tx.set(self.ik_jnts[3].tx.get())


        # ...Resize tweak controls to fit new limb dimensions ----------------------------------------------------------
        self.resize_tweak_controls()
