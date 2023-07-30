from Snowman3.rigger.rig_factory.objects.base_objects.properties import DataProperty, ObjectProperty
from Snowman3.rigger.rig_factory.objects.base_objects.base_object import BaseObject
import Snowman3.rigger.rig_factory as rig_factory



class KeyFrame(BaseObject):

    animation_curve = ObjectProperty( name='animation_curve' )
    in_value = DataProperty( name='in_value' )
    out_value = DataProperty( name='out_value' )
    in_tangent = DataProperty( name='in_tangent', default_value='linear' )
    out_tangent = DataProperty( name='out_tangent', default_value='linear' )
    """
    out_angle = DataProperty( name='out_angle' )
    in_angle = DataProperty( name='in_angle' )
    in_tangent_weight = DataProperty( name='in_tangent_weight' )
    out_tangent_weight = DataProperty( name='out_tangent_weight' )
    in_tangent_type = DataProperty( name='in_tangent_type' )
    out_tangent_type = DataProperty( name='out_tangent_type' )
    tangents_locked = DataProperty( name='tangents_locked' )
    is_breakdown = DataProperty( name='is_breakdown' )
    """
    suffix = 'Key'

    def __init__(self, **kwargs):
        super(KeyFrame, self).__init__(**kwargs)

    def delete(self):
        self.controller.delete_keyframe(self)

    def set_values(self, **kwargs):
        self.controller.change_keyframe(
            self,
            **kwargs
        )


    @classmethod
    def create(cls, **kwargs):
        animation_curve = kwargs.get('animation_curve', None)
        in_value = kwargs.get('in_value', None)
        out_value = kwargs.get('out_value', None)
        index = kwargs.get('index', None)
        if index is None:
            raise Exception('You must provide an index to create a keyframe')
        if animation_curve is None:
            raise Exception(
                'You must provide a animation_curve to create a %s' % KeyFrame.__name__
            )
        if in_value is None:
            raise Exception(
                'You must provide a in_value to create a %s' % KeyFrame.__name__
            )
        if in_value in animation_curve.keyframes.keys():
            raise Exception(
                'A keyframe at the in value of "%s" already exists' % in_value
            )
        kwargs['root_name'] = animation_curve.root_name
        kwargs['segment_name'] = '%s%s' % (animation_curve.segment_name, rig_factory.index_dictionary[index].upper())
        kwargs['functionality_name'] = animation_curve.functionality_name
        kwargs.setdefault('out_value', out_value if out_value is not None else animation_curve.driven_plug.get_value())
        kwargs.setdefault('parent', animation_curve)
        this = super(KeyFrame, cls).create(**kwargs)
        animation_curve.keyframes[in_value] = this
        this.create_in_scene()
        return this


    def create_in_scene(self):
        self.controller.scene.create_keyframe(
            self.animation_curve.m_object,
            self.in_value,
            self.out_value,
            self.controller.scene.tangents[self.in_tangent],
            self.controller.scene.tangents[self.out_tangent]
        )


    def teardown(self):
        # self.controller.scene.delete_keyframe(self.animation_curve.m_object, self.in_value)
        super(KeyFrame, self).teardown()


    def get_out_value(self):
        self.out_value = self.controller.scene.get_key_value(
            self.animation_curve.m_object,
            self.in_value
        )
        return self.out_value
