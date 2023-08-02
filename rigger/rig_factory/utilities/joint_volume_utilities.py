from Snowman3.rigger.rig_factory.objects.node_objects.depend_node import DependNode
from Snowman3.rigger.rig_factory.objects.node_objects.dag_node import DagNode
from Snowman3.rigger.rig_factory.objects.node_objects.nurbs_curve import NurbsCurve
from Snowman3.rigger.rig_factory.objects.node_objects.nurbs_surface import NurbsSurface
from Snowman3.rigger.rig_factory.objects.node_objects.plug import Plug
import Snowman3.rigger.rig_factory as rig_factory


def generate_volume_plugs(nurbs_object, parameters):
    """
    Measure a set of segment lengths along nurbs object and generate plugs to drive scale values
    """
    plugs = []
    arc_length_nodes = []
    global_scale_plug = nurbs_object.create_plug(
        'GlobalScale',
        at='double',
        dv=1.0
    )
    auto_volume_plug = nurbs_object.create_plug(
        'AutoVolume',
        at='double'
    )
    min_auto_volume_plug = nurbs_object.create_plug(
        'MinAutoVolume',
        at='double',
        dv=0.1
    )
    max_auto_volume_plug = nurbs_object.create_plug(
        'MaxAutoVolume',
        at='double',
        dv=2.0
    )
    for i in range(len(parameters)):
        index_character = rig_factory.index_dictionary[i].upper()
        arc_length_dimension = nurbs_object.parent.create_child(
            DagNode,
            segment_name='%sSegmentLength%s' % (nurbs_object.segment_name, index_character),
            node_type='arcLengthDimension'
        )
        arc_length_dimension.plugs['visibility'].set_value(False)
        nurbs_object.plugs['worldSpace'].element(0).connect_to(
            arc_length_dimension.plugs['nurbsGeometry'],
        )
        arc_length_divide = nurbs_object.create_child(
            DependNode,
            node_type='multiplyDivide',
            segment_name='%sArcLength%s' % (nurbs_object.segment_name, index_character)
        )
        arc_length_divide.plugs['operation'].set_value(2)

        if isinstance(parameters[i], Plug):
            parameters[i].connect_to(arc_length_dimension.plugs['uParamValue'])
        else:
            arc_length_dimension.plugs['uParamValue'].set_value(parameters[i])
        if i != 0:
            plus_minus_average = nurbs_object.create_child(
                DependNode,
                node_type='plusMinusAverage',
                segment_name='%sSegmentLength%s' % (nurbs_object.segment_name, index_character)
            )
            plus_minus_average.plugs['operation'].set_value(2)
            subtract_default = nurbs_object.create_child(
                DependNode,
                node_type='plusMinusAverage',
                segment_name='%sSubtractDefault%s' % (nurbs_object.segment_name, index_character)
            )
            multiply_normalize = nurbs_object.create_child(
                DependNode,
                node_type='multiplyDivide',
                segment_name='%sSegmentNormalize%s' % (nurbs_object.segment_name, index_character),
            )
            multiply_normalize_clamp = nurbs_object.create_child(
                DependNode,
                node_type='clamp',
                segment_name='%sSegmentNormalizeClamp%s' % (nurbs_object.segment_name, index_character),
            )
            multiply_squash_factor = nurbs_object.create_child(
                DependNode,
                node_type='multiplyDivide',
                segment_name='%sSquashFactor%s' % (nurbs_object.segment_name, index_character),
            )
            volume_clamp = nurbs_object.create_child(
                DependNode,
                node_type='clamp',
                segment_name='%sVolume%s' % (nurbs_object.segment_name, index_character),
            )
            subtract_default.plugs['operation'].set_value(2)
            subtract_default.plugs['input1D'].element(1).set_value(1.0)
            arc_length_dimension.plugs['arcLength'].connect_to(
                plus_minus_average.plugs['input1D'].element(0),
            )
            if arc_length_nodes:
                arc_length_nodes[-1].plugs['arcLength'].connect_to(
                    plus_minus_average.plugs['input1D'].element(1),
                )
            plus_minus_average.plugs['output1D'].connect_to(arc_length_divide.plugs['input1X'])
            global_scale_plug.connect_to(arc_length_divide.plugs['input2X'])
            segment_length = arc_length_divide.plugs['outputX'].get_value()
            multiply_normalize.plugs['operation'].set_value(2)

            # Set values on clamp node so that it wont divide by zero in the multiply_normalize node
            for colour in ['R', 'G', 'B']:
                multiply_normalize_clamp.plugs['min{0}'.format(colour)].set_value(0.001)
                multiply_normalize_clamp.plugs['max{0}'.format(colour)].set_value(9999999999)

            arc_length_divide.plugs['outputX'].connect_to(
                multiply_normalize_clamp.plugs['inputR']
            )
            multiply_normalize_clamp.plugs['outputR'].connect_to(
                multiply_normalize.plugs['input2X']
            )
            arc_length_divide.plugs['outputX'].connect_to(
                multiply_normalize_clamp.plugs['inputB']
            )
            multiply_normalize_clamp.plugs['outputB'].connect_to(
                multiply_normalize.plugs['input2Z']
            )
            multiply_normalize.plugs['input1X'].set_value(segment_length)
            multiply_normalize.plugs['input1Z'].set_value(segment_length)
            multiply_normalize.plugs['outputX'].connect_to(subtract_default.plugs['input1D'].element(0))
            subtract_default.plugs['output1D'].connect_to(multiply_squash_factor.plugs['input1X'])
            multiply_squash_factor.plugs['outputX'].connect_to(volume_clamp.plugs['inputR'])
            auto_volume_plug.connect_to(multiply_squash_factor.plugs['input2X'])
            min_auto_volume_plug.connect_to(volume_clamp.plugs['minR'])
            max_auto_volume_plug.connect_to(volume_clamp.plugs['maxR'])
            plugs.append((volume_clamp.plugs['outputR'],  volume_clamp.plugs['outputR']))
        arc_length_nodes.append(arc_length_dimension)

    plugs.insert(0, plugs[0])
    return plugs


