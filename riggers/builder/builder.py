# Title: build_biped.py
# Author: Sam Leheny
# Contact: samleheny@live.com

# Description: Class to handle the building of biped armature and final rig.


###########################
##### Import Commands #####
import importlib
import pymel.core as pm
import Snowman3.riggers.utilities.classes.class_Armature as classArmature
import Snowman3.riggers.utilities.classes.class_Rig as classRig
importlib.reload(classArmature)
importlib.reload(classRig)
Armature = classArmature.Armature
Rig = classRig.Rig

import Snowman3.utilities.general_utils as gen_utils
importlib.reload(gen_utils)

import Snowman3.dictionaries.nameConventions as nameConventions
importlib.reload(nameConventions)
nom = nameConventions.create_dict()

import Snowman3.riggers.utilities.bodyRigWrapup as rigWrapup
importlib.reload(rigWrapup)

import Snowman3.riggers.utilities.directories.get_armature_data as get_armature_data
importlib.reload(get_armature_data)
###########################
###########################


###########################
######## Variables ########

###########################
###########################



#...Symmetry and side variables
symmetry_info = gen_utils.symmetry_info("Left drives Right")
default_symmetry_mode = symmetry_info[0]





########################################################################################################################
def build_armature_in_scene(armature):

    #...Create and move into armature namespace
    pm.namespace(add=nom.setupRigNamespace)
    pm.namespace(set=nom.setupRigNamespace)

    #...Build armature
    armature.populate_armature()

    #...Return to default scene namespace
    pm.namespace(set=":")
    pm.select(clear=1)
    return armature





########################################################################################################################
def build_prefab_armature(prefab_tag, symmetry_mode=None):

    armature = get_armature_data.armature(prefab_tag, symmetry_mode=symmetry_mode)
    build_armature_in_scene(armature)

    return armature





########################################################################################################################
def build_armature_from_data(data):

    armature = Armature(name = data["name"],
                        root_size = data["root_size"],
                        symmetry_mode = data["symmetry_mode"],
                        modules = data["modules"])
    armature.modules_from_data()
    build_armature_in_scene(armature)

    return armature





