# Title: general_utils.py
# Author: Sam Leheny
# Contact: samleheny@live.com
# Description: We generally want to avoid importing utility files into one another as it quickly leads to infinite
# recursion errors. 'general_utils' is an exception to this rule; A function belongs here if it is general enough that
# it's likely to be useful in the bodies of other utility functions.


###########################
##### Import Commands #####
import importlib
import copy
import pymel.core as pm
import maya.OpenMaya as om
import maya.api.OpenMaya as om2
import math as math
import numpy as np

import Snowman3.dictionaries.nurbsCurvePrefabs as nurbsCurvePrefabs
importlib.reload(nurbsCurvePrefabs)
curve_prefabs = nurbsCurvePrefabs.create_dict()

import Snowman3.dictionaries.nameConventions as nameConventions
importlib.reload(nameConventions)
nom = nameConventions.create_dict()
###########################
###########################


# Global variables ########
ALL_TRANSFORM_ATTRS = ['translate', 'tx', 'ty', 'tz', 'rotate', 'rx', 'ry', 'rz', 'scale', 'sx', 'sy', 'sz', 'shear',
                       'shearXY', 'shearXZ', 'shearYZ']
KEYABLE_ATTRS = ['translate', 'tx', 'ty', 'tz', 'rotate', 'rx', 'ry', 'rz', 'scale', 'sx', 'sy', 'sz', 'visibility']
KEYABLE_TRANSFORM_ATTRS = ['translate', 'tx', 'ty', 'tz', 'rotate', 'rx', 'ry', 'rz', 'scale', 'sx', 'sy', 'sz']
TRANSLATE_ATTRS = ['tx', 'ty', 'tz']
ALL_TRANSLATE_ATTRS = ['translate', 'tx', 'ty', 'tz']
ROTATE_ATTRS = ['rx', 'ry', 'rz']
ALL_ROTATE_ATTRS = ['rotate', 'rx', 'ry', 'rz']
SCALE_ATTRS = ['sx', 'sy', 'sz']
ALL_SCALE_ATTRS = ['scale', 'sx', 'sy', 'sz']
SHEAR_ATTRS = ['shearXY', 'shearXZ', 'shearYZ']
ALL_SHEAR_ATTRS = ['shear', 'shearXY', 'shearXZ', 'shearYZ']
VIS_ATTRS = ['visibility']
###########################



########################################################################################################################
############# ------------------------------    TABLE OF CONTENTS    ----------------------------------- ###############
########################################################################################################################
'''
buffer_obj
zero_out
distance_between
vector_between
flip_obj
get_color
set_color
cross_product
normalize_vector
orthogonal_vectors
vectors_to_euler
format_axis_arg
rearrange_point_list_vectors
nurbs_curve
get_colour_from_sided_list
curve_obj
rename_shapes
prefab_curve_obj
break_connections
get_clean_name
get_opposite_side_obj
position_between
copy_shapes
compose_matrix
decompose_matrix
zero_offsetParentMatrix
convert_offset
get_skin_cluster
create_attr_blend_nodes
get_attr_blend_nodes
point_on_surface_matrix
flip
get_shape_center
interp
get_shape_data_from_obj
matrix_to_list
list_to_matrix
get_obj_matrix
drive_attr
create_lock_memory
lock_attrs_from_memory
match_pose_ori
create_follicle
get_closest_uv_on_surface
parent_jnt
safe_parent
'''
########################################################################################################################
########################################################################################################################
########################################################################################################################



########################################################################################################################
def buffer_obj(child, suffix=None, name=None, _parent=None):
    """
        Creates a new transform object above provided object and moves provided object's dirty transforms into the new
            parent, allowing the child's transforms to be clean (zeroed) while maintaining its world transforms.
        Args:
            child (dagNode): The object to be moved into new buffer obj.
            suffix (string): String to be appended to child object's name to produce the name of the new buffer obj.
            name (string): (Optional) If provided, suffix parameter will be ignored and instead the new buffer obj's
                name will be determined by this argument.
            _parent (dagNode): (Optional) Specifies object to parent new buffer node to. If argument not provided, will
                default to parenting new buffer obj to child obj's original parent.
        Returns:
            (transform node) The newly created buffer obj.
    """

    def remove_leading_underscore(_string):
        if _string[0] == '_':
            _suffix = _string.split('_')[1]
        return _string


    pm.select(clear=1)

    # Variables
    default_suffix = 'buffer'
    child_name = get_clean_name(child.nodeName())

    # Ensure a valid naming method for new buffer obj
    if not name:
        suffix = suffix if suffix else default_suffix
        suffix = remove_leading_underscore(suffix)

    # Check if child's transforms are free to be cleaned (not receiving connections)
    connected_attrs = []

    for attr in ALL_TRANSFORM_ATTRS:
        incoming_connection = pm.listConnections(f'{child}.{attr}', source=1, destination=0, plugs=1)
        if incoming_connection:
            connected_attrs.append(f'{child_name}.{attr}')

    if connected_attrs:
        error_string = ''
        for attr in connected_attrs:
            error_string += f'{attr}\n'
        pm.error("\nCould not clean child object transforms - The following transforms have incoming connections:"
                 f"\n{error_string}\n")

    # Check for locked attributes. If any are found, remember them, then unlock them for the duration of this function
    lock_memory = []
    for attr in ALL_TRANSFORM_ATTRS:
        if pm.getAttr(f'{child}.{attr}', lock=1):
            lock_memory.append(attr)
            pm.setAttr(f'{child}.{attr}', lock=0)

    # Get child obj's parent
    world_is_original_parent = False
    if not _parent:
        _parent = child.getParent()
    if not _parent:
        world_is_original_parent = True

    buffer_name = name if name else f'{child_name}_{suffix}'

    buffer_node = pm.shadingNode('transform', name=buffer_name, au=1)

    # Match buffer obj to child's transforms
    buffer_node.setParent(child)
    for attr in ('translate', 'rotate', 'shear'):
        pm.setAttr(f'{buffer_node}.{attr}', 0, 0, 0)
        buffer_node.scale.set(1, 1, 1)
    buffer_node.setParent(world=1)

    safe_parent(child, buffer_node)

    # Clean child's transforms
    [pm.setAttr(f'{child}.{attr}', 0, 0, 0) for attr in ('translate', 'rotate', 'shear')]
    child.scale.set(1, 1, 1)

    # Parent buffer obj
    if not world_is_original_parent:
        safe_parent(buffer_node, _parent)

    # Re-lock any attributes on child obj that were locked previously
    if lock_memory:
        [pm.setAttr(f'{child}.{attr}', lock=1) for attr in lock_memory]

    pm.select(clear=1)
    return buffer_node



