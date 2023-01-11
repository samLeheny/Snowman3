# Title: general_utils.py
# Author: Sam Leheny
# Contact: samleheny@live.com

# Description: We generally want to avoid importing utility files into one another as it quickly leads to infinite
# recursion errors. 'general_utils' is an exception to this rule; A function belongs here if it is general enough that
# it's likely to be useful in the bodies of other utility functions.


###########################
##### Import Commands #####
import importlib
import pymel.core as pm
import maya.OpenMaya as om
import maya.api.OpenMaya as om2
import math as math
import numpy as np
import time

import Snowman3.dictionaries.nurbsCurvePrefabs as nurbsCurvePrefabs
importlib.reload(nurbsCurvePrefabs)
curve_prefabs = nurbsCurvePrefabs.create_dict()

import Snowman3.dictionaries.nameConventions as nameConventions
importlib.reload(nameConventions)
nom = nameConventions.create_dict()

import Snowman3.utilities.get_utils as get_utils
importlib.reload(get_utils)
###########################
###########################


# Global variables ########
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
shear_attrs = ["shearXY", "shearXZ", "shearYZ"]
all_shear_attrs = ["shear", "shearXY", "shearXZ", "shearYZ"]
vis_attrs = ["visibility"]
###########################



########################################################################################################################
############# ------------------------------    TABLE OF CONTENTS    ----------------------------------- ###############
########################################################################################################################
'''
get
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
side_tag_from_string
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
get_shape_info_from_obj
matrix_to_list
list_to_matrix
get_obj_matrix
add_attr
symmetry_info
add_attr
get_attr_data
migrate_attr
migrate_connections
drive_attr
'''
########################################################################################################################
########################################################################################################################
########################################################################################################################




########################################################################################################################
def get(node):
    """
        An entry point function to fire one of various functions to find and get specific nodes in the scene.
        Args:
            node (string): The key to specify which 'get' function to be run inside this function (what node to
                look for)
        Return:
            (mObject): The found node.
    """


    node_functions = {
        "rootCtrl" : get_utils.root_ctrl,
        "rootControl" : get_utils.root_ctrl,
        "root" : get_utils.root_ctrl,
        "root_ctrl" : get_utils.root_ctrl,

        "setupRoot" : get_utils.setup_root_ctrl,
        "setupRootCtrl" : get_utils.setup_root_ctrl,
        "setup_root_ctrl" : get_utils.setup_root_ctrl,
        "setup_root" : get_utils.setup_root_ctrl,
    }

    #...Check argument integrity
    if node not in node_functions:
        print("Invalid argument: {}".format(node))
        return None

    #...If valid arg provided, fire the corresponding 'get' function and return the node
    node = node_functions[node]()


    return node





