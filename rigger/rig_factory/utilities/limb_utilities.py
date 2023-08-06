import Snowman3.rigger.rig_factory as rig_factory
from Snowman3.rigger.rig_factory.objects.node_objects.depend_node import DependNode
from Snowman3.rigger.rig_factory.objects.node_objects.locator import Locator
from Snowman3.rigger.rig_factory.objects.node_objects.mesh import Mesh
from Snowman3.rigger.rig_factory.objects.node_objects.transform import Transform
import Snowman3.rigger.rig_math.utilities as rmu
import Snowman3.rigger.rig_factory.environment as env

SIDE_SCALE = 's{0}'.format(env.side_vector_axis['left'][-1])  # scale attribute to scale for squash and stretch
AXES = ['x', 'y', 'z']
AXES.remove(env.side_vector_axis['left'][-1])
AXES.remove(env.aim_vector_axis[-1])
FRONT_SCALE = 's{0}'.format(AXES[0])  # scale attribute to scale for squash and stretch


def generate_squash_and_stretch_based_on_curve_length(curve_info_node,
                                                      joints,
                                                      attr_object,
                                                      attr_label='stretch_multiplier',
                                                      scale_axis_side=SIDE_SCALE,
                                                      scale_axis_front=FRONT_SCALE,
                                                      ):
    root = attr_object.hierarchy_parent.get_root()
    stretch_multiplier_plug = attr_object.create_plug(attr_label, at='double', k=True, dv=1, min=0, max=10)
    root.add_plugs([stretch_multiplier_plug])

    default_length = curve_info_node.plugs['arcLength'].get_value()

    squash_ratio = joints[0].create_child(
        DependNode,
        node_type='multiplyDivide',
        segmentName='squashRatio'
    )
    squash_ratio.plugs['input1X'].set_value(default_length)  # default length
    squash_ratio.plugs['operation'].set_value(2)  # divide by
    curve_info_node.plugs['arcLength'].connect_to(squash_ratio.plugs['input2X'])  # live length

    stretch_ratio = joints[0].create_child(
        DependNode,
        node_type='multiplyDivide',
        segmentName='stretchRatio'
    )
    stretch_ratio.plugs['input1X'].set_value(default_length)  # default length
    stretch_ratio.plugs['operation'].set_value(2)  # divide by
    curve_info_node.plugs['arcLength'].connect_to(stretch_ratio.plugs['input2X'])  # live length

    first_half_len = len(joints) / 2
    squash_first_half_multiplier = rmu.calculate_in_between_weights(first_half_len)
    squash_last_half_multiplier = rmu.calculate_in_between_weights(len(joints) - first_half_len)[::-1]
    squash_multiplier_values = rmu.smooth_average_list_values(
        squash_first_half_multiplier + squash_last_half_multiplier)
    for i, (joint, blend_weight) in enumerate(zip(joints, squash_multiplier_values)):
        index_character = rig_factory.index_dictionary[i].title()
        squash_blend = joints[0].create_child(
            DependNode,
            node_type='blendColors',
            segment_name='squashBlender%s' % index_character
        )
        squash_blend.plugs['color2R'].set_value(1)
        squash_blend.plugs['blender'].set_value(blend_weight)
        squash_ratio.plugs['outputX'].connect_to(squash_blend.plugs['color1R'])

        stretch_blend = joints[0].create_child(
            DependNode,
            node_type='blendColors',
            segment_name='stretchBlend%s' % index_character

        )
        stretch_blend.plugs['color2R'].set_value(1)
        stretch_blend.plugs['blender'].set_value(blend_weight)
        stretch_ratio.plugs['outputX'].connect_to(stretch_blend.plugs['color1R'])

        squash_stretch_flip_cond = joint.create_child(
            DependNode,
            node_type='condition',
            segment_name='squashFlip%s' % index_character
        )
        stretch_ratio.plugs['outputX'].connect_to(squash_stretch_flip_cond.plugs['firstTerm'])  # if user attr
        squash_stretch_flip_cond.plugs['operation'].set_value(4)  # less than
        squash_stretch_flip_cond.plugs['secondTerm'].set_value(1)  # 1
        stretch_blend.plugs['outputR'].connect_to(squash_stretch_flip_cond.plugs['colorIfTrueR'])
        squash_blend.plugs['outputR'].connect_to(squash_stretch_flip_cond.plugs['colorIfFalseR'])

        multiplier = joints[0].create_child(
            DependNode,
            node_type='multiplyDivide',
            segment_name=f'multiplier{index_character}'
        )
        squash_stretch_flip_cond.plugs['outColorR'].connect_to(multiplier.plugs['input1X'])
        multiplier.plugs['operation'].set_value(3)
        stretch_multiplier_plug.connect_to(multiplier.plugs['input2X'])  # live length

        for axis in (scale_axis_side, scale_axis_front):
            multiplier.plugs['outputX'].connect_to(joint.plugs[axis])

    return [stretch_multiplier_plug]


