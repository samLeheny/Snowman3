"""
Utilities called by Tasks that relate to character face setups
"""
import logging
import Snowman3.rigger.rig_factory as rig_factory
import Snowman3.rigger.rig_factory.objects as obs
import Snowman3.rigger.rig_factory.build.utilities.controller_utilities as cut

import Snowman3.rigger.rig_factory.environment as env

from Snowman3.rigger.rig_factory.objects.node_objects.depend_node import DependNode
from Snowman3.rigger.rig_factory.objects.node_objects.plug import Plug


def setup_auto_eye():
    controller = cut.get_controller()
    container = controller.root
    # eye_arrays = dict((part.root_name, part) for part in container.find_parts(obs.ProjectionEyeArray))  # TODO: should ProjectionEyeArray be used elsewhere here?

    projection_eyes = container.find_parts(obs.ProjectionEye)
    sliders = container.find_parts(obs.OpenEyeRegionsSlider)

    for eye_array in controller.root.find_parts(obs.EyeArray):

        if eye_array.eyelid_auto_follow:
            main_eye_handle = eye_array.handles[0]
            follow_plug = main_eye_handle.plugs["LidFollow"]
            upper_follow_plug = main_eye_handle.plugs["UpperLidFollow"]

            lower_follow_plug = main_eye_handle.plugs["LowerLidFollow"]
            lid_follow_curve_plug = main_eye_handle.plugs["LidFollowCurve"]



            for slider in sliders:
                blink = slider.handles[-1]
                upcontrol = slider.handles[2]
                downcontrol = slider.handles[3]
                size = slider.size
                for projection_eye in projection_eyes:
                    if slider.root_name == projection_eye.root_name and slider.side == projection_eye.side:
                        logging.getLogger('rig_build').info(
                            'Setting up auto eye for : %s and %s' % (
                                slider.name,
                                projection_eye.name
                            )
                        )

                        n = 0
                        if projection_eye.side == "left":
                            n = -1
                        elif projection_eye.side == "right":
                            n = 1

                        blink_remap_x = blink.plugs['tx'].remap(
                            (size * -2.0, -2.0),
                            (0.0, 0.0),
                            (size * 2.0, 2.0)
                        )
                        ubr = blink_remap_x.multiply(main_eye_handle.plugs["UpperLidFollow"].subtract(1))
                        dbr = blink_remap_x.multiply(main_eye_handle.plugs["LowerLidFollow"].subtract(1))

                        #EYE_JNT_ROT(xyz)* -0.0625 * LID_FOLLOW(0-1) * UP_LID_FOLLOW(0-1) * y_blinkRMP*x_blinkRMP + (LID_CTRL_TRANS(x,y,z) * x_blinkRMP_reverse) )
                        projection_eye.driver_transform.plugs['rx'].multiply(main_eye_handle.plugs['LidFollow'])\
                            .multiply(main_eye_handle.plugs["UpperLidFollow"].subtract(ubr)) \
                            .multiply(-0.0625) \
                            .connect_to(slider.plugs['UpLidInVerticalAdd'])

                        projection_eye.driver_transform.plugs['rx'].multiply(main_eye_handle.plugs['LidFollow'])\
                            .multiply(main_eye_handle.plugs["LowerLidFollow"].subtract(dbr))\
                            .multiply(-0.0625)\
                            .connect_to( slider.plugs['DownLidInVerticalAdd'])

                        projection_eye.driver_transform.plugs['rz'].multiply(main_eye_handle.plugs['LidFollow'])\
                            .multiply(main_eye_handle.plugs["UpperLidFollow"].subtract(ubr))\
                            .multiply(n*0.0625)\
                            .connect_to(slider.plugs['UpLidInHorizontalAdd'])

                        projection_eye.driver_transform.plugs['rz'].multiply(main_eye_handle.plugs['LidFollow'])\
                            .multiply(main_eye_handle.plugs["LowerLidFollow"].subtract(dbr))\
                            .multiply(n*0.0625)\
                            .connect_to(slider.plugs['DownLidInHorizontalAdd'])

                        projection_eye.driver_transform.plugs['rx'].multiply(main_eye_handle.plugs['LidFollow'])\
                            .multiply(main_eye_handle.plugs["UpperLidFollow"].subtract(ubr))\
                            .multiply(-0.0625)\
                            .connect_to(slider.plugs['UpLidOutVerticalAdd'])

                        projection_eye.driver_transform.plugs['rx'].multiply(main_eye_handle.plugs['LidFollow'])\
                            .multiply(main_eye_handle.plugs["LowerLidFollow"].subtract(dbr))\
                            .multiply(-0.0625)\
                            .connect_to(slider.plugs['DownLidOutVerticalAdd'])

                        projection_eye.driver_transform.plugs['rz'].multiply(main_eye_handle.plugs['LidFollow'])\
                            .multiply(main_eye_handle.plugs["UpperLidFollow"].subtract(ubr))\
                            .multiply(n*0.0625)\
                            .connect_to(slider.plugs['UpLidOutHorizontalAdd'])

                        projection_eye.driver_transform.plugs['rz'].multiply(main_eye_handle.plugs['LidFollow'])\
                            .multiply(main_eye_handle.plugs["LowerLidFollow"].subtract(dbr))\
                            .multiply(n*0.0625)\
                            .connect_to(slider.plugs['DownLidOutHorizontalAdd'])

                        projection_eye.driver_transform.plugs['rx'].multiply(main_eye_handle.plugs['LidFollow'])\
                            .multiply(main_eye_handle.plugs['LidFollowCurve'].add(1))\
                            .multiply(main_eye_handle.plugs["UpperLidFollow"].subtract(ubr))\
                            .multiply(-0.0625)\
                            .connect_to(slider.plugs['UpLidMidVerticalAdd'])

                        projection_eye.driver_transform.plugs['rx'].multiply(main_eye_handle.plugs['LidFollow'])\
                            .multiply(main_eye_handle.plugs['LidFollowCurve'].add(1))\
                            .multiply(main_eye_handle.plugs["LowerLidFollow"].subtract(dbr))\
                            .multiply(-0.0625)\
                            .connect_to(slider.plugs['DownLidMidVerticalAdd'])

                        projection_eye.driver_transform.plugs['rz'].multiply(main_eye_handle.plugs['LidFollow'])\
                            .multiply(main_eye_handle.plugs['LidFollowCurve'].add(1))\
                            .multiply(main_eye_handle.plugs["UpperLidFollow"].subtract(ubr))\
                            .multiply(n*0.0625)\
                            .connect_to(slider.plugs['UpLidMidHorizontalAdd'])

                        projection_eye.driver_transform.plugs['rz'].multiply(main_eye_handle.plugs['LidFollow'])\
                            .multiply(main_eye_handle.plugs['LidFollowCurve'].add(1))\
                            .multiply (main_eye_handle.plugs["LowerLidFollow"].subtract(dbr))\
                            .multiply(n*0.0625)\
                            .connect_to(slider.plugs['DownLidMidHorizontalAdd'])


