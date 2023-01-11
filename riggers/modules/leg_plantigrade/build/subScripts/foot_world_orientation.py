# Title: foot_world_orientation.py
# Author: Sam Leheny
# Contact: samleheny@live.com

# Description: Changes orientation of ik feet to (symmetrical) world orientation. So world up (+y) is foot up. World
# forward (+z) is foot forward, etc.


###########################
##### Import Commands #####
import importlib
import pymel.core as pm

import Snowman3.utilities.general_utils as gen_utils
importlib.reload(gen_utils)

import Snowman3.dictionaries.nameConventions as nameConventions
importlib.reload(nameConventions)
nom = nameConventions.create_dict()
###########################
###########################


###########################
######## Variables ########

###########################
###########################

def reorient_ik_foot(ik_foot_ctrl, side):

    side_tag = f'_{side}' if side else ''

    #...Give IK foot control world orientation
    ctrl = ik_foot_ctrl
    ctrl_buffer = ctrl.getParent()

    #...Temporarily moved shapes into a holder node (will move them back after reorientation)
    temp_shape_holder = pm.shadingNode('transform', name='TEMP_shape_holder', au=1)
    gen_utils.copy_shapes(ctrl, temp_shape_holder, keep_original=True)
    [pm.delete(shape) for shape in ctrl.getShapes()]

    ori_offset = pm.shadingNode('transform', name=f'{side_tag}ikFoot_ori_OFFSET', au=1)
    ori_offset.setParent(ctrl_buffer)
    gen_utils.zero_out(ori_offset)
    ori_offset.setParent(world=1)

    [child.setParent(ori_offset) for child in ctrl.getChildren()]

    par = ctrl_buffer.getParent()
    ctrl_buffer.setParent(world=1)

    if side == nom.leftSideTag:
        ctrl_buffer.rotate.set(0, 0, 0)
        ctrl_buffer.scale.set(1, 1, 1)
    elif side == nom.rightSideTag:
        ctrl_buffer.rotate.set(0, 180, 0)
        ctrl_buffer.scale.set(1, 1, -1)
    ctrl_buffer.setParent(par)

    ori_offset.setParent(ctrl)

    #...Return shapes to control transform
    gen_utils.copy_shapes(temp_shape_holder, ctrl, keep_original=False)