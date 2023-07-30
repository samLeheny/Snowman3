from Snowman3.rigger.rig_factory.objects.node_objects.transform import Transform
from Snowman3.rigger.rig_factory.objects.node_objects.mesh import Mesh
from Snowman3.rigger.rig_factory.objects.node_objects.nurbs_curve import NurbsCurve
from Snowman3.rigger.rig_factory.objects.base_objects.properties import DataProperty, ObjectProperty, ObjectListProperty



class Constraint(Transform):

    transform = ObjectProperty( name='transform' )
    targets = ObjectListProperty( name='targets' )
    create_kwargs = DataProperty( name='create_kwargs' )

    suffix = 'Cns'


    @classmethod
    def create(cls, *args, **kwargs):
        targets = args[0:-1]
        transform = args[-1]
        if not isinstance(transform, Transform):
            raise Exception(f"You cannot constrain a '{type(transform)}'")
        if not transform.segment_name:
            raise Exception('You cannot constrain a transform without a segment_name')

        parent = kwargs.pop('parent', transform)
        namespace = kwargs.pop('namespace', transform)
        root_name = transform.root_name
        if ':' in transform.name:
            prefix = ''.join(x.capitalize() or '_' for x in transform.name.split(':')[0].split('_'))
            if root_name:
                root_name = f'{prefix}{root_name}'
            else:
                root_name = prefix
        """
        WARNING. Needs change.
        Editing of kwargs should happen in Node.pre-process kwarg function.
        Otherwise there is no way to predict the name of this node before its created
        """

        kwargs['create_kwargs'] = dict(kwargs)
        kwargs.setdefault('root_name', root_name)
        kwargs['segment_name'] = transform.segment_name
        kwargs['differentiation_name'] = transform.differentiation_name
        kwargs['subsidiary_name'] = transform.subsidiary_name
        kwargs['functionality_name'] = transform.functionality_name
        kwargs['namespace'] = namespace

        # Need to add transform.suffix and cls.suffx to get something like "*_Jnt_Prc", with "Jnt" being
        # transform.suffix and "Prc" being cls.suffix
        kwargs['suffix'] = '{0}_{1}'.format(transform.suffix, cls.suffix)

        kwargs.setdefault('side', transform.side)
        kwargs['parent'] = parent
        kwargs['transform'] = transform  # must exist in kwargs because of create_in_scene()
        kwargs['targets'] = targets  # must exist in kwargs because of create_in_scene()
        this = super().create(**kwargs)
        return this


    def __init__(self, **kwargs):
        super().__init__(**kwargs)


    def create_in_scene(self):
        transforms = list(self.targets)
        transforms.append(self.transform)
        self.m_object = self.controller.scene.create_constraint(
            self.node_type,
            name=self.name.split(':')[-1],
            parent=self.parent.m_object,
            *[x.m_object for x in transforms],
            **self.create_kwargs
        )


    def get_weight_plug(self, target):
        return self.plugs['%sW%s' % (target.name.split(':')[-1], self.targets.index(target))]



class ParentConstraint(Constraint):

    suffix = 'Prc'


    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.node_type = 'parentConstraint'


    @classmethod
    def create(cls, *args, **kwargs):
        if len(args) < 2:
            raise Exception(f'Cannot make {cls.__name__} with less than 2 transforms passed as arguments')
        if not all([isinstance(x, Transform) for x in args]):
            raise Exception(f"Use 'Transform' as arguments when you create a '{cls.__name__}'")
        return super().create( *args, **kwargs)



class PointConstraint(Constraint):

    suffix = 'Poc'


    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.node_type = 'pointConstraint'


    @classmethod
    def create(cls, *args, **kwargs):
        if len(args) < 2:
            raise Exception(f'Cannot make {cls.__name__} with less than 2 transforms passed arguments')
        if not all([isinstance(x, Transform) for x in args]):
            raise Exception(f"Use 'Transform' as arguments when you create a '{cls.__name__}'")
        return super().create(*args, **kwargs)



class ScaleConstraint(Constraint):

    suffix = 'Scc'


    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.node_type = 'scaleConstraint'


    @classmethod
    def create(cls, *args, **kwargs):
        if len(args) < 2:
            raise Exception(f'Cannot make {cls.__name__} with less than 2 transforms passed arguments')
        if not all([isinstance(x, Transform) for x in args]):
            raise Exception(f"Use 'Transform' as arguments when you create a '{cls.__name__}'")
        return super().create(*args, **kwargs)



class AimConstraint(Constraint):


    world_up_object = ObjectProperty(
        name='world_up_object'
    )


    suffix = 'Acn'


    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.node_type = 'aimConstraint'


    @classmethod
    def create(cls, *args, **kwargs):
        up_object = kwargs.pop('worldUpObject', None)
        if up_object:
            kwargs['worldUpObject'] = str(up_object)
        if len(args) < 2:
            raise Exception('Cannot make {cls.__name__} with less than 2 transforms passed arguments')
        if not all([isinstance(x, Transform) for x in args]):
            raise Exception(f"You must use 'Transform' as arguments when you create a '{cls.__name__}'")
        return super().create(*args, **kwargs)



class OrientConstraint(Constraint):

    suffix = 'Ocn'


    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.node_type = 'orientConstraint'


    @classmethod
    def create(cls, *args, **kwargs):
        if len(args) < 2:
            raise Exception(f'Cannot make {cls.__name__} with less than 2 transforms passed arguments')
        if not all([isinstance(x, Transform) for x in args]):
            raise Exception(f"Use 'Transform' as arguments when you create a '{cls.__name__}'")
        return super().create(*args, **kwargs)



class PoleVectorConstraint(Constraint):

    suffix = 'Pvc'


    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.node_type = 'poleVectorConstraint'


    @classmethod
    def create(cls, *args, **kwargs):
        if len(args) < 2:
            raise Exception(f'Cannot make {cls.__name__} with less than 2 transforms passed arguments')
        if not all([isinstance(x, Transform) for x in args]):
            raise Exception(f"Use 'Transform' as arguments when you create a '{cls.__name__}'")
        return super().create(*args, **kwargs)



class TangentConstraint(Constraint):

    suffix = 'Tnc'


    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.node_type = 'tangentConstraint'


    @classmethod
    def create(cls, *args, **kwargs):
        if len(args) < 2:
            raise Exception(f"Cannot make {cls.__name__} with less than 2 objects passed arguments")
        if len(args) > 2:
            raise Exception(f'Cannot make {cls.__name__} with more than 2 objects passed arguments')
        if not isinstance(args[0], NurbsCurve):
            raise Exception(f"You must use 'NurbsCurve' as first argument when you create a '{cls.__name__}'")
        if not isinstance(args[1], Transform):
            raise Exception(f"Use 'Transform' as second argument when you create a '{cls.__name__}'")
        return super().create(*args, **kwargs)



class GeometryConstraint(Constraint):

    suffix = 'Gmc'


    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.node_type = 'geometryConstraint'


    @classmethod
    def create(cls, *args, **kwargs):
        if len(args) < 2:
            raise Exception(f'Cannot make {cls.__name__} with less than 2 transforms passed arguments')
        if not all([isinstance(x, (Transform, Mesh)) for x in args]):
            raise Exception(f"Use 'Transform' as arguments when you create a '{cls.__name__}'")
        return super().create(*args, **kwargs)
