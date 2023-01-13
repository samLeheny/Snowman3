# Title: rig_utils.py
# Author: Sam Leheny
# Contact: samleheny@live.com

# Description: Utility functions specific to rigging.


###########################
##### Import Commands #####
import importlib
import pymel.core as pm

import Snowman3.utilities.general_utils as gen_utils
importlib.reload(gen_utils)

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
joint
control
embed_transform_lock_data
connector_curve
orienter
joint_rot_to_orient
soft_ik_network
insert_nurbs_strip
ribbon
get_skinClust_input_geo
mesh_to_skinClust_input
apply_ctrl_locks
limb_rollers
ribbon_tweak_ctrls
space_blender
space_switch
'''
########################################################################################################################
########################################################################################################################
########################################################################################################################





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
        side_tag_string = ""
    else:
        side_tag_string = "{0}_".format( gen_utils.side_tag_from_string(side) )


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
    joint_name = "{0}{1}_{2}".format(side_tag_string, name, joint_type_suffix)

    # Create joint
    jnt = pm.joint(name=joint_name, radius=radius, position=position)


    # Set joint's color (if specific color not provided, then color joint based on joint_type argument)
    if joint_type and not color:

        if joint_type == nom.nonBindJnt:
            color = 3

        elif joint_type == nom.bindJnt:
            color = 1

    if color:
        gen_utils.set_color(jnt, color)


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





########################################################################################################################
def control(ctrl_info=None, name=None, ctrl_type=None, side=None, parent=None, num_particle=None, color=None,
            scale=None):
    """
        Creates a nurbs curves control object from information arranged in a standard dictionary format used throughout
            the suite rigging tools. Using this function when creating controls fast tracks certain repetitive such as
            locking off certain transforms, or correctly naming the control.
        Args:
            ctrl_info (): Dictionary containing information about the desired control such as shape prefab, scale,
                degree, colour, transforms to be locked, etc.
            name (): The string name of the control to be.
            ctrl_type (): Whether it's an animation control. Will be used to determine things about the control
                like what it's prefix should be.
            side (): If the control is sided and if so, which side. Things like side string particle and control colour
                can be derived from this info.
            parent (): The object to parent the new control to (option.)
            num_particle (): The numbered string particle if desired.
            color (): he desired color for the control's nurbs curve. If provided, argument will override any color
                information in the ctrlInfo dictionary argument.
            scale (): The scale factor for control's nurbs curve. If provided, argument will override any scale
                information in the ctrlInfo dictionary argument.
    Return:
            (transform node) The created control.
    """



    # Determine control prefix
    ctrl_type_dict = {
        nom.animCtrl : ["CTRL", "control", "animCtrl", "anim_ctrl", "anim_control", "animControl", "anim", "AnimCtrl",
                        "Anim_Ctrl", "Anim Ctrl", "anim ctrl", "anim", "Anim", nom.animCtrl],
        nom.nonAnimCtrl : ["setupCtrl", "SetupCTRL", "nonAnimCtrl", "non_anim_ctrl", "non_anim_control",
                           "nonAnimControl", "nonAnim", "NonAnimCtrl", "Non_Anim_Ctrl", "Non Anim Ctrl",
                           "non anim ctrl", "Non Anim", nom.nonAnimCtrl],
    }

    ctrl_suffix = nom.animCtrl

    for key in ctrl_type_dict:
        if ctrl_type in ctrl_type_dict[key]:
            ctrl_suffix = key
            break

    if ctrl_suffix:
        ctrl_suffix = "_{0}".format(ctrl_suffix)


    # Determine if control name needs a sided prefix
    side_prefix = ""
    side_dict = { nom.leftSideTag : [nom.leftSideTag, nom.leftSideTag2],
                  nom.rightSideTag : [nom.rightSideTag, nom.rightSideTag2],
                  nom.midSideTag : [nom.midSideTag, nom.midSideTag2] }
    if side:
        for key in side_dict:
            if side in side_dict[key]:
                side_prefix = f'{key}_'
                break


    # Determine num particle
    num_chunk = ""
    if isinstance(num_particle, int):
        num_particle = str(num_particle)
    if num_particle:
        if num_particle != "":
            num_chunk = f'_{num_particle}'


    # Determine control name
    name_chunk = name if name else ctrl_info["name"]
    ctrl_name = f'{side_prefix}{name_chunk}{ctrl_suffix}'


    # Check to see if a control with this name already exists
    ### if pm.objExists(ctrl_name):
    ###     pm.error(f'A control with name "{ctrl_name}" already exists')


    # Determine control colour
    if not color:
        color = [ ctrl_info["color"] if "color" in ctrl_info else None ][0]


    # Determine scale factor
    if not scale:
        scale = [ ctrl_info["scale"] if "scale" in ctrl_info else None ][0]


    # Determine shape offset factor
    shape_offset = [ ctrl_info["offset"] if "offset" in ctrl_info else [0, 0, 0] ][0]


    # Determine forward and up direction
    forward_direction = ctrl_info["forward_direction"] if "forward_direction" in ctrl_info else [0, 0, 1]
    up_direction = ctrl_info["up_direction"] if "up_direction" in ctrl_info else [0, 1, 0]


    # Create the control's curve shape based on control info
    ctrl = gen_utils.prefab_curve_construct(
        prefab=ctrl_info["shape"],
        name=ctrl_name,
        color=color,
        scale=scale,
        shape_offset=shape_offset,
        forward_direction=forward_direction,
        up_direction=up_direction,
        side=side
    )

    # Embed lock information into hidden attributes on control
    embed_transform_lock_data(ctrl, ctrl_info)

    # Parent control
    ctrl.setParent(parent) if parent else None


    pm.select(clear=1)
    return ctrl





########################################################################################################################
def embed_transform_lock_data(ctrl, ctrl_info):

    #...Confirm lock data was provided. If not, skip embedding procedure
    if 'locks' not in ctrl_info:
        return False

    locks = ctrl_info['locks']

    #...Fill in missing entries with zeroed lists
    for key in ('t', 'r', 's', 'v'):
        if key not in locks:
            locks[key] = [0, 0, 0] if key in ('t', 'r', 's') else 0

    #...Add compound attr to ctrl
    pm.addAttr(ctrl, longName="LockAttrData", keyable=0, attributeType="compound", numberOfChildren=4)
    for key in ('t', 'r', 's', 'v'):
        pm.addAttr(ctrl, longName=f'LockAttrData{key.upper()}', keyable=0, dataType="string", parent="LockAttrData")

    #...Embed lock data values in new attrs
    for key in ('t', 'r', 's', 'v'):
        pm.setAttr(f'{ctrl}.LockAttrData{key.upper()}', str(locks[key]), type="string")

    return True




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


    name_chunk = [name if name else ""][0]


    # Compose curve name
    crv_name = "{}_connector_{}".format(name_chunk, nom.curve)

    # Create curve
    curve = pm.curve(name=crv_name, degree=1, point=[[0, 0, 0], [1, 0, 0]])
    curve.getShape().lineWidth.set(line_width)
    [pm.setAttr(curve + "." + attr, lock=1, keyable=0) for attr in gen_utils.keyable_transform_attrs]

    # Make curve selectable if desired
    if override_display_type:
        curve.getShape().overrideEnabled.set(1)
        curve.getShape().overrideDisplayType.set(override_display_type)

    # Get nodes to drive ends of curve
    if use_locators:
        loc_1 = pm.spaceLocator(name="{}_1_{}".format(name_chunk, nom.locator))
        loc_2 = pm.spaceLocator(name="{}_2_{}".format(name_chunk, nom.locator))
        if end_driver_1 and end_driver_2:
            loc_1.setParent(end_driver_1)
            loc_2.setParent(end_driver_2)
            gen_utils.zero_out(loc_1)
            gen_utils.zero_out(loc_2)
            loc_1.visibility.set(0, lock=1)
            loc_2.visibility.set(0, lock=1)
        curve_plugs = [loc_1.getShape().worldPosition[0],
                       loc_2.getShape().worldPosition[0]]
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
def orienter(name=None, side=None, scale=1):


    # Initialize variables
    name = name if name else ""
    side_tag = "{}_".format(side) if side else ""


    cvs = [
        [
            [0, 1.4, 0.369],
            [-0.261, 1.4, 0.261],
            [-0.369, 1.4, 0],
            [-0.261, 1.4, -0.261],
            [0, 1.4, -0.369],
            [0.261, 1.4, -0.261],
            [0.369, 1.4, 0],
            [0.261, 1.4, 0.261],
        ], [
            [0, 1.4, 0.333],
            [0, 2.5, 0],
            [0, 1.4, -0.333]
        ], [
            [0.333, 1.4, 0],
            [0, 2.5, 0],
            [-0.333, 1.4, 0]
        ], [
            [1.4, 0, 0.369],
            [1.4, 0.261, 0.261],
            [1.4, 0.369, 0],
            [1.4, 0.261, -0.261],
            [1.4, 0, -0.369],
            [1.4, -0.261, -0.261],
            [1.4, -0.369, 0],
            [1.4, -0.261, 0.261],
        ], [
            [1.4, 0, 0.333],
            [2.5, 0, 0],
            [1.4, 0, -0.333]
        ], [
            [1.4, 0.333, 0],
            [2.5, 0, 0],
            [1.4, -0.333, 0]
        ], [
            [0, 0.369, 1.4],
            [-0.261, 0.261, 1.4],
            [-0.369, 0, 1.4],
            [-0.261, -0.261, 1.4],
            [0, -0.369, 1.4],
            [0.261, -0.261, 1.4],
            [0.369, 0, 1.4],
            [0.261, 0.261, 1.4],
        ], [
            [0, 0.333, 1.4],
            [0, 0, 2.5],
            [0, -0.333, 1.4]
        ], [
            [0.333, 0, 1.4],
            [0, 0, 2.5],
            [-0.333, 0, 1.4]
        ]
    ]
    colors = [14, 14, 14,
              13, 13, 13,
              6, 6, 6]
    forms = ["periodic", "open", "open",
             "periodic", "open", "open",
             "periodic", "open", "open"]
    degrees = [3, 1, 1,
               3, 1, 1,
               3, 1, 1]


    # Compose orienter name
    ori_name = "{}{}_{}".format(side_tag, name, nom.orienter)

    orienter = gen_utils.curve_construct(cvs=cvs, name=ori_name, color=None, form=forms, scale=scale, side=None,
                                         degree=degrees)

    # Color orienter
    shapes = orienter.getShapes()
    for s, c in zip(shapes, colors):
        gen_utils.set_color(s, c)



    return orienter





########################################################################################################################
def joint_rot_to_ori(joint):

    jointOrient_attrs = ("jointOrientX", "jointOrientY", "jointOrientZ")

    for i in range(3):
        pm.setAttr(joint + "." + jointOrient_attrs[i],
                   pm.getAttr(joint + "." + jointOrient_attrs[i]) + pm.getAttr(joint + "." + gen_utils.rotate_attrs[i]))

    pm.setAttr(joint.rotate, 0, 0, 0)





########################################################################################################################
def soft_ik_network(side=None, ik_solver=None, ik_ctrl=None, root_scale=None, limb_name=None, upper_limb_name=None,
           fore_limb_name=None, total_limb_length=None, ik_distance=None, stretchy_attr=None, destination_jnts=None,
           limb_mult_attrs=None, blend_attr_node=None):
    """

        Args:
            side ():
            ik_solver ():
            ik_ctrl ():
            root_scale ():
            limb_name ():
            upper_limb_name ():
            fore_limb_name ():
            total_limb_length ():
            ik_distance ():
            stretchy_attr ():
            destination_jnts ():
            limb_mult_attrs ():
            blend_attr_node ():
    """


    soft_ik_attr = "soft_ik"

    side_tag = "{}_".format(side) if side else ""

    if not blend_attr_node:
        blend_attr_node = ik_ctrl

    # Raise precision of ik solver, so we don't get that ugly stair-stepping effect
    pm.setAttr(ik_solver + '.tolerance', 7e-10)

    # Create Soft IK attribute
    if not pm.attributeQuery(soft_ik_attr, node=blend_attr_node, exists=True):
        pm.addAttr(blend_attr_node, longName=soft_ik_attr, attributeType='float', minValue=0, maxValue=10,
                   defaultValue=0, keyable=True)

    # Account for rig scale in limb IK distance
    scale_div = node_utils.floatMath(name='scaledDistance_{}_{}'.format(limb_name, side), operation="div",
                                     floatA=ik_distance, floatB=root_scale)

    # Convergence point
    converge_div = node_utils.floatMath(name='div_converge_{}_{}'.format(limb_name, side), operation="div",
                                        floatA=scale_div.outFloat, floatB=total_limb_length)

    # Scaled curve length
    scaled_curve_length = node_utils.floatMath(name='scaledCrvLen_{}_{}'.format(limb_name, side), operation="div",
                                               floatA=100, floatB=total_limb_length)
    #
    scaled_mult = node_utils.multDoubleLinear(name='scaledDist_crv_ikEnd_{}_{}'.format(limb_name, side),
                                              input1=scale_div.outFloat, input2=scaled_curve_length.outFloat)

    # Remapped Soft IK
    remap_soft_ik = pm.shadingNode('remapValue', name='remap_softIK_{}_{}'.format(limb_name, side), au=1)
    pm.connectAttr(blend_attr_node + '.' + soft_ik_attr, remap_soft_ik + '.inputValue')
    pm.setAttr(remap_soft_ik + '.inputMin', 0, lock=True)
    pm.setAttr(remap_soft_ik + '.inputMax', 10, lock=True)
    pm.setAttr(remap_soft_ik + '.outputMin', 1, lock=True)

    # Animation curve
    def soft_ik_curve(input, output):
        # Create anim curve node
        anim_curve = pm.shadingNode('animCurveUU', name='{}_anim_crv_softIk_{}'.format(side_tag, limb_name),
                                     au=1)
        pm.connectAttr(input, anim_curve + '.input')
        pm.setKeyframe(anim_curve, float=10, value=1)
        pm.setKeyframe(anim_curve, float=77.5, value=0.91)
        pm.setKeyframe(anim_curve, float=100, value=1)

        pm.keyTangent(anim_curve, index=(0, 0), lock=False, edit=True)
        pm.keyTangent(anim_curve, index=(0, 0), weightedTangents=True, edit=True)
        pm.keyTangent(anim_curve, index=(0, 0), outAngle=0, edit=True)
        pm.keyTangent(anim_curve, index=(0, 0), outWeight=544.42547, edit=True)

        pm.keyTangent(anim_curve, index=(1, 1), lock=False, edit=True)
        pm.keyTangent(anim_curve, index=(1, 1), weightedTangents=True, edit=True)
        pm.keyTangent(anim_curve, index=(1, 1), inAngle=0, edit=True)
        pm.keyTangent(anim_curve, index=(1, 1), inWeight=396.596271, edit=True)
        pm.keyTangent(anim_curve, index=(1, 1), outAngle=0, edit=True)
        pm.keyTangent(anim_curve, index=(1, 1), outWeight=300, edit=True)

        pm.keyTangent(anim_curve, index=(2, 2), lock=False, edit=True)
        pm.keyTangent(anim_curve, index=(2, 2), weightedTangents=True, edit=True)
        pm.keyTangent(anim_curve, index=(2, 2), inAngle=0.023, edit=True)
        pm.keyTangent(anim_curve, index=(2, 2), inWeight=40.000005, edit=True)

        pm.connectAttr(anim_curve + '.output', output)
        return anim_curve

    anim_crv = soft_ik_curve(input=scaled_mult + '.output', output=remap_soft_ik + '.outputMax')

    for limb_mult_attr in limb_mult_attrs:

        # Scale up mult
        scale_up_mult = node_utils.multDoubleLinear(name='mult_upscale_{}_{}'.format(limb_name, side),
                                                    input1=converge_div.outFloat, input2=limb_mult_attr)

        # Remapped Stretchy
        remap_stretchy = pm.shadingNode('remapValue', name='remap_stretchy_{}_{}'.format(limb_name, side),
                                         au=1)
        pm.connectAttr(stretchy_attr, remap_stretchy + '.inputValue')
        pm.setAttr(remap_stretchy + '.inputMin', 0, lock=True)
        pm.setAttr(remap_stretchy + '.inputMax', 10, lock=True)
        pm.setAttr(remap_stretchy + '.outputMin', 1, lock=True)
        pm.connectAttr(scale_up_mult + '.output', remap_stretchy + '.outputMax')

        # Condition
        cond = pm.shadingNode('condition', name='cond_stretch_{}_{}'.format(limb_name, side), au=1)
        pm.setAttr(cond + '.operation', 2, lock=True)
        pm.connectAttr(scale_div + '.outFloat', cond + '.firstTerm')
        pm.connectAttr(total_limb_length, cond + '.secondTerm')
        pm.connectAttr(remap_stretchy + '.outValue', cond + '.colorIfTrue.colorIfTrueR')
        pm.connectAttr(limb_mult_attr, cond + '.colorIfFalse.colorIfFalseR')

        # Mult converge
        mult_converge = node_utils.multDoubleLinear(name='mult_converge_{}_{}'.format(limb_name, side),
                                                    input1=cond.outColor.outColorR, input2=remap_soft_ik.outValue)

        # Plug it all into the joints!
        pm.connectAttr(mult_converge+'.output', destination_jnts[limb_mult_attrs.index(limb_mult_attr)]+'.sx',
                       force=True)





########################################################################################################################
def insert_nurbs_strip(name, start_obj, end_obj, up_obj, up_vector=(0, 1, 0), side=None):


    side_tag = "{}_".format(side) if side else ""

    # Determine length of eventual nurbs strip
    length = gen_utils.distance_between(start_obj, end_obj)

    # Create nurbs strip
    strip = pm.nurbsPlane(name="{}{}_ribbon".format(side_tag, name), axis=(0, 1, 0), width=length, lengthRatio=0.1)[0]
    pm.delete(strip, constructionHistory=1)

    # Position and orient nurbs strip
    pm.delete(pm.pointConstraint(start_obj, end_obj, strip))
    pm.delete(pm.aimConstraint(end_obj, strip, worldUpType="object", worldUpObject=up_obj, aimVector=(1, 0, 0),
                               upVector=up_vector))


    return strip





########################################################################################################################
def ribbon_plane(name, start_obj, end_obj, up_obj, density, up_vector=(0, 1, 0), side=None):


    # Create nurbs strip
    strip = insert_nurbs_strip(name, start_obj, end_obj, up_obj, up_vector, side)

    # Create output math nodes and connect them to nurbs strip shape
    surf_point_nodes, four_by_four_nodes, decomp_nodes = [], [], []

    for i in range(0, density):

        n = i + 1

        # PointOnSurfacesInfo nodes
        surf_point = pm.shadingNode("pointOnSurfaceInfo", au=1)
        surf_point.turnOnPercentage.set(1)
        surf_point_nodes.append(surf_point)
        strip.getShape().worldSpace[0].connect(surf_point.inputSurface)
        surf_point.parameterV.set(0.5)
        surf_point.parameterU.set(1.0 / (density-1) * i)

        # FourByFourMatrix nodes
        four_by_four = pm.shadingNode("fourByFourMatrix", au=1)
        four_by_four_nodes.append(four_by_four)
        surf_point.tangentUx.connect(four_by_four.in00)
        surf_point.tangentUy.connect(four_by_four.in01)
        surf_point.tangentUz.connect(four_by_four.in02)
        surf_point.normalX.connect(four_by_four.in10)
        surf_point.normalY.connect(four_by_four.in11)
        surf_point.normalZ.connect(four_by_four.in12)
        surf_point.tangentVx.connect(four_by_four.in20)
        surf_point.tangentVy.connect(four_by_four.in21)
        surf_point.tangentVz.connect(four_by_four.in22)
        surf_point.positionX.connect(four_by_four.in30)
        surf_point.positionY.connect(four_by_four.in31)
        surf_point.positionZ.connect(four_by_four.in32)

        # DecomposeMatrix nodes
        decomp = pm.shadingNode("decomposeMatrix", au=1)
        decomp_nodes.append(decomp)
        four_by_four.output.connect(decomp.inputMatrix)


    return {"nurbsStrip" : strip,
            "pointOnSurfaceNodes" : surf_point_nodes,
            "fourByFourMatrices" : four_by_four_nodes,
            "decomposedMatrices" : decomp_nodes,
            "length" : gen_utils.distance_between(start_obj, end_obj)}





########################################################################################################################
def get_skinClust_input_geo(skin_cluster, return_input_groupparts=False):
    """
        Find the node serving as the input shape to a skin cluster network.
        Args:
            skin_cluster (mObj): The skin cluster node to get the input shape to.
            return_input_go_out_plug (mPlug):
        Returns:
            (mObj): Input shape node
    """

    input_geo = None


    skin_clust_input_node = pm.listConnections(skin_cluster.input, s=1, d=0, shapes=1)
    input_geo = skin_clust_input_node[0] if skin_clust_input_node else None

    return input_geo





########################################################################################################################
def mesh_to_skinClust_input(mesh, skin_cluster):

    mesh.worldSpace[0].connect(skin_cluster.input[0].inputGeometry, force=True)





########################################################################################################################
def apply_ctrl_locks(ctrl):
    """
    Checks for lock data in hidden attributes of provided ctrl, then locks ctrl's transforms in accordance with that
        data (translate, rotate, scale, and visibility.)
    Args:
        ctrl (mObj): The control whose transform attrs are to be locked.
    """

    attr_string = "LockAttrData"

    #...Confirm lock data attrs are present on this ctrl
    if not pm.attributeQuery(attr_string, node=ctrl, exists=1):
        return False

    #...Dictionary pairing each child attr and the transform attrs it corresponds to
    pairs = ((f'{attr_string}T', (ctrl.tx, ctrl.ty, ctrl.tz)),
             (f'{attr_string}R', (ctrl.rx, ctrl.ry, ctrl.rz)),
             (f'{attr_string}S', (ctrl.sx, ctrl.sy, ctrl.sz)))


    for attr, transform_attrs in pairs:

        #...Extract data from lock info attribute (get its string and convert to tuple of integers)
        string_val = pm.getAttr(f'{ctrl}.{attr}')
        string_list = ( string_val.split("[")[1].split("]")[0] )
        string_list = string_list.split(", ")
        numeric_data = (int(string_list[0]), int(string_list[1]), int(string_list[2]))

        #...Lock transform attrs in accordance with extracted lock info
        for a, lock_val in zip(transform_attrs, numeric_data):
            a.set(lock=lock_val, keyable=lock_val ^ 1)

    #...Delete lock data attribute. It has done its job. Now... it may rest.
    pm.deleteAttr(ctrl, attribute=attr_string)

    return True





########################################################################################################################
def limb_rollers(start_node, end_node, roller_name, world_up_obj, side=None, parent=None, jnt_radius=0.3,
                 up_axis=(0, 0, 1), ctrl_color=15, roll_axis=(1, 0, 0), ctrl_size=0.15, populate_ctrls=[1, 1, 1]):
    """

    """

    side_tag = f'{side}_' if side else ''

    #...Stretch rig group
    stretch_rig_grp = pm.group(name=f'{side_tag}stretch_rig_{roller_name}', p=parent, em=1)
    pm.pointConstraint(start_node, stretch_rig_grp)
    pm.aimConstraint(end_node, stretch_rig_grp, aimVector=roll_axis, upVector=up_axis, worldUpType='objectrotation',
                     worldUpObject=world_up_obj)


    #...Start, Mid, and End controls
    def bend_control(tag, match_node, rot_match_node):

        ctrl = control(ctrl_info={'shape': 'circle',
                                  'scale': [ctrl_size, ctrl_size, ctrl_size],
                                  'up_direction': roll_axis,
                                  'forward_direction': up_axis},
                       name=f'{roller_name}_bend_{tag}', ctrl_type=nom.animCtrl, side=side, color=ctrl_color)

        jnt = joint(name=f'{roller_name}bend_{tag}', side=side, joint_type=nom.nonBindJnt, radius=jnt_radius)
        jnt.setParent(ctrl)

        mod = gen_utils.buffer_obj(ctrl, suffix='MOD')

        buffer = gen_utils.buffer_obj(mod, suffix='BUFFER', parent=stretch_rig_grp)
        gen_utils.zero_out(buffer)

        pm.delete(pm.pointConstraint(match_node, buffer))
        buffer.scale.set(1, 1, 1)

        return jnt, ctrl, mod, buffer


    start_jnt, start_ctrl, start_mod, start_buffer = bend_control(
        tag="start", match_node=start_node, rot_match_node=start_node)

    mid_jnt, mid_ctrl, mid_mod, mid_buffer = bend_control(
        tag="mid", match_node=(start_node, end_node), rot_match_node=start_node)

    end_jnt, end_ctrl, end_mod, end_buffer = bend_control(
        tag="end", match_node=end_node, rot_match_node=start_node)

    #...Exclude controls based on arguments
    for ctrl, param in zip((start_ctrl, mid_ctrl, end_ctrl), populate_ctrls):
        if param: continue
        pm.rename(ctrl, str(ctrl).replace('_CTRL', '_handle'))
        [pm.delete(s) for s in ctrl.getShapes()]

    #...Roll locators
    start_roll_loc = pm.spaceLocator(name=f'{side_tag}{roller_name}_roll_start_{nom.locator}')
    start_roll_loc.setParent(stretch_rig_grp)
    gen_utils.zero_out(start_roll_loc)

    roll_socket_target = pm.spaceLocator(name=f'{side_tag}{roller_name}_rollStart_target_{nom.locator}')
    roll_socket_target.setParent(start_node)
    gen_utils.zero_out(roll_socket_target)
    pm.delete(pm.orientConstraint(start_roll_loc, roll_socket_target))
    gen_utils.matrix_constraint(objs=[roll_socket_target, start_roll_loc], decompose=True,
                                maintain_offset=True, translate=True, rotate=True, scale=False, shear=False)

    end_roll_loc = pm.spaceLocator(name=f'{side_tag}{roller_name}_roll_end_{nom.locator}')
    end_roll_loc.setParent(stretch_rig_grp)
    gen_utils.zero_out(end_roll_loc)
    pm.delete(pm.pointConstraint(end_ctrl, end_roll_loc))
    gen_utils.matrix_constraint(objs=[end_node, end_roll_loc], decompose=True, maintain_offset=True,
                                translate=True, rotate=True, scale=False, shear=False)

    #...Position ctr grps based on locators
    #...Start
    start_roll_loc.translate.connect(start_buffer.translate)

    rotate_attr_tag = ('X', 'x')

    decomp = node_utils.decomposeMatrix(inputMatrix=start_roll_loc.matrix)
    start_rot_convert = pm.shadingNode("quatToEuler", au=1)
    pm.connectAttr(f'{decomp}.outputQuat.outputQuat{rotate_attr_tag[0]}',
                   f'{start_rot_convert}.inputQuat.inputQuat{rotate_attr_tag[0]}')
    decomp.outputQuat.outputQuatW.connect(start_rot_convert.inputQuat.inputQuatW)
    pm.connectAttr(f'{start_rot_convert}.outputRotate.outputRotate{rotate_attr_tag[0]}',
                   f'{start_mod}.r{rotate_attr_tag[1]}')

    #...End
    end_roll_loc.translate.connect(end_buffer.translate)

    decomp = node_utils.decomposeMatrix(inputMatrix=end_roll_loc.matrix)
    end_rot_convert = pm.shadingNode("quatToEuler", au=1)
    pm.connectAttr(decomp + ".outputQuat.outputQuat" + rotate_attr_tag[0],
                   end_rot_convert + ".inputQuat.inputQuat" + rotate_attr_tag[0])
    pm.connectAttr(decomp.outputQuat.outputQuatW, end_rot_convert.inputQuat.inputQuatW)
    pm.connectAttr(f'{end_rot_convert}.outputRotate.outputRotate{rotate_attr_tag[0]}',
                   f'{end_mod}.r{rotate_attr_tag[1]}')

    #...Mid
    node_utils.multDoubleLinear(input1=end_roll_loc.tx, input2=0.5, output=mid_buffer.tx)

    blend = pm.shadingNode("blendWeighted", au=1)
    pm.connectAttr(f'{start_rot_convert}.outputRotate.outputRotate{rotate_attr_tag[0]}', blend.input[0])
    pm.connectAttr(f'{end_rot_convert}.outputRotate.outputRotate{rotate_attr_tag[0]}', blend.input[1])
    node_utils.multDoubleLinear(input1=blend.output, input2=0.5, output=f'{mid_mod}.r{rotate_attr_tag[1]}')


    # --------------------------------------------------------------------------------------------------------------
    return {"ctrls": (start_ctrl, mid_ctrl, end_ctrl),
            "jnts": (start_jnt, mid_jnt, end_jnt),
            "roll_socket_target": roll_socket_target}





########################################################################################################################
def ribbon_tweak_ctrls(ribbon, ctrl_name, length_ends, length_attr, attr_ctrl, side=None, ctrl_color=14,
                       ctrl_resolution=5, parent=None, ctrl_size=1, jnt_size=0.1):

    side_tag = "{}_".format(side) if side else ""

    #...Create live length measurement
    live_len = node_utils.distanceBetween(inMatrix1=length_ends[0].worldMatrix,
                                          inMatrix2=length_ends[1].worldMatrix)
    stretch_output = node_utils.floatMath(floatA=live_len.distance, floatB=length_attr, operation=3)
    squash_output = node_utils.floatMath(floatA=length_attr, floatB=live_len.distance, operation=3)

    squash_weight = node_utils.remapValue(inputValue=attr_ctrl + "." + "Volume",
                                          inputMin=0, inputMax=10, outputMin=1, outputMax=squash_output.outFloat)


    thick_attr_string = "{}_thick".format(ctrl_name)
    pm.addAttr(attr_ctrl, longName=thick_attr_string, attributeType="float", minValue=0.001,
               defaultValue=1, keyable=1)


    #...Group for tweak controls, parented under segment bend control
    tweak_ctrls_grp = pm.group(name="{}{}_tweak_ctrls".format(side_tag, ctrl_name), em=1,
                               p=parent)
    if side == nom.rightSideTag:
        gen_utils.flip(tweak_ctrls_grp)

    tweak_ctrls = []


    #...Bend controls visibility attribute ------------------------------------------------------------------------
    tweak_ctrl_vis_attr_string = "TweakCtrls"
    if not pm.attributeQuery(tweak_ctrl_vis_attr_string, node=attr_ctrl, exists=1):
        pm.addAttr(attr_ctrl, longName=tweak_ctrl_vis_attr_string, attributeType="bool", keyable=0, defaultValue=0)
        pm.setAttr(attr_ctrl + '.' + tweak_ctrl_vis_attr_string, channelBox=1)



    for i in range(ctrl_resolution):

        ctrl = control(ctrl_info={"shape": "square",
                                  "scale": [ctrl_size, ctrl_size, ctrl_size],
                                  "up_direction": [0, 1, 0],
                                  "forward_direction": [1, 0, 0]},
                       name="{}_tweak_{}".format(ctrl_name, str(i+1)),
                       ctrl_type=nom.animCtrl,
                       side=side,
                       color=ctrl_color)


        pm.connectAttr(attr_ctrl + "." + tweak_ctrl_vis_attr_string, ctrl.visibility)


        mod = gen_utils.buffer_obj(ctrl, suffix="MOD")
        attach = gen_utils.buffer_obj(mod, suffix="ATTACH")

        joint(name="{}_tweak_{}".format(ctrl_name, str(i+1)), side=side, joint_type=nom.bindJnt, parent=ctrl,
              radius=jnt_size)

        gen_utils.zero_out(attach)
        attach.setParent(tweak_ctrls_grp)


        pin = gen_utils.point_on_surface_matrix(input_surface=ribbon.getShape().worldSpace, parameter_V=0.5,
                                                parameter_U=(1.0/ctrl_resolution)*i, decompose=True,
                                                switch_U_V=True)

        pin.outputTranslate.connect(attach.translate)
        pin.outputRotate.connect(attach.rotate)

        offset = gen_utils.buffer_obj(mod, suffix="OFFSET")
        offset.setParent(ribbon)
        gen_utils.zero_out(offset)
        offset.setParent(attach)
        offset.translate.set(0, 0, 0)
        offset.scale.set(1, 1, 1)


        stretch_output.outFloat.connect(attach.sx)
        squash_weight.outValue.connect(attach.sy)
        squash_weight.outValue.connect(attach.sz)

        [pm.connectAttr(attr_ctrl + "." + thick_attr_string, mod + "." + a) for a in ("sy", "sz")]

        tweak_ctrls.append(ctrl)



    return tweak_ctrls





########################################################################################################################
def space_blender(target, source, source_name, name, attr_node, attr_name=None, default_value=10, reverse=False,
                  global_space_parent=None, side=None, translate=False, rotate=False, scale=False):

    side_tag = f'{side}_' if side else ''
    attr_name = attr_name if attr_name else 'Global'

    #...Create attribute ----------------------------------------------------------------------------------------------
    pm.addAttr(attr_node, longName=attr_name, attributeType="float", minValue=0, maxValue=10,
               defaultValue=default_value, keyable=1)



    #...Create space locators -----------------------------------------------------------------------------------------
    locs = []

    global_space_loc = pm.spaceLocator(name=f'{side_tag}{name}_global_SPACE')
    global_space_loc.setParent(global_space_parent)
    locs.append(global_space_loc)

    source_loc = pm.spaceLocator(name=f'{side_tag}{name}_{source_name}_SPACE')
    source_loc.setParent(source)
    locs.append(source_loc)

    for loc in locs:
        orig_parent = loc.getParent()
        loc.setParent(target)
        gen_utils.zero_out(loc)
        loc.setParent(orig_parent)
        gen_utils.convert_offset(loc)


    #...Create driver network -----------------------------------------------------------------------------------------
    blend = gen_utils.create_attr_blend_nodes(attr=attr_name, node=attr_node, reverse=reverse)

    blend_matrix = node_utils.blendMatrix(inputMatrix=source_loc.worldMatrix,
                                          targetMatrix=global_space_loc.worldMatrix)
    if reverse:
        pm.connectAttr(blend.revOutput, blend_matrix.target[0].weight)
    else:
        pm.connectAttr(blend.multOutput, blend_matrix.target[0].weight)

    mult_matrix = node_utils.multMatrix(matrixIn=(blend_matrix.outputMatrix, target.parentInverseMatrix))

    decomp = node_utils.decomposeMatrix(inputMatrix=mult_matrix.matrixSum)
    if translate:
        decomp.outputTranslate.connect(target.translate, f=1)
    if rotate:
        decomp.outputRotate.connect(target.rotate, f=1)
    if scale:
        decomp.outputScale.connect(target.scale, f=1)





########################################################################################################################
def space_switch(target, sources, source_names, name, attr_node, attr_name=None, global_space_parent=None, side=None,
                 translate=False, rotate=False, scale=False):

    side_tag = f'{side}_' if side else ''
    attr_name = attr_name if attr_name else 'Space'


    #...Create attribute ----------------------------------------------------------------------------------------------
    enum_name_string = source_names[0]
    for i in range(1, len(source_names)):
        enum_name_string += f':{source_names[i]}'
    enum_name_string += ':Global'

    pm.addAttr(attr_node, longName=attr_name, attributeType='enum', enumName=enum_name_string, keyable=1)


    #...Create space locators -----------------------------------------------------------------------------------------
    locs = []

    global_space_loc = pm.spaceLocator(name=f'{side_tag}{name}_global_SPACE')
    global_space_loc.setParent(global_space_parent)
    locs.append(global_space_loc)

    local_locs = []
    for source_name, source in zip(source_names, sources):
        loc = pm.spaceLocator(name=f'{side_tag}{name}_{source_name}_SPACE')
        local_locs.append(loc)
        locs.append(loc)
        loc.setParent(source)

    for loc in locs:
        orig_parent = loc.getParent()
        loc.setParent(target)
        gen_utils.zero_out(loc)
        loc.setParent(orig_parent)
        gen_utils.convert_offset(loc)


    #...Create driver network -----------------------------------------------------------------------------------------
    blend = gen_utils.create_attr_blend_nodes(attr=attr_name, node=attr_node, reverse=False)

    blend_matrix = node_utils.blendMatrix(inputMatrix=local_locs[0].worldMatrix,
                                          targetMatrix=global_space_loc.worldMatrix)
    for i in range(1, len(local_locs)):
        local_locs[i].worldMatrix.connect(blend_matrix.target[i].targetMatrix)
    global_space_loc.worldMatrix.connect(blend_matrix.target[len(local_locs)].targetMatrix)

    for i in range(1, len(local_locs)+1):
        con = node_utils.condition(firstTerm=f'{attr_node}.{attr_name}', secondTerm=i, operation='equal',
                                   colorIfTrue=(1, 0, 0), colorIfFalse=(0, 1, 1),
                                   outColor=(blend_matrix.target[i].weight, None, None))

    mult_matrix = node_utils.multMatrix(matrixIn=(blend_matrix.outputMatrix, target.parentInverseMatrix))

    decomp = node_utils.decomposeMatrix(inputMatrix=mult_matrix.matrixSum)
    if translate:
        decomp.outputTranslate.connect(target.translate, f=1)
    if rotate:
        decomp.outputRotate.connect(target.rotate, f=1)
    if scale:
        decomp.outputScale.connect(target.scale, f=1)
