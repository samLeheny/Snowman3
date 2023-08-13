from Snowman3.rigger.rig_math.matrix import Matrix
from Snowman3.rigger.rig_factory.objects.node_objects.transform import Transform
from Snowman3.rigger.rig_factory.objects.node_objects.joint import Joint
from Snowman3.rigger.rig_factory.objects.node_objects.depend_node import DependNode
from Snowman3.rigger.rig_factory.objects.base_objects.properties import ObjectProperty
from Snowman3.rigger.rig_factory.objects.base_objects.base_object import BaseObject
from Snowman3.rigger.rig_factory.objects.rig_objects.matrix_space_switcher import MatrixSpaceSwitcher


class MatrixConstraint(BaseObject):

    transform_1 = ObjectProperty( name='transform_1' )
    transform_2 = ObjectProperty( name='transform_2' )
    mult_matrix = ObjectProperty( name='mult_matrix' )
    offset_matrix_plug = ObjectProperty( name='offset_matrix_plug' )
    decompose_matrix = ObjectProperty( name='decompose_matrix' )
    suffix = 'Mxc'

    @classmethod
    def create(cls, *args, **kwargs):
        if len(args) != 2:
            raise Exception(
                'Cannot make %s with less than 2 transforms passed arguments' % cls.__name__
            )
        if not all([isinstance(x, Transform) for x in args]):
            raise Exception(
                'You must use "Transform" node_objects as arguments when you create a "%s"' % cls.__name__
            )
        transform_1, transform_2 = args
        kwargs.setdefault('root_name', transform_2.root_name)
        kwargs['segment_name'] = transform_2.segment_name
        kwargs['parent'] = transform_2
        ignore_parent_matrix = kwargs.pop('ignore_parent_matrix', False)
        if transform_2.functionality_name and transform_2.suffix:
            kwargs.setdefault('functionality_name', '%s%s' % (
                transform_2.functionality_name,
                transform_2.suffix
            ))
        elif transform_2.functionality_name:
            kwargs.setdefault('functionality_name', transform_2.functionality_name)
        elif transform_2.suffix:
            kwargs.setdefault('functionality_name', transform_2.suffix)
        kwargs.setdefault('differentiation_name', transform_2.differentiation_name)
        kwargs.setdefault('side', transform_2.side)
        this = super().create(**kwargs)
        mult_matrix = transform_2.create_child( DependNode, node_type='multMatrix', index=0 )
        decompose_matrix = transform_2.create_child( DependNode, node_type='decomposeMatrix' )

        matrix_plug = mult_matrix.create_plug( 'offsetMatrix', at='matrix' )
        default_matrix_data = list(Matrix())
        world_matrix_plug = transform_2.plugs['worldMatrix']
        matrix_element_plug = world_matrix_plug.element(0)
        matrix_element_value = matrix_element_plug.get_value(default_matrix_data)
        target_inverse_matrix = Matrix(*matrix_element_value)
        world_inverse_matrix = Matrix(
            *transform_1.plugs['worldInverseMatrix'].element(0).get_value(default_matrix_data))
        offset_matrix = list(world_inverse_matrix * target_inverse_matrix)
        matrix_plug.set_value(offset_matrix)

        matrix_plug.connect_to(mult_matrix.plugs['matrixIn'].element(0))
        transform_1.plugs['worldMatrix'].element(0).connect_to(mult_matrix.plugs['matrixIn'].element(1))

        if transform_2.parent and not ignore_parent_matrix:  # Use ignore_parent_matrix if parent is a static group
            transform_2.parent.plugs['worldInverseMatrix'].element(0).connect_to(
                mult_matrix.plugs['matrixIn'].element(2))

        mult_matrix.plugs['matrixSum'].connect_to(decompose_matrix.plugs['inputMatrix'])
        this.transform_2 = transform_2
        this.transform_1 = transform_1
        this.mult_matrix = mult_matrix
        this.offset_matrix_plug = matrix_plug
        this.decompose_matrix = decompose_matrix
        return this

    def teardown(self):
        super().teardown()
        self.controller.schedule_objects_for_deletion(
            self.mult_matrix,
            self.decompose_matrix
        )


class PointMatrixConstraint(MatrixConstraint):

    suffix = 'Pmxc'

    @classmethod
    def create(cls, *args, **kwargs):
        this = super().create(*args, **kwargs)
        this.decompose_matrix.plugs['outputTranslate'].connect_to(args[-1].plugs['translate'])
        return this


