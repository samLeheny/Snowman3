import math
import Snowman3.rigger.rig_factory as rig_factory
import Snowman3.rigger.rig_factory.environment as env
from Snowman3.rigger.rig_factory.objects.node_objects.joint import Joint
from Snowman3.rigger.rig_factory.objects.node_objects.locator import Locator
from Snowman3.rigger.rig_factory.objects.node_objects.dag_node import DagNode
from Snowman3.rigger.rig_factory.objects.node_objects.transform import Transform
from Snowman3.rigger.rig_factory.objects.node_objects.depend_node import DependNode
from Snowman3.rigger.rig_factory.objects.node_objects.nurbs_curve import NurbsCurve
import Snowman3.rigger.rig_factory.utilities.node_utilities.ik_handle_utilities as iks


def create_spline(
        base_joints,
        parent_group,
        utility_group,
        spline_matrices,
        settings_handle,
        scale_multiply_transform

):
    curve_degree = 3
    spline_joints = []
    spline_joint_parent = base_joints[0]
    driver_spline_joints = []
    driver_spline_joint_parent = base_joints[0]
    for i, matrix in enumerate(spline_matrices):
        segment_string = rig_factory.index_dictionary[i].title()
        spline_joint = spline_joint_parent.create_child(
            Joint,
            segment_name='Secondary%s' % segment_string,
            index=i,
            matrix=matrix
        )
        driver_spline_joint = driver_spline_joint_parent.create_child(
            Joint,
            segment_name='SecondaryDriver%s' % segment_string,
            functionality_name=None,
            index=i,
            matrix=matrix
        )
        # Connect driver to bind joints
        for attr in ['translate', 'rotate', 'scale', 'jointOrient']:
            driver_spline_joint.plugs[attr].connect_to(spline_joint.plugs[attr])

        if spline_joints:
            spline_joints[-1].plugs['scale'].connect_to(
                spline_joint.plugs['inverseScale'],
            )
        if driver_spline_joints:
            driver_spline_joints[-1].plugs['scale'].connect_to(
                driver_spline_joint.plugs['inverseScale'],
            )

        driver_spline_joint.zero_rotation()

        spline_joints.append(spline_joint)
        driver_spline_joints.append(driver_spline_joint)

        spline_joint_parent = spline_joint
        driver_spline_joint_parent = driver_spline_joint

        # hide secondary part joints
        driver_spline_joint.plugs['drawStyle'].set_value(2)

    curve_locators = []

    for joint in base_joints:
        blend_locator = joint.create_child(
            Locator
        )
        blend_locator.plugs['v'].set_value(0)
        curve_locators.append(blend_locator)

    positions = [[0.0, 0.0, 0.0]] * len(curve_locators)

    segment_name = '%sSpline' % parent_group.segment_name

    nurbs_curve_transform = parent_group.create_child(
        Transform,
        segment_name=segment_name
    )
    nurbs_curve = nurbs_curve_transform.create_child(
        NurbsCurve,
        degree=curve_degree,
        positions=positions
    )
    curve_info = nurbs_curve_transform.create_child(
        DependNode,
        node_type='curveInfo'
    )

    scale_divide = nurbs_curve_transform.create_child(
        DependNode,
        node_type='multiplyDivide'
    )
    scale_divide.plugs['operation'].set_value(2)
    curve_info.plugs['arcLength'].connect_to(scale_divide.plugs['input1X'])
    curve_info.plugs['arcLength'].connect_to(scale_divide.plugs['input1Y'])
    curve_info.plugs['arcLength'].connect_to(scale_divide.plugs['input1Z'])
    scale_multiply_transform.plugs['scale'].connect_to(scale_divide.plugs['input2'])
    length_divide = parent_group.create_child(
        DependNode,
        segment_name='%sLengthDivide' % segment_name,
        node_type='multiplyDivide'
    )
    scale_divide.plugs['output'].connect_to(length_divide.plugs['input1'])
    nurbs_curve_transform.plugs['visibility'].set_value(False)
    nurbs_curve_transform.plugs['inheritsTransform'].set_value(False)
    nurbs_curve.plugs['worldSpace'].element(0).connect_to(curve_info.plugs['inputCurve'])
    length_divide.plugs['operation'].set_value(2)
    length_divide.plugs['input2Y'].set_value(len(spline_matrices) - 1)
    for i, blend_locator in enumerate(curve_locators):
        blend_locator.plugs['worldPosition'].element(0).connect_to(
            nurbs_curve.plugs['controlPoints'].element(i)
        )
    rebuild_curve = nurbs_curve.create_child(
        DependNode,
        node_type='rebuildCurve'
    )
    rebuild_curve.plugs.set_values(
        keepRange=0,
        keepControlPoints=1,
    )
    nurbs_curve.plugs['worldSpace'].element(0).connect_to(
        rebuild_curve.plugs['inputCurve'],
    )
    nurbs_curve.plugs['degree'].connect_to(
        rebuild_curve.plugs['degree'],
    )
    arc_length_dimension_parameter = 1.0 / (len(spline_matrices) - 1)
    previous_arc_length_dimension = None
    for i, matrix in enumerate(spline_matrices):
        driver_spline_joint = driver_spline_joints[i]

        if i > 0:
            length_divide.plugs['outputY'].connect_to(
                driver_spline_joint.plugs['t{0}'.format(env.aim_vector_axis)],
            )

        if i not in {0, len(spline_matrices) - 1}:
            arc_length_segment_name = (
                    'Secondary%s' % rig_factory.index_dictionary[i].title()
            )
            arc_length_dimension = driver_spline_joint.create_child(
                DagNode,
                segment_name=arc_length_segment_name,
                node_type='arcLengthDimension',
                parent=utility_group
            )
            arc_length_dimension.plugs.set_values(
                uParamValue=arc_length_dimension_parameter * i,
                visibility=False,
            )
            rebuild_curve.plugs['outputCurve'].connect_to(
                arc_length_dimension.plugs['nurbsGeometry'],
            )
            plus_minus_average = driver_spline_joint.create_child(
                DependNode,
                node_type='plusMinusAverage',
            )
            plus_minus_average.plugs['operation'].set_value(2)
            arc_length_dimension.plugs['arcLength'].connect_to(
                plus_minus_average.plugs['input1D'].element(0),
            )
            if previous_arc_length_dimension:
                previous_arc_length_dimension.plugs['arcLength'].connect_to(
                    plus_minus_average.plugs['input1D'].element(1),
                )
            multiply_divide = driver_spline_joint.create_child(
                DependNode,
                node_type='multiplyDivide',
            )
            multiply_divide.plugs['operation'].set_value(2)
            multiply_divide.plugs['input1X'].set_value(
                plus_minus_average.plugs['output1D'].get_value(),
            )
            plus_minus_average.plugs['output1D'].connect_to(
                multiply_divide.plugs['input2X'],
            )

            inverse_scale = driver_spline_joint.create_child(
                DependNode,
                node_type='multiplyDivide',
                segment_name='%sInverse' % driver_spline_joint.segment_name,
            )
            inverse_scale.plugs['operation'].set_value(1)
            multiply_divide.plugs['outputX'].connect_to(
                inverse_scale.plugs['input1X'],
            )
            scale_multiply_transform.plugs['scaleX'].connect_to(
                inverse_scale.plugs['input2X'],
            )

            blend_colors = driver_spline_joint.create_child(
                DependNode,
                node_type='blendColors',
            )
            blend_colors.plugs['color2R'].set_value(1)
            inverse_scale.plugs['outputX'].connect_to(
                blend_colors.plugs['color1R'],
            )
            settings_handle.plugs['squash'].connect_to(
                blend_colors.plugs['blender'],
            )

            clamp = driver_spline_joint.create_child(
                DependNode,
                node_type='clamp',
            )
            blend_colors.plugs['outputR'].connect_to(
                clamp.plugs['inputR'],
            )
            settings_handle.plugs['squashMin'].connect_to(
                clamp.plugs['minR'],
            )
            settings_handle.plugs['squashMax'].connect_to(
                clamp.plugs['maxR'],
            )
            clamp.plugs['outputR'].connect_to(
                driver_spline_joint.plugs['scaleX'],
            )
            clamp.plugs['outputR'].connect_to(
                driver_spline_joint.plugs['scaleZ'],
            )
            previous_arc_length_dimension = arc_length_dimension
    spline_ik_handle = iks.create_spline_ik(
        driver_spline_joints[0],
        driver_spline_joints[-1],
        nurbs_curve,
        world_up_object=base_joints[0],
        world_up_object_2=base_joints[-1],
        up_vector=[0.0, 0.0, -1.0],
        up_vector_2=[0.0, 0.0, -1.0],
        world_up_type=4,
    )
    spline_ik_handle.plugs['visibility'].set_value(False)
    return dict(
        spline_joints=spline_joints,
        driver_spline_joints=driver_spline_joints
    )


