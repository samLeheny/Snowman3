import importlib

import maya.api.OpenMaya as om

import Snowman3.riggers.utilities.curve_utils as curve_utils
importlib.reload(curve_utils)



# ----------------------------------------------------------------------------------------------------------------------
def create_m_depend_node(**kwargs):
    if kwargs.get('parent', None) is not None:
        return om.MFnDependencyNode().create(
            kwargs['node_type'],
            kwargs['name'],
            kwargs['parent'] )
    else:
        return om.MFnDependencyNode().create(
            kwargs['node_type'],
            kwargs['name'] )


# ----------------------------------------------------------------------------------------------------------------------
def compose_curve_construct_cvs(**kwargs):
    return curve_utils.compose_curve_construct_cvs(**kwargs)


# ----------------------------------------------------------------------------------------------------------------------
def create_nurbs_curve(**kwargs):
    return curve_utils.create_nurbs_curve(**kwargs)