class OrientMatrixConstraint(MatrixConstraint):

    rotation_plug = ObjectProperty(
        name='rotation_plug'
    )

    suffix = 'Omxc'

    @classmethod
    def create(cls, controller, *args, **kwargs):
        this = super().create(
            controller,
            *args,
            **kwargs
        )
        transform = args[-1]
        if type(transform) == Joint:
            euler_to_quat = transform.create_child(
                DependNode,
                node_type='eulerToQuat',
                root_name=this.root_name
            )
            quat_invert = transform.create_child(
                DependNode,
                node_type='quatInvert',
                root_name=this.root_name
            )
            quat_product = transform.create_child(
                DependNode,
                node_type='quatProd',
                root_name=this.root_name
            )
            quat_to_euler = transform.create_child(
                DependNode,
                node_type='quatToEuler',
                root_name=this.root_name
            )
            transform.plugs['jointOrient'].connect_to(euler_to_quat.plugs['inputRotate'])
            euler_to_quat.plugs['outputQuat'].connect_to(quat_invert.plugs['inputQuat'])
            this.decompose_matrix.plugs['outputQuat'].connect_to(quat_product.plugs['input1Quat'])
            quat_invert.plugs['outputQuat'].connect_to(quat_product.plugs['input2Quat'])
            quat_product.plugs['outputQuat'].connect_to(quat_to_euler.plugs['inputQuat'])
            this.rotation_plug = quat_to_euler.plugs['outputRotate']
        else:
            this.rotation_plug = this.decompose_matrix.plugs['outputRotate']
        this.rotation_plug.connect_to(transform.plugs['rotate'])
        return this


class ParentMatrixConstraint(PointMatrixConstraint, OrientMatrixConstraint):
    suffix = 'Prmxc'

    @classmethod
    def create(cls, *args, **kwargs):
        shear = kwargs.pop('shear', False)
        this = super().create( *args, **kwargs )
        this.decompose_matrix.plugs['outputScale'].connect_to(this.transform_2.plugs['scale'])
        if shear:  # To support uneven scale from a differently oriented target
            this.decompose_matrix.plugs['outputShear'].connect_to(this.transform_2.plugs['shear'])
        return this


class ScaleShearMatrixConstraint(MatrixConstraint):
    suffix = 'Ssmxc'

    @classmethod
    def create(cls, *args, **kwargs):
        this = super().create(
            *args,
            **kwargs
        )
        this.decompose_matrix.plugs['outputScale'].connect_to(this.transform.plugs['scale'])
        return this


class ParentMatrixBlendConstraint(OrientMatrixConstraint):

    weight_plug = ObjectProperty(
        name='weight_plug'
    )

    suffix = 'Pbmxc'

    @classmethod
    def create(cls, *args, **kwargs):
        this = super().create(
            *args,
            **kwargs
        )
        kwargs.setdefault('skip_scale', True)
        transform_2 = this.transform_2

        # Remove existing output from OrientMatrixConstraint
        this.rotation_plug.disconnect_from(transform_2.plugs['rotate'])

        # Create pairBlend to enable weighting the influence on/off
        pair_blend = transform_2.create_child(
            DependNode,
            node_type='pairBlend',
            root_name=this.root_name
        )
        pair_blend.plugs['rotInterpolation'].set_value(1)  # Quaternion Rot Interpolation
        this.decompose_matrix.plugs['outputTranslate'].connect_to(pair_blend.plugs['inTranslate2'])
        this.rotation_plug.connect_to(pair_blend.plugs['inRotate2'])
        pair_blend.plugs['outTranslate'].connect_to(transform_2.plugs['translate'])
        pair_blend.plugs['outRotate'].connect_to(transform_2.plugs['rotate'])
        this.weight_plug = pair_blend.plugs['weight']
        this.weight_plug.set_value(1.0)

        if not kwargs['skip_scale']:
            # Blend scale value too
            vector_blend = transform_2.create_child(
                DependNode,
                node_type='blendColors',
                root_name=this.root_name
            )
            this.decompose_matrix.plugs['outputScale'].connect_to(vector_blend.plugs['color1'])
            vector_blend.plugs['color2'].set_value([1, 1, 1])  # Assumes default scale of 1
            this.weight_plug.connect_to(vector_blend.plugs['blender'])
            vector_blend.plugs['output'].connect_to(transform_2.plugs['scale'])

        return this