########################################################################################################################
def zero_out(obj, translate=None, rotate=None, scale=None, shear=None, jnt_orient=True, unlock=False):
    """
        Reduce provided object's local transform attributes to 0 (1, for scale attributes).
            Will target specific transforms if their arguments are specified. If all left blank, will default to zeroing
            out all transforms.
        Args:
            obj (transform node): The object whose transforms should be zeroed.
            translate (bool): If specified, transform attribute will be zeroed (as opposed to all transform attributes)
            rotate (bool): If specified, transform attribute will be zeroed (as opposed to all transform attributes)
            scale (bool): If specified, transform attribute will be zeroed (as opposed to all transform attributes)
            shear (bool): If specified, transform attribute will be zeroed (as opposed to all transform attributes)
            jnt_orient (bool):
            unlock (bool): If True, any attributes unlocked throughout function will remain unlocked.
    """

    # Determine which transform attributes to target
    transforms = {'translate' : True,
                  'rotate' : True,
                  'scale' : True,
                  'shear' : True}

    transform_attrs = ALL_TRANSFORM_ATTRS


    if translate is None and rotate is None and scale is None and shear is None:
        pass

    else:

        transforms['translate'] = translate
        transforms['rotate'] = rotate
        transforms['scale'] = scale
        transforms['shear'] = shear

        transform_attrs = []
        if transforms['translate']:
            for attr in ALL_TRANSLATE_ATTRS:
                transform_attrs.append(attr)
        if transforms['rotate']:
            for attr in ALL_ROTATE_ATTRS:
                transform_attrs.append(attr)
        if transforms['scale']:
            for attr in ALL_SCALE_ATTRS:
                transform_attrs.append(attr)
        if transforms['shear']:
            for attr in ALL_SHEAR_ATTRS:
                transform_attrs.append(attr)


    # Check if child's transforms are free to be cleaned (not receiving connections)
    connected_attrs = []

    for attr in transform_attrs:

        incoming_connection = pm.listConnections(f'{obj}.{attr}', source=1, destination=0, plugs=1)

        if incoming_connection:
            connected_attrs.append(f'{obj}.{attr}')

    if connected_attrs:

        error_string = ""

        for attr in connected_attrs:
            error_string += ("{0}\n".format(attr))

        pm.error(f"\nCould not clean object ({obj}) transforms - The following transforms have incoming connections:"
                 f"\n{error_string}\n")


    # Check for locked attributes. If any are found, remember them, then unlock them for the duration of this function
    lock_memory = []

    for attr in transform_attrs:

        if pm.getAttr(obj + "." + attr, lock=1):

            lock_memory.append(attr)

            pm.setAttr(obj + "." + attr, lock=0)


    # Zero out transforms
    if transforms["translate"]:
        obj.translate.set(0, 0, 0)

    if transforms["rotate"]:
        obj.rotate.set(0, 0, 0)
        # Include jointOrient attributes in procedure
        if jnt_orient:
            if obj.nodeType() == "joint":
                obj.jointOrient.set(0, 0, 0)

    if transforms["scale"]:
        obj.scale.set(1, 1, 1)

    if transforms["shear"]:
        obj.shear.set(0, 0, 0)


    # Re-lock attributes
    if lock_memory:

        if not unlock:

            for attr in lock_memory:
                pm.setAttr(obj + "." + attr, lock=1)



########################################################################################################################
def distance_between(obj_1=None, obj_2=None, position_1=None, position_2=None):
    """
        Returns the world space distance between two objects or between two world space positions. Can also mix and
            match objects and positions, e.g. the distance between one object and one position.
        Args:
            obj_1 (transform node): First object. Will be used if obj_2 arg or position2 arg is also provided.
            obj_2 (transform node): Second object. Will be used if obj_1 arg or position1 arg is also provided.
            position_1 (tuple(float, float, float)): First world space position. Will be used if position_2 arg or obj_2
                arg is also provided.
            position_2 (tuple(float, float, float)): Second world space position. Will be used if position1 arg or obj_1
                arg is also provided.
        Returns:
            (float) The distance calculated between the provided arguments.
    """


    # Initialize final position variables
    pos_1 = None
    pos_2 = None
    
    
    # Determine which combination of objects and positions to use based on which arguments were provided.
    #   Order of priority:
    #       obj_1 & obj_2
    #       position_1 & position_2
    #       obj_1 & position_2
    #       position_1 & obj_2
    if obj_1 and obj_2:
        pos_1 = pm.xform(obj_1, q=1, worldSpace=1, rotatePivot=1)
        pos_2 = pm.xform(obj_2, q=1, worldSpace=1, rotatePivot=1)
    
    elif position_1 and position_2:
        pos_1 = position_1
        pos_2 = position_2
    
    elif obj_1 and position_2:
        pos_1 = pm.xform(obj_1, q=1, worldSpace=1, rotatePivot=1)
        pos_2 = position_2
    
    elif position_1 and obj_2:
        pos_1 = position_1
        pos_2 = pm.xform(obj_2, q=1, worldSpace=1, rotatePivot=1)
    
    else:
        pm.error("Not enough arguments provided. Two of the following arguments must be provided:"
                 "'obj_1', 'obj_2', 'position_1', 'position_2'")
    
    
    if pos_1 and pos_2:
        pass
    else:
        pm.error("Something went wrong. Need to define both 'pos_1' and 'pos_2' variables.")

    
    # Use distance formula in 3 dimensions
    distance = (((pos_1[0] - pos_2[0]) ** 2)
                + ((pos_1[1] - pos_2[1]) ** 2)
                + ((pos_1[2] - pos_2[2]) ** 2)) ** 0.5
    


    return distance



########################################################################################################################
def vector_between(obj_1=None, obj_2=None, vector_1=None, vector_2=None):
    """
    Calculates a vector from one object to another. Can provide either two objects to use their vectors, or can provide
        two specific vectors.
    Args:
        obj_1 (mTransformObj):
        obj_2 (mTransformObj):
        vector_1 (tuple(float, float, float)):
        vector_2 (tuple(float, float, float)):
    Returns:
        (float, float, float) The calculated vector.
    """


    # Initialize final position variables
    pos_1 = None
    pos_2 = None

    # Determine which combination of objects and positions to use based on which arguments were provided.
    #   Order of priority:
    #       obj_1 & obj_2
    #       position_1 & position_2
    #       obj_1 & position_2
    #       position_1 & obj_2
    if obj_1 and obj_2:
        pos_1 = pm.xform(obj_1, q=1, worldSpace=1, rotatePivot=1)
        pos_2 = pm.xform(obj_2, q=1, worldSpace=1, rotatePivot=1)

    elif vector_1 and vector_2:
        pos_1 = vector_1
        pos_2 = vector_2

    elif obj_1 and vector_2:
        pos_1 = pm.xform(obj_1, q=1, worldSpace=1, rotatePivot=1)
        pos_2 = vector_2

    elif vector_1 and obj_2:
        pos_1 = vector_1
        pos_2 = pm.xform(obj_2, q=1, worldSpace=1, rotatePivot=1)

    else:
        pm.error("Not enough arguments provided. Two of the following arguments must be provided:"
                 "'obj_1', 'obj_2', 'position_1', 'position_2'")



    result_vector = (pos_2[0] - pos_1[0],
                     pos_2[1] - pos_1[1],
                     pos_2[2] - pos_1[2])


    return result_vector