########################################################################################################################
def buffer_obj(child, suffix=None, name=None, parent=None):
    """
        Creates a new transform object above provided object and moves provided object's dirty transforms into the new
            parent, allowing the child's transforms to be clean (zeroed) while maintaining its world transforms.
        Args:
            child (dagNode): The object to be moved into new buffer obj.
            suffix (string): String to be appended to child object's name to produce the name of the new buffer obj.
            name (string): (Optional) If provided, suffix parameter will be ignored and instead the new buffer obj's
                name will be determined by this argument.
            parent (dagNode): (Optional) Specifies object to parent new buffer node to. If argument not provided, will
                default to parenting new buffer obj to child obj's original parent.
        Returns:
            (transform node) The newly created buffer obj.
    """

    pm.select(clear=1)

    # Variables
    default_suffix = "buffer"
    child_name = get_clean_name(str(child))


    # Ensure a valid naming method for new buffer obj
    if not name:
        if not suffix:
            suffix = default_suffix

        # If suffix came with its own underscore, remove it
        if suffix[0] == "_":
            suffix = suffix.split("_")[1]



    # Check if child's transforms are free to be cleaned (not receiving connections)
    connected_attrs = []

    for attr in all_transform_attrs:

        incoming_connection = pm.listConnections(child + "." + attr, source=1, destination=0, plugs=1)

        if incoming_connection:
            connected_attrs.append("{0}.{1}".format(child_name, attr))

    if connected_attrs:

        error_string = ""

        for attr in connected_attrs:
            error_string += ("{0}\n".format(attr))

        pm.error("\nCould not clean child object transforms - The following transforms have incoming connections:"
                 "\n{0}\n".format(error_string))



    # Check for locked attributes. If any are found, remember them, then unlock them for the duration of this function
    lock_memory = []

    for attr in all_transform_attrs:
        if pm.getAttr(child + "." + attr, lock=1):

            lock_memory.append(attr)

            pm.setAttr(child + "." + attr, lock=0)



    # Get child obj's parent
    world_is_original_parent = False

    if not parent:
        parent = child.getParent()

    if not parent:
        world_is_original_parent = True



    # Compose buffer obj name
    if name:
        buffer_name = name

    else:
        buffer_name = "{0}_{1}".format(child_name, suffix)



    # Create buffer obj
    buffer_node = pm.shadingNode("transform", name=buffer_name, au=1)



    # Match buffer obj to child's transforms
    buffer_node.setParent(child)

    for attr in ("translate", "rotate", "shear"):
        pm.setAttr(buffer_node + "." + attr, 0, 0, 0)

    buffer_node.scale.set(1, 1, 1)

    buffer_node.setParent(world=1)



    # Parent child to buffer
    child.setParent(buffer_node)



    # Clean child's transforms
    for attr in ("translate", "rotate", "shear"):
        pm.setAttr(child + "." + attr, 0, 0, 0)

    child.scale.set(1, 1, 1)



    # Parent buffer obj
    if not world_is_original_parent:
        buffer_node.setParent(parent)



    # Re-lock any attributes on child obj that were locked previously
    if lock_memory:

        for attr in lock_memory:
            pm.setAttr(child + "." + attr, lock=1)



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
    transforms = {
        "translate" : True,
        "rotate" : True,
        "scale" : True,
        "shear" : True,
    }

    transform_attrs = all_transform_attrs


    if translate is None and rotate is None and scale is None and shear is None:
        pass

    else:

        transforms["translate"] = translate
        transforms["rotate"] = rotate
        transforms["scale"] = scale
        transforms["shear"] = shear

        transform_attrs = []
        if transforms["translate"]:
            for attr in all_translate_attrs:
                transform_attrs.append(attr)
        if transforms["rotate"]:
            for attr in all_rotate_attrs:
                transform_attrs.append(attr)
        if transforms["scale"]:
            for attr in all_scale_attrs:
                transform_attrs.append(attr)
        if transforms["shear"]:
            for attr in all_shear_attrs:
                transform_attrs.append(attr)


    # Check if child's transforms are free to be cleaned (not receiving connections)
    connected_attrs = []

    for attr in transform_attrs:

        incoming_connection = pm.listConnections(obj + "." + attr, source=1, destination=0, plugs=1)

        if incoming_connection:
            connected_attrs.append("{0}.{1}".format(obj, attr))

    if connected_attrs:

        error_string = ""

        for attr in connected_attrs:
            error_string += ("{0}\n".format(attr))

        pm.error("\nCould not clean object ({0}) transforms - The following transforms have incoming connections:"
                 "\n{1}\n".format(obj, error_string))


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
            made from those points will be rotated.
            Requires: numpy
        Args:
            point_list (mTransformObj): The list of coordinates to be rearranged.
            up_direction ([float, float, float]):
            forward_direction ([float, float, float]):
        Returns:
            (list) List with entries rearranged to obey new vectors
    """


    # Determine remaining axis:
    first_direction, second_direction = up_direction, forward_direction
    flip = False

    if up_direction == [1, 0, 0]:
        if forward_direction in ([0, -1, 0], [0, 0, 1]):
            flip = True

    elif up_direction == [-1, 0, 0]:
        if forward_direction in ([0, 1, 0], [0, 0, -1]):
            flip = True

    elif up_direction == [0, 1, 0]:
        if forward_direction in ([1, 0, 0], [0, 0, -1]):
            flip = True

    elif up_direction == [0, -1, 0]:
        if forward_direction in ([-1, 0, 0], [0, 0, 1]):
            flip = True

    elif up_direction == [0, 0, 1]:
        if forward_direction in ([-1, 0, 0], [0, 1, 0]):
            flip = True

    elif up_direction == [0, 0, -1]:
        if forward_direction in ([1, 0, 0], [0, -1, 0]):
            flip = True

    if flip:
        first_direction, second_direction = forward_direction, up_direction

    remaining_direction = cross_product(first_direction, second_direction)



    # Determine axes
    axes_dict = {"x": ([1, 0, 0], [-1, 0, 0]),
                 "y": ([0, 1, 0], [0, -1, 0]),
                 "z": ([0, 0, 1], [0, 0, -1])}

    up_axis, forward_axis, remaining_axis = None, None, None

    for key in axes_dict:
        if up_direction in axes_dict[key]:
            up_axis = key
            break

    for key in axes_dict:
        if forward_direction in axes_dict[key]:
            forward_axis = key
            break

    for key in axes_dict:
        if remaining_direction in axes_dict[key]:
            remaining_axis = key
            break


    # Determine signs of directions (positive or negative)
    up_mult, forward_mult, remaining_mult = 1, 1, 1

    if up_direction in ([-1, 0, 0], [0, -1, 0], [0, 0, -1]):
        up_mult = -1

    if forward_direction in ([-1, 0, 0], [0, -1, 0], [0, 0, -1]):
        forward_mult = -1

    if remaining_direction in ([-1, 0, 0], [0, -1, 0], [0, 0, -1]):
        remaining_mult = -1


    mults = (remaining_mult, up_mult, forward_mult)


    default_places = {"x": 0, "y": 1, "z": 2}


    #...Rearrange columns
    array = np.array(point_list)
    columns = np.array([default_places[remaining_axis],
                        default_places[up_axis],
                        default_places[forward_axis]])
    new_array = array[ np.array(list(range(0, len(point_list))))[:, np.newaxis], columns ]

    #...Switch directions of columns if needed
    multipliers = (mults[default_places[remaining_axis]],
                   mults[default_places[up_axis]],
                   mults[default_places[forward_axis]])

    if multipliers == (1, 1, 1):
        output_array = new_array

    else:
        multipliers = np.array(multipliers)
        multiplier_array = np.tile(multipliers, (len(point_list), 1))

        output_array = np.multiply(new_array, multiplier_array)


    return output_array.tolist()





########################################################################################################################
def nurbs_curve(name=None, color=0, form="open", cvs=None, degree=3, scale=1, points_offset=None, up_direction=None,
                forward_direction=None, side=None):
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
        scale (numeric): Factor by which to scale shape CV placement vectors. Defines scale of resulting curve
            shape.
        points_offset ([float, float, float]): The vector by which to offset the entire curve shape.
        up_direction ([float, float, float]): The unit vector indicating the world direction of the curve shape's local
        positive y direction.
        forward_direction ([float, float, float]): The unit vector indicating the world direction of the curve shape's
            local positive z direction.
        side (string): In the event multiple colours are provided, the side argument will be used to determine which
            colour to use.
    Returns:
        (mTransform object) The newly created curve object.
    """

    up_direction = up_direction if up_direction else (0, 1, 0)
    forward_direction = forward_direction if forward_direction else (0, 0, 1)
    points_offset = points_offset if points_offset else (0, 0, 0)
    side_tag = side_tag_from_string(side) if side else None

    # Rearrange CV coordinates to match provided axes
    if up_direction == forward_direction:
        pm.error("up_direction and forward_direction parameters cannot have the same argument.")
    cvs = rearrange_point_list_vectors(cvs, up_direction=up_direction, forward_direction=forward_direction)

    # Flip CV x coordinates if curve is right-sided
    x_offset_direction = 1

    # Process scale factor in case only one value was passed
    scale = scale if isinstance(scale, list) else (scale, scale, scale)


    # Build a list of points at which to place the curve's CVs (incorporating scale and points_offset)
    points = [[(v[i] * scale[i]) + points_offset[i] for i in range(3)] for v in cvs]
    # This appears to be a rare case of vanilla Python being faster than Numpy
    # points = np.array(cvs).astype(float)
    # for i in range(3):
    #    points[:,i] *= float(scale[i])

    # Build curve
    crv = None

    crv = pm.curve(name=name, degree=degree, point=points)
    if form == "periodic":
        pm.closeCurve(crv, replaceOriginal=1, preserveShape=0)

    # Delete construction history
    if crv:
        pm.delete(crv, constructionHistory=True)

    # Color curve. If color info is a list, treat the two entries as left color and right color. Refer to side argument
    # to determine which color is correct
    if color:
        if isinstance(color, list) and len(color) == 2:
            sided_color = get_colour_from_sided_list(color, side_tag)
            color = sided_color

        set_color(crv, color)


    pm.select(clear=1)
    return crv





