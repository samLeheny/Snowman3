from Snowman3.rigger.rig_factory.objects.node_objects.animation_curve import AnimationCurve
from Snowman3.rigger.rig_factory.objects.sdk_objects.sdk_keyframe import SDKKeyFrame
from Snowman3.rigger.rig_factory.objects.base_objects.properties import DataProperty
from Snowman3.rigger.rig_factory.objects.node_objects.depend_node import DependNode



class SDKCurve(AnimationCurve):

    default_value = DataProperty( name='post_infinity_type', default_value='default_value' )


    def __init__(self, **kwargs):
        super(SDKCurve, self).__init__(**kwargs)


    @classmethod
    def create(cls, **kwargs):
        sdk_group = kwargs.get('sdk_group', None)
        driven_plug = kwargs.get('driven_plug', None)
        if not sdk_group:
            raise Exception(
                'You must provide a sdk_group to create a %s' % SDKCurve.__name__
            )
        if not driven_plug:
            raise Exception(
                'You must provide a driven_plug to create a %s' % SDKCurve.__name__
            )
        kwargs['default_value'] = driven_plug.get_value()
        kwargs['driver_plug'] = sdk_group.driver_plug
        kwargs['post_infinity_type'] = sdk_group.sdk_network.post_infinity_type
        kwargs['pre_infinity_type'] = sdk_group.sdk_network.post_infinity_type
        kwargs['is_weighted'] = sdk_group.sdk_network.is_weighted
        kwargs.setdefault('parent', sdk_group)
        this = super(SDKCurve, cls).create(**kwargs)
        input_plug = this.initialize_plug('input')
        sdk_group.driver_plug.connect_to(input_plug)
        return this


    def create_in_scene(self):
        blend_node = self.driven_plug.relationships.get('blend_node', None)
        if not blend_node:
            raise Exception(
                'SDK driven plug "%s" seems not to have a "blend_node" relationship' % self.driven_plug
            )
        blend_weighted_plug = blend_node.plugs['input'].element(self.sdk_group.index)

        self.m_object = self.controller.scene.create_animation_curve(
            blend_weighted_plug.m_plug,
            name=self.name.split(':')[-1]
        )


    def create_keyframe(self, **kwargs):
        return self.controller.create_object(
            SDKKeyFrame,
            animation_curve=self,
            **kwargs
        )