########################################################################################################################
def build_rig_in_scene(asset_name=None, armature=None):

    #...Create namespace for final rig and set it as current namespace
    pm.namespace(add=nom.finalRigNamespace)
    pm.namespace(set=nom.finalRigNamespace)

    rig = Rig(name=asset_name, armature=armature)
    rig.populate_rig()

    #...Put a bow on this puppy!
    rigWrapup.execute(modules=rig.modules)
    pm.select(clear=1)



    '''
    # --------------------------------------------------------------------------------------------------------------
    #...Body modules ----------------------------------------------------------------------------------------------
    # --------------------------------------------------------------------------------------------------------------

    #...Root controls module ######################################################################################
    rig_module_parent = None
    root_module = root_build.build(rig_parent=rig_grp)
    rig_module_parent = root_module["rig_modules_grp"]





    #...Spine module ##############################################################################################
    ################################################################################################################

    armature_module = get_armature_modules("biped_spine", armature)

    spine_rig = modules["spine"] = RigModule(
        name = "spine",
        rig_module_type = "biped_spine",
        armature_module = armature_module,
        piece_keys = ["spine_1", "spine_2", "spine_3", "spine_4", "spine_5", "spine_6"]
    )

    spine_build.build(rig_module=modules["spine"], rig_parent=rig_module_parent)





    #...Neck module ###############################################################################################
    ################################################################################################################

    armature_module = get_armature_modules("biped_neck", armature)

    neck_rig = modules["neck"] = RigModule(
        name = "neck",
        rig_module_type = "biped_neck",
        armature_module = armature_module,
        piece_keys=["neck", "head"],
    )

    neck_build.build(rig_module=modules["neck"], rig_parent=rig_module_parent,
                     rig_space_connector=modules["spine"].neck_connector)

    #...Neck rotation space blend -----------------------------------------------------------------------------
    rig_utils.space_blender(target=modules["neck"].ctrls["neck"].getParent(),
                            source=modules["spine"].ctrls["ik_chest"],
                            source_name="chest",
                            name="neck",
                            attr_node=modules["neck"].ctrls["neck"],
                            default_value=10,
                            global_space_parent=root_module["root_spaces_grp"],
                            rotate=True)
    #...Head rotation space blend -----------------------------------------------------------------------------
    rig_utils.space_blender(target=modules["neck"].ctrls["head"].getParent(),
                            source=modules["neck"].neck_len_end_node,
                            source_name="neck",
                            name="head",
                            attr_node=modules["neck"].ctrls["head"],
                            default_value=0,
                            global_space_parent=root_module["root_spaces_grp"],
                            rotate=True)





    #...Clavicle modules ##########################################################################################
    ################################################################################################################

    for side in [nom.leftSideTag, nom.rightSideTag]:

        armature_module = get_armature_modules("{}_clavicle".format(side), armature)

        clavicle_rig = modules[side + "_clavicle"] = sided_modules[side]["clavicle"] = RigModule(
            name = "clavicle",
            rig_module_type = "biped_clavicle",
            armature_module = armature_module,
            side = side,
            piece_keys = ["clavicle", "clavicle_end"],
            is_driven_side = False,
        )

        clavicle_build.build(
            rig_module = modules[side + "_clavicle"],
            rig_parent = rig_module_parent,
            rig_space_connector = modules["spine"].clavicles_connector
        )





    #...Arm modules ###############################################################################################
    ################################################################################################################

    for side in [nom.leftSideTag, nom.rightSideTag]:

        armature_module = get_armature_modules("{}_arm".format(side), armature)

        arm_rig = modules[side + "_arm"] = sided_modules[side]["arm"] = RigModule(
            name = "arm",
            rig_module_type = "biped_arm",
            armature_module = armature_module,
            side = side,
            piece_keys = ["upperarm", "lowerarm", "lowerarm_end", "wrist_end", "ik_elbow"],
            is_driven_side = False,

        )
        arm_build.build(
            rig_module = modules[side + "_arm"],
            rig_parent = rig_module_parent,
            rig_space_connector = modules[side + "_clavicle"].shoulder_connector,
            settings_ctrl_parent = modules["spine"].clavicles_connector)

        #...Space blends --------------------------------------------------------------------------------------
        #...FK shoulder
        rig_utils.space_blender(target=arm_rig.ctrls["fk_upperarm"].getParent(),
                                source=modules["spine"].ctrls["ik_chest"],
                                source_name="chest",
                                name="fkShoulder",
                                attr_node=arm_rig.ctrls["fk_upperarm"],
                                default_value=10,
                                global_space_parent=root_module["root_spaces_grp"],
                                rotate=True)
        #...IK elbow pole vector
        rig_utils.space_blender(target=arm_rig.ctrls["ik_elbow"].getParent(),
                                source=arm_rig.ctrls["ik_hand"],
                                source_name="hand",
                                name="ikElbow",
                                attr_node=arm_rig.ctrls["ik_elbow"],
                                default_value=10,
                                global_space_parent=root_module["root_spaces_grp"],
                                rotate=True, translate=True)
        #...IK biped_hand
        rig_utils.space_blender(target=arm_rig.ctrls["ik_hand"].getParent(),
                                source=arm_rig.ctrls["ik_hand_follow"],
                                source_name="ikHandFollow",
                                name="ikHand",
                                attr_node=arm_rig.ctrls["ik_hand"],
                                default_value=10,
                                global_space_parent=root_module["root_spaces_grp"],
                                rotate=True, translate=True, scale=True)





    #...Hand modules ##############################################################################################
    ################################################################################################################

    for side in [nom.leftSideTag, nom.rightSideTag]:

        armature_module = get_armature_modules("{}_hand".format(side), armature)

        hand_rig = modules[side + "_hand"] = sided_modules[side]["hand"] = RigModule(
            name = "hand",
            rig_module_type = "biped_hand",
            armature_module = armature_module,
            side = side,
            piece_keys=["hand", "index_metacarpal", "index_1", "index_2", "index_3", "index_end",
                        "middle_metacarpal", "middle_1", "middle_2", "middle_3", "middle_end",
                        "ring_metacarpal", "ring_1", "ring_2", "ring_3", "ring_end",
                        "pinky_metacarpal", "pinky_1", "pinky_2", "pinky_3", "pinky_end",
                        "thumb_1", "thumb_2", "thumb_3", "thumb_end",
                        "ik_index", "ik_middle", "ik_ring", "ik_pinky", "ik_thumb"],
            is_driven_side = False,
        )

        hand_build.build(
            rig_module = modules[side + "_hand"],
            rig_parent=rig_module_parent,
            rig_space_connector=modules[side + "_arm"].hand_connector)





    #...Leg modules ###############################################################################################
    ################################################################################################################
    
    for side in [nom.leftSideTag, nom.rightSideTag]:

        armature_module = get_armature_modules("{}_leg".format(side), armature)

        leg_rig = modules[side + "_leg"] = sided_modules[side]["leg"] = RigModule(
            name = "leg",
            rig_module_type = "leg_plantigrade",
            armature_module = armature_module,
            side = side,
            piece_keys = ["thigh", "calf", "calf_end", "ankle_end", "ik_knee"],
            is_driven_side = False
        )

        leg_build.build(
            rig_module = modules[side + "_leg"],
            rig_parent = rig_module_parent,
            rig_space_connector = modules["spine"].hips_connector,
            ctrl_parent = modules["spine"].hips_connector)

        #...Space blends --------------------------------------------------------------------------------------
        #...FK thigh
        rig_utils.space_blender(target=leg_rig.ctrls["fk_thigh"].getParent(),
                                source=modules["spine"].ctrls["ik_pelvis"],
                                source_name="pelvis",
                                name="fkHip",
                                attr_node=leg_rig.ctrls["fk_thigh"],
                                default_value=10,
                                global_space_parent=root_module["root_spaces_grp"],
                                rotate=True)
        #...IK knee pole vector
        rig_utils.space_blender(target=leg_rig.ctrls["ik_knee"].getParent(),
                                source=leg_rig.ctrls["ik_foot"],
                                source_name="foot",
                                name="ikKnee",
                                attr_node=leg_rig.ctrls["ik_knee"],
                                default_value=10,
                                global_space_parent=root_module["root_spaces_grp"],
                                rotate=True, translate=True)
        #...IK foot
        rig_utils.space_blender(target=leg_rig.ctrls["ik_foot"].getParent(),
                                source=leg_rig.ctrls["ik_foot_follow"],
                                source_name="ikFootFollow",
                                name="ikFoot",
                                attr_node=leg_rig.ctrls["ik_foot"],
                                default_value=10,
                                global_space_parent=root_module["root_spaces_grp"],
                                rotate=True, translate=True, scale=True)





    #...Foot modules ##############################################################################################
    ################################################################################################################
    
    for side in [nom.leftSideTag, nom.rightSideTag]:

        armature_module = get_armature_modules("{}_foot".format(side), armature)

        foot_rig = modules[side + "_foot"] = sided_modules[side]["foot"] = foot_rig = RigModule(
            name = "foot",
            rig_module_type = "foot_plantigrade",
            armature_module = armature_module,
            side = side,
            piece_keys = ["foot", "ball", "ball_end", "sole_toe", "sole_toe_end",
                          "sole_inner", "sole_outer", "sole_heel"],
            is_driven_side = False,
        )

        foot_build.build(
            rig_module = modules[side + "_foot"],
            rig_parent=rig_module_parent,
            settings_ctrl=modules[side + "_leg"].ctrls["hip_pin"],
            foot_roll_ctrl=modules[side + "_leg"].ctrls["ik_foot"])

        #...Connect various foot rig modules to biped_leg rig
        #...Bind skeleton
        foot_rig.bind_connector.setParent(modules[side + "_leg"].leg_end_bind_connector)
        #...FK rig
        foot_rig.fk_root_input.setParent(modules[side + "_leg"].ctrls["fk_foot"])
        #...IK rig
        foot_rig.ik_connector.setParent(modules[side + "_leg"].leg_end_ik_connector)
        foot_rig.ik_chain_connector.setParent(modules[side + "_leg"].leg_end_ik_jnt_connector)
        modules[side + "_leg"].ik_handle.setParent(foot_rig.foot_roll_jnts["ankle"])
        foot_rig.foot_roll_jnts["ankle"].worldMatrix[0].connect(
            modules[side + "_leg"].ik_foot_dist_node.inMatrix2, f=1)





    for module in modules.values():
        pm.connectAttr(root_module["controls"]["root"] + "." + "RigScale", module.rig_module_grp + "." + "RigScale",
                       force=1)


    #...Put a bow on this puppy!
    rigWrapup.execute(modules=modules)

    #...Clear any selections
    pm.select(clear=1)'''