########################################################################################################################
def get_colour_from_sided_list(sided_list, side):

    sided_colors = {nom.leftSideTag: sided_list[0],
                    nom.rightSideTag: sided_list[1]}

    color = sided_colors[side]

    return color





########################################################################################################################
def curve_construct(cvs=None, name=None, color=None, form='open', scale=1, degree=1, shape_offset=None,
                    up_direction=None, forward_direction=None, side=None):
    """
        Produces a nurbs curve object based on parameters. As opposed to other functions, if parameters are provided as
            lists, the function will produce an object with multiple curve shapes. Useful for producing complex curve
            objects to be used as animation controls.
        Args:
            cvs (list): List of coordinates for curve CVs.
            name (string): Name of curve object.
            color (numeric/ [float, float, float]): Override color of curve. If an integer is provided, will use as
                override color index. If list of three numbers (integers or floats) is provided, will use as RGB color.
            form (string): Determines whether curve shape should be a closed loop. Acceptable
                inputs: "open", "periodic"
            scale (numeric): Factor by which to scale shape CV placement vectors. Defines scale of resulting curve
                shape.
            degree (int): Curve smoothing degree. Acceptable degrees: 1, 3. If an integer is provided, will apply that
                degree to all curves in curve object. If a list is provided, will apply each list entry as degree of
                corresponding curve in curve object.
            shape_offset ([float, float, float]): Vector by which to offset all CV positions so shape will not be
                centered to object pivot. Requires coordinates in form of list of three number values (integers or
                floats).
            up_direction ([float, float, float]): The unit vector indicating the world direction of the curve shape's
                local positive y direction.
            forward_direction ([float, float, float]): The unit vector indicating the world direction of the curve
                shape's local positive z direction.
            side (string): In the event multiple colours are provided, the side argument will be used to determine which
                colour to use.
        Returns:
            (mTransform) The created curve object.
    """

    if not up_direction:
        up_direction = [0, 1, 0]

    if not forward_direction:
        forward_direction = [0, 0, 1]



    ##### Check input integrity #####

    # Function to easily convert a variable into a list of itself - if it isn't already a list
    def bulk_up_list(output_variable=None, check_variable=None, new_length=None):
        """
            Args:
                output_variable: The variable to be turned into a list (if needed.)
                check_variable: The variable whose type should be checked. If it's already a list, then the function is
                    redundant. If none provided, will use output_variable as check_variable.
                new_length: If only one value was provided but a returned list of a certain index length is needed, input
                    argument of the desired index length and function will duplicate the one provided value to bulk up
                    the resulting list.
            Return:
        """
        output = output_variable
        if check_variable is None:
            check_variable = output_variable

        if not isinstance(check_variable, list):
            output = [output]

        if len(output) < new_length:
            for i in range(len(output), new_length):
                output.append(output[0])

        return output



    # Check CV data integrity
    if not cvs:
        pm.error("Unable to create curve. No control point data provided.")

    elif not isinstance(cvs, list):
        pm.error("Unable to create curve. Control points data must be of type: list")


    # Determine how many discrete curves are needed to complete this curve object
    shape_count = 1
    if isinstance(cvs[0][0], list):
        shape_count = len(cvs)
    else:
        cvs = [cvs]


    #...Determine which shape build method to use
    form = bulk_up_list(form, new_length=shape_count)

    for entry in form:
        if not isinstance(entry, str):
            pm.error("Unable to create curve. form received invalid string argument: {}".format(entry))

    form_strings = {
        "open": ["open", "Open", "opened", "Opened"],
        "periodic": ["periodic", "Periodic", "closed", "Closed", "close", "Close"]
    }

    for f in form:

        string_is_recognized = False

        for key in form_strings:
            if f in form_strings[key]:
                f = key
                string_is_recognized = True
                break

        if not string_is_recognized:
            pm.error("Unable to create curve. form received invalid string argument:"
                     "'{}'".format(f))

    acceptable_form_inputs = []
    for string_list in form_strings.values():
        for string in string_list:
            acceptable_form_inputs.append(string)


    #...Check degree input integrity
    degree_is_valid = True

    degree = bulk_up_list(degree, new_length=shape_count)

    for entry in degree:
        if isinstance(entry, int):
            if not entry in [1, 3]:
                degree_is_valid = False

        else:

            degree_is_valid = False

    if degree_is_valid in [False, 0]:
        pm.error("Unable to create curve. 'degree' parameter received invalid argument: {}".format(degree))



    #...Check shape_offset input integrity
    if not shape_offset:
        shape_offset = [0, 0, 0]
    shape_offset = bulk_up_list(output_variable=shape_offset, check_variable=shape_offset[0], new_length=shape_count)
    for entry in shape_offset:
        if not isinstance(entry, list):
            pm.error("Unable to create curve. 'shape_offset' parameter received invalid argument: {}".format(entry))

        else:
            if len(entry) != 3:
                pm.error("Unable to create curve. 'shape_offset' parameter received invalid argument: {}".format(entry))

    if not isinstance(scale, list):
        scale = [scale, scale, scale]
        
    for entry in scale:
        if not isinstance(entry, (int, float)):
            pm.error("Unable to create curve. 'scale' parameter received invalid argument: {}".format(entry))


    ##### BUILD SHAPES #####
    crvs = []
    for i in range(shape_count):
        shape_form = form[i]
        shape_cvs = cvs[i]
        shape_degree = degree[i]
        shape_scale = scale
        points_offset = shape_offset[i]
        #...For each curve in curve object, build curve using the home-brewed 'curve' function

        curve = nurbs_curve( color = color,
                             form = shape_form,
                             cvs = shape_cvs,
                             degree = shape_degree,
                             scale = shape_scale,
                             points_offset = points_offset,
                             up_direction = up_direction,
                             forward_direction = forward_direction,
                             side = side)


        if curve:
            crvs.append(curve)

    #...Parent shapes together under a single transform node
    crv_obj = crvs[0]

    for i in range(1, len(crvs)):
        pm.parent(crvs[i].getShape(), crv_obj, relative=1, shape=1)
        pm.delete(crvs[i])

    #...Name curve and shapes
    pm.rename(crv_obj, name)
    rename_shapes(crv_obj)


    pm.select(clear=1)
    return crv_obj





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
def prefab_curve_construct(prefab=None, name=None, color=None, up_direction=None, forward_direction=None, scale=None,
                           shape_offset=None, side=None):
    """
        Retrieves curve object data from curves dictionary, compiles it and feeds it to the curveObj function then
            returns the resulting curve object.
        Args:
            prefab (string): Entry to look up in curves dictionary for curve data.
            name (string): Name of curve object.
            color (numeric/ [float, float, float]): Override color of curve. If an integer is provided, will use as
                override color index. If list of three numbers (integers or floats) is provided, will use as RGB color.
            up_direction ([float, float, float]): The unit vector indicating the world direction of the curve shape's
                local positive y direction.
            forward_direction ([float, float, float]): The unit vector indicating the world direction of the curve
                shape's local positive z direction.
            scale (numeric): Factor by which to scale shape CV placement vectors. Defines scale of resulting curve
                shape.
            shape_offset ([float, float, float]): Vector by which to offset all CV positions so shape will not be
                centered to object pivot. Requires coordinates in form of list of three number values (integers or
                floats).
            side (string): In the event multiple colours are provided, the side argument will be used to determine which
                colour to use.
        Returns:
            (mTransform) The created curve object.
    """


    #...Initialize parameters
    if not up_direction:
        up_direction = [0, 1, 0]

    if not forward_direction:
        forward_direction = [0, 0, 1]

    if not shape_offset:
        shape_offset = [0, 0, 0]


    #...Test that provided dictionary entry exists
    if prefab not in curve_prefabs:
        pm.error("Cannot create prefab curve object. " \
                 "Provided prefab dictionary key '{}' is invalid".format(prefab))


    #...Get shape data dictionary for this prefab
    prefab_dict = curve_prefabs[prefab]


    #...Initialize dictionary to assemble curve object input data
    crv_obj_inputs = {
        "cvs" : None,
        "name" : name,
        "color" : 0,
        "buildMethod" : "open",
        "scale" : 1,
        "degree" : 1,
        "shape_offset" : shape_offset,
    }

    #...Update curve object input dictionary with data from the shape dictionary
    for key in prefab_dict:
        crv_obj_inputs[key] = prefab_dict[key]


    #...Update curve object input dictionary with provided parameters.
    if color:
        crv_obj_inputs["color"] = color

    if not scale:
        scale = 1


    #...If a name was provided, override any name that came through with the control info
    if name:
        crv_obj_inputs["name"] = name

    #...Create the shape object with assembled data
    output_obj = curve_construct(
                    cvs = crv_obj_inputs["cvs"],
                    name = crv_obj_inputs["name"],
                    color = crv_obj_inputs["color"],
                    form = crv_obj_inputs["form"],
                    scale = crv_obj_inputs["scale"] * scale,
                    degree = crv_obj_inputs["degree"],
                    shape_offset = crv_obj_inputs["shape_offset"],
                    up_direction = up_direction,
                    forward_direction = forward_direction,
                    side = side,
    )



    return output_obj