def setup_auto_lips():
    """
    SDK replacements. Needs to run after create_deformation_rigs in order to link to zip attributes.
    Currently only supports a single MouthSlider.
    """
    controller = cut.get_controller()
    container = controller.root

    # Find face panel/sliders for lips
    mouth_sliders = container.find_parts(obs.MouthSlider)
    if not mouth_sliders:
        return
    elif len(mouth_sliders) > 1:
        # No logic for which ones to link, leave up to SDKs (legacy)
        return
    mouth_panel = mouth_sliders[0]

    lip_type_parts = container.find_parts(obs.DoubleSurfaceSplineUpvectors, obs.DoubleSurfaceSpline)

    # Lip roll falloff width
    if mouth_panel.create_roll_width:
        lip_roll_width_driver = mouth_panel.corner_handles[0].plugs['RollAreaWidth']

        # Find lips with dynamic lip roll falloff width enabled
        for lip in lip_type_parts:
            if not hasattr(lip, 'roll_width_plug') or lip.roll_width_plug is None:
                continue

            # Link panel to lips - slider 0.0 = default value; slider -1 = 0.001 width; slider 1 = 1.0 width
            roll_driver_output, dynamic_nodes = create_auto_driven_key_setup(
                lip,
                lip_roll_width_driver,
                lip.roll_width_default_plug,
                base_name='AutoDk',
                in_range=(-1, 1),
                out_range=(0, 1),
                override_clamp_range=(0.001, None))  # lip.roll_width_plug doesn't support 0 width
            roll_driver_output.connect_to(lip.roll_width_plug)

    # Lip Zip
    if mouth_panel.create_zip:
        zip_height_driver = mouth_panel.main_handle.plugs['ZipHeight']
        zip_driver_handles = mouth_panel.pinch_handles

        # Find lips with zip enabled
        for lip in lip_type_parts:
            if not hasattr(lip, 'create_zip') or not lip.create_zip:
                continue

            zip_dest_plugs = lip.zip_driver_plugs

            # Lip zip height
            zip_value = zip_height_driver.set_range(in_min=-1, in_max=1, out_min=0, out_max=1)
            zip_value.connect_to(zip_dest_plugs[-1])  # ZipHeight

            for i, side in enumerate('LR'):
                zip_driver = zip_driver_handles[i].plugs['tx']
                zip_falloff_driver = zip_driver_handles[i].plugs['ty']

                # Link main zip value so that it only drives the zip when less than 0
                zip_value = zip_driver.set_range(in_min=-1, in_max=0, out_min=1, out_max=0)
                zip_value.connect_to(zip_dest_plugs[i])  # Zip

                # Link falloff - default 0.2, range from 0.001 to 1.0. (Previous driven keys were linear)
                zip_falloff_dest_plug = zip_dest_plugs[2+i]  # ZipFalloff
                default_lip_falloff = zip_falloff_dest_plug.get_value()
                zip_falloff_value = zip_falloff_driver.remap((-1, 0.001), (0, default_lip_falloff), (1, 1.0))
                zip_falloff_value.connect_to(zip_falloff_dest_plug)


