# Title: curve_utils.py
# Author: Sam Leheny
# Contact: samleheny@live.com

# Description:


###########################
##### Import Commands #####
import importlib
import copy
from dataclasses import dataclass, field
from typing import Union
import maya.cmds as mc
import pymel.core as pm
import maya.api.OpenMaya as om

import Snowman3.utilities.general_utils as gen
importlib.reload(gen)

import Snowman3.dictionaries.nurbsCurvePrefabs as prefab_curve_shapes
importlib.reload(prefab_curve_shapes)
###########################
###########################


###########################
######## Variables ########
PREFAB_CRV_SHAPES = prefab_curve_shapes.create_dict()
NURBS_CURVE_FORMS = { 'open': om.MFnNurbsCurve.kOpen,
                      'closed': om.MFnNurbsCurve.kClosed,
                      'periodic': om.MFnNurbsCurve.kPeriodic }
NURBS_CURVE_FORM_INDICES = { 'open': 0,
                             'closed': 1,
                             'periodic': 2 }
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
def get_shape_data_from_prefab(prefab_shape, size=None, shape_offset=None, up_direction=None,
                               forward_direction=None):
    cv_data = compose_curve_construct_cvs(
        curve_data=copy.deepcopy(PREFAB_CRV_SHAPES[prefab_shape]),
        scale=size,
        shape_offset=shape_offset,
        up_direction=up_direction,
        forward_direction=forward_direction
    )
    return cv_data



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
def create_nurbs_curve(name, degree, cvs, form, color, parent):
    # Create the transform node in advance
    name = name or 'TEMPCRV'
    transform_node = parent # or pm.shadingNode('transform', name=name, au=1)

    # mc.select(transform_node.nodeName(), replace=1)
    #sel = om.MSelectionList()
    #om.MGlobal.getActiveSelectionList(sel)
    #mObj = om.MObject()
    #sel.getDependNode(0, mObj)

    # Function for getting the expected Knots input from the points list.
    def calculate_knots(spans, degree, form):
        knots = []
        knot_count = spans + 2 * degree - 1
        if form == 2:
            pit = (degree - 1) * -1
            for itr in range(knot_count):
                knots.append(pit)
                pit += 1
            return knots
        for itr in range(degree):
            knots.append(0)
        for itr in range(knot_count - (degree * 2)):
            knots.append(itr + 1)
        for kit in range(degree):
            knots.append(itr + 2)
        return knots

    # The easy-for-humans-to-understand curve inputs
    # -------------------------------------------------
    if form == 'periodic':
        if degree == 3:
            if not cvs[:3] == cvs[-3:]:
                cvs.extend(cvs[:3])
        else:
            if not cvs[0] == cvs[-1]:
                cvs.append(cvs[0])
    spans = len(cvs) - degree
    # --------- Still not sure what these do ----------
    create_2d = False
    rational = False

    # Convert the points into Maya's native format...
    point_array = om.MPointArray()
    for p in cvs:
        point_array.append(om.MPoint(*p))
    # ...Do the same for the knots
    knots_array = om.MDoubleArray()
    for k in calculate_knots(spans, degree, NURBS_CURVE_FORM_INDICES[form]):
        knots_array.append(k)

    # Assemble the arguments expected by OpenMaya's MFnNurbsCurve function
    args = [
        point_array,
        knots_array,
        degree,
        NURBS_CURVE_FORMS[form],
        create_2d,
        rational,
        parent #mObj
    ]
    # Create the nurbs curve
    m_object = om.MFnNurbsCurve().create(*args)
    # Name the nurbs curve
    om.MFnDependencyNode(m_object).setName(f'{name}Shape')

    '''
    # Non-api version. Suspected to be slower.
    crv = pm.curve(name=name, degree=degree, point=cvs)
    if form == 'periodic':
        pm.closeCurve(crv, replaceOriginal=1, preserveShape=0)
    pm.delete(crv, constructionHistory=True)'''
    if color:
        gen.set_mobj_color(m_object, color)

    pm.select(clear=1)
    return transform_node



# ----------------------------------------------------------------------------------------------------------------------
def curve_construct(curves, name=None, color=None, scale=1, shape_offset=None, up_direction=None,
                    forward_direction=None, composed_cv_data=None):
    transform_node = pm.shadingNode('transform', name=name, au=1)
    if not composed_cv_data:
        composed_cv_data = compose_curve_construct_cvs(
            curve_data=curves, scale=scale, shape_offset=shape_offset, up_direction=up_direction,
            forward_direction=forward_direction )

    mc.select(transform_node.nodeName(), replace=1)
    sel = om.MGlobal.getActiveSelectionList(0)
    mObj = sel.getDependNode(0)

    [ create_nurbs_curve(
        name=None,
        color=color,
        form=curves[i]['form'],
        cvs=curves[i]['cvs'],
        degree=curves[i]['degree'],
        parent=mObj
    ) for i, _ in enumerate(composed_cv_data) ]
    gen.rename_shapes(transform_node)
    return transform_node



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