########################################################################################################################
def side_tag_from_string(side):
    """
    Takes in string describing directions left, right, or middle and returns a correctly formatted side tag that can be
        used as the correct arguments to parameters in other functions.
    Args:
        side (string): The string describing the direction of the desired side tag. String should refer to directions:
            left, right, or middle
    Return:
        (string) The resulting side tag.
    """

    if not side:
        return None


    side_tag = None


    side_strings_dict = {
        nom.leftSideTag : ["left", "Left", "LEFT", "l", "L"],
        nom.rightSideTag : ["right", "Right", "RIGHT", "r", "R"],
        nom.midSideTag : ["middle", "Middle", "MIDDLE", "mid", "Mid", "MID", "m", "M"]
    }

    for key in side_strings_dict:
        if side in side_strings_dict[key]:
            side_tag = key
            break


    if not side_tag:
        pm.error("Failed to get side tag from string argument. Check that argument '{0}' is valid.".format(side))

    return side_tag





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


    node_to_check = ""

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
    side_tags = {nom.leftSideTag: "{}_".format(nom.leftSideTag),
                 nom.rightSideTag: "{}_".format(nom.rightSideTag)}
    opp_side_tags = {nom.leftSideTag: side_tags[nom.rightSideTag],
                     nom.rightSideTag: side_tags[nom.leftSideTag]}

    this_obj_clean_name = get_clean_name(str(obj))

    opp_side_tag = None


    key = None
    for key in side_tags:
        if this_obj_clean_name.startswith(side_tags[key]):

            opp_side_tag = opp_side_tags[key]
            break

    if not opp_side_tag:
        print("Object: '{0}' is not sided. Can't get opposite sided object.".format(obj))
        return None

    # Get expected name of opposite obj
    opp_obj_check_string = this_obj_clean_name.replace( side_tags[key], opp_side_tag )

    # Check for an obj of this expected name
    opp_obj = pm.PyNode(f'::{opp_obj_check_string}') if pm.objExists(f'::{opp_obj_check_string}') else None


    if not obj:
        print("Unable to find opposite side object. Expected an object of name: '{0}'".format(opp_obj_check_string))


    return opp_obj





