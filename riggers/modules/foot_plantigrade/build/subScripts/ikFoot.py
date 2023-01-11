# Title: ikFoot.py
# Author: Sam Leheny
# Contact: samleheny@live.com

# Description: Builds setup module of biped foot rig.


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
###########################
###########################


###########################
######## Variables ########
body_module_type = "foot_plantigrade"
###########################
###########################





########################################################################################################################
def build(side=None, parent=None, bind_jnt_keys=None, orienters=None, ctrls=None, foot_roll_ctrl=None):


    side_tag = f'{side}_' if side else ''



    #...IK joints -----------------------------------------------------------------------------------------------------
    ik_connector = pm.group(name=f'{side_tag}ikConnector', em=1, p=parent)
    gen_utils.zero_out(ik_connector)
    pm.delete(pm.pointConstraint(orienters['foot'], ik_connector))

    ik_jnts = {}
    ik_chain_buffer = None
    for i, key in enumerate(bind_jnt_keys):
        par = ik_jnts[bind_jnt_keys[i-1]] if i > 0 else None
        ik_jnts[key] = rig_utils.joint(name=f'ik_{key}', joint_type=nom.nonBindJnt, side=side, radius=1.0, parent=par)
        if i == 0:
            ik_chain_buffer = gen_utils.buffer_obj(ik_jnts[key])

    ik_chain_buffer.setParent(ik_connector)
    gen_utils.zero_out(ik_chain_buffer)

    for i, key in enumerate(bind_jnt_keys):
        if i == 0:
            pm.matchTransform(ik_chain_buffer, orienters[key])
        else:
            pm.matchTransform(ik_jnts[key], orienters[key])
            rig_utils.joint_rot_to_ori(ik_jnts[key])




    #...Foot roll jnts-------------------------------------------------------------------------------------------------
    foot_roll_jnts = {}
    foot_roll_chain_buffer = None
    foot_roll_keys = ("heel", "ballPivot", "outer", "inner", "toeTip", "ball", "ankle")
    for i, key in enumerate(foot_roll_keys):
        par = foot_roll_jnts[foot_roll_keys[i-1]] if i > 0 else None
        foot_roll_jnts[key] = rig_utils.joint(name=f'footRoll_{key}', joint_type=nom.nonBindJnt, side=side, radius=1.5,
                                              parent=par)
        if i == 0:
            foot_roll_chain_buffer = gen_utils.buffer_obj(foot_roll_jnts[key])

    foot_roll_chain_buffer.setParent(ik_connector)
    gen_utils.zero_out(foot_roll_chain_buffer)

    #... Get foot roll placer positions
    foot_roll_placer_keys = ("sole_heel", "sole_toe", "sole_outer", "sole_inner", "sole_toe_end", "ball", "foot")

    for placer_key, roll_key in zip(foot_roll_placer_keys, foot_roll_keys):
        pm.delete(pm.pointConstraint(orienters[placer_key], foot_roll_jnts[roll_key]))

    ctrls["ik_toe"].setParent(foot_roll_jnts["toeTip"])




    #...IK handles ----------------------------------------------------------------------------------------------------
    ik_handles = {}
    ik_effectors = {}

    for tag, jnts, parent in (("foot", (ik_jnts["foot"], ik_jnts["ball"]), foot_roll_jnts["ball"]),
                              ("toe", (ik_jnts["ball"], ik_jnts["ball_end"]), ctrls["ik_toe"])):

        ik_handles[tag], ik_effectors[tag] = pm.ikHandle(name=f'{side_tag}{tag}_{nom.ikHandle}',
                                                         startJoint=jnts[0], endEffector=jnts[1], solver='ikSCsolver')
        ik_effectors[tag].rename(f'{side_tag}ik_{tag}_{nom.effector}')
        ik_handles[tag].setParent(parent)
    
    
    
    
    #...Foot roll attributes ------------------------------------------------------------------------------------------
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


    #...Ball
    #...Roll
    ball_toe_total_delay = node_utils.addDoubleLinear(input1=f'{foot_roll_ctrl}.BallDelay',
                                                      input2=f'{foot_roll_ctrl}.ToeRollStart')

    pushed_ball_return = node_utils.addDoubleLinear(input1=ball_toe_total_delay.output,
                                                    input2=f'{foot_roll_ctrl}.ToeRollStart')

    ball_remap_A = node_utils.remapValue(inputValue=f'{foot_roll_ctrl}.FootRoll',
                                         inputMin=f'{foot_roll_ctrl}.BallDelay',
                                         inputMax=ball_toe_total_delay.output, outputMin=0,
                                         outputMax=f'{foot_roll_ctrl}.ToeRollStart')

    ball_remap_B = node_utils.remapValue(inputValue=f'{foot_roll_ctrl}.FootRoll',
                                         inputMin=ball_toe_total_delay.output,
                                         inputMax=pushed_ball_return.output,
                                         outputMin=f'{foot_roll_ctrl}.ToeRollStart', outputMax=0)

    ball_con = node_utils.condition(firstTerm=f'{foot_roll_ctrl}.FootRoll',
                                    secondTerm=ball_toe_total_delay.output,
                                    colorIfTrue=(ball_remap_B.outValue, 0, 0),
                                    colorIfFalse=(ball_remap_A.outValue, 1, 1),
                                    operation='greater or equal',
                                    outColor=(foot_roll_jnts['ball'].rx, None, None))

    node_utils.addDoubleLinear(input1=ball_con.outColor.outColorR, input2=f'{foot_roll_ctrl}.BallRoll',
                               output=foot_roll_jnts['ball'].rx, force=True)

    #...Spin
    pm.connectAttr(f'{foot_roll_ctrl}.BallSpin', foot_roll_jnts['ballPivot'].ry)


    #...Toe tip
    #...Roll
    pushed_toe_total = node_utils.addDoubleLinear(input1=total_angle, input2=ball_toe_total_delay.output)

    toe_remap = node_utils.remapValue(inputValue=f'{foot_roll_ctrl}.FootRoll', inputMin=ball_toe_total_delay.output,
                                      inputMax=pushed_toe_total.output, outputMin=0, outputMax=total_angle,
                                      outValue=foot_roll_jnts["toeTip"].rx)

    node_utils.addDoubleLinear(input1=toe_remap.outValue, input2=f'{foot_roll_ctrl}.ToeRoll',
                               output=foot_roll_jnts['toeTip'].rx, force=True)
    #...Spin
    pm.connectAttr(f'{foot_roll_ctrl}.ToeSpin', foot_roll_jnts['toeTip'].ry)


    #...Heel
    #...Roll
    clamp = node_utils.clamp(input=(f'{foot_roll_ctrl}.FootRoll', None, None), min=(-total_angle, 0, 0),
                             max=(0, 0, 0), output=(foot_roll_jnts['heel'].rx, None, None))

    node_utils.addDoubleLinear(input1=clamp.output.outputR, input2=f'{foot_roll_ctrl}.HeelRoll',
                               output=foot_roll_jnts['heel'].rx, force=True)
    #...Spin
    pm.connectAttr(f'{foot_roll_ctrl}.HeelSpin', foot_roll_jnts['heel'].ry)


    #...Banking
    [pm.connectAttr(foot_roll_ctrl + "." + "Bank", foot_roll_jnts[key].rz) for key in ("outer", "inner")]
    pm.setAttr(foot_roll_jnts["outer"] + '.maxRotLimitEnable.maxRotZLimitEnable', 1)
    pm.setAttr(foot_roll_jnts["outer"] + '.maxRotLimit.maxRotZLimit', 0)
    pm.setAttr(foot_roll_jnts["inner"] + '.minRotLimitEnable.minRotZLimitEnable', 1)
    pm.setAttr(foot_roll_jnts["inner"] + '.minRotLimit.minRotZLimit', 0)





    # ------------------------------------------------------------------------------------------------------------------
    pm.select(clear=1)
    return {"ik_connector": ik_connector,
            "ik_jnts": ik_jnts,
            "foot_roll_jnts": foot_roll_jnts}