########################################################################################################################
def flip_obj(obj=None, axis="x"):
    """
        Flips an object across the desired axis.
        Args:
            obj (mTransformObj):
            axis (string/ [int, int, int]):
    """

    if axis in ("x", "X", (1, 0, 0)):
        obj.ry.set( obj.ry.get() + 180 )
        obj.sz.set( obj.sz.get() * -1 )

    if axis in ("y", "Y", (0, 1, 0)):
        obj.rx.set( obj.rx.get() + 180 )
        obj.sz.set( obj.sz.get() * -1 )

    if axis in ("z", "Z", (0, 0, 1)):
        obj.sz.set(obj.sz.get() * -1)



########################################################################################################################
def get_color(obj):

    decimals = 4

    color = None
    objs = []

    if obj.overrideEnabled.get():
        objs.append(obj)
    else:
        shapes = obj.getShapes()
        if shapes:
            for s in shapes:
                if s.overrideEnabled.get():
                    objs.append(s)


    for obj in objs:
        # Test to see if colour override index or custom colour is used, and return found colour data as a float, or
        # list
        if obj.overrideRGBColors.get() is False:
            color = obj.overrideColor.get()
        else:
            color = obj.overrideColorRGB.get()
            color = list(color)
            color = [round(color[i], decimals) for i, v in enumerate(color)]
        if color:
            break


    # Return colour information
    return color



########################################################################################################################
def set_color(obj, color=None, apply_to_transform=False):


    # Colour assign function
    def apply_override_color(obj_to_color=None):

        obj_to_color.overrideEnabled.set(True)

        # Choose whether to use index colour or RGB based on whether the col parameter is one value or three
        if isinstance(color, (int, float)):
            obj_to_color.overrideRGBColors.set(False)
            obj_to_color.overrideColor.set(color)

        elif isinstance(color, (tuple, list)) and len(color) == 3:
            obj_to_color.overrideRGBColors.set(True)
            obj_to_color.overrideColorRGB.set( tuple(color) )



    # Colour object
    # If object is a joint, apply to joint
    if obj.nodeType() == 'joint':
        apply_override_color(obj)

    # If object is a transform...
    elif obj.nodeType() == 'transform':

        # Apply colour to transform if specified...
        if apply_to_transform:
            apply_override_color(obj)

        # Or else, find shapes nodes under transform and apply colour to them
        else:
            obj_shapes = obj.getShapes()
            for shape in obj_shapes:
                apply_override_color(shape)



    # If provided object was already a shape node, apply to object
    elif obj.nodeType() in ('mesh', 'nurbsCurve', 'nurbsSurface', 'locator'):
        apply_override_color(obj)



########################################################################################################################
def cross_product(a, b, normalize=False):
    """
        Gets cross product of input vectors a and b.
        Args:
            a ((numeric, numeric, numeric)): First of two input vectors.
            b ((numeric, numeric, numeric)): Second of two input vectors.
            normalize (bool): If on, will convert resulting vector to a unit vector (magnitude of 1, but same direction)
        Returns:
            ((float, float, float)) Cross product of a and b.
    """

    c = np.cross(np.array(a), np.array(b)).tolist()

    if normalize:
        c = normalize_vector(c)

    return c



########################################################################################################################
def normalize_vector(vector):
    """
        Normalizes a vector (reduces its magnitude/length to 1.0, without disturbing its direction (if negative, will
            remain negative))
        Args:
            vector ((float, float, float)): The input vector to be normalized.
        Return:
            ((float, float, float)) normalized vector result.
    """

    c = np.array(vector)
    c_len = np.linalg.norm(c)

    normalized_c = []
    for v in c:
        normalized_c.append(v / abs(c_len))

    normalized_c = tuple(normalized_c)


    return normalized_c



########################################################################################################################
def orthogonal_vectors(vector_1, vector_2):
    """
        Given any two vectors, returns three orthogonal vector (all perpendicular) based on the cross product between
            the two provided vectors.
        Args:
            vector_1 ((float, float, float)): First vector. This will end up being the first vector in the final three.
            vector_2 ((float, float, float)): Second vector. Will be used in a cross product with the vector_1 in order
                to find the two orthogonal vectors to vector_1.
        Return:
            ((float, float, float)): Three orthogonal vectors corresponding to the vector_1 arg.
    """

    final_vector_1 = normalize_vector(vector_1)
    final_remaining_vector = cross_product(vector_1, vector_2, normalize=True)
    final_vector_2 = cross_product(final_remaining_vector, vector_1, normalize=True)


    return final_vector_1, final_vector_2, final_remaining_vector



########################################################################################################################
def vectors_to_euler(aim_vector, up_vector, aim_axis, up_axis, rotation_order):

    #...Neatly format axis arguments, so we don't have to keep checking multiple possible input types
    aim_axis = format_axis_arg(aim_axis)
    up_axis = format_axis_arg(up_axis)

    #...Vector order matters. X comes before Y which comes before Z
    flip_order = False
    if not aim_axis == "x":
        if aim_axis == "y":
            if not up_axis == "z":
                flip_order = True
        else:
            flip_order = True


    if not flip_order:
        final_aim_vector, final_up_vector, final_remaining_vector = orthogonal_vectors(aim_vector, up_vector)
    else:
        final_up_vector, final_aim_vector, final_remaining_vector = orthogonal_vectors(up_vector, aim_vector)


    mat_x = [0, 0, 0]
    if aim_axis == "x":
        mat_x = [final_aim_vector[0], final_aim_vector[1], final_aim_vector[2]]
    elif up_axis == "x":
        mat_x = [final_up_vector[0], final_up_vector[1], final_up_vector[2]]
    else:
        mat_x = [final_remaining_vector[0], final_remaining_vector[1], final_remaining_vector[2]]


    mat_y = [0, 0, 0]
    if aim_axis == "y":
        mat_y = [final_aim_vector[0], final_aim_vector[1], final_aim_vector[2]]
    elif up_axis == "y":
        mat_y = [final_up_vector[0], final_up_vector[1], final_up_vector[2]]
    else:
        mat_y = [final_remaining_vector[0], final_remaining_vector[1], final_remaining_vector[2]]


    mat_z = [0, 0, 0]
    if aim_axis == "z":
        mat_z = [final_aim_vector[0], final_aim_vector[1], final_aim_vector[2]]
    elif up_axis == "z":
        mat_z = [final_up_vector[0], final_up_vector[1], final_up_vector[2]]
    else:
        mat_z = [final_remaining_vector[0], final_remaining_vector[1], final_remaining_vector[2]]


    matrix_list = [mat_x[0], mat_x[1], mat_x[2], 0,
                   mat_y[0], mat_y[1], mat_y[2], 0,
                   mat_z[0], mat_z[1], mat_z[2], 0,
                   0, 0, 0, 1]

    mMatrix = om.MMatrix()
    om.MScriptUtil.createMatrixFromList(matrix_list, mMatrix)

    mTransformMtx = om.MTransformationMatrix(mMatrix)
    eulerRot = mTransformMtx.eulerRotation()
    eulerRot.reorderIt(rotation_order)

    angles = [math.degrees(angle) for angle in (eulerRot.x, eulerRot.y, eulerRot.z)]

    return angles



########################################################################################################################
def format_axis_arg(axis):

    output = False


    if input in ("x", "X", (1, 0, 0)):
        output = "x"

    elif input in ("y", "Y", (0, 1, 0)):
        output = "y"

    elif input in ("z", "Z", (0, 0, 1)):
        output = "z"


    return output



