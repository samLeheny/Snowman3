import functools

from Snowman3.rigger.rig_factory.objects.base_objects.properties import DataProperty, ObjectProperty, ObjectListProperty, ObjectDictProperty
from Snowman3.rigger.rig_factory.objects.base_objects.base_object import BaseObject
from Snowman3.rigger.rig_factory.objects.sdk_objects.sdk_curve import SDKCurve
from Snowman3.rigger.rig_factory.objects.sdk_objects.keyframe_group import KeyframeGroup
from Snowman3.rigger.rig_factory.objects.node_objects.plug import Plug
import Snowman3.rigger.rig_factory.utilities.string_utilities as stu
import Snowman3.rigger.rig_factory.common_modules as com


class SDKGroup(BaseObject):

    sdk_network = ObjectProperty( name='sdk_network' )
    driver_plug = ObjectProperty( name='driver_plug' )
    animation_curves = ObjectDictProperty( name='animation_curves' )
    keyframe_groups = ObjectListProperty( name='keyframe_groups' )
    active = DataProperty( name='active' )
    index = DataProperty( name='index' )
    suffix = 'Sdkgp'


    def __init__(self, **kwargs):
        super(SDKGroup, self).__init__(**kwargs)


    def isolate(self):
        sdk_network = self.sdk_network
        sdk_groups = sdk_network.sdk_groups
        driven_plugs = sdk_network.driven_plugs

        def undo(plug_data):
            for plug in plug_data:
                plug.set_value(plug_data[plug])

        undo_function = functools.partial(
            undo,
            dict((plug, plug.get_value()) for plug in driven_plugs)
        )

        for driven_plug in driven_plugs:
            current_value = round(driven_plug.get_value(), 5)
            if current_value != driven_plug.default_value:
                difference = 0.0
                for gi in range(len(sdk_groups)):
                    if self.index != gi:
                        blend_input_plug = driven_plug.relationships['blend_node'].plugs['input'].element(gi)
                        difference += blend_input_plug.get_value(0.0)
                driven_plug.set_value(driven_plug.get_value(0.0) - difference)

        return undo_function


    def set_active(self, value):
        self.controller.set_active(self, value)


    def set_weight(self, value):
        for driven_plug in self.sdk_network.driven_plugs:
            driven_plug.relationships['blend_node'].plugs['weight'].element(self.index).set_value(value)


    def create_keyframe_group(self, **kwargs):
        kwargs['index'] = self.get_next_avaliable_index()
        kwargs['segment_name'] = self.segment_name
        return self.create_child(
            KeyframeGroup,
            sdk_group=self,
            **kwargs
        )


    def get_animation_curve_data(self):
        curves_data = dict()
        for driver_plug_name in self.animation_curves:
            animation_curve = self.animation_curves[driver_plug_name]
            curve_data = dict()
            for in_value in animation_curve.keyframes:
                curve_data[in_value] = animation_curve.keyframes[in_value].out_value
            curves_data[driver_plug_name] = curve_data
        return curves_data


    @classmethod
    def create(cls, **kwargs):
        controller = com.controller_utilities.get_controller()
        sdk_network = kwargs.get('sdk_network', None)
        if not isinstance(kwargs.get('driver_plug', None), Plug):
            raise Exception(
                'Cannot create an %s without a "driver_plug" keyword argument' % SDKGroup.__name__
            )
        if not sdk_network or not sdk_network.__class__.__name__ == 'SDKNetwork':
            raise Exception(
                'You must provide an SDKNetwork as the keyword argument'
            )
        kwargs.setdefault(
            'index',
            sdk_network.get_next_avaliable_index()
        )
        controller.start_sdk_ownership_signal.emit(None, sdk_network)
        this = super(SDKGroup, cls).create(**kwargs)
        sdk_network.sdk_groups.append(this)
        controller.end_sdk_ownership_signal.emit(this, sdk_network)
        return this


    def get_next_avaliable_index(self):
        existing_indices = [x.index for x in self.keyframe_groups]
        current_index = 0
        while True:
            if current_index not in existing_indices:
                return current_index
            current_index += 1


    def get_animation_curve(self, driven_plug):
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
        if driven_plug.root_name in plug_map:
            driven_plug = driven_plug.get_node().plugs[plug_map[driven_plug.root_name]]

        if driven_plug not in self.sdk_network.driven_plugs:
            raise Exception('The plug "%s" was not found in SdkNetwork.driven_plugs' % driven_plug.name)
        if driven_plug.name in self.animation_curves:
            return self.animation_curves[driven_plug.name]

        default_value = driven_plug.get_value()
        driver_plug = self.driver_plug
        driver_node_name, driver_attribute_name = driver_plug.name.split('.')
        driven_node_name, driven_attribute_name = driven_plug.name.split('.')

        segment_name = '{}{}{}{}'.format(
            stu.underscore_to_pascalcase(driver_node_name.split(':')[-1]),
            driver_attribute_name.title(),
            stu.underscore_to_pascalcase(driven_node_name.split(':')[-1]),
            driven_attribute_name.title()
        )

        animation_curve = self.controller.create_object(
            SDKCurve,
            sdk_group=self,
            parent=self,
            root_name=self.root_name,
            segment_name=segment_name,
            driven_plug=driven_plug,
            index=len(self.animation_curves)
        )

        self.animation_curves[driven_plug.name] = animation_curve
        if self.sdk_network.lock_curves:
            self.controller.scene.lock_node(animation_curve.name, lock=True)
        animation_curve.plugs['output'].set_value(default_value)
        return animation_curve


    def teardown(self):
        self.controller.start_sdk_disown_signal.emit(
            self,
            self.sdk_network
        )
        self.controller.schedule_objects_for_deletion(
            self.animation_curves.values()
        )
        sdk_network = self.sdk_network
        sdk_network.sdk_groups.remove(self)
        self.sdk_network = None
        super(SDKGroup, self).teardown()
        self.controller.end_sdk_disown_signal.emit(self, sdk_network)
