import copy
from Snowman3.rigger.rig_factory.objects.base_objects.weak_list import WeakList



def get_blueprint(sdk_network):
    sdk_group_blueprints = []
    blueprint = dict(
        root_name=sdk_network.root_name,
        segment_name=sdk_network.segment_name,
        side=sdk_network.side,
        size=sdk_network.size,
        groups=sdk_group_blueprints,
        driven_plugs=[x.name for x in sdk_network.driven_plugs]
    )
    for sdk_group in sdk_network.sdk_groups:
        keyframe_group_blueprints = []
        group_blueprint = dict(
            root_name=sdk_group.root_name,
            segment_name=sdk_group.segment_name,
            side=sdk_group.side,
            size=sdk_group.size,
            driver_plug=sdk_group.driver_plug.name,
            keyframe_groups=keyframe_group_blueprints
        )
        sdk_group_blueprints.append(group_blueprint)
        for keyframe_group in sdk_group.keyframe_groups:
            keyframe_data = []
            keyframe_group_blueprint = dict(
                root_name=keyframe_group.root_name,
                segment_name=keyframe_group.segment_name,
                in_value=keyframe_group.in_value,
                in_tangent_type=keyframe_group.in_tangent_type,
                out_tangent_type=keyframe_group.out_tangent_type,
                keyframe_data=keyframe_data
            )
            keyframe_group_blueprints.append(keyframe_group_blueprint)
            for key in keyframe_group.keyframes:
                keyframe_data.append((key.animation_curve.driven_plug.name, key.out_value))
    return blueprint


def get_plug_with_strings(controller, driven_plugs):
    converted_plugs = WeakList()
    for plug_string in driven_plugs:
        node_string, attr_string = plug_string.split('.')
        if node_string not in controller.named_objects:
            raise Exception('The plug node "%s" was not found in the controller' % node_string)
        node = controller.named_objects[node_string]
        mock_mode = controller.scene.mock

        if not mock_mode and controller.scene.listConnections(plug_string, s=True, d=False):
            raise Exception('invalid connected plug "%s"' % plug_string)
        elif not mock_mode and controller.scene.getAttr(plug_string, l=True):
            raise Exception('invalid locked plug "%s"' % plug_string)
        else:
            converted_plugs.append(node.plugs[attr_string])
    return converted_plugs


def build_blueprint(controller, blueprint):
    if bool(blueprint.get('klass', None)):
        raise Exception('Legacy SDK data detected. Custom Sdks will be skipped')
    sdk_groups_data = blueprint.pop('groups', [])
    driven_plugs = get_plug_with_strings(controller, blueprint.pop('driven_plugs'))
    network = controller.create_sdk_network(
        **blueprint
    )
    network.set_driven_plugs(driven_plugs)
    for group_data in sdk_groups_data:
        group_data = copy.deepcopy(group_data)
        keyframe_groups_data = group_data.pop('keyframe_groups')
        node_name, plug_name = group_data.pop('driver_plug').split('.')
        driver_node = controller.named_objects.get(node_name, None)
        if driver_node is None:
            raise Exception('The node "%s" was not found.\n Unable to build sdk blueprint' % node_name)
        driver_plug = driver_node.plugs[plug_name]
        sdk_group = network.create_group(
            driver_plug=driver_plug,
            **group_data
        )
        for key_group_data in keyframe_groups_data:
            key_group_data = copy.deepcopy(key_group_data)
            sdk_group.create_keyframe_group(
                **key_group_data
            )
    controller.dg_dirty()
    return network