########################################################################################################################
def rearrange_point_list_vectors(point_list=None, up_direction=None, forward_direction=None):
    """
        Goes through a list of point coordinates and rearranges each point's coordinates such that the resulting shape
            made from those points will be rotated. (Requires: numpy)
        Args:
            point_list (mTransformObj): The list of coordinates to be rearranged.
            up_direction ([float, float, float]):
            forward_direction ([float, float, float]):
        Returns:
            (list) List with entries rearranged to obey new vectors
    """

    y = up_direction
    z = forward_direction
    x = cross_product(y, z)

    move_matrix = np.asmatrix(np.array([ [x[0], y[0], z[0]],
                                         [x[1], y[1], z[1]],
                                         [x[2], y[2], z[2]] ]))

    new_point_list = [move_matrix.dot(p).tolist()[0] for p in point_list]

    return new_point_list



########################################################################################################################
def get_colour_from_sided_list(sided_list, side):
    sided_colors = {nom.leftSideTag: sided_list[0],
                    nom.rightSideTag: sided_list[1]}
    color = sided_colors[side]
    return color



########################################################################################################################
def nurbs_curve(name=None, cvs=None, degree=3, form='open', color=None):
    """
    Creates a nurbs curve from information in provided arguments.
    Args:
        name (string): Curve name.
        color (numeric/ [float, float, float]): Override color of curve. If an integer is provided, will use as
            override color index. If list of three numbers (integers or floats) is provided, will use as RGB color.
        form (string): Determines whether curve shape should be a closed loop. Acceptable
            inputs: 'open', 'periodic'
        cvs (list): List of coordinates for curve CVs.
        degree (int): Curve smoothing degree. Acceptable degrees: 1, 3.
    Returns:
        (mTransform object) The newly created curve object.
    """

    crv = pm.curve(name=name, degree=degree, point=cvs)
    if form == "periodic":
        pm.closeCurve(crv, replaceOriginal=1, preserveShape=0)
    pm.delete(crv, constructionHistory=True)
    if color:
        set_color(crv, color)

    pm.select(clear=1)
    return crv



########################################################################################################################
def rename_shapes(obj):

    #...Make sure we're dealing with shape nodes, not transform nodes
    if not pm.nodeType(obj) in ['transform']:
        print("Cannot rename shapes for node '{}'. Function must be given a transform node".format(obj))
        return None

    shapes = obj.getShapes()
    if not shapes:
        return None

    #...Compose dictionary of new shape names
    new_shape_names = []
    for i, v in enumerate(shapes):
        new_name = "{}Shape{}".format( get_clean_name(obj), str(i+1) )
        new_shape_names.append(new_name)

    #...Give all shapes temporary names to avoid conflicts while we rename
    for shape in shapes:
        shape.rename("TEMP_SHAPE_NAME_{}".format( str(shapes.index(shape)) ))

    #...Give shapes their final names
    for shape in shapes:
        shape.rename(new_shape_names[ shapes.index(shape) ])

    return new_shape_names



########################################################################################################################
def break_connections(attr, incoming=True, outgoing=False):
    """

        Args:
            attr ():
            incoming (bool):
            outgoing (bool):
    """


    if incoming:

        connected_attrs = pm.listConnections(attr, source=1, plugs=1)
        for connected_attr in connected_attrs:
            try:
                pm.setAttr(attr, lock=0)
                pm.disconnectAttr(connected_attr, attr)
            except Exception:
                pass

    if outgoing:

        connected_attrs = pm.listConnections(attr, destination=1, plugs=1)
        for connected_attr in connected_attrs:
            try:
                pm.setAttr(attr, lock=0)
                pm.disconnectAttr(attr, connected_attr)
            except Exception:
                pass



########################################################################################################################
def match_position(obj, match_to, method="parent", preserve_scale=1, enforce_scale_of_one=0):

    pm.select(clear=1)

    jnt_status = False

    if pm.objectType(obj) == "joint":
        jnt_status = True

    if method == "parent":
        try:
            parent = obj.getParent()
        except Exception:
            try:
                parent = pm.ls(obj)[0].getParent()
            except Exception:
                parent=None
        pm.parent(obj, match_to)
        zero_out(obj, jnt_orient=jnt_status)


        if parent in [None, "parentIsWorld"]:
            pm.parent(obj, world=1)

        else:
            pm.parent(obj, parent)


    elif method == "constraint":
        pm.delete(pm.parentConstraint(match_to, obj))
        pm.delete(pm.scaleConstraint(match_to, obj))

    if preserve_scale:
        scale_vals = list(obj.scale.get())
        axes = ["x", "y", "z"]
        for i in range(3):
            if scale_vals[i] > 0:
                pm.setAttr("{}.s{}".format(obj, axes[i]), 1)
            elif scale_vals[i] < 0:
                pm.setAttr("{}.s{}".format(obj, axes[i]), -1)

    if enforce_scale_of_one in [1, True]:
        pm.setAttr(f'{obj}.scale', 1, 1, 1)

    pm.select(clear=1)



########################################################################################################################
def get_clean_name(node_name, keep_namespace=False):
    """
        Derives a new string from an object's name by stripping out namespaces, colons, and vertical bars.

        :param node_name:
            The node whose name a clean name will be derived from.
        :param keep_namespace:
            If True, namespaces will remain in returned name.

        :return:
            Cleaned name.
    """


    node_to_check = ''

    if isinstance(node_name, (list,)):
        node_to_check = node_name[0]
    else:
        node_to_check = node_name

    node_clean_name = node_to_check


    name_is_clean = False

    while not name_is_clean:

        if "|" in str(node_clean_name):
            node_clean_name = node_clean_name.rsplit("|", 1)[1]

        elif ":" in str(node_clean_name) and not keep_namespace:
            node_clean_name = node_clean_name.rsplit(":", 1)[1]

        else:
            name_is_clean = True


    return node_clean_name



########################################################################################################################
def get_opposite_side_obj(obj):

    # Get side of this object
    side_tags = {nom.leftSideTag: f'{nom.leftSideTag}_',
                 nom.rightSideTag: f'{nom.rightSideTag}_'}
    opp_side_tags = {nom.leftSideTag: side_tags[nom.rightSideTag],
                     nom.rightSideTag: side_tags[nom.leftSideTag]}

    this_obj_clean_name = get_clean_name(str(obj))

    opp_side_tag = None
    for key in side_tags:
        if this_obj_clean_name.startswith(side_tags[key]):
            opp_side_tag = opp_side_tags[key]
            break

    if not opp_side_tag:
        print(f"Object: '{obj}' is not sided. Can't get opposite sided object.")
        return None

    # Get expected name of opposite obj
    opp_obj_check_string = f'{opp_side_tag}{this_obj_clean_name[2:]}'

    # Check for an obj of this expected name
    search = pm.ls(f'::{opp_obj_check_string}')
    opp_obj = search[0] if search else None

    if not obj:
        print(f"Unable to find opposite side object. Expected an object of name: '{opp_obj_check_string}'")

    return opp_obj