########################################################################################################################
def position_between(obj, between, ratios=None, include_orientation=False):


    if not ratios:
        ratios = []
        for i in between:
            ratios.append(1.0/len(between))


    #...Check that an equal number of between nodes and ratio values were provided
    if len(between) != len(ratios):
        pm.error("Parameters 'between' and 'ratios' require list arguments of equal length.")


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
    [pm.setAttr(source_obj + "." + attr, lock=0, channelBox=1) for attr in all_transform_attrs]
    [break_connections(source_obj + "." + attr) for attr in all_transform_attrs + ["offsetParentMatrix"]]

    source_obj.inheritsTransform.set(lock=0)
    source_obj.inheritsTransform.set(1)
    source_obj.setParent(destination_obj)
    pm.makeIdentity(source_obj, apply=1)


    for source_shape in source_obj.getShapes():

        # Assign dummy names to source shapes to avoid naming conflicts during re_parenting process
        source_shape.rename("TEMP_shapeName" + get_clean_name(str(source_obj)) + "_")

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
        if not translate in [False, 0]:
            pm.connectAttr(decompose_node+'.outputTranslate', target_obj+'.translate')
        if not rotate in [False, 0]:
            pm.connectAttr(decompose_node+'.outputRotate', target_obj+'.rotate')
        if not scale in [False, 0]:
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
def flip(obj, axis="x"):

    obj.ry.set(180)
    obj.sz.set(-1)





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
def get_shape_info_from_obj(obj=None):


    open_form_tag = "open"
    periodic_form_tag = "periodic"


    #...If no object provided, try getting object from current selection
    if not obj:

        sel = pm.ls(sl=1)
        if sel:
            obj = sel[0]
        else:
            pm.error("No object provided.")


    #...
    shapes = obj.getShapes()

    if not shapes:
        pm.error("Provided object has no shape nodes.")


    #...Collect and compose data from all object's nurbs curves
    #...Curve degrees
    degrees = [shape.degree() for shape in shapes]

    #...Curve forms (open or periodic curve shapes)
    forms = [shape.form().key for shape in shapes]

    #...CV positions
    cv_counts = [shape.numCVs() for shape in shapes]
    cv_positions = []

    for shp, deg in zip(shapes, degrees):
        shape_cvs = ([[cv.x, cv.y, cv.z] for cv in shp.getCVs()])
        #...If degree of 3, the last three CVs will be repeats. Remove them from final list
        cv_positions.append(shape_cvs[0: -3] if deg == 3 else shape_cvs)


    return {"form": forms,
            "cvs": cv_positions,
            "degree": degrees}