def finalize_auto_lips():
    controller = cut.get_controller()
    # Find lips with dynamic lip roll falloff width enabled
    lip_type_parts = controller.root.find_parts(obs.DoubleSurfaceSplineUpvectors, obs.DoubleSurfaceSpline)

    nodes_to_delete = False
    for lip in lip_type_parts:
        if not hasattr(lip, 'roll_width_plug') or lip.roll_width_plug is None:
            continue

        # Delete the temp animCurves that define each point of the remap node for lip roll width
        # Refreshing the output plug first to ensure values are kept
        dynamic_node_names = controller.scene.listConnections(
            lip.roll_width_default_plug.name, s=False, d=True, t='animCurve')
        if dynamic_node_names:
            dynamic_nodes = [controller.named_objects[name] for name in dynamic_node_names]
            controller.scene.dgeval(lip.roll_width_plug.name)
            controller.schedule_objects_for_deletion(dynamic_nodes)
            del dynamic_nodes
            nodes_to_delete = True

    if nodes_to_delete:
        controller.delete_scheduled_objects()


def create_auto_driven_key_setup(
        parent, in_plug, mid_point_value_plug, base_name='AutoDk',
        in_range=(-1, 1), out_range=(0, 1),
        use_clamp=True, override_clamp_range=(None, None)):
    """
    Create a setup where the panel driver goes from eg. -1 to 1 and outputs 0 to 1
    but the center input value 0 outputs an arbitrary/dynamic default value

    Returns the output plug, plus the driven keys linking the mid_point_value_plug to the remap node, in case they are
     to be deleted (eg. if mid_point_value_plug is a static value)
    """
    controller = cut.get_controller()

    dynamic_remap = parent.create_child(
        DependNode,
        node_type='remapValue',
        segment_name=parent.segment_name+base_name,
    )
    in_plug.connect_to(dynamic_remap.plugs['inputValue'])

    # Adjust for non-normalised input or output range
    if float(in_range[0]) != 0.0 or float(in_range[1]) != 1.0:
        dynamic_remap.plugs['inputMin'].set_value(in_range[0])
        dynamic_remap.plugs['inputMax'].set_value(in_range[1])

    if float(out_range[0]) != 0.0 or float(out_range[1]) != 1.0:
        dynamic_remap.plugs['outputMin'].set_value(out_range[0])
        dynamic_remap.plugs['outputMax'].set_value(out_range[1])

        # Ensure the mid_point_value is not affected by the output range
        if isinstance(mid_point_value_plug, Plug):
            scale_mid_point = parent.create_child(
                DependNode,
                node_type='setRange',
                segment_name=parent.segment_name + base_name + "Range",
            )
            mid_point_value_plug.connect_to(scale_mid_point.plugs['valueX'])
            scale_mid_point.plugs['oldMinX'].set_value(out_range[0])
            scale_mid_point.plugs['oldMaxX'].set_value(out_range[1])
            scale_mid_point.plugs['maxX'].set_value(1.0)

            mid_point_value_plug = scale_mid_point.plugs['outValueX']
        else:
            mid_point_value_plug = (mid_point_value_plug - out_range[0])/(out_range[1] - out_range[0])  # calc input value to end up at given output mid_point_value

    remap_variable_points = env.falloff_curves['auto_interpolation_remap_points']
    num_remap_points = len(remap_variable_points)
    num_spans = num_remap_points - 3  # Extra point beyond each end for tangents, eg. 8 spans = 9 points + 2 end points
    span_width = 1.0 / num_spans
    dynamic_nodes = []
    for i, curve_data in enumerate(env.falloff_curves['auto_interpolation_remap_points']):
        c = rig_factory.index_dictionary[i].upper()

        # Create an animcurve defining where to plot the remap points for the given default value
        remap_pt_animcurve = parent.create_child(
            DependNode,
            node_type='animCurveUU',  # Standard 'driven key' animCurve
            segment_name='%s%sRemap%s' % (parent.segment_name, base_name, c),
            differentiation_name=parent.differentiation_name)
        controller.scene.create_animcurve_from_data(
            remap_pt_animcurve.name, remap_pt_animcurve.name, curve_data, subrange=None)

        if not isinstance(mid_point_value_plug, Plug):
            mid_point_value_plug = parent.create_plug(
                '%s%sMidValue' % (base_name, c),
                dv=mid_point_value_plug,
                keyable=True,
                min=out_range[0],
                max=out_range[1]
            )
        mid_point_value_plug.connect_to(remap_pt_animcurve.plugs['input'])

        # (With first and last points being outside of the active range, to control the end tangents)
        dynamic_remap.plugs['value'][i][0].set_value(span_width*(i-1))  # 'value_Position'
        remap_pt_animcurve.plugs['output'].connect_to(dynamic_remap.plugs['value'][i][1])  # 'value_FloatValue'
        dynamic_remap.plugs['value'][i][2].set_value(3)  # 'value_Interp' to 'spline'

        dynamic_nodes.append(remap_pt_animcurve)

    out_plug = dynamic_remap.plugs['outValue']
    if use_clamp:
        # Clamp the values to the out range (as the remapValue node is hard to get to have a flat tangent when the mid
        #  value is near the min or max...)
        remap_clamp = parent.create_child(
            DependNode,
            node_type='clamp',
            segment_name='%s%sClamp' % (parent.segment_name, base_name),
            differentiation_name=parent.differentiation_name)
        remap_clamp.plugs['minR'].set_value(override_clamp_range[0] if override_clamp_range[0] else out_range[0])
        remap_clamp.plugs['maxR'].set_value(override_clamp_range[1] if override_clamp_range[1] else out_range[1])
        out_plug.connect_to(remap_clamp.plugs['inputR'])
        out_plug = remap_clamp.plugs['outputR']

    return out_plug, dynamic_nodes