def generate_distribution_plugs(nurbs_object, parameters, driver_plugs, segment_name, *args, **kwargs):
    if isinstance(nurbs_object, NurbsSurface):
        spans_value = float(nurbs_object.plugs['spansU'].get_value())
    elif isinstance(nurbs_object, NurbsCurve):
        spans_value = float(nurbs_object.plugs['spans'].get_value())
    else:
        raise Exception('Invalid nurbs_object type: %s' % type(nurbs_object))

    return generate_distribution_plugs_spans(
        nurbs_object, spans_value, parameters, driver_plugs, segment_name, *args, **kwargs)


def generate_distribution_plugs_spans(
        parent_object, spans, parameters, driver_plugs, segment_name, subtract_value=None, tangent_type=2):
    """ Generate plug drivers to distribute a few values over a larger number of outputs

    Use generate_distribution_plugs_spans directly when no nurbsCurve to reference, otherwise use
    generate_distribution_plugs wrapper.
    """
    if isinstance(tangent_type, Plug):
        tangent_type_plug = tangent_type
    elif parent_object.plugs.exists('TangentType'):
        tangent_type_plug = parent_object.plugs['TangentType']
    else:
        tangent_type_plug = parent_object.create_plug(
            'TangentType',
            at='long',
            min=0,
            max=2,
            dv=tangent_type
        )
    remap = parent_object.create_child(
        DependNode,
        node_type='remapValue',
        segment_name='Distribution%s' % segment_name,
    )
    for i, driver_plug in enumerate(driver_plugs):
        driver_node = driver_plug.get_node()
        if driver_node.plugs.exists('parameter_driver'):
            driver_node.plugs['parameter_driver'].connect_to(remap.plugs['value'].element(i).child(0))
        else:
            remap.plugs['value'].element(i).child(0).set_value(spans / (len(driver_plugs) - 1) * i)
        driver_plug.connect_to(remap.plugs['value'].element(i).child(1))
        tangent_type_plug.connect_to(remap.plugs['value'].element(i).child(2))
    distribution_plugs = []
    for i, parameter in enumerate(parameters):
        segment_character = rig_factory.index_dictionary[i].upper()
        segment_remap = parent_object.create_child(
            DependNode,
            node_type='remapValue',
            segment_name='Segment%s%s' % (segment_name, segment_character),
        )
        for p in range(len(driver_plugs)):
            remap.plugs['value'].element(p).child(0).connect_to(segment_remap.plugs['value'].element(p).child(0))
            remap.plugs['value'].element(p).child(1).connect_to(segment_remap.plugs['value'].element(p).child(1))
            remap.plugs['value'].element(p).child(2).connect_to(segment_remap.plugs['value'].element(p).child(2))
        if isinstance(parameters[i], Plug):
            parameters[i].connect_to(segment_remap.plugs['inputValue'])
        else:
            segment_remap.plugs['inputValue'].set_value(parameters[i])
        out_plug = segment_remap.plugs['outValue']
        if subtract_value is not None:
            subtract_default = parent_object.create_child(
                DependNode,
                node_type='plusMinusAverage',
                segment_name='SubtractDefault%s%s' % (segment_name, segment_character),
            )
            subtract_default.plugs['operation'].set_value(2)
            out_plug.connect_to(subtract_default.plugs['input1D'].element(0))
            subtract_default.plugs['input1D'].element(1).set_value(subtract_value)
            out_plug = subtract_default.plugs['output1D']
        distribution_plugs.append(out_plug)
    return distribution_plugs