def generate_squash_and_stretch_adjacent_distances(joints,
                                                   attr_object,
                                                   attr_label='volume_stretch',
                                                   scale_axis_side=SIDE_SCALE,
                                                   scale_axis_front=FRONT_SCALE,
                                                   default_value=1):
    """
    Converts mesh skinning joints to be able to squash and stretch. This system looks at the distance between its
    surrounding joint positions and scales itself based on those distances.
    NOTE: if applying to IK spline DO NOT include the last joint of the VERY last joing in the spline IK, go from first
    joint to second last. jointsList[:-1]

    :param joints: list() all the joints which will have the squash and stretch applied.
    :param attr_object: Object in your rig which the custom attributes will be applied.
    :param attr_label: str() Text label for the stretch custom attribute.
    :param scale_axis_side: str() Attr string for which attribute to scale up when stretching and scale down for
    squashing.
    :param scale_axis_front: str() Attr string for which attribute to scale up when stretching and scale down for
    squashing.
    :param default_value: float() Default value of the custom attribute, default is 1 for on.
    """
    root_name = joints[0].root_name

    stretchable_weight_plug = attr_object.create_plug(
        '{0}_weight'.format(attr_label),
        at='double',
        k=True,
        dv=1,
        min=0,
        max=1)  # 1 for stretchable, 0 for not stretchable

    stretchable_plug = attr_object.create_plug(
        attr_label,
        at='double',
        k=True,
        dv=default_value,
        min=0,
        max=10)  # 1 for stretchable, 0 for not stretchable

    position_locators = []
    for i, jnt in enumerate(joints):
        pos = jnt.create_child(Locator, root_name='{0}_distancePosition'.format(root_name), index=i)
        position_locators.append(pos)

    distance_nodes = []
    for i in range(len(position_locators) - 1):
        distance_between_node = position_locators[i].create_child(
            DependNode,
            node_type='distanceBetween',
            root_name=f'{root_name}_distanceBetween',
            index=i)
        position_locators[i].plugs['worldPosition'].element(0).connect_to(distance_between_node.plugs['point1'])
        position_locators[i + 1].plugs['worldPosition'].element(0).connect_to(distance_between_node.plugs['point2'])
        distance_nodes.append(distance_between_node)

    for i, jnt in enumerate(joints[1:]):
        default_distance = distance_nodes[i].plugs['distance'].get_value()

        # stretchable weight blend node
        stretchable_weight = joints[0].create_child(
            DependNode,
            node_type='blendColors',
            root_name='{0}_stretchableWeight{1:03d}'.format(root_name, i),
            index=i)
        stretchable_weight.plugs['color2R'].set_value(1.0)
        stretchable_weight_plug.connect_to(stretchable_weight.plugs['blender'])

        if not (default_distance <= 0.0001 and default_distance >= -0.0001):
            distance_ratio = jnt.create_child(
                DependNode,
                node_type='multiplyDivide',
                root_name='%s_distanceRatio' % root_name,
                index=i
            )
            distance_ratio.plugs['input1X'].set_value(default_distance)  # default distance
            distance_ratio.plugs['operation'].set_value(2)  # divide by
            distance_nodes[i].plugs['distance'].connect_to(distance_ratio.plugs['input2X'])  # live distance

            stretch_add = jnt.create_child(
                DependNode,
                node_type='plusMinusAverage',
                root_name='%s_stretchAdd' % root_name,
                index=i
            )
            distance_ratio.plugs['outputX'].connect_to(stretch_add.plugs['input1D'].element(0))  # live distance
            stretch_add.plugs['operation'].set_value(1)  # add by
            stretchable_plug.connect_to(stretch_add.plugs['input1D'].element(1))

            stretch_add.plugs['output1D'].connect_to(stretchable_weight.plugs['color1R'])

            stretchable_weight.plugs['outputR'].connect_to(jnt.plugs[scale_axis_side])
            stretchable_weight.plugs['outputR'].connect_to(jnt.plugs[scale_axis_front])
        else:
            stretch_add.plugs['output1D'].connect_to(stretchable_weight.plugs['color1R'])

            stretchable_weight.plugs['outputR'].connect_to(jnt.plugs[scale_axis_side])
            stretchable_weight.plugs['outputR'].connect_to(jnt.plugs[scale_axis_front])

    root = attr_object.hierarchy_parent.get_root()
    root.add_plugs([stretchable_weight_plug, stretchable_plug])