########################################################################################################################
def get_opposite_side_string(name):

    # Get side of this object
    side_tags = {nom.leftSideTag: f'{nom.leftSideTag}_',
                 nom.rightSideTag: f'{nom.rightSideTag}_'}
    opp_side_tags = {nom.leftSideTag: side_tags[nom.rightSideTag],
                     nom.rightSideTag: side_tags[nom.leftSideTag]}

    opp_side_tag = None
    for key in side_tags:
        if name.startswith(side_tags[key]):
            opp_side_tag = opp_side_tags[key]
            break

    if not opp_side_tag:
        print(f"String: '{name}' is not sided. Can't create opposite sided string.")
        return None

    # Get expected name of opposite string
    opp_name = f'{opp_side_tag}{name[2:]}'

    return opp_name



########################################################################################################################
def position_between(obj, between, ratios=None, include_orientation=False):
    if not ratios:
        ratios = []
        for i in between:
            ratios.append(1.0/len(between))

    #...Check that an equal number of between nodes and ratio values were provided
    if len(between) != len(ratios):
        pm.error("Parameters 'between' and 'ratios' require list arguments of equal size.")

    #...Create constraint
    if include_orientation:
        constraint = pm.parentConstraint(tuple(between), obj)
    else:
        constraint = pm.pointConstraint(tuple(between), obj)

    #...Get constraint weights to edit
    if include_orientation:
        weights = pm.parentConstraint(constraint, query=1, weightAliasList=1)
    else:
        weights = pm.pointConstraint(constraint, query=1, weightAliasList=1)

    #...Apply weights
    [pm.setAttr(w, r) for w, r in zip(weights, ratios)]

    #...Delete constraint. We're finished with it
    pm.delete(constraint)



########################################################################################################################
def copy_shapes(source_obj, destination_obj, keep_original=False, delete_existing_shapes=False):
    """
        Transfers shape node(s) from one transform object to another, and deletes the original.
        
        Args:
            source_obj (transform node): Transform object whose shape(s) you want to transfer to new object.
            destination_obj (transform node): Transform object who you want to receive shapes.
            keep_original (bool): If on, original transform object (and shapes) will not be deleted.
            delete_existing_shapes (bool): If on, any shapes already under destination_obj will be deleted first.
                Otherwise, shit gets weird, yo.
    """

    #...Remove existing shapes from destination object (if specified)
    if delete_existing_shapes:
        destination_obj_shapes = destination_obj.getShapes()
        pm.delete(destination_obj_shapes) if destination_obj_shapes else None

    # Get name of destination object for use in renaming shapes later
    destination_obj_name = get_clean_name(str(destination_obj))


    #...If keeping original object, work from a duplicate, so the duplicate is what gets deleted at the end of
    #...this function
    if keep_original:
        source_obj = pm.duplicate(source_obj, name=str(source_obj) + '_TEMP', renameChildren=1)[0]

    #...Unlock all transform attributes on source object(s) to avoid the shapes jumping when re-parented
    [pm.setAttr(f'{source_obj}.{attr}', lock=0, channelBox=1) for attr in ALL_TRANSFORM_ATTRS]
    [break_connections(f'{source_obj}.{attr}') for attr in ALL_TRANSFORM_ATTRS + ['offsetParentMatrix']]

    source_obj.inheritsTransform.set(lock=0)
    source_obj.inheritsTransform.set(1)
    source_obj.setParent(destination_obj)
    #pm.makeIdentity(source_obj, apply=1)
    convert_offset(source_obj, reverse=True)
    pm.makeIdentity(source_obj, apply=1)

    for source_shape in source_obj.getShapes():

        # Assign dummy names to source shapes to avoid naming conflicts during re_parenting process
        source_shape.rename(f'TEMP_shapeName{get_clean_name(str(source_obj))}_')

        # Re-parent source shape to destination object
        pm.parent(source_shape, destination_obj, relative=1, shape=1)

    pm.delete(source_obj)

    # Rename shapes
    final_shapes = destination_obj.getShapes()

    rename_shapes(destination_obj)

    pm.select(clear=1)



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


    if isinstance(matrix, str):
        attr_mode = True
    elif isinstance(matrix, list):
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


    #...Take note of any locked attributes
    #...tx, ty, tz, rx, ry, rz, sx, sy, sz
    locks = [0, 0, 0, 0, 0, 0, 0, 0, 0]
    lock_attr_list = ['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz']

    for attr in lock_attr_list:
        if pm.getAttr(obj+'.'+attr, lock=1) in [True, 1]:
            locks[lock_attr_list.index(attr)] = 1


    for attr in ["tx", "ty", "tz", "rx", "ry", "rz", "sx", "sy", "sz", "shearXY", "shearXZ", "shearYZ"]:
        pm.setAttr(obj+'.'+attr, lock=0)


    #...Zero out offset parent matrix
    pm.setAttr(obj+'.offsetParentMatrix', compose_matrix([0, 0, 0, 0, 0, 0, 1, 1, 1, 0, 0, 0]),
               type='matrix')


    #...Zero out transforms if specified
    if zero_transforms in [True, 1]:
        zero_out(obj)


    #...Re-lock attributes
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

    for i, a in enumerate(attr_list):
        attr = f'{obj}.{a}'
        if pm.getAttr(attr, lock=1):
            lock_status[i] = 1
            pm.setAttr(attr, lock=0, keyable=1)
            lock_list.append(attr)


    if not reverse:
        #...Get current matrix of object
        m = pm.getAttr(obj + ".matrix")

        #...Get current offset parent matrix of object
        opm = pm.getAttr(obj + ".offsetParentMatrix")

        #...Convert both matrices to standard attribute form
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

        #...Compose new matrix from the sum of object's matrix and offset parent matrix
        nm = compose_matrix(transforms)

        #...Set offset parent matrix as new matrix
        pm.setAttr(obj+'.offsetParentMatrix', nm, type='matrix')

        #...Zero out transform attributes
        zero_out(obj)

        #...Re-lock any transform values that were locked
        for locked, a in zip(lock_status, attr_list):
            if locked:
                pm.setAttr(f'{obj}.{a}', lock=1, keyable=0)




    elif reverse in [True, 1]:
        temp_loc = pm.spaceLocator()
        temp_loc.setParent(obj.getParent())
        match_position(temp_loc, obj, method='parent', preserve_scale=0)

        try:
            source = pm.listConnections(obj+'.offsetParentMatrix', source=1, plugs=1)[0]
            pm.disconnectAttr(source, obj+'.offsetParentMatrix')
        except Exception:
            pass

        zero_offsetParentMatrix(obj)
        match_position(obj, temp_loc, method='parent', preserve_scale=0)
        if obj.type() == "joint":
            obj.rotate.set( obj.rotate.get() + obj.jointOrient.get() )
            obj.jointOrient.set(0, 0, 0)
        pm.delete(temp_loc)



########################################################################################################################
def get_skin_cluster(obj):
    obj = obj[0] if isinstance(obj, (tuple, list)) else obj

    #...If not arg provided, try getting obj from selection
    if not obj:
        sel = pm.ls(sl=1)
        if sel:
            obj = sel[0]


    #...Make sure this is a shape node
    obj = obj.getShape() if obj.nodeType() == "transform" else obj


    skin_cluster = None

    for node in obj.connections(source=1):
        if node.nodeType() == 'skinCluster':
            skin_cluster = node
            break


    return skin_cluster



