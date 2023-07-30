from Snowman3.rigger.rig_factory.objects.node_objects.transform import Transform
from Snowman3.rigger.rig_factory.objects.base_objects.properties import DataProperty, ObjectProperty
import Snowman3.rigger.rig_factory.common_modules as com


class IkSplineHandle(Transform):

    start_joint = ObjectProperty( name='start_joint' )
    end_effector = ObjectProperty( name='end_effector' )
    end_joint = ObjectProperty( name='end_joint' )
    solver = DataProperty( name='solver' )
    curve = ObjectProperty( name='curve' )

    suffix = 'Sikh'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.node_type = 'ikHandle'
        self.solver = 'ikSplineSolver'

    @classmethod
    def create(cls, *args, **kwargs):
        if len(args) != 3:
            raise Exception('You must pass two joints and a curve as arguments to create a {0}'.format(cls.__name__))
        controller = com.controller_utils.get_controller()
        start_joint, end_joint, curve = args
        kwargs['root_name'] = end_joint.root_name
        kwargs['functionality_name'] = end_joint.functionality_name
        kwargs['differentiation_name'] = end_joint.differentiation_name
        kwargs['segment_name'] = end_joint.segment_name
        kwargs['side'] = end_joint.side
        kwargs['end_joint'] = end_joint
        kwargs['start_joint'] = start_joint
        kwargs['curve'] = curve
        effector_kwargs = dict(kwargs)
        effector_kwargs['parent'] = end_joint.parent
        end_effector = controller.create_object(
            'IkEffector',
            **effector_kwargs
        )
        end_joint.plugs['tx'].connect_to(end_effector.plugs['tx'])
        end_joint.plugs['ty'].connect_to(end_effector.plugs['ty'])
        end_joint.plugs['tz'].connect_to(end_effector.plugs['tz'])
        kwargs['end_effector'] = end_effector
        this = super().create(**kwargs)
        return this

    def create_in_scene(self):
        self.m_object = self.controller.scene.create_ik_spline_handle(
            self.start_joint.m_object,
            self.end_effector.m_object,
            self.curve.m_object,
            self.name.split(':')[-1],
            self.solver,
            self.parent.m_object
        )