def generate_squash_and_stretch_lite(joints,
                                     attr_object,
                                     attr_labels=None,
                                     attr_labels_suffix='volume_stretch',
                                     default_value=0.0,
                                     scale_axis_side=SIDE_SCALE,
                                     scale_axis_front=FRONT_SCALE,
                                     anchor_handles=None,
                                     inherit_scale_on_last_chain=False):
    """
    Converts mesh skinning joints to be able to squash and stretch. It works best if there are same amount of skin
    joints between every control control provided(anchor_handles). This system works by looking at the distances
    between the provided controls in the anchor_handles, and evenly distributes that distance between the in between
    joints, provided in the joints arg.
    Note: This also works best with the convert_ik_to_stretchable function in the limb utils.

    :param joints: list() all the joints which will have the squash and stretch applied.
    :param attr_object: Object in your rig which the custom attributes will be applied.
    :param attr_labels: list(str) List of strings of the limb "bone" which will be on the custom attributes.
    Example: ['biceot', 'forearm'] or ['thigh', 'shin'] etc.
    Note: Make sure this list has the length one less longer than the attr_labels list
    together.
    :param attr_labels_suffix: str() the suffix string that comes after every attr_labels arg.
    :param default_value: float() Default value of the custom attribute, default is 1 for on.
    :param scale_axis_side: str() Attr string for which attribute to scale up when stretching and scale down for
    squashing.
    :param scale_axis_front: str() Attr string for which attribute to scale up when stretching and scale down for
    squashing.
    :param anchor_handles: list() List of rig handles(controls) that the code will use to measure the distances between
    for the squash and stretch.
    Note: Make sure this list has the length one more longer than the attr_labels list
    :param inherit_scale_on_last_chain: bool() For something like the leg, where the squash and stretch goes to the toe,
    setting this arg to True, the last chain(Toe) will inherit whatever scale is coming out of the second last joint
    (foot).
    """
    if len(anchor_handles) - 1 != len(attr_labels):
        raise Exception(
            'Make sure the attr_labels list has the length 1 less than the anchor_handles list. For example, attr_labels=["thigh", "shin"], anchor_handles[jointA, jointB, jointC]')

    root_name = joints[0].root_name

    # linear falloff
    length_of_one_segment = len(joints) / (len(anchor_handles) - 1)
    linear_values = [0.0 for i in range(length_of_one_segment * (len(anchor_handles) - 1))]
    list_start_linear = [i * (1.0 / (length_of_one_segment - 1)) for i in range(length_of_one_segment)]
    list_end_linear = list_start_linear[::-1]
    linear_values[:length_of_one_segment] = list_end_linear
    if inherit_scale_on_last_chain:
        linear_values[-length_of_one_segment:] = list_end_linear  # Tapers small to large at last chain
    else:
        linear_values[-length_of_one_segment:] = list_start_linear  # Tapers large to small at last chain

    # smoothed list
    smoothed_values = linear_values

    # break from anchor indicies
    anchor_indicies = [i * length_of_one_segment for i in range(len(anchor_handles))]
    chains = []
    last_index = anchor_indicies[0]
    for index in anchor_indicies[1:]:
        chains.append(joints[last_index:index])
        last_index = index
    output_nodes = []
    for i, chain in enumerate(chains):
        distance_node = create_distance_between(anchor_handles[i],
                                                anchor_handles[i + 1])  # TODO: fix broken function..?
        default_distance = distance_node.plugs['distance'].get_value()

        distance_ratio = joints[0].create_child(DependNode,
                                                node_type='multiplyDivide',
                                                root_name='%s_defaultDistanceRatio' % root_name,
                                                index=i)
        distance_node.plugs['distance'].connect_to(distance_ratio.plugs['input1X'])  # live length
        distance_ratio.plugs['operation'].set_value(2)  # divide by
        distance_ratio.plugs['input2X'].set_value(default_distance)  # default distance

        squash_and_stretch_offset = joints[0].create_child(DependNode,
                                                           node_type='multiplyDivide',
                                                           root_name='%s_chainSquashAndStretchOffset' % root_name,
                                                           index=i)
        squash_and_stretch_offset.plugs['input1X'].set_value(1)
        squash_and_stretch_offset.plugs['operation'].set_value(2)  # divide by
        distance_ratio.plugs['outputX'].connect_to(squash_and_stretch_offset.plugs['input2X'])  # live length ratio

        output_nodes.append({'node': squash_and_stretch_offset, 'chain': chain})

    joint_index = 0
    last_stretch_add = None
    for i, data in enumerate(output_nodes):
        stretchable_weight_plug = attr_object.create_plug(
            '{0}_{1}_weight'.format(attr_labels[i], attr_labels_suffix),
            at='double',
            k=True,
            dv=1,
            min=0,
            max=1)  # 1 for stretchable, 0 for not stretchable
        stretchable_plug = attr_object.create_plug(
            '{0}_{1}'.format(attr_labels[i], attr_labels_suffix),
            at='double',
            k=True,
            dv=default_value,
            min=-10,
            max=10)  # 1 for stretchable, 0 for not stretchable
        for j, jnt in enumerate(data['chain']):
            # blend
            per_joint_blend = joints[0].create_child(DependNode,
                                                     node_type='blendColors',
                                                     root_name='{0}_perJointBlend{1:03d}'.format(root_name, j),
                                                     index=i)
            per_joint_blend.plugs['color1R'].set_value(1.0)
            data['node'].plugs['outputX'].connect_to(per_joint_blend.plugs['color2R'])
            per_joint_blend.plugs['blender'].set_value(smoothed_values[joint_index])
            joint_index += 1

            stretch_add = joints[0].create_child(DependNode,
                                                 node_type='plusMinusAverage',
                                                 root_name='{0}_stretchAdd{1:03d}'.format(root_name, j),
                                                 index=i)
            per_joint_blend.plugs['outputR'].connect_to(stretch_add.plugs['input1D'].element(0))  # blend result output
            stretch_add.plugs['operation'].set_value(1)  # add by
            stretchable_plug.connect_to(stretch_add.plugs['input1D'].element(1))  # stretchable attribute

            # stretchable weight blend node
            stretchable_weight = joints[0].create_child(DependNode,
                                                        node_type='blendColors',
                                                        root_name='{0}_stretchableWeight{1:03d}'.format(root_name,
                                                                                                        j),
                                                        index=i)
            stretchable_weight.plugs['color2R'].set_value(1.0)
            stretchable_weight_plug.connect_to(stretchable_weight.plugs['blender'])

            if inherit_scale_on_last_chain and i == len(output_nodes) - 1:  # inherit scale to True and last chain
                inherit_scale = joints[0].create_child(DependNode,
                                                       node_type='multiplyDivide',
                                                       root_name='{0}_inheritScale{1:03d}'.format(root_name, j),
                                                       index=i)
                last_stretch_add.plugs['output1D'].connect_to(inherit_scale.plugs['input1X'])
                inherit_scale.plugs['operation'].set_value(1)  # multiply by
                stretch_add.plugs['output1D'].connect_to(inherit_scale.plugs['input2X'])

                inherit_scale.plugs['outputX'].connect_to(stretchable_weight.plugs['color1R'])

                stretchable_weight.plugs['outputR'].connect_to(jnt.plugs[scale_axis_side])
                stretchable_weight.plugs['outputR'].connect_to(jnt.plugs[scale_axis_front])
            elif i == len(output_nodes) - 1:  # inherit scale to False last chain
                last_stretch_add = stretch_add

                stretch_add.plugs['output1D'].connect_to(stretchable_weight.plugs['color1R'])

                stretchable_weight.plugs['outputR'].connect_to(jnt.plugs[scale_axis_side])
                stretchable_weight.plugs['outputR'].connect_to(jnt.plugs[scale_axis_front])
            else:  # every other joint other than last joint
                last_stretch_add = stretch_add

                stretch_add.plugs['output1D'].connect_to(stretchable_weight.plugs['color1R'])

                stretchable_weight.plugs['outputR'].connect_to(jnt.plugs[scale_axis_side])
                stretchable_weight.plugs['outputR'].connect_to(jnt.plugs[scale_axis_front])

        root = attr_object.hierarchy_parent.get_root()
        root.add_plugs([stretchable_weight_plug, stretchable_plug])