########################################################################################################################
def create_attr_blend_nodes(attr, node, reverse=True):
    mult = pm.shadingNode('multDoubleLinear', au=1)
    pm.connectAttr(node+'.'+attr, mult+'.input1')
    pm.setAttr(mult+'.input2', 0.1)

    # Reverse node, if needed
    if reverse in [True, 1]:

        rev = pm.shadingNode('reverse', au=1)
        pm.connectAttr(mult+'.output', rev+'.inputX')

        # Establish output class
        class NodeOutputs:

            def __init__(self, mult, rev):
                self.mult = mult
                self.rev = rev
                self.multOutput = mult + '.output'
                self.revOutput = rev + '.outputX'

        outputs = NodeOutputs(mult, rev)

        return outputs


    # Establish output class
    class NodeOutputs:
        def __init__(self, mult):
            self.mult = mult
            self.multOutput = mult + '.output'

    outputs = NodeOutputs(mult)

    return outputs



########################################################################################################################
def get_attr_blend_nodes(attr, node, mult=None, reverse=None, output=1):

    # Get all output nodes from attribute
    output_nodes = pm.listConnections(node+'.'+attr, destination=1)
    mult_node = None
    for node in output_nodes:
        if pm.objectType(node) == 'multDoubleLinear':
            mult_node = node
            break

    if mult_node:
        if mult in [True, 1]:
            if output in [True, 1]:
                return mult_node.output
            return mult_node

        elif reverse in [True, 1]:
            output_nodes = pm.listConnections(mult_node.output, destination=1)
            rev_node = None
            for node in output_nodes:
                if pm.objectType(node) == 'reverse':
                    rev_node = node
                    break

            if rev_node:
                if output in [True, 1]:
                    return rev_node.outputX

                return rev_node

    else:

        return None



########################################################################################################################
def point_on_surface_matrix(input_surface, parameter_U=None, parameter_V=None, turn_on_percentage=True,
                            decompose=False, switch_U_V=False):


    point_on_surface = pm.shadingNode("pointOnSurfaceInfo", au=1)

    pm.connectAttr(input_surface, point_on_surface + ".inputSurface")

    point_on_surface.turnOnPercentage.set(turn_on_percentage)
    if parameter_U:
        point_on_surface.parameterU.set(parameter_U)
    if parameter_V:
        point_on_surface.parameterV.set(parameter_V)


    four_by_four = pm.shadingNode("fourByFourMatrix", au=1)

    if switch_U_V:
        point_on_surface.tangentU.tangentUx.connect(four_by_four.in00)
        point_on_surface.tangentU.tangentUy.connect(four_by_four.in01)
        point_on_surface.tangentU.tangentUz.connect(four_by_four.in02)
    else:
        point_on_surface.tangentV.tangentVx.connect(four_by_four.in00)
        point_on_surface.tangentV.tangentVy.connect(four_by_four.in01)
        point_on_surface.tangentV.tangentVz.connect(four_by_four.in02)

    point_on_surface.normal.normalX.connect(four_by_four.in10)
    point_on_surface.normal.normalY.connect(four_by_four.in11)
    point_on_surface.normal.normalZ.connect(four_by_four.in12)

    if switch_U_V:
        point_on_surface.tangentV.tangentVx.connect(four_by_four.in20)
        point_on_surface.tangentV.tangentVy.connect(four_by_four.in21)
        point_on_surface.tangentV.tangentVz.connect(four_by_four.in22)
    else:
        point_on_surface.tangentU.tangentUx.connect(four_by_four.in20)
        point_on_surface.tangentU.tangentUy.connect(four_by_four.in21)
        point_on_surface.tangentU.tangentUz.connect(four_by_four.in22)

    point_on_surface.position.positionX.connect(four_by_four.in30)
    point_on_surface.position.positionY.connect(four_by_four.in31)
    point_on_surface.position.positionZ.connect(four_by_four.in32)


    if not decompose:
        output_node = four_by_four

    else:
        decomp = pm.shadingNode("decomposeMatrix", au=1)

        four_by_four.output.connect(decomp.inputMatrix)

        output_node = decomp


    return output_node



