# Title: general_utils.py
# Author: Sam Leheny
# Contact: samleheny@live.com

# Description: We generally want to avoid importing utility files into one another as it quickly leads to infinite
# recursion errors. 'general_utils' is an exception to this rule; A function belongs here if it is general enough that
# it's likely to be useful in the bodies of other utility functions.


###########################
##### Import Commands #####
import pymel.core as pm

import Snowman.utilities.general_utils as gen_utils
reload(gen_utils)
###########################
###########################


# Global variables #####################################################################################################
all_transform_attrs = ["translate", "tx", "ty", "tz", "rotate", "rx", "ry", "rz", "scale", "sx", "sy", "sz", "shear",
                       "shearXY", "shearXZ", "shearYZ"]
keyable_attrs = ["translate", "tx", "ty", "tz", "rotate", "rx", "ry", "rz", "scale", "sx", "sy", "sz", "visibility"]
keyable_transform_attrs = ["translate", "tx", "ty", "tz", "rotate", "rx", "ry", "rz", "scale", "sx", "sy", "sz"]
translate_attrs = ["tx", "ty", "tz"]
all_translate_attrs = ["translate", "tx", "ty", "tz"]
rotate_attrs = ["rx", "ry", "rz"]
all_rotate_attrs = ["rotate", "rx", "ry", "rz"]
scale_attrs = ["sx", "sy", "sz"]
all_scale_attrs = ["scale", "sx", "sy", "sz"]
vis_attrs = ["visibility"]



########################################################################################################################
#############-------------------------------    TABLE OF CONTENTS    ------------------------------------###############
########################################################################################################################
'''
compose_matrix
decompose_matrix
zero_offsetParentMatrix
convert_offset
'''
########################################################################################################################
########################################################################################################################
########################################################################################################################





########################################################################################################################
def compose_matrix(transforms):
    """

        Args:
            transforms ():
        Return:
    """

    t = transforms
    compose = pm.shadingNode("composeMatrix", au=1)

    pm.setAttr(compose + ".inputTranslate", t[0], t[1], t[2])
    pm.setAttr(compose + ".inputRotate", t[3], t[4], t[5])
    pm.setAttr(compose + ".inputScale", t[6], t[7], t[8])
    pm.setAttr(compose + ".inputShear", t[9], t[10], t[11])

    matrix = pm.getAttr(compose + ".outputMatrix")

    pm.delete(compose)


    return matrix





########################################################################################################################
def decompose_matrix(matrix):
    """

        Args:
            matrix ():
        Return:
    """

    attr_mode = None
    array_mode = None
    matrix_mode = None


    if type(matrix) == str:
        attr_mode = True
    elif type(matrix) == list:
        array_mode = True
    else:
        matrix_mode = True


    # Use decomposeMatrix node to break provided matrix down into attributes
    decomp = pm.shadingNode("decomposeMatrix", au=1)

    if attr_mode:
        pm.connectAttr(matrix, decomp + ".inputMatrix")

    elif array_mode:
        m = matrix
        pm.setAttr(decomp + ".inputMatrix", m[0], m[1], m[2], m[3], m[4], m[5], m[6], m[7], m[8], m[9], m[10], m[11],
                   m[12], m[13], m[14], m[15], type="matrix")

    elif matrix_mode:
        pm.setAttr(decomp + ".inputMatrix", matrix)


    # Compose output dictionary
    output_translate = [pm.getAttr(decomp + ".outputTranslate.outputTranslateX"),
                       pm.getAttr(decomp + ".outputTranslate.outputTranslateY"),
                       pm.getAttr(decomp + ".outputTranslate.outputTranslateZ")]

    output_rotate = [pm.getAttr(decomp + ".outputRotate.outputRotateX"),
                    pm.getAttr(decomp + ".outputRotate.outputRotateY"),
                    pm.getAttr(decomp + ".outputRotate.outputRotateZ")]

    output_scale = [pm.getAttr(decomp + ".outputScale.outputScaleX"),
                   pm.getAttr(decomp + ".outputScale.outputScaleY"),
                   pm.getAttr(decomp + ".outputScale.outputScaleZ")]

    output_shear = [pm.getAttr(decomp + ".outputShear.outputShearX"),
                   pm.getAttr(decomp + ".outputShear.outputShearY"),
                   pm.getAttr(decomp + ".outputShear.outputShearZ")]


    output = {"translate": output_translate,
              "rotate": output_rotate,
              "scale": output_scale,
              "shear": output_shear}

    # Delete decomposeMatrix node. We're finished with it.
    pm.delete(decomp)


    return output





