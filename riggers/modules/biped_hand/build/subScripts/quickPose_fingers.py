# Title: quickPos_fingers.py
# Author: Sam Leheny
# Contact: samleheny@live.com

# Description: Setups up nodes and math connections to implement quick pose control over the fingers of a hand rig.


###########################
##### Import Commands #####
import importlib
import pymel.core as pm

import Snowman3.utilities.general_utils as gen_utils
importlib.reload(gen_utils)

import Snowman3.utilities.node_utils as node_utils
importlib.reload(node_utils)
###########################
###########################


###########################
######## Variables ########
finger_keys = ['index', 'middle', 'ring', 'pinky']
###########################
###########################





########################################################################################################################
#def build(rig_module=None, rig_parent=None, rig_space_connector=None):
def install(quick_pose_ctrl, finger_rigs):

    quickPose_ctrl = quick_pose_ctrl

    unit_convert = pm.shadingNode('unitConversion', au=1)
    quickPose_ctrl.tz.connect(unit_convert.input)
    unit_convert.conversionFactor.set(-0.1)

    #...Create curl transforms above each segment in fingers (exclude metacarpals)
    for key in finger_keys:

        finger = finger_rigs[key]

        # Curling
        for i in range(1, len(finger['segs'])):
            seg = finger['segs'][i]
            curl_buffer = seg['curl_buffer'] = gen_utils.buffer_obj(seg['ctrl'])
            quickPose_ctrl.rz.connect(curl_buffer.rz)

            if i == 1:
                unit_convert.output.connect(curl_buffer.ry)

        # Spread + Fanning
        seg_1 = finger['segs'][1]
        spread_buffer = finger['spread_buffer'] = gen_utils.buffer_obj(seg_1['ctrl'])

    # Spread + Fanning network
    zeroSpace_sum = node_utils.addDoubleLinear(input1=quickPose_ctrl.sz, input2=-1)
    for key, spread_weight, fan_weight in (('index', -50, -1),
                                           ('middle', -16.666, -0.333),
                                           ('ring', 16.666, 0.333),
                                           ('pinky', 50, 1)):
        spread_mult = node_utils.multDoubleLinear(input1=zeroSpace_sum.output, input2=spread_weight,
                                                  output=finger_rigs[key]['spread_buffer'].ry)
        fan_mult = pm.shadingNode('animBlendNodeAdditiveDA', au=1)
        quickPose_ctrl.rx.connect(fan_mult.inputA)
        fan_mult.weightA.set(fan_weight)
        fan_mult.output.connect(finger_rigs[key]['spread_buffer'].rz)