########################################################################################################################
def matrix_to_list(matrix):

    return (
        matrix(0, 0), matrix(0, 1), matrix(0, 2), matrix(0, 3),
        matrix(1, 0), matrix(1, 1), matrix(1, 2), matrix(1, 3),
        matrix(2, 0), matrix(2, 1), matrix(2, 2), matrix(2, 3),
        matrix(3, 0), matrix(3, 1), matrix(3, 2), matrix(3, 3)
    )





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
def symmetry_info(symmetry_mode):
    """
    Given symmetry info, logically derives other side/symmetry-related information
    Args:
        symmetry_mode (string): Acceptable inputs: "Left drives Right", "Right drives Left", None
    Returns:
        (tuple): symmetry mode (str),
                 driver_side (str),
                 driven_side(str),
                 symmetry on/off(str)
    """

    is_symmetry_on, driver_side, driven_side = False, None, None

    if symmetry_mode:
        is_symmetry_on = True
        if symmetry_mode == "Left drives Right":
            driver_side = nom.leftSideTag
            driven_side = nom.rightSideTag
        elif symmetry_mode == "Right drives Left":
            driver_side = nom.rightSideTag
            driven_side = nom.leftSideTag

    return symmetry_mode, driver_side, driven_side, is_symmetry_on





########################################################################################################################
def add_attr(obj, long_name, nice_name="", attribute_type=None, keyable=False, channel_box=False, enum_name=None,
             default_value=0, min_value=None, max_value=None, lock=False, parent="", number_of_children=0):

    #...String type
    if attribute_type == "string":

        if parent:
            pm.addAttr(
                obj,
                longName=long_name,
                niceName=nice_name,
                dataType=attribute_type,
                keyable=keyable,
                parent=parent
            )
        else:
            pm.addAttr(
                obj,
                longName=long_name,
                niceName=nice_name,
                dataType=attribute_type,
                keyable=keyable
            )

        if default_value:
            pm.setAttr(obj + "." + long_name, default_value, type="string", lock=lock)

    else:

    #...Non-string type
        #...Compound type
        if attribute_type == "compound":
            pm.addAttr(
                obj,
                longName=long_name,
                niceName=nice_name,
                attributeType=attribute_type,
                keyable=keyable,
                numberOfChildren=number_of_children
            )
        else:
            if parent:
                pm.addAttr(
                    obj,
                    longName=long_name,
                    niceName=nice_name,
                    attributeType=attribute_type,
                    keyable=keyable,
                    enumName=enum_name,
                    parent=parent
                )
            else:
                pm.addAttr(
                    obj,
                    longName=long_name,
                    niceName=nice_name,
                    attributeType=attribute_type,
                    keyable=keyable,
                    enumName=enum_name,
                )

        attr = obj+f'.{long_name}'
        if default_value:
            pm.addAttr(attr, e=1, defaultValue=default_value)
            try:
                pm.setAttr(attr, default_value)
            except Exception:
                pass
        if min_value:
            pm.addAttr(attr, e=1, minValue=min_value)
        if max_value:
            pm.addAttr(attr, e=1, maxValue=max_value)

        if lock:
            pm.setAttr(obj+f'.{long_name}', lock=True)


    if channel_box and not keyable:
        pm.setAttr(obj+f'.{long_name}', channelBox=True)


    return f'{str(obj.name)}.{long_name}'





