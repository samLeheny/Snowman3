# Title: curve_utils.py
# Author: Sam Leheny
# Contact: samleheny@live.com

# Description:


###########################
##### Import Commands #####
import importlib
import pymel.core as pm
import copy
from dataclasses import dataclass, field
from typing import Union

import Snowman3.utilities.general_utils as gen
importlib.reload(gen)

import Snowman3.dictionaries.nurbsCurvePrefabs as prefab_curve_shapes
importlib.reload(prefab_curve_shapes)
###########################
###########################


###########################
######## Variables ########
PREFAB_CRV_SHAPES = prefab_curve_shapes.create_dict()
###########################
###########################


# CLASSES ##############################################################################################################
########################################################################################################################
class CurveConstruct:
    def __init__(
        self,
        name: str,
        shape: str,
        color: Union[list, int] = None,
    ):
        self.name = name
        self.shape = shape
        self.color = color


    @classmethod
    def create_prefab(cls, name, prefab_shape, size=None, shape_offset=None, up_direction=None, forward_direction=None,
                      color=None):
        cv_data = compose_curve_construct_cvs(
            curve_data=copy.deepcopy(PREFAB_CRV_SHAPES[prefab_shape]),
            scale=size,
            shape_offset=shape_offset,
            up_direction=up_direction,
            forward_direction=forward_direction
        )
        return CurveConstruct(name=name, shape=cv_data, color=color)


    def create_scene_obj(self):
        return curve_construct( name=self.name, color=self.color, curves=self.shape )





# FUNCTIONS ############################################################################################################
########################################################################################################################
def compose_curve_cvs(cvs=None, scale=1, up_direction=None, forward_direction=None, points_offset=None):
    if not up_direction: up_direction = (0, 1, 0)
    if not forward_direction: forward_direction = (0, 0, 1)
    points_offset = points_offset if points_offset else (0, 0, 0)
    # Rearrange CV coordinates to match provided axes
    if up_direction == forward_direction:
        pm.error("up_direction and forward_direction parameters cannot have the same argument.")
    cvs = gen.rearrange_point_list_vectors(cvs, up_direction=up_direction, forward_direction=forward_direction)
    # Process scale factor in case only one value was passed
    scale = scale if isinstance(scale, list) else (scale, scale, scale)
    # Build a list of points at which to place the curve's CVs (incorporating scale and points_offset)
    points = [[(v[i] * scale[i]) + points_offset[i] for i in range(3)] for v in cvs]
    # This appears to be a rare case of vanilla Python being faster than Numpy
    # points = np.array(cvs).astype(float)
    # for i in range(3):
    #    points[:,i] *= float(scale[i])
    return points



# ----------------------------------------------------------------------------------------------------------------------
def compose_curve_construct_cvs(curve_data, scale=1, shape_offset=None, up_direction=None, forward_direction=None):
    if not up_direction: up_direction = [0, 1, 0]
    if not forward_direction: forward_direction = [0, 0, 1]
    if not shape_offset: shape_offset = [0, 0, 0]
    for i, curve in enumerate(curve_data):
        # ...For each curve in curve object, build curve using the home-brewed 'curve' function
        cv_list = compose_curve_cvs(cvs=curve['cvs'], scale=scale,  points_offset=shape_offset,
                                    up_direction=up_direction, forward_direction=forward_direction)
        curve_data[i]['cvs'] = cv_list
    return curve_data



# ----------------------------------------------------------------------------------------------------------------------
def nurbs_curve(name=None, cvs=None, degree=3, form='open', color=None):
    crv = pm.curve(name=name, degree=degree, point=cvs)
    pm.closeCurve(crv, replaceOriginal=1, preserveShape=0) if form == 'periodic' else None
    pm.delete(crv, constructionHistory=True)
    gen.set_color(crv, color) if color else None
    pm.select(clear=1)
    return crv



# ----------------------------------------------------------------------------------------------------------------------
def curve_construct(curves, name=None, color=None, scale=1, shape_offset=None, up_direction=None,
                    forward_direction=None):
    """
        Produces a nurbs curve object based on parameters. As opposed to other functions, if parameters are provided as
            lists, the function will produce an object with multiple curve shapes. Useful for producing complex curve
            objects to be used as animation controls.
        Args:
            scale (numeric): Factor by which to scale shape CV placement vectors. Defines scale of resulting curve
                shape.
            shape_offset ([float, float, float]): Vector by which to offset all CV positions so shape will not be
                centered to object pivot. Require coordinates in form of list of three number values (integers or
                floats).
            up_direction ([float, float, float]): The unit vector indicating the world direction of the curve shape's
                local positive y direction.
            forward_direction ([float, float, float]): The unit vector indicating the world direction of the curve
                shape's local positive z direction.
        Returns:
            (mTransform) The created curve object.
    """
    composed_cv_data = compose_curve_construct_cvs(
        curve_data=curves, scale=scale, shape_offset=shape_offset, up_direction=up_direction,
        forward_direction=forward_direction )
    ##### BUILD SHAPES #####
    crvs = [ nurbs_curve(color=color,
                         form=curves[i]['form'],
                         cvs=curves[i]['cvs'],
                         degree=curves[i]['degree']) for i, _ in enumerate(composed_cv_data) ]
    #...Parent shapes together under a single transform node
    crv_obj = crvs[0]
    for i in range(1, len(crvs)):
        pm.parent(crvs[i].getShape(), crv_obj, relative=1, shape=1)
        pm.delete(crvs[i])
    #...Name curve and shapes
    pm.rename(crv_obj, name)
    gen.rename_shapes(crv_obj)

    pm.select(clear=1)
    return crv_obj



# ----------------------------------------------------------------------------------------------------------------------
def prefab_curve_construct(prefab=None, name=None, color=None, up_direction=None, forward_direction=None, scale=None,
                           shape_offset=None):
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
        Returns:
            (mTransform) The created curve object.
    """

    #...Initialize parameters
    if not up_direction: up_direction = [0, 1, 0]
    if not forward_direction: forward_direction = [0, 0, 1]
    if not shape_offset: shape_offset = [0, 0, 0]
    if not scale: scale = 1

    #...Test that provided dictionary entry exists
    if prefab not in PREFAB_CRV_SHAPES:
        pm.error("Cannot create prefab curve object. "
                 "Provided prefab dictionary key '{}' is invalid".format(prefab))

    #...Get shape data dictionary for this prefab
    prefab_list = copy.deepcopy(PREFAB_CRV_SHAPES[prefab])

    #...Create the shape object with assembled data
    output_obj = curve_construct(
        curves=prefab_list,
        name = name,
        color = color,
        scale = scale,
        shape_offset = shape_offset,
        up_direction = up_direction,
        forward_direction = forward_direction,
    )
    return output_obj