def create_stretchy_ik_joints(nurbs_curve, joints, side):
    """
    Converts your IK spline to be stretchable(joints, evenly spaced). This function does not generate a custom attribute
    for blending on and off the stretching. Possible future development could add the custom attribute, but as of the
    moment, we do not have a use for it.
    :param nurbs_curve: Nurbs curve object to measure the length from.
    :param joints: list(), Joints to set translation on for the stretching.
    :param side: str(), 'left', 'right', or 'center'
    :return:
    """
    root_name = nurbs_curve.root_name

    # create arclen node
    curve_info = nurbs_curve.create_child(DependNode,
                                          root_name='%s_curveInfo' % root_name,
                                          node_type='curveInfo')
    nurbs_curve.plugs['worldSpace'].element(0).connect_to(curve_info.plugs['inputCurve'])

    # divide arc length evenly between the joint translate
    arm_length_divide = nurbs_curve.create_child(DependNode,
                                                 root_name='%s_curveLengthDivide' % root_name,
                                                 node_type='multiplyDivide')
    curve_info.plugs['arcLength'].connect_to(arm_length_divide.plugs['input1'].child(0))  # live arc length
    arm_length_divide.plugs['operation'].set_value(2)  # divide by
    arm_length_divide.plugs['input2X'].set_value(
        (len(joints) - 1) * -1 if side == 'right' else len(joints) - 1)  # divide by number of joints

    for i, joint in enumerate(joints):  # enumerate for now, http://youtrack.icon.local:8585/issue/PAX-1086
        if i != 0 and i != len(joints) - 1:
            arm_length_divide.plugs['outputX'].connect_to(joint.plugs['t{0}'.format(env.aim_vector_axis)])

    arm_length_divide.plugs['outputX'].connect_to(joints[-1].plugs['t{0}'.format(env.aim_vector_axis)])

    return [curve_info, arm_length_divide]


def convert_ik_to_stretchable(part, start_transform, end_transform, joints, attribute_handle):
    """
    Converts your IK limb to be stretchable joints This function also generates the custom attribute
    for blending on and off the stretching/softIK.
    :param start_transform:
        Root control which it will get the transforms data from.
    :param end_transform:
        Tip(AKA effector) control which it will get the transforms data from.
    :param joints: list(),
        Joints from your IK rig
    :param attribute_handle: Handle,
        the handle on which to put the attrubutes
    """

    root = part.get_root()
    total_length = 0.0
    for i, joint in enumerate(joints):
        if i > 0:
            length = (joint.get_translation() - joints[i - 1].get_translation()).mag()
            total_length += length

    auto_stretch_plug = attribute_handle.create_plug(
        'auto_stretch',
        at='double',
        dv=1.0,
        k=True,
        min=0,
        max=1
    )
    soft_ik_plug = attribute_handle.create_plug(
        'soft_ik',
        at='double',
        dv=1.0,
        k=True,
        min=0,
        max=1
    )
    length_plug = attribute_handle.create_plug(
        'length',
        at='double',
        dv=0.0,
        k=True
    )
    orig_length_plug = attribute_handle.create_plug(
        'orig_length',
        at='double',
        dv=total_length
    )
    root.add_plugs(
        auto_stretch_plug,
        soft_ik_plug,
        length_plug,
        keyable=True
    )
    distance_node = part.create_child(
        DependNode,
        node_type='distanceBetween',
        segment_name='Stretch'
    )
    start_locator = start_transform.create_child(
        Locator,
        segment_name='StartPosition'
    )
    end_locator = end_transform.create_child(
        Locator,
        segment_name='EndPosition'
    )
    start_locator.plugs['worldPosition'].element(0).connect_to(distance_node.plugs['point1'])
    end_locator.plugs['worldPosition'].element(0).connect_to(distance_node.plugs['point2'])

    length_add = start_transform.create_child(
        DependNode,
        node_type='plusMinusAverage',
        segment_name='StretchLength'
    )
    auto_multiply = start_transform.create_child(
        DependNode,
        node_type='multiplyDivide',
        segment_name='Auto'
    )
    scale_divide = start_transform.create_child(
        DependNode,
        node_type='multiplyDivide',
        segment_name='Scale'
    )
    # This is to calculate the percentage of length compared to fully stretched
    percent_length = start_transform.create_child(
        DependNode,
        node_type='multiplyDivide',
        segment_name='PercentLength'
    )
    scale_divide.plugs['operation'].set_value(2)
    distance_node.plugs['distance'].connect_to(scale_divide.plugs['input1X'])
    part.scale_multiply_transform.plugs['sy'].connect_to(scale_divide.plugs['input2X'])

    # This remap is for the scaling and works even though it overshoots the min/max values
    remap_out_plug = scale_divide.plugs['outputX'].remap(
        (
            total_length,
            0.0
        ),
        (
            (10000.0 * part.size) + total_length,
            (10000.0 * part.size)
        )
    )

    # This remap is for the soft_ik
    soft_remap = part.create_child(
        DependNode,
        node_type='remapValue',
        segment_name='Soft'
    )

    start_distance = distance_node.plugs['distance'].get_value()
    distance_to_lock = total_length - start_distance

    percent_length.plugs['operation'].set_value(2)
    percent_length.plugs['input2X'].set_value((total_length + distance_to_lock))
    scale_divide.plugs['outputX'].connect_to(percent_length.plugs['input1X'])

    soft_remap.plugs['value'].element(0).child(0).set_value((total_length / ((total_length + distance_to_lock))))
    soft_remap.plugs['value'].element(0).child(1).set_value(0.0)
    soft_remap.plugs['value'].element(0).child(2).set_value(2)

    soft_remap.plugs['value'].element(1).child(0).set_value(1)
    soft_ik_plug.multiply(distance_to_lock).connect_to(soft_remap.plugs['value'].element(1).child(1))

    percent_length.plugs['outputX'].connect_to(soft_remap.plugs['inputValue'])

    length_add.plugs['input1D'].element(0).set_value(total_length)
    remap_out_plug.connect_to(auto_multiply.plugs['input1X'])
    auto_stretch_plug.connect_to(auto_multiply.plugs['input2X'])
    auto_multiply.plugs['outputX'].connect_to(length_add.plugs['input1D'].element(1))
    soft_remap.plugs['outValue'].connect_to(length_add.plugs['input1D'].element(2))
    length_plug.connect_to(length_add.plugs['input1D'].element(3))

    for j in range(len(joints)):
        if j != 0:
            joint = joints[j]
            length = (joint.get_translation() - joints[j - 1].get_translation()).mag()
            joint_length_multiply = joints[j].create_child(
                DependNode,
                node_type='multDoubleLinear',
                segment_name='%sStretch' % joint.segment_name
            )
            length_add.plugs['output1D'].connect_to(joint_length_multiply.plugs['input1'])
            if part.side == 'right':
                segment_ratio = length / total_length * -1.0
            else:
                segment_ratio = length / total_length
            joint_length_multiply.plugs['input2'].set_value(segment_ratio)
            joint_length_multiply.plugs['output'].connect_to(joint.plugs['ty'])