def create_rig_spline(
        parent_group,
        joint_group,
        driver_transforms,
        twist_type,
        degree,
        count

):
    controller = parent_group.controller
    spline_node = parent_group.create_child(
        DependNode,
        node_type='rigSpline',
        segment_name='Spline',
    )
    if degree is None:
        if len(driver_transforms) < 3:
            degree = 1
        elif len(driver_transforms) < 4:
            degree = 2
        else:
            degree = 3

    spline_node.plugs.set_values(
        sourceUpVector=5,
        squashType=0,
        scaleType=2,
        matrixType=1,
        twistType=twist_type,
        originalLength=controller.scene.get_predicted_curve_length(
            [x.get_translation() for x in driver_transforms],
            degree,
            0
        )
    )
    for i in range(len(driver_transforms)):
        driver_transforms[i].plugs['matrix'].connect_to(spline_node.plugs['inMatrices'].element(i))

    if degree is not None:
        spline_node.plugs['degree'].set_value(degree)

    spline_joint_parent = joint_group
    spline_joints = []

    for i in range(count):
        segment_string = rig_factory.index_dictionary[i].title()
        spline_joint = spline_joint_parent.create_child(
            Joint,
            segment_name='Secondary%s' % segment_string
        )
        if spline_joints:
            spline_joints[-1].plugs['scale'].connect_to(
                spline_joint.plugs['inverseScale'],
            )
        # spline_joint.zero_rotation()
        spline_joints.append(spline_joint)
        spline_joint_parent = spline_joint
        spline_node.plugs['outTranslate'].element(i).connect_to(spline_joint.plugs['translate'])
        spline_node.plugs['outRotate'].element(i).connect_to(spline_joint.plugs['rotate'])
        spline_node.plugs['outScale'].element(i).connect_to(spline_joint.plugs['scale'])
        parameter_plug = spline_joint.create_plug('SplineParameter', at='double')
        parameter_plug.set_value(1.0 / (count - 1) * i)
        parameter_plug.connect_to(spline_node.plugs['inParameters'][i])

    for i in range(len(spline_joints)):
        this_position = controller.scene.xform(spline_joints[i], q=True, ws=True, t=True)
        if i == count - 1:
            other_position = controller.scene.xform(spline_joints[i - 1], q=True, ws=True, t=True)
        else:
            other_position = controller.scene.xform(spline_joints[i + 1], q=True, ws=True, t=True)
        local_position = [this_position[x] - other_position[x] for x in range(3)]
        segment_length = math.sqrt(sum(x ** 2 for x in local_position))
        segment_length_plug = spline_joints[i].create_plug('SegmentLength', at='double')
        segment_length_plug.set_value(segment_length)
        segment_length_plug.connect_to(spline_node.plugs['segmentLengths'][i])

    return dict(
        spline_node=spline_node,
        spline_joints=spline_joints
    )
