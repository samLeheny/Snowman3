# Title: rig_utils.py
# Author: Sam Leheny
# Contact: samleheny@live.com

# Description: Utility functions specific to rigging.


###########################
##### Import Commands #####
import importlib
import pymel.core as pm

import Snowman3.utilities.general_utils as gen
importlib.reload(gen)

import Snowman3.utilities.node_utils as node_utils
importlib.reload(node_utils)

import Snowman3.dictionaries.nameConventions as nameConventions
importlib.reload(nameConventions)
nom = nameConventions.create_dict()
###########################
###########################



########################################################################################################################
############# ------------------------------    TABLE OF CONTENTS    ----------------------------------- ###############
########################################################################################################################
'''
connector_curve
'''
########################################################################################################################
########################################################################################################################
########################################################################################################################



########################################################################################################################
def connector_curve(name=None, end_driver_1=None, end_driver_2=None, override_display_type=None, line_width=-1.0,
                    parent=None, inheritsTransform=True, use_locators=True):
    """
    Creates a straight line curve pulled between to points.
    Args:
        name (string): Name of curve.
        end_driver_1 (dagObject): The node to serve as the first end locator's parent.
        end_driver_2 (dagObject): The node to serve as the second end locator's parent.
        override_display_type (int): The value to feed the curve's overrideDisplayType attribute. Valid args: 0, 1, 2.
            1 = 'reference', 2 = 'template'
        line_width (float): Drawing thickness of curve.
        parent (dag obj): Node to parent curve to (optional.)
    Return:
        (transform, locator, locator): A list containing the curve and the two end locators.
    """

    pm.select(clear=1)

    name_chunk = name if name else ''

    # Compose curve name
    crv_name = f'{name_chunk}_connector_{nom.curve}'

    # Create curve
    curve = pm.curve(name=crv_name, degree=1, point=[[0, 0, 0], [1, 0, 0]])
    curve.getShape().lineWidth.set(line_width)
    [pm.setAttr(f'{curve}.{attr}', lock=1, keyable=0) for attr in gen.keyable_transform_attrs]

    # Make curve selectable if desired
    if override_display_type:
        curve.getShape().overrideEnabled.set(1)
        curve.getShape().overrideDisplayType.set(override_display_type)

    # Get nodes to drive ends of curve
    curve_plugs = []
    if use_locators:
        loc_1 = pm.spaceLocator(name=f'{name_chunk}_1_{nom.locator}')
        loc_2 = pm.spaceLocator(name=f'{name_chunk}_2_{nom.locator}')
        if end_driver_1 and end_driver_2:
            loc_1.setParent(end_driver_1)
            loc_2.setParent(end_driver_2)
            gen.zero_out(loc_1)
            gen.zero_out(loc_2)
            loc_1.visibility.set(0, lock=1)
            loc_2.visibility.set(0, lock=1)
        [curve_plugs.append(loc.getShape().worldPosition[0]) for loc in (loc_1, loc_2)]
    elif end_driver_1 and end_driver_2:
        decomp_1 = node_utils.decomposeMatrix(inputMatrix=end_driver_1.worldMatrix)
        decomp_2 = node_utils.decomposeMatrix(inputMatrix=end_driver_2.worldMatrix)
        curve_plugs = [decomp_1.outputTranslate,
                       decomp_2.outputTranslate]

    # Attach to curve
    curve_plugs[0].connect(curve.getShape().controlPoints[0])
    curve_plugs[1].connect(curve.getShape().controlPoints[1])

    if parent:
        curve.setParent(parent)
    if not inheritsTransform:
        curve.inheritsTransform.set(0, lock=1)

    pm.select(clear=1)
    return curve, curve_plugs[0], curve_plugs[1]