def convert_ik_to_stretchable_two_segments(part, start_ctrl, pv_ctrl, end_ctrl, ikh, joints,
                                           global_scale_plug, lock_plug_name='lockKnee',
                                           stretchMode='translate'):
    # full_dist_node
    full_dist_node = part.create_child(
        DependNode,
        node_type='distanceBetween',
        segment_name='FullDist'
    )
    start_ctrl.plugs['worldMatrix'][0].connect_to(full_dist_node.plugs['inMatrix1'])
    ikh.parent.plugs['worldMatrix'][0].connect_to(full_dist_node.plugs['inMatrix2'])

    # joints
    if len(joints) != 3:
        raise Exception(
            'limb_utilities.convert_ik_to_stretchable_two_segments expects 3 joints only, eg: Hip, Knee, Ankle!')

    hip_jnt = joints[0]
    knee_jnt = joints[1]
    ankle_jnt = joints[2]

    # segment joints lengths
    limb_1_length = (hip_jnt.get_translation() - knee_jnt.get_translation()).mag()
    limb_2_length = (knee_jnt.get_translation() - ankle_jnt.get_translation()).mag()

    # length of both segments
    total_length = limb_1_length + limb_2_length

    # attrs
    soft_dist_plug = end_ctrl.create_plug(
        'soft_ik',
        at='double',
        k=True,
        dv=0.0,
        min=0.0,
    )
    stretch_plug = end_ctrl.create_plug(
        'auto_stretch',
        at='double',
        k=True,
        dv=1,
        min=0,
        max=1,
    )
    lock_knee_plug = end_ctrl.create_plug(
        lock_plug_name,
        at='double',
        k=True,
        min=0,
        max=1,
    )
    full_len_plug = end_ctrl.create_plug(
        'length',
        at='double',
        k=True,
    )
    limb1_len_plug = end_ctrl.create_plug(
        'lengthA',
        at='double',
        k=True,
    )
    limb2_len_plug = end_ctrl.create_plug(
        'lengthB',
        at='double',
        k=True,
    )
    part.get_root().add_plugs(
        soft_dist_plug,
        stretch_plug,
        lock_knee_plug,
        full_len_plug,
        limb1_len_plug,
        limb2_len_plug,
        keyable=True
    )

    # full len
    full_len_pma = part.create_child(
        DependNode,
        node_type='plusMinusAverage',
        segment_name='FullDefaultLen'
    )
    full_len_pma.plugs['input1D'][0].set_value(total_length)
    full_len_plug.connect_to(full_len_pma.plugs['input1D'][1])
    limb1_len_plug.connect_to(full_len_pma.plugs['input1D'][2])
    limb2_len_plug.connect_to(full_len_pma.plugs['input1D'][3])

    # soft_dist
    soft_dist = part.create_child(
        DependNode,
        node_type='plusMinusAverage',
        segment_name='SoftDist'
    )
    soft_dist.plugs['operation'].set_value(2)
    full_len_pma.plugs['output1D'].connect_to(soft_dist.plugs['input1D'][0])
    soft_dist_plug.connect_to(soft_dist.plugs['input1D'][1])

    # global_scale
    global_scale = part.create_child(
        DependNode,
        node_type='multiplyDivide',
        segment_name='GlobalScale'
    )
    global_scale.plugs['operation'].set_value(2)
    full_dist_node.plugs['distance'].connect_to(global_scale.plugs['input1X'])
    global_scale_plug.connect_to(global_scale.plugs['input2X'])

    # dist_minus_soft_dist
    dist_minus_soft_dist = part.create_child(
        DependNode,
        node_type='plusMinusAverage',
        segment_name='DistMinusSoftDist'
    )
    dist_minus_soft_dist.plugs['operation'].set_value(2)
    global_scale.plugs['outputX'].connect_to(dist_minus_soft_dist.plugs['input1D'][0])
    soft_dist.plugs['output1D'].connect_to(dist_minus_soft_dist.plugs['input1D'][1])

    # neg_soft_dist
    neg_soft_dist = part.create_child(
        DependNode,
        node_type='multiplyDivide',
        segment_name='NegMinusSoftDist'
    )
    neg_soft_dist.plugs['input2X'].set_value(-1)
    dist_minus_soft_dist.plugs['output1D'].connect_to(neg_soft_dist.plugs['input1X'])

    # clamp soft_ik value to not go less than 0.0001
    soft_clamp = part.create_child(
        DependNode,
        node_type='clamp',
        segment_name='SoftValueClamp'
    )
    soft_clamp.plugs['minR'].set_value(0.0001)
    soft_clamp.plugs['maxR'].set_value(999999)
    soft_dist_plug.connect_to(soft_clamp.plugs['inputR'])

    # div_by_soft
    div_by_soft = part.create_child(
        DependNode,
        node_type='multiplyDivide',
        segment_name='DivBySoft'
    )
    div_by_soft.plugs['operation'].set_value(2)
    neg_soft_dist.plugs['outputX'].connect_to(div_by_soft.plugs['input1X'])
    soft_clamp.plugs['outputR'].connect_to(div_by_soft.plugs['input2X'])

    # exponent
    exponent = part.create_child(
        DependNode,
        node_type='multiplyDivide',
        segment_name='Exponent'
    )
    exponent.plugs['operation'].set_value(3)
    exponent.plugs['input1X'].set_value(2.71828)
    div_by_soft.plugs['outputX'].connect_to(exponent.plugs['input2X'])

    # one_minus_exponent
    one_minus_exponent = part.create_child(
        DependNode,
        node_type='plusMinusAverage',
        segment_name='OneMinusExponent'
    )
    one_minus_exponent.plugs['operation'].set_value(2)
    one_minus_exponent.plugs['input1D'][0].set_value(1)
    exponent.plugs['outputX'].connect_to(one_minus_exponent.plugs['input1D'][1])

    # soft_times_soft_dist
    soft_times_soft_dist = part.create_child(
        DependNode,
        node_type='multiplyDivide',
        segment_name='SoftTimesSoftDist'
    )
    soft_dist_plug.connect_to(soft_times_soft_dist.plugs['input1X'])
    one_minus_exponent.plugs['output1D'].connect_to(soft_times_soft_dist.plugs['input2X'])

    # soft_plus_soft_dist
    soft_plus_soft_dist = part.create_child(
        DependNode,
        node_type='plusMinusAverage',
        segment_name='SoftPlusSoftDist'
    )
    soft_dist.plugs['output1D'].connect_to(soft_plus_soft_dist.plugs['input1D'][0])
    soft_times_soft_dist.plugs['outputX'].connect_to(soft_plus_soft_dist.plugs['input1D'][1])

    # stretch_condition
    stretch_condition = part.create_child(
        DependNode,
        node_type='condition',
        segment_name='Stretch'
    )
    global_scale.plugs['outputX'].connect_to(stretch_condition.plugs['firstTerm'])
    soft_dist.plugs['output1D'].connect_to(stretch_condition.plugs['secondTerm'])
    stretch_condition.plugs['operation'].set_value(5)
    global_scale.plugs['outputX'].connect_to(stretch_condition.plugs['colorIfTrueR'])
    soft_plus_soft_dist.plugs['output1D'].connect_to(stretch_condition.plugs['colorIfFalseR'])

    # ik_move_amount
    ik_move_amount = part.create_child(
        DependNode,
        node_type='plusMinusAverage',
        segment_name='IkMoveAmount'
    )
    ik_move_amount.plugs['operation'].set_value(2)
    global_scale.plugs['outputX'].connect_to(ik_move_amount.plugs['input1D'][0])
    stretch_condition.plugs['outColorR'].connect_to(ik_move_amount.plugs['input1D'][1])

    # stretch attr reverse
    stretch_attr_rev = part.create_child(
        DependNode,
        node_type='reverse',
        segment_name='StretchAttr'
    )
    stretch_plug.connect_to(stretch_attr_rev.plugs['inputX'])

    # ik_move_switch
    ik_move_switch = part.create_child(
        DependNode,
        node_type='blendTwoAttr',
        segment_name='IkMoveSwtich'
    )
    ik_move_switch.plugs['input'][1].set_value(0)
    ik_move_amount.plugs['output1D'].connect_to(ik_move_switch.plugs['input'][1])
    stretch_attr_rev.plugs['outputX'].connect_to(ik_move_switch.plugs['attributesBlender'])

    # aim ikh
    part.controller.create_aim_constraint(
        start_ctrl,
        ikh.parent,
        aimVector=[0, 1, 0],
        upVector=[1, 0, 0],
        worldUpObject=ikh.parent.parent,
        worldUpType='objectRotation',
        worldUpVector=[1.0, 0.0, 0.0]
    )

    # stretch joints
    # ==========

    # soft_ratio
    soft_ratio = part.create_child(
        DependNode,
        node_type='multiplyDivide',
        segment_name='SoftRatio'
    )
    soft_ratio.plugs['operation'].set_value(2)
    global_scale.plugs['outputX'].connect_to(soft_ratio.plugs['input1X'])
    stretch_condition.plugs['outColorR'].connect_to(soft_ratio.plugs['input2X'])

    # stretch
    stretch = part.create_child(
        DependNode,
        node_type='blendTwoAttr',
        segment_name='Stretch'
    )
    stretch.plugs['input'][0].set_value(1)
    soft_ratio.plugs['outputX'].connect_to(stretch.plugs['input'][1])
    stretch_plug.connect_to(stretch.plugs['attributesBlender'])

    # limb len ratio
    limbs_len_ratio = part.create_child(
        DependNode,
        node_type='multiplyDivide',
        segment_name='LimbsLengthRatio'
    )
    limbs_len_ratio.plugs['operation'].set_value(2)
    limb1_len_plug.connect_to(limbs_len_ratio.plugs['input1X'])
    limb2_len_plug.connect_to(limbs_len_ratio.plugs['input1Y'])
    full_len_plug.connect_to(limbs_len_ratio.plugs['input1Z'])
    limbs_len_ratio.plugs['input2X'].set_value(limb_1_length)
    limbs_len_ratio.plugs['input2Y'].set_value(limb_2_length)
    limbs_len_ratio.plugs['input2Z'].set_value(total_length)

    # User Added Lengths (limb1 length + limb2 length + length attributes)
    user_added_lengths = part.create_child(
        DependNode,
        node_type='plusMinusAverage',
        segment_name='UserAddedLengths'
    )
    limbs_len_ratio.plugs['outputX'].connect_to(user_added_lengths.plugs['input3D'][0][0])
    limbs_len_ratio.plugs['outputY'].connect_to(user_added_lengths.plugs['input3D'][0][1])
    limbs_len_ratio.plugs['outputZ'].connect_to(user_added_lengths.plugs['input3D'][1][0])
    limbs_len_ratio.plugs['outputZ'].connect_to(user_added_lengths.plugs['input3D'][1][1])

    # convert stretch values from scale to length change
    scale_ratio_to_length_change = part.create_child(
        DependNode,
        node_type='multiplyDivide',
        segment_name='ScaleRatioToLengthChange'
    )
    user_added_lengths.plugs['output3Dx'].connect_to(scale_ratio_to_length_change.plugs['input2X'])
    user_added_lengths.plugs['output3Dy'].connect_to(scale_ratio_to_length_change.plugs['input2Y'])
    stretch.plugs['output'].connect_to(scale_ratio_to_length_change.plugs['input1X'])
    stretch.plugs['output'].connect_to(scale_ratio_to_length_change.plugs['input1Y'])

    # add automated stretch value + manual stretches added by user
    mix_of_auto_and_manual_stretch = part.create_child(
        DependNode,
        node_type='plusMinusAverage',
        segment_name='MixOfAutoAndManualStretch'
    )
    scale_ratio_to_length_change.plugs['outputX'].connect_to(mix_of_auto_and_manual_stretch.plugs['input3D'][0][0])
    scale_ratio_to_length_change.plugs['outputY'].connect_to(mix_of_auto_and_manual_stretch.plugs['input3D'][0][1])
    stretch.plugs['output'].connect_to(mix_of_auto_and_manual_stretch.plugs['input3D'][1][0])
    stretch.plugs['output'].connect_to(mix_of_auto_and_manual_stretch.plugs['input3D'][1][1])

    # lock pv
    # ==========

    # limb_1_dist
    limb_1_dist = part.create_child(
        DependNode,
        node_type='distanceBetween',
        segment_name='SegADist'
    )
    start_ctrl.plugs['worldMatrix'][0].connect_to(limb_1_dist.plugs['inMatrix1'])
    pv_ctrl.plugs['worldMatrix'][0].connect_to(limb_1_dist.plugs['inMatrix2'])

    # limb_1_global_scaled
    limb_1_global_scaled = part.create_child(
        DependNode,
        node_type='multiplyDivide',
        segment_name='SegAGlobalScaled'
    )
    limb_1_global_scaled.plugs['operation'].set_value(2)
    limb_1_dist.plugs['distance'].connect_to(limb_1_global_scaled.plugs['input1X'])
    global_scale_plug.connect_to(limb_1_global_scaled.plugs['input2X'])

    # limb2Dist
    limb_2_dist = part.create_child(
        DependNode,
        node_type='distanceBetween',
        segment_name='SegBDist'
    )
    pv_ctrl.plugs['worldMatrix'][0].connect_to(limb_2_dist.plugs['inMatrix1'])
    ikh.parent.plugs['worldMatrix'][0].connect_to(limb_2_dist.plugs['inMatrix2'])

    # limb_2_global_scaled
    limb_2_global_scaled = part.create_child(
        DependNode,
        node_type='multiplyDivide',
        segment_name='SegBGlobalScaled'
    )
    limb_2_global_scaled.plugs['operation'].set_value(2)
    limb_2_dist.plugs['distance'].connect_to(limb_2_global_scaled.plugs['input1X'])
    global_scale_plug.connect_to(limb_2_global_scaled.plugs['input2X'])

    # limb_1_lock_length
    limb_1_lock_length = part.create_child(
        DependNode,
        node_type='multiplyDivide',
        segment_name='SegALockLength'
    )
    limb_1_lock_length.plugs['operation'].set_value(2)
    limb_1_global_scaled.plugs['outputX'].connect_to(limb_1_lock_length.plugs['input1X'])
    limb_1_lock_length.plugs['input2X'].set_value(limb_1_length)

    # limb_2_lock_length
    limb_2_lock_length = part.create_child(
        DependNode,
        node_type='multiplyDivide',
        segment_name='SegBLockLength'
    )
    limb_2_lock_length.plugs['operation'].set_value(2)
    limb_2_global_scaled.plugs['outputX'].connect_to(limb_2_lock_length.plugs['input1X'])
    limb_2_lock_length.plugs['input2X'].set_value(limb_2_length)

    # limb_1_lock_switch
    limb_1_lock_switch = part.create_child(
        DependNode,
        node_type='blendTwoAttr',
        segment_name='SegALockSwitch'
    )
    mix_of_auto_and_manual_stretch.plugs['output3Dx'].connect_to(limb_1_lock_switch.plugs['input'][0])
    limb_1_lock_length.plugs['outputX'].connect_to(limb_1_lock_switch.plugs['input'][1])
    lock_knee_plug.connect_to(limb_1_lock_switch.plugs['attributesBlender'])

    # limb_2_lock_switch
    limb_2_lock_switch = part.create_child(
        DependNode,
        node_type='blendTwoAttr',
        segment_name='SegBLockSwitch'
    )
    mix_of_auto_and_manual_stretch.plugs['output3Dy'].connect_to(limb_2_lock_switch.plugs['input'][0])
    limb_2_lock_length.plugs['outputX'].connect_to(limb_2_lock_switch.plugs['input'][1])
    lock_knee_plug.connect_to(limb_2_lock_switch.plugs['attributesBlender'])

    # connect pv lock stretch result
    connectStretch(
        part=part,
        stretchResultAttr=limb_1_lock_switch.plugs['output'],
        joints=[hip_jnt, knee_jnt],
        mode=stretchMode
    )

    connectStretch(
        part=part,
        stretchResultAttr=limb_2_lock_switch.plugs['output'],
        joints=[knee_jnt, ankle_jnt],
        mode=stretchMode
    )

    # no_soft_when_locked
    no_soft_when_locked = part.create_child(
        DependNode,
        node_type='multiplyDivide',
        segment_name='NoSoftWhenLock'
    )
    no_soft_when_locked.plugs['operation'].set_value(2)
    limb_2_global_scaled.plugs['outputX'].connect_to(no_soft_when_locked.plugs['input1X'])
    no_soft_when_locked.plugs['input2X'].set_value(limb_2_length)

    # lockPV attr reverse
    lock_pv_attr_rev = part.create_child(
        DependNode,
        node_type='reverse',
        segment_name='LockPVAttrRev'
    )
    lock_knee_plug.connect_to(lock_pv_attr_rev.plugs['inputX'])

    # no_ik_move_when_lock_pv
    no_ik_move_when_lock_pv = part.create_child(
        DependNode,
        node_type='blendTwoAttr',
        segment_name='NoIkMoveWhenLockPV'
    )
    no_ik_move_when_lock_pv.plugs['input'][0].set_value(0)
    ik_move_switch.plugs['output'].connect_to(no_ik_move_when_lock_pv.plugs['input'][1])
    lock_pv_attr_rev.plugs['outputX'].connect_to(no_ik_move_when_lock_pv.plugs['attributesBlender'])

    # ikMove towards upper limb to prevent sudden straightening of limbs
    no_ik_move_when_lock_pv.plugs['output'].connect_to(ikh.plugs['translateY'])