########################################################################################################################
def matrix_constraint(objs=None, maintain_offset=False, translate=None, rotate=None, scale=None, shear=None,
                     decompose=False):

    objs = objs if objs else []

    #...Varify and sort input objects ---------------------------------------------------------------------------------
    if len(objs) < 2:
        pm.error("At least two objects need to be provided")

    #...Determine source object(s) and target object
    target_obj = objs[-1]
    objs.remove(objs[-1])
    source_objs = objs


    #...Determine if target is parented to world, if not, get parent --------------------------------------------------
    target_has_parent = True
    try:
        target_parent = pm.listRelatives(target_obj, parent=1)[0]
    except Exception:
        target_has_parent = False


    #...Determine if there are multiple source objects ----------------------------------------------------------------
    multiple_sources = False
    if len(source_objs) > 1:
        multiple_sources = True


    if multiple_sources:
        matrix_blend = pm.shadingNode('blendMatrix', name='matrix_blend', au=1)
        
        if not target_has_parent:
            offset_parent_matrix_input = matrix_blend + '.outputMatrix'
            
        for i, source in enumerate(source_objs):
            
            if i == 0:
                pm.connectAttr(source + '.worldMatrix[0]', matrix_blend + '.inputMatrix')
            else:
                pm.connectAttr(source + '.worldMatrix[0]',
                               matrix_blend + '.target[{}].targetMatrix'.format(str(i-1)))
                pm.setAttr(matrix_blend+'.target[{}].weight'.format(str(i-1)), 1.0/len(source_objs))
                
        world_matrix_input = matrix_blend + '.outputMatrix'
        

    if target_has_parent or maintain_offset:
        mult_matrix = pm.shadingNode('multMatrix', name='multMatrix', au=1)
        offset_parent_matrix_input = mult_matrix + '.matrixSum'
    if multiple_sources and not maintain_offset and not target_has_parent:
        offset_parent_matrix_input = source_objs[0] + '.worldMatrix[0]'

    if not multiple_sources:
        world_matrix_input = source_objs[0] + '.worldMatrix[0]'


    if maintain_offset:

        #offset_matrix_input, mult_matrix, world_matrix_input = None, None, None
        for i, source in enumerate(source_objs):
            offset = pm.shadingNode('multMatrix', name='tempMultMatrix', au=1)
            pm.connectAttr(target_obj + '.worldMatrix[0]', offset + '.matrixIn[0]')
            pm.connectAttr(source + '.worldInverseMatrix[0]', offset + '.matrixIn[1]')

            pm.addAttr(source, longName='offsetMatrix_{}'.format(get_clean_name(target_obj)),
                       attributeType='matrix', keyable=False)
            val = pm.getAttr(offset + '.matrixSum')
            pm.setAttr(source + '.offsetMatrix_{}'.format(get_clean_name(target_obj)), val, type='matrix')
            pm.delete(offset)
            if i == 0 and multiple_sources == False:
                offset_matrix_input = source + '.offsetMatrix_{}'.format(get_clean_name(target_obj))


        if multiple_sources:
            offset_matrix_blend = pm.shadingNode('blendMatrix', name='matrix_blend', au=1)
            for i, source in enumerate(source_objs):
                if i == 0:
                    pm.connectAttr(source + '.offsetMatrix_{}'.format(get_clean_name(target_obj)),
                                   offset_matrix_blend + '.inputMatrix')
                else:
                    pm.connectAttr(source + '.offsetMatrix_{}'.format(get_clean_name(target_obj)),
                                   offset_matrix_blend + '.target[{}].targetMatrix'.format(str(i-1)))
            offset_matrix_input = offset_matrix_blend + '.outputMatrix'


        pm.connectAttr(offset_matrix_input, mult_matrix + '.matrixIn[0]')
        pm.connectAttr(world_matrix_input, mult_matrix + '.matrixIn[1]')
        if target_has_parent:
            #pm.connectAttr(target_parent + '.worldInverseMatrix[0]', mult_matrix + '.matrixIn[2]')
            pm.connectAttr(target_obj + ".parentInverseMatrix[0]", mult_matrix + ".matrixIn[2]")
        else:
            pm.connectAttr(target_obj + ".parentInverseMatrix[0]", mult_matrix + ".matrixIn[2]")
    else:

        if target_has_parent:
            pm.connectAttr(world_matrix_input, mult_matrix + '.matrixIn[0]')
            #pm.connectAttr(target_parent + '.worldInverseMatrix[0]', mult_matrix + '.matrixIn[1]')
            pm.connectAttr(target_obj + ".parentInverseMatrix[0]", mult_matrix + ".matrixIn[2]")


    for attr in ("tx", "ty", "tz", "rx", "ry", "rz"):
        try:
            pm.setAttr(target_obj + "." + attr, 0)
        except Exception:
            pass
    for attr in ("sx", "sy", "sz"):
        try:
            pm.setAttr(target_obj + "." + attr, 1)
        except Exception:
            pass



    if not decompose:
        if translate or rotate or scale:
            pick_matrix = pm.shadingNode('pickMatrix', au=1)
            pm.connectAttr(offset_parent_matrix_input, pick_matrix+'.inputMatrix')
            offset_parent_matrix_input = pick_matrix+'.outputMatrix'
            if not translate:
                pm.setAttr(pick_matrix + '.useTranslate', 0)
            if not rotate:
                pm.setAttr(pick_matrix + '.useRotate', 0)
            if not scale:
                pm.setAttr(pick_matrix + '.useScale', 0)
            if not shear:
                pm.setAttr(pick_matrix + '.useShear', 0)


    if not decompose:
        pm.connectAttr(offset_parent_matrix_input, target_obj + '.offsetParentMatrix')

    else:
        decompose_node = pm.shadingNode('decomposeMatrix', au=1)
        pm.connectAttr(offset_parent_matrix_input, decompose_node+'.inputMatrix')
        if translate not in [False, 0]:
            pm.connectAttr(decompose_node+'.outputTranslate', target_obj+'.translate')
        if rotate not in [False, 0]:
            pm.connectAttr(decompose_node+'.outputRotate', target_obj+'.rotate')
        if scale not in [False, 0]:
            pm.connectAttr(decompose_node+'.outputScale', target_obj+'.scale')


    # Compose output dictionary
    output = {'constraintOutput' : offset_parent_matrix_input,
              'multMatrix' : None,
              'weights' : None}
    try:
        output['multMatrix'] = mult_matrix
    except Exception:
        pass
    if multiple_sources:
        weights = []
        for i in range(1, len(source_objs)):
            weights.append(matrix_blend+'.target[{}].weight'.format(str(i-1)))
        output['weights'] = weights
        if maintain_offset:
            for i in range(1, len(source_objs)):
                output['offsetWeights'] = offset_matrix_blend+'.target[{}].weight'.format(str(i-1))

    return output



########################################################################################################################
def get_shape_center(obj):


    cv_positions = None

    shapes = obj.getShapes()

    for i, shape in enumerate(shapes):
        obj_list = om2.MSelectionList()
        obj_list.add(shape.name())
        dag_path = obj_list.getDagPath(0)
        nurbs_curve_fn = om2.MFnNurbsCurve(dag_path)
        cv_pos = nurbs_curve_fn.cvPositions(om2.MSpace.kWorld)
        cv_count = nurbs_curve_fn.numCVs

        cv_pos_array = np.array(cv_pos)

        if i == 0:
            cv_positions = cv_pos_array
        else:
            np.concatenate((cv_positions, cv_pos_array))

    slice_0 = cv_positions[:, 0]
    slice_1 = cv_positions[:, 1]
    slice_2 = cv_positions[:, 2]

    max_x, min_x = max(slice_0), min(slice_0)
    max_y, min_y = max(slice_1), min(slice_1)
    max_z, min_z = max(slice_2), min(slice_2)

    mean_pos = ((max_x + min_x) / 2,
                (max_y + min_y) / 2,
                (max_z + min_z) / 2)


    return mean_pos



########################################################################################################################
def reset_transform_to_shape_center(obj):
    
    current_coord = pm.xform(obj, q=1, worldSpace=1, rotatePivot=1)
    
    shape_center_coord = get_shape_center(obj)

    temp_loc = pm.spaceLocator()
    temp_loc.translate.set(shape_center_coord)
    
    adjustment_vector = (shape_center_coord[0] - current_coord[0],
                         shape_center_coord[1] - current_coord[1],
                         shape_center_coord[2] - current_coord[2])
    counter_vector = (-adjustment_vector[0],
                      -adjustment_vector[1],
                      -adjustment_vector[2])
    
    obj.translate.set(obj.translate.get() + adjustment_vector)
    
    # Counter-move shape
    for shape in obj.getShapes():
        
        cv_count = None
        
        for i in range(0, cv_count):
            pm.move(pm.NurbsCurveCV(shape, i), counter_vector, relative=True)



########################################################################################################################
def scale_obj_shape(obj, scale=(1, 1, 1)):
    #...Get object center
    obj_center = pm.xform(obj, q=1, worldSpace=1, rotatePivot=1)

    #...Get shapes
    for shape in obj.getShapes():

        cv_count = shape.numCVs()

        for i in range(cv_count):

            #...Get vert world position
            cv_pos = pm.pointPosition(shape.cv[i], world=1)

            #...Determine delta
            delta = (cv_pos[0] - obj_center[0],
                     cv_pos[1] - obj_center[1],
                     cv_pos[2] - obj_center[2])

            #...Scale delta
            scaled_delta = (delta[0] * scale[0],
                            delta[1] * scale[1],
                            delta[2] * scale[2])

            #...Reposition CV
            pm.move(scaled_delta[0], scaled_delta[1], scaled_delta[2], shape.cv[i], relative=1)



########################################################################################################################
def interpolate(interp_point, point_1, point_2):

    x1, y1 = point_1
    x2, y2 = point_2
    x = interp_point

    #...Standard 2d linear interpolation formula
    y = y1 + ((x-x1) * ( (y2-y1) / (x2-x1) ))

    return y



########################################################################################################################
def get_shape_data_from_obj(obj=None):
    shapes = obj.getShapes()
    pm.error("Provided object has no shape nodes.") if not shapes else None
    return [get_data_from_shape(shape) for shape in shapes]