########################################################################################################################
def zero_offsetParentMatrix(obj, force=0, zero_transforms=0):
    """

        Args:
            obj ():
            force ():
            zero_transforms ():
    """

    if force in [True, 1]:
        pm.setAttr(obj+'.offsetParentMatrix', lock=0)
        pm.disconnectAttr(node=obj, attr='offsetParentMatrix', source=True)


    # Take note of any locked attributes
    # tx, ty, tz, rx, ry, rz, sx, sy, sz
    locks = [0, 0, 0, 0, 0, 0, 0, 0, 0]
    lock_attr_list = ['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz']

    for attr in lock_attr_list:
        if pm.getAttr(obj+'.'+attr, lock=1) in [True, 1]:
            locks[lock_attr_list.index(attr)] = 1


    for attr in ["tx", "ty", "tz", "rx", "ry", "rz", "sx", "sy", "sz", "shearXY", "shearXZ", "shearYZ"]:
        pm.setAttr(obj+'.'+attr, lock=0)
        #pm.setAttr(obj+'.'+attr, channelBox=1)


    # Zero out offset parent matrix
    pm.setAttr(obj+'.offsetParentMatrix', compose_matrix([0, 0, 0, 0, 0, 0, 1, 1, 1, 0, 0, 0]),
               type='matrix')


    # Zero out transforms if specified
    if zero_transforms in [True, 1]:
        gen_utils.zero_out(obj)


    # Re-lock attributes
    for val in locks:
        if val == 1:
            pm.setAttr( obj + "." + lock_attr_list[locks.index(val)], lock=1)





########################################################################################################################
def convert_offset(obj, reverse=False):
    """
        Moves any non-zero values from the transform values and moves them into the Offset Parent Matrix, retaining the
        position of the object while keeping the transform attributes clean.

        Args:
            obj (dagObj): The object to perform transform conversion on.
            reverse (bool): If True, performs conversion in reverse - moving the values from the Offset Parent Matrix
                into the transform attributes.
    """


    # Check if any transform attributes on object are locked, and if so unlock them
    lock_status = [0,0,0,0,0,0,0,0,0,0,0,0]
    attr_list = ["tx", "ty", "tz", "rx", "ry", "rz", "sx", "sy", "sz", "shearXY", "shearXZ", "shearYZ"]
    lock_list = []

    for i in xrange(len(attr_list)):

        attr = "{}.{}".format(obj, attr_list[i])
        if pm.getAttr(attr, lock=1):
            lock_status[i] = 1
            pm.setAttr("{}.{}".format(obj, attr_list[i]), lock=0, keyable=1)
            lock_list.append(attr)


    if not reverse:

        # Get current matrix of object
        m = pm.getAttr(obj + ".matrix")

        # Get current offset parent matrix of object
        opm = pm.getAttr(obj + ".offsetParentMatrix")

        # Convert both matrices to standard attribute form
        matrix_transforms = decompose_matrix(m)
        offset_parent_matrix_transforms = decompose_matrix(opm)
        transforms = [
            matrix_transforms["translate"][0] + offset_parent_matrix_transforms["translate"][0],
            matrix_transforms["translate"][1] + offset_parent_matrix_transforms["translate"][1],
            matrix_transforms["translate"][2] + offset_parent_matrix_transforms["translate"][2],

            matrix_transforms["rotate"][0] + offset_parent_matrix_transforms["rotate"][0],
            matrix_transforms["rotate"][1] + offset_parent_matrix_transforms["rotate"][1],
            matrix_transforms["rotate"][2] + offset_parent_matrix_transforms["rotate"][2],

            matrix_transforms["scale"][0] * offset_parent_matrix_transforms["scale"][0],
            matrix_transforms["scale"][1] * offset_parent_matrix_transforms["scale"][1],
            matrix_transforms["scale"][2] * offset_parent_matrix_transforms["scale"][2],

            matrix_transforms["shear"][0] + offset_parent_matrix_transforms["shear"][0],
            matrix_transforms["shear"][1] + offset_parent_matrix_transforms["shear"][1],
            matrix_transforms["shear"][2] + offset_parent_matrix_transforms["shear"][2],
        ]

        # Compose new matrix from the sum of object's matrix and offset parent matrix
        nm = compose_matrix(transforms)

        # Set offset parent matrix as new matrix
        pm.setAttr(obj+'.offsetParentMatrix', nm, type='matrix')

        # Zero out transform attributes
        gen_utils.zero_out(obj)

        # Re-lock any transform values that were locked
        for i in xrange(len(attr_list)):
            if lock_status[i] == 1:
                attr = "{}.{}".format(obj, attr_list[i])
                pm.setAttr(attr, lock=1, keyable=0)



    elif reverse in [True, 1]:
        temp_loc = pm.spaceLocator()
        temp_loc.setParent(obj.getParent())
        gen_utils.match_position(temp_loc, obj, method='parent', preserve_scale=0)

        try:
            source = pm.listConnections(obj+'.offsetParentMatrix', source=1, plugs=1)[0]
            pm.disconnectAttr(source, obj+'.offsetParentMatrix')
        except:
            pass

        zero_offsetParentMatrix(obj)
        gen_utils.match_position(obj, temp_loc, method='parent', preserve_scale=0)
        if obj.type() == "joint":
            obj.rotate.set( obj.rotate.get() + obj.jointOrient.get() )
            obj.jointOrient.set(0, 0, 0)
        pm.delete(temp_loc)