########################################################################################################################
def get_attr_data(attr, node):
    """
    Given an attribute, and a node, will compose and return a dictionary of queried data from that attribute. This
        dictionary can be used to recreate the attribute one-to-one elsewhere.
    Args:
        attr (str): The name of the targeted attribute.
        node (mObj): The node the attribute is on.
    Returns:
        (dict): Queried attribute information.
    """

    #...Check attribute exists
    if not pm.attributeQuery(attr, node=node, exists=1):
        print("Attribute '{}' does not exist".format(node + "." + attr))
        return None

    #...Query attribute information and compose into a dictionary
    attr_data = {
        "longName": pm.attributeQuery(attr, node=node, longName=1),
        "niceName": pm.attributeQuery(attr, node=node, niceName=1),
        "attributeType": pm.attributeQuery(attr, node=node, attributeType=1),
        "keyable": pm.attributeQuery(attr, node=node, keyable=1),
        "channelBox": pm.attributeQuery(attr, node=node, channelBox=1),
        "enumName": pm.attributeQuery(attr, node=node, listEnum=1),
        "hasMin": pm.attributeQuery(attr, node=node, minExists=1),
        "hasMax": pm.attributeQuery(attr, node=node, maxExists=1),
        "lock": pm.getAttr(node + "." + attr, lock=1),
        "currentValue": pm.getAttr(node + "." + attr),
        "parent": pm.attributeQuery(attr, node=node, listParent=1),
        "children": pm.attributeQuery(attr, node=node, listChildren=1),
        "numberOfChildren": pm.attributeQuery(attr, node=node, numberOfChildren=1),
        "readable": pm.attributeQuery(attr, node=node, readable=1),
        "writable": pm.attributeQuery(attr, node=node, writable=1),
        "shortName": pm.attributeQuery(attr, node=node, shortName=1),
    }

    #...Add condition-dependant data
    if attr_data["attributeType"] == "typed":
        attr_data["attributeType"] = "string"

    attr_data["minValue"] = pm.attributeQuery(attr, node=node, minimum=1)[0] if attr_data["hasMin"] else None
    attr_data["maxValue"] = pm.attributeQuery(attr, node=node, maximum=1)[0] if attr_data["hasMax"] else None

    try:
        attr_data["defaultValue"] = pm.attributeQuery(attr, node=node, listDefault=1)[0]
    except Exception:
        attr_data["defaultValue"] = None


    return attr_data





