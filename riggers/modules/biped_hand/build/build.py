# Title: hand_build.py
# Author: Sam Leheny
# Contact: samleheny@live.com

# Description: Builds setup module of biped biped_hand rig.


###########################
##### Import Commands #####
import importlib
import pymel.core as pm

import Snowman3.utilities.general_utils as gen_utils
importlib.reload(gen_utils)

import Snowman3.utilities.node_utils as node_utils
importlib.reload(node_utils)

import Snowman3.utilities.rig_utils as rig_utils
importlib.reload(rig_utils)

import Snowman3.dictionaries.nameConventions as nameConventions
importlib.reload(nameConventions)
nom = nameConventions.create_dict()

import Snowman3.riggers.modules.biped_hand.utilities.animCtrls as animCtrls
importlib.reload(animCtrls)

###########################
###########################


###########################
######## Variables ########

###########################
###########################





########################################################################################################################
#def build(rig_module=None, rig_parent=None, rig_space_connector=None):
def build(rig_module, rig_parent=None):


    '''
    # Stick biped_hand to end of biped_arm rig -------------------------------------------------------------------------
    gen_utils.matrix_constraint(objs=[rig_space_connector, rig_module.transform_grp], decompose=True,
                                translate=True, rotate=True, scale=True, shear=False)



    # ...Controls ------------------------------------------------------------------------------------------------------
    [ctrls[key].setParent(rig_module.transform_grp) for key in ctrl_data]


    gen_utils.convert_offset(ctrls["handBend"])



    # ...Finger rigs ---------------------------------------------------------------------------------------------------

    finger_rigs = {}

    def build_finger_rig(finger_dict, seg_count=4, has_metacarpal=True):

        # ...If a non-Thumb finger, include zero segment (the metacarpal)
        start_index = 0 if has_metacarpal else 1

        prev_seg_connector = None

        # ...Run procedure for each segment in finger
        for i in range(start_index, start_index + seg_count):


            n = str(i) if i > 0 else "meta"

            # Get segment control
            ctrl = ctrls[finger_dict["key"] + "_" + n]

            #  Parent control to output of preceding segment (if there is a preceding segment)
            if i > start_index:
                ctrl.setParent(prev_seg_connector)

            # Create joint under control
            jnt = rig_utils.joint(name="fingerIndex_{}".format(n), side=rig_module.side, joint_type=nom.bindJnt,
                                  radius=0.5)
            temp_grp = gen_utils.buffer_obj(jnt, parent=ctrl)
            gen_utils.zero_out(temp_grp)
            jnt.setParent(ctrl)
            pm.delete(temp_grp)

            # Use joint as output that connects this segment to the next
            prev_seg_connector = jnt


            # If this is the first segment, wrap it in an extra group to absorb dirty rotations
            if i == start_index:
                finger_root = gen_utils.buffer_obj(ctrl)
                finger_dict["root"] = finger_root


            # ...Compose segment output dictionary
            finger_dict["segs"].append({"jnt": jnt,
                                       "ctrl": ctrl})



    for finger_key in ("index", "middle", "ring", "pinky", "thumb"):

        finger_rig = finger_rigs[finger_key] = {"segs": [],
                                                "key": finger_key}

        if finger_key == "thumb":
            seg_count = 3
            has_metacarpal = False
        else:
            seg_count = 4
            has_metacarpal = True

        build_finger_rig(seg_count=seg_count, finger_dict=finger_rig, has_metacarpal=has_metacarpal)


    for key in ("index", "middle", "ring", "pinky"):

        # Wrap metacarpal segments in an extra group to receive rotation from the handBend control
        finger_rig = finger_rigs[key]
        ctrl_meta_offset = finger_rig["handBend_offset"] = gen_utils.buffer_obj(finger_rig["segs"][0]["ctrl"],
                                                                                suffix="HANDBEND")



    for finger_key, multiplier in (("middle", 0.15),
                                   ("ring", 0.5),
                                   ("pinky", 1.0)):

        if multiplier == 1.0:
            output_plug = ctrls["handBend"].rotate
        else:
            mult = pm.shadingNode("animBlendNodeAdditiveRotation", au=1)
            ctrls["handBend"].rotate.connect(mult.inputA)
            mult.weightA.set(multiplier)
            output_plug = mult.output

        output_plug.connect(finger_rigs[finger_key]["handBend_offset"].rotate)




    # ...Quick Pose control --------------------------------------------------------------------------------------------
    quickPose_ctrl = ctrls["quickPose_fingers"]

    unit_convert = pm.shadingNode("unitConversion", au=1)
    quickPose_ctrl.tz.connect(unit_convert.input)
    unit_convert.conversionFactor.set(-0.1)

    # ...Create curl transforms above each segment in fingers (exclude metacarpals)
    for key in ("index", "middle", "ring", "pinky"):

        finger = finger_rigs[key]

        # Curling
        for i in range(1, len(finger["segs"])):
            seg = finger["segs"][i]
            curl_buffer = seg["curl_buffer"] = gen_utils.buffer_obj(seg["ctrl"])
            quickPose_ctrl.rz.connect(curl_buffer.rz)

            if i == 1:
                unit_convert.output.connect(curl_buffer.ry)

        # Spread + Fanning
        seg_1 = finger["segs"][1]
        spread_buffer = finger["spread_buffer"] = gen_utils.buffer_obj(seg_1["ctrl"])

    # Spread + Fanning network
    zeroSpace_sum = node_utils.addDoubleLinear(input1=quickPose_ctrl.sz, input2=-1)
    for key, spread_weight, fan_weight in (("index", -50, -1),
                                           ("middle", -16.666, -0.333),
                                           ("ring", 16.666, 0.333),
                                           ("pinky", 50, 1)):

        spread_mult = node_utils.multDoubleLinear(input1=zeroSpace_sum.output, input2=spread_weight,
                                                  output=finger_rigs[key]["spread_buffer"].ry)
        fan_mult = pm.shadingNode("animBlendNodeAdditiveDA", au=1)
        quickPose_ctrl.rx.connect(fan_mult.inputA)
        fan_mult.weightA.set(fan_weight)
        fan_mult.output.connect(finger_rigs[key]["spread_buffer"].rz)



    # ...Clean control transforms --------------------------------------------------------------------------------------
    for ctrl in ctrls.values():
        gen_utils.convert_offset(ctrl)



    # ------------------------------------------------------------------------------------------------------------------
    pm.select(clear=1)
    return rig_module'''