def setDriven(part, drvr, drvn, drvrValues, drvnValues,
              itt='spline', ott='spline', poi='cycleRelative', pri='cycleRelative'):
    for dv, v in zip(drvrValues, drvnValues):
        part.controller.scene.setDrivenKeyframe(drvn.name, cd=drvr.name, dv=dv, v=v, itt=itt, ott=ott)
    part.controller.scene.setInfinity(drvn.name, poi=poi, pri=pri)


def connectStretch(part, stretchResultAttr, joints, axes='y', mode='scale'):
    if mode == 'scale':
        stretchResultAttr.connect_to(joints[0].plugs['s' + axes])

    elif mode == 'translate':
        defaultDrivenVal = joints[1].plugs['t' + axes].get_value()
        setDriven(
            part=part,
            drvr=stretchResultAttr,
            drvn=joints[1].plugs['t' + axes],
            drvrValues=(1.0, 100),
            drvnValues=(defaultDrivenVal, defaultDrivenVal * 100)
        )


def make_ik_plane(part, start_handle, end_handle, up_handle):
    """
    Creates a poly plane that will keep the middle ik guide planar

    :return:
    """

    plane_transform = part.create_child(
        Transform,
        segment_name='LimbPlane'
    )

    plane_node = plane_transform.create_child(
        DependNode,
        node_type='polyPlane',
        segment_name='Plane'
    )

    plane_mesh = plane_transform.create_child(
        Mesh,
        segment_name='PlaneMesh'
    )

    start_decomp_matrix_node = plane_transform.create_child(
        DependNode,
        node_type='decomposeMatrix',
        segment_name='StartDecomposeMatrix'
    )

    end_decomp_matrix_node = plane_transform.create_child(
        DependNode,
        node_type='decomposeMatrix',
        segment_name='EndDecomposeMatrix'
    )

    up_decomp_matrix_node = plane_transform.create_child(
        DependNode,
        node_type='decomposeMatrix',
        segment_name='UpDecomposeMatrix'
    )

    # set plane attributes
    plane_node.plugs['subdivisionsWidth'].set_value(1)
    plane_node.plugs['subdivisionsHeight'].set_value(1)
    plane_node.plugs['width'].set_value(0.01)
    plane_node.plugs['height'].set_value(0.01)
    plane_transform.plugs['visibility'].set_value(0)

    # connect guides to plane
    plane_node.plugs['output'].connect_to(plane_mesh.plugs['inMesh'])
    start_handle.plugs['worldMatrix'].element(0).connect_to(start_decomp_matrix_node.plugs['inputMatrix'])
    start_decomp_matrix_node.plugs['outputTranslate'].connect_to(plane_mesh.plugs['pnts'].element(0))
    up_handle.plugs['worldMatrix'].element(0).connect_to(up_decomp_matrix_node.plugs['inputMatrix'])
    up_decomp_matrix_node.plugs['outputTranslate'].connect_to(plane_mesh.plugs['pnts'].element(1))
    end_handle.plugs['worldMatrix'].element(0).connect_to(end_decomp_matrix_node.plugs['inputMatrix'])
    end_decomp_matrix_node.plugs['outputTranslate'].connect_to(plane_mesh.plugs['pnts'].element(2))
    up_decomp_matrix_node.plugs['outputTranslate'].connect_to(plane_mesh.plugs['pnts'].element(3))

    part.limb_plane = plane_mesh

    # extrude and connect IK plane to up vector
    distance_node = part.create_child(
        DependNode,
        node_type='distanceBetween',
        segment_name='Offset'
    )

    poly_extrude_m_object = part.controller.scene.polyExtrudeEdge('{}.e[1]'.format(plane_mesh.name))

    poly_extrude_edge_node = part.create_child(
        DependNode,
        node_type='polyExtrudeEdge',
        segment_name='Offset',
        m_object=poly_extrude_m_object
    )

    start_handle.plugs['worldMatrix'].element(0).connect_to(distance_node.plugs['inMatrix1'])
    up_handle.plugs['worldMatrix'].element(0).connect_to(distance_node.plugs['inMatrix2'])
    distance_node.plugs['distance'].multiply(0.5).connect_to(poly_extrude_edge_node.plugs['offset'])
