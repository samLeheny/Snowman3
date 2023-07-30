import Snowman3.rigger.rig_factory.common_modules as com
import Snowman3.rigger.rig_factory.utilities.string_utilities as stu
from Snowman3.rigger.rig_factory.objects.base_objects.base_object import BaseObject
from Snowman3.rigger.rig_factory.objects.sdk_objects.sdk_group import SDKGroup
from Snowman3.rigger.rig_factory.objects.node_objects.depend_node import DependNode
from Snowman3.rigger.rig_factory.objects.base_objects.properties import DataProperty, ObjectListProperty, ObjectProperty


class SDKNetwork(BaseObject):

    sdk_groups = ObjectListProperty(
        name='sdk_groups'
    )
    driven_plugs = ObjectListProperty(
        name='driven_plugs'
    )
    post_infinity_type = DataProperty(
        name='post_infinity_type'
    )
    pre_infinity_type = DataProperty(
        name='pre_infinity_type'
    )
    is_weighted = DataProperty(
        name='is_weighted'
    )
    in_tangent = DataProperty(
        name='in_tangent'
    )
    out_tangent = DataProperty(
        name='out_tangent'
    )
    out_angle = DataProperty(
        name='out_angle'
    )
    in_angle = DataProperty(
        name='in_angle'
    )
    in_tangent_weight = DataProperty(
        name='in_tangent_weight'
    )
    out_tangent_weight = DataProperty(
        name='out_tangent_weight'
    )
    in_tangent_type = DataProperty(
        name='in_tangent_type'
    )
    out_tangent_type = DataProperty(
        name='out_tangent_type'
    )
    tangents_locked = DataProperty(
        name='tangents_locked'
    )
    is_breakdown = DataProperty(
        name='is_breakdown'
    )
    pickwalk_groups = DataProperty(
        name='pickwalk'
    )
    container = ObjectProperty(
        name='container'
    )
    lock_curves = DataProperty(
        name='lock_curves',
        default_value=True
    )
    suffix = 'Sdk'

    @classmethod
    def create(cls, **kwargs):
        controller = com.controller_utilities.get_controller()
        kwargs.setdefault('post_infinity_type', 'linear')
        kwargs.setdefault('pre_infinity_type', 'linear')
        kwargs.setdefault('in_tangent', 'linear')
        kwargs.setdefault('out_tangent', 'linear')
        container = kwargs.get('container', None)
        if container:
            controller.start_sdk_ownership_signal.emit(None, container)
        this = super(SDKNetwork, cls).create(**kwargs)
        if container:
            container.sdk_networks.append(this)
            controller.end_sdk_ownership_signal.emit(this, container)
        return this

    def __init__(self, **kwargs):
        super(SDKNetwork, self).__init__(**kwargs)

    def remove_driven_plugs(self, driven_plugs):
        for plug in driven_plugs:
            if plug not in self.driven_plugs:
                raise Exception('The plug "%s" was not a driven plug of "%s"' % (plug.name, self.name))
            self.driven_plugs.remove(plug)
        nodes_to_delete = []
        for plug in driven_plugs:
            for sdk_group in self.sdk_groups:
                if plug.name in sdk_group.animation_curves:
                    nodes_to_delete.append(sdk_group.animation_curves[plug.name])
            for key in ['add_node', 'blend_node']:
                if key in plug.relationships:
                    nodes_to_delete.append(plug.relationships[key])
        self.controller.schedule_objects_for_deletion(nodes_to_delete)
        del nodes_to_delete
        self.controller.delete_scheduled_objects()

    def add_driven_plugs(self, plugs):
        existing_plugs = self.driven_plugs
        existing_count = len(existing_plugs)
        plug_map = dict(
            translateX='tx',
            translateY='ty',
            translateZ='tz',
            rotateX='rx',
            rotateY='ry',
            rotateZ='rz',
            scaleX='sx',
            scaleY='sy',
            scaleZ='sz'
        )
        for i, plug in enumerate(plugs):
            if plug.root_name in plug_map:
                plug = plug.get_node().plugs[plug_map[plug.root_name]]
            if plug not in self.driven_plugs:
                # if not isinstance(plug, DrivenPlug):
                #     raise Exception('driven plugs must be of type "%s"' % DrivenPlug.__name__)
                if not self.controller.scene.mock and self.controller.scene.listConnections(plug.name, s=True, d=False):
                    raise Exception('The driven plug "%s" already seems to have an incoming connection' % plug)
                node_name, attribute_name = plug.name.split('.')
                blend_node = self.create_child(
                    DependNode,
                    side=None,
                    root_name=self.root_name,
                    segment_name=stu.underscore_to_pascalcase(node_name.split(':')[-1]),
                    functionality_name=stu.underscore_to_pascalcase(attribute_name),
                    index=existing_count + i,
                    node_type='blendWeighted',
                    parent=plug.get_node()
                )
                plug.get_node().plugs['nodeState'].connect_to(blend_node.plugs['nodeState'])  # stops maya from cleaning up this node
                blend_out_plug = blend_node.initialize_plug('output')

                current_value = plug.get_value()
                if abs(round(current_value, 6)) != 0.0:
                    add_node = blend_node.create_child(
                        DependNode,
                        side=None,
                        node_type='addDoubleLinear',
                        root_name=self.root_name,
                        segment_name=stu.underscore_to_pascalcase(node_name),
                        functionality_name=stu.underscore_to_pascalcase(attribute_name),
                    )
                    blend_out_plug.connect_to(add_node.plugs['input1'])
                    add_node.plugs['input2'].set_value(current_value)
                    add_node.plugs['output'].connect_to(plug)
                    plug.relationships['add_node'] = add_node

                else:
                    blend_out_plug.connect_to(plug)

                plug.get_node().plugs['nodeState'].connect_to(blend_node.plugs['nodeState'])
                blend_node.initialize_plug('input')
                self.driven_plugs.append(plug)
                plug.relationships['blend_node'] = blend_node
                plug.default_value = plug.get_value()

    def reset_driven_plugs(self):
        for plug in self.driven_plugs:
            if plug.root_name in ['sx', 'sy', 'sz', 'scaleX', 'scaleY', 'scaleZ']:
                plug.set_value(1.0)
            else:
                plug.set_value(0.0)

    def set_driven_plugs(self, plugs):
        self.driven_plugs = []
        self.add_driven_plugs(plugs)

    def initialize_driven_plugs(self, nodes, attributes):
        self.add_driven_plugs([node.plugs[attr] for node in nodes for attr in attributes])

    def create_group(self, **kwargs):
        return self.create_child(
            SDKGroup,
            sdk_network=self,
            **kwargs
        )

    def get_curves(self):
        curves = []
        for g in self.sdk_groups:
            for c in g.animation_curves:
                curves.append(c)
        return curves

    def get_positions(self):
        positions = []
        for driven_plug in self.driven_plugs:
            result_plug = driven_plug.node.plugs['output'].connections[0].in_plug
            positions.append(result_plug.get_value())
        return positions

    def get_user_positions(self):
        positions = []
        for driven_plug in self.driven_plugs:
            result_plug = driven_plug.node.plugs['output'].connections[0].in_plug
            result_value = result_plug.get_value()
            difference = 0.0
            for index in driven_plug.plugs:
                    difference += driven_plug.plugs[index].get_value()
            positions.append(result_value-difference)
        return positions

    def teardown(self):

        if self.container:

            container = self.container
            self.controller.start_sdk_disown_signal.emit(self, container)
            self.container.sdk_networks.remove(self)
            self.container = None
            self.controller.end_sdk_disown_signal.emit(self, container)
            del container

        self.controller.schedule_objects_for_deletion(
            self.sdk_groups,
            [x.relationships['blend_node'] for x in self.driven_plugs]
        )

        super(SDKNetwork, self).teardown()

    def get_next_avaliable_index(self):
        existing_indices = [x.index for x in self.sdk_groups]
        i = 0
        while i in existing_indices:
            i += 1
        return i

    def set_weight(self, weight):
        for group in self.sdk_groups:
            group.set_weight(weight)