########################################################################################################################
def get_data_from_shape(curve, cv_position_decimals=6):
    degree = curve.degree()
    form = curve.form().key
    cvs = [curve.getCV(i) for i in range(curve.numCVs())]
    for i, cv in enumerate(cvs):
        cvs[i] = [round(cv[j], cv_position_decimals) for j in range(3)]
    return {'cvs': cvs, 'degree': degree, 'form': form}



########################################################################################################################
def matrix_to_list(matrix):
    return (matrix(0, 0), matrix(0, 1), matrix(0, 2), matrix(0, 3),
            matrix(1, 0), matrix(1, 1), matrix(1, 2), matrix(1, 3),
            matrix(2, 0), matrix(2, 1), matrix(2, 2), matrix(2, 3),
            matrix(3, 0), matrix(3, 1), matrix(3, 2), matrix(3, 3))



########################################################################################################################
def list_to_matrix(list_matrix):
    m_matrix = om.MMatrix()
    om.MScriptUtil.createMatrixFromList(list_matrix, m_matrix)
    return m_matrix



########################################################################################################################
def get_obj_matrix(obj):
    m_xform = pm.xform(obj, worldSpace=True, m=1, q=1)
    return list_to_matrix(m_xform)



########################################################################################################################
def drive_attr(obj_1, obj_2, attr):
    if not isinstance(attr, (list, tuple)):
        attr = (attr,)
    for a in attr:
        if not pm.listConnections(f'{obj_2}.{a}', source=1):
            pm.connectAttr(f'{obj_1}.{a}', obj_2 + "." + a)
            pm.setAttr(f'{obj_2}.{a}', lock=1, keyable=0, channelBox=1)



########################################################################################################################
def get_angle_convergence_between_two_vectors(vector_1, vector_2):
    v1, v2 = vector_1, vector_2
    vector_product = v1[0] * v2[0] + v1[1] * v2[1] + v1[2] * v2[2]
    squared_vector_product = (v1[0] ** 2 + v1[1] ** 2 + v1[2] ** 2) * (v2[0] ** 2 + v2[1] ** 2 + v2[2] ** 2)
    cos_angle = vector_product / math.sqrt(squared_vector_product)
    return cos_angle



########################################################################################################################
def side_tag(side):
    side_tag_string = f'{side}_' if side else ''
    return side_tag_string



########################################################################################################################
def opposite_side(side):
    sides = {'L': 'R', 'R': 'L'}
    return sides[side]



########################################################################################################################
def install_uniform_scale_attr(obj, attr_name, minValue=0.001, keyable=True):
    pm.addAttr(obj, longName=attr_name, minValue=minValue, defaultValue=1, keyable=keyable)
    for attr in ('sx', 'sy', 'sz'):
        pm.connectAttr(f'{obj}.{attr_name}', f'{obj}.{attr}')
        pm.setAttr(f'{obj}.{attr}', lock=1, keyable=0)



########################################################################################################################
def delete_history(obj):
    pm.select(obj, replace=1)
    pm.delete(constructionHistory=1)
    pm.select(clear=1)


########################################################################################################################
def get_obj_side(obj):
    side_tags = {'L_': 'L', 'R_': 'R', 'M_': 'M'}
    obj_name = get_clean_name(str(obj))
    for tag in side_tags:
        if obj_name.startswith(tag):
            return side_tags[tag]
    return None



########################################################################################################################
def create_lock_memory(obj, unlock=True):
    lock_memory = []
    for attr in ALL_TRANSFORM_ATTRS:
        if pm.getAttr(f'{obj}.{attr}', lock=1):
            lock_memory.append(attr)
            if unlock:
                pm.setAttr(f'{obj}.{attr}', lock=0)
    return lock_memory



########################################################################################################################
def lock_attrs_from_memory(obj, lock_memory):
    for attr in ALL_TRANSFORM_ATTRS:
        if attr in lock_memory:
            pm.setAttr(f'{obj}.{attr}', lock=1)



########################################################################################################################
def match_pos_ori(target, source):
    pm.matchTransform(target, source)
    for attr in ('sx', 'sy', 'sz'):
        val = pm.getAttr(f'{target}.{attr}')
        pm.setAttr(f'{target}.{attr}', val/abs(val))



########################################################################################################################
def create_follicle(surface, uPos=0.0, vPos=0.0):

    if surface.type() == 'transform':
        surface = surface.getShape()
    if surface.type() not in ('nurbsSurface', 'mesh'):
        pm.warning("Provided node must be a nurbsSurface or mesh")

    follicle_name = f'{surface.shortName()}_{"FOL"}'

    follicle = pm.createNode('follicle', name=follicle_name)

    if surface.nodeType() == 'nurbsSurface':
        surface.local.connect(follicle.inputSurface)
    elif surface.nodeType() == 'mesh':
        surface.outMesh.connect(follicle.inputMesh)

    surface.worldMatrix[0].connect(follicle.inputWorldMatrix)
    follicle.outRotate.connect(follicle.getParent().rotate)
    follicle.outTranslate.connect(follicle.getParent().translate)
    follicle.parameterU.set(uPos)
    follicle.parameterV.set(vPos)
    follicle.getParent().t.lock()
    follicle.getParent().r.lock()

    return follicle



########################################################################################################################
def get_closest_uv_on_surface(obj, surface):

    if obj.nodeType() == 'locator':
        obj_output = obj.worldPosition
    else:
        matrix_node = pm.shadingNode('decomposeMatrix', au=1)
        obj.worldMatrix.connect(matrix_node.inputMatrix)
        obj_output = matrix_node.outputTranslate

    point_node = pm.shadingNode('closestPointOnSurface', au=1)
    obj_output.connect(point_node.inPosition)

    if surface.nodetype() == 'transform':
        surface = surface.getShape()
    surface.worldSpace.connect(point_node.inputSurface)

    div_node = pm.shadingNode('multiplyDivide', au=1)
    div_node.operation.set(2)
    point_node.result.parameterU.connect(div_node.input1.input1X)
    point_node.result.parameterV.connect(div_node.input1.input1Y)
    surface.minMaxRangeU.maxValueU.connect(div_node.input2.input2X)
    surface.minMaxRangeV.maxValueV.connect(div_node.input2.input2Y)

    u_value = div_node.output.outputX.get()
    v_value = div_node.output.outputV.get()

    pm.delete(point_node)

    return u_value, v_value



########################################################################################################################
def parent_jnt(jnt, _parent):
    if not jnt.nodeType() == 'joint':
        pm.error("Provided object must be of type 'joint'")
        return False
    recorded_transforms = pm.xform(jnt, q=1, matrix=1, worldSpace=1)
    jnt.setParent(_parent)
    offset = jnt.getParent()
    if offset == _parent:
        return
    zero_out(offset)
    jnt.setParent(_parent)
    pm.xform(jnt, matrix=recorded_transforms, worldSpace=1)
    pm.delete(offset)
    pm.select(clear=1)



########################################################################################################################
def safe_parent(obj, _parent):
    if obj.nodeType() == 'joint':
        parent_jnt(obj, _parent)
        return
    obj.setParent(_parent)
    pm.select(clear=1)