########################################################################################################################
def migrate_attr(old_node, new_node, attr, include_connections=True, remove_original=True):


    #...If attribute conflicts with an attribute already on new node, merge them
    if pm.attributeQuery(attr, node=new_node, exists=1):
        migrate_connections(f'{old_node}.{attr}', f'{new_node}.{attr}')
        return

    attr_data = get_attr_data(attr, old_node)

    recreated_attr = add_attr(
        new_node,
        long_name=attr_data["longName"],
        nice_name=attr_data["niceName"],
        attribute_type=attr_data["attributeType"],
        keyable=attr_data["keyable"],
        channel_box=attr_data["channelBox"],
        enum_name=attr_data["enumName"],
        default_value=attr_data["defaultValue"],
        min_value=attr_data["minValue"],
        max_value=attr_data["maxValue"],
        parent=attr_data["parent"],
        number_of_children=attr_data["numberOfChildren"]
    )

    pm.setAttr(new_node + "." + attr, attr_data["currentValue"])

    if attr_data["lock"]:
        pm.setAttr(new_node + "." + attr, lock=1)

    #...Migrate connections
    if include_connections:
        migrate_connections(f'{old_node}.{attr}', f'{new_node}.{attr}')

    #...Delete attribute in original location to complete apparent migration
    if remove_original:
        pm.deleteAttr(old_node + "." + attr)





########################################################################################################################
def migrate_connections(old_attr, new_attr):

    plugs = pm.listConnections(old_attr, source=1, destination=0, plugs=1)
    for plug in plugs:
        pm.connectAttr(plug, new_attr, force=1)
        pm.disconnectAttr(plug, old_attr)

    plugs = pm.listConnections(old_attr, source=0, destination=1, plugs=1)
    for plug in plugs:
        pm.connectAttr(new_attr, plug, force=1)





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