class AddLocalsConstraint(BaseObject):
    """
    adds local matrix of all drivers and connects the result to driven directly.
    acts similar to world matrix connection, but more efficient as it only considers
    given drivers and ignores nodes above them
    """
    parent = ObjectProperty(
        name='parent'
    )

    child = ObjectProperty(
        name='child'
    )

    mult_matrix = ObjectProperty(
        name='mult_matrix'
    )

    decompose_matrix = ObjectProperty(
        name='decompose_matrix'
    )

    suffix = 'Mxc'

    @classmethod
    def create(cls, *args, **kwargs):
        if len(args) < 2:
            raise Exception(
                'Cannot make %s with less than 2 transforms passed arguments' % cls.__name__
            )
        if not all([isinstance(x, Transform) for x in args]):
            raise Exception(
                'You must use "Transform" node_objects as arguments when you create a "%s"' % cls.__name__
            )
        drivers = args[:-1]
        driven = args[-1]
        kwargs.setdefault('root_name', driven.root_name)
        kwargs['segment_name'] = driven.segment_name

        # if spline_part.disconnected_joint is True, then pass part.joints_group to offset_transform
        offset_transform = kwargs.get('offset_transform')

        if driven.functionality_name and driven.suffix:
            kwargs.setdefault('functionality_name', '%s%s' % (
                driven.functionality_name,
                driven.suffix
            ))
        elif driven.functionality_name:
            kwargs.setdefault('functionality_name', driven.functionality_name)
        elif driven.suffix:
            kwargs.setdefault('functionality_name', driven.suffix)
        kwargs.setdefault('side', driven.side)
        kwargs.setdefault('index', driven.index)

        this = super().create(**kwargs)
        mult_matrix = driven.create_child(
            DependNode,
            node_type='multMatrix',
            index=0
        )
        decompose_matrix = driven.create_child(
            DependNode,
            node_type='decomposeMatrix'
        )

        for i, driver in enumerate(reversed(drivers)):
            driver.plugs['matrix'].connect_to(mult_matrix.plugs['matrixIn'].element(i))

        if offset_transform:
            offset_transform.plugs['inverseMatrix'].connect_to(mult_matrix.plugs['matrixIn'].element(i + 1))

        mult_matrix.plugs['matrixSum'].connect_to(decompose_matrix.plugs['inputMatrix'])

        decompose_matrix.plugs['outputTranslate'].connect_to(driven.plugs['translate'])
        decompose_matrix.plugs['outputRotate'].connect_to(driven.plugs['rotate'])
        decompose_matrix.plugs['outputScale'].connect_to(driven.plugs['scale'])

        return this


def create_matrix_space_switcher(*handles):
    """
    GET THIS WORKING

    """
    handle = handles[-1]
    targets = handles[:-1]
    handle_parent = handle.parent
    controller = handle.controller
    root_name = handle.name
    if handle_parent is None:
        raise Exception("Transform has no parent.")

    this = controller.create_object(
        MatrixSpaceSwitcher,
        root_name=root_name,
        parent=handle
    )
    mult_matrix = handle.create_child(
        DependNode,
        node_type='multMatrix',
        root_name=root_name,
        parent=handle
    )
    decompose_matrix = handle.create_child(
        DependNode,
        node_type='decomposeMatrix',
        root_name=root_name,
        parent=handle
    )
    space_choice = handle.create_child(
        DependNode,
        node_type='choice',
        root_name='%s_space_choice' % root_name,
        parent=handle
    )
    offset_choice = handle.create_child(
        DependNode,
        node_type='choice',
        root_name='%s_offset_choice' % root_name,
        parent=handle
    )
    handle.create_plug(
        'space',
        at='enum',
        k=True,
        en=':'.join(map(str, targets))
    )
    default_matrix_data = list(Matrix())
    handle_inverse_matrix = Matrix(
        *handle.plugs['worldMatrix'].element(0).get_value(default_matrix_data)
    )
    for index in range(len(targets)):
        world_inverse_matrix = Matrix(
            *targets[index].plugs['worldInverseMatrix'].element(0).get_value(default_matrix_data)
        )
        offset_matrix = world_inverse_matrix * handle_inverse_matrix
        matrix_plug = offset_choice.create_plug(
            '%s_offset' % targets[index],
            at='matrix'
        )
        matrix_plug.set_value(offset_matrix.data)
        matrix_plug.connect_to(offset_choice.plugs['input'].element(index))
        targets[index].plugs['worldMatrix'].element(0).connect_to(space_choice.plugs['input'].element(index))
    handle.plugs['space'].connect_to(space_choice.plugs['selector'])
    handle.plugs['space'].connect_to(offset_choice.plugs['selector'])

    offset_choice.plugs['output'].connect_to(mult_matrix.plugs['matrixIn'].element(0))
    space_choice.plugs['output'].connect_to(mult_matrix.plugs['matrixIn'].element(1))

    if handle_parent.parent:
        handle_parent.parent.plugs['worldInverseMatrix'].element(0).connect_to(mult_matrix.plugs['matrixIn'].element(2))

    mult_matrix.plugs['matrixSum'].connect_to(decompose_matrix.plugs['inputMatrix'])

    this.handle = handle
    this.targets = targets
    this.decompose_matrix = decompose_matrix
    this.utility_nodes = [mult_matrix, offset_choice, space_choice]
    return this
