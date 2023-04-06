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
orienter
joint
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



########################################################################################################################
def orienter(name=None, scale=1):
    # Initialize variables
    name = name if name else ''
    cvs = [
        [
            [0, 1.4, 0.369], [-0.261, 1.4, 0.261], [-0.369, 1.4, 0], [-0.261, 1.4, -0.261], [0, 1.4, -0.369],
            [0.261, 1.4, -0.261], [0.369, 1.4, 0], [0.261, 1.4, 0.261],
        ], [
            [0, 1.4, 0.333], [0, 2.5, 0], [0, 1.4, -0.333]
        ], [
            [0.333, 1.4, 0], [0, 2.5, 0], [-0.333, 1.4, 0]
        ], [
            [1.4, 0, 0.369], [1.4, 0.261, 0.261], [1.4, 0.369, 0], [1.4, 0.261, -0.261], [1.4, 0, -0.369],
            [1.4, -0.261, -0.261], [1.4, -0.369, 0], [1.4, -0.261, 0.261],
        ], [
            [1.4, 0, 0.333], [2.5, 0, 0], [1.4, 0, -0.333]
        ], [
            [1.4, 0.333, 0], [2.5, 0, 0], [1.4, -0.333, 0]
        ], [
            [0, 0.369, 1.4], [-0.261, 0.261, 1.4], [-0.369, 0, 1.4], [-0.261, -0.261, 1.4], [0, -0.369, 1.4],
            [0.261, -0.261, 1.4], [0.369, 0, 1.4], [0.261, 0.261, 1.4],
        ], [
            [0, 0.333, 1.4], [0, 0, 2.5], [0, -0.333, 1.4]
        ], [
            [0.333, 0, 1.4], [0, 0, 2.5], [-0.333, 0, 1.4]
        ]
    ]
    colors = [14, 14, 14, 13, 13, 13, 6, 6, 6]
    forms = ["periodic", "open", "open", "periodic", "open", "open", "periodic", "open", "open"]
    degrees = [3, 1, 1, 3, 1, 1, 3, 1, 1]
    # Compose orienter name
    orienter = gen.curve_construct(cvs=cvs, name=name, color=None, form=forms, scale=scale, side=None,
                                   degree=degrees)
    # Color orienter
    shapes = orienter.getShapes()
    for s, c in zip(shapes, colors):
        gen.set_color(s, c)
    return orienter



########################################################################################################################
def joint(name=None, radius=1.0, color=None, parent=None, position=None, joint_type="JNT", side=None, draw_style=None,
          visibility=True):
    """
        Creates a joint. More robust than Maya's native joint command. Allows for more aspects of the joint to be
            handled within a single function.
        Args:
            name (string): Joint name.
            radius (numeric): Joint radius.
            color (int/ [numeric, numeric, numeric]): Joint override colour.
            parent (dagNode): Parent of newly created joint (optional.)
            position ([numeric, numeric, numeric]): Joint's world position.
            joint_type (string): The joint type can be extrapolated upon to determine other aspects like override
                colour.
            side (string): The side of the desired side prefix of joint name.
            draw_style (bool): Joint draw style (0(default)='bone', 1='multi child box', 2='none'.)
            visibility (bool): Joint visibility.
        Returns:
            (joint node) The newly created joint.
    """

    # Dictionaries
    joint_type_name_chunks = {
        nom.bindJnt: [nom.bindJnt, "bind", "bindJoints", "bind_joint", "BindJoint", "Bind_Joint", "bind joint", "Bind"],
        nom.nonBindJnt: [nom.nonBindJnt, "nonBind", "non bind", "non_bind", "Non_Bind", "Non Bind", "non-bind",
                         "nonbind"]
    }
    side_tag_string = None
    if not side:
        side_tag_string = ''
    else:
        side_tag_string = f'{gen.side_tag_from_string(side)}_'
    # Clear selection so joint doesn't auto-parent somewhere weird
    pm.select(clear=1)
    # Make joint and set its name, radius, and position (if any were provided)
    if not position:
        position = [0, 0, 0]
    # Determine joint type name chunk
    joint_type_suffix = None
    for key in joint_type_name_chunks:
        if joint_type in joint_type_name_chunks[key]:
            joint_type_suffix = key
    # Determine joint name on arguments
    joint_name = f'{side_tag_string}{name}_{joint_type_suffix}'
    # Create joint
    jnt = pm.joint(name=joint_name, radius=radius, position=position)
    # Set joint's color (if specific color not provided, then color joint based on joint_type argument)
    if joint_type and not color:
        if joint_type == nom.nonBindJnt:
            color = 3
        elif joint_type == nom.bindJnt:
            color = 1
    if color:
        gen.set_color(jnt, color)
    # Parent joint (if parent argument provided)
    if parent:
        jnt.setParent(parent)
    # Set joint's visibility and draw style
    if draw_style in [1, 2]:
        jnt.drawStyle.set(draw_style)
    if visibility in [False, 0]:
        jnt.visibility.set(False)

    pm.select(clear=1)
    return jnt
