import logging
from Snowman3.rigger.rig_factory.objects.base_objects.properties import ObjectListProperty, ObjectProperty
from Snowman3.rigger.rig_factory.objects.node_objects.depend_node import DependNode
from Snowman3.rigger.rig_factory.objects.node_objects.transform import Transform
from Snowman3.rigger.rig_factory.objects.node_objects.joint import Joint
from Snowman3.rigger.rig_factory.objects.node_objects.mesh import Mesh
from Snowman3.rigger.rig_factory.objects.node_objects.shader import Shader

from Snowman3.rigger.rig_factory.objects.node_objects.plug import Plug
import Snowman3.rigger.rig_factory.utilities.decorators as dec
from Snowman3.rigger.rig_math.matrix import Matrix


class LocalConstraint(Transform):

    targets = ObjectListProperty( name='targets' )
    transform = ObjectProperty( name='transform' )

    def get_weight_plug(self, target):
        return self.plugs[extract_segment_name(target.name)]


@dec.flatten_args
def create_matrix_constraint(
    *transforms,
    **kwargs
):
    if len(transforms) < 3:
        raise Exception(
            'you must provide at-least 3 transforms. provided: %s' % [x.name for x in transforms]
        )
    if 'rotate_type' in kwargs:
        raise Exception()
    skip_rotate_x = kwargs.get('skip_rotate_x', False)
    skip_rotate_y = kwargs.get('skip_rotate_y', False)
    skip_rotate_z = kwargs.get('skip_rotate_z', False)
    maintain_offset = kwargs.get('maintain_offset', False)
    use_blend_weighted = kwargs.get('use_blend_weighted', False)
    connect_scale = kwargs.get('connect_scale', False)
    connect_rotate = kwargs.get('connect_rotate', False)
    connect_translate = kwargs.get('connect_translate', False)
    interpolation = kwargs.get('interpolation', 'quaternions')

    name = kwargs.get('name', None)

    interpolation_dict = dict(
        euler=0,
        quaternions=1
    )
    if interpolation not in interpolation_dict:
        raise Exception('Invalid interpolation value: %s. Try one of the following : %s' % (
            interpolation,
            interpolation_dict.keys()
        )
                        )

    common_ancestor = get_common_ancestor(*transforms)

    segment_name = ''
    for transform in transforms:
        segment_name += extract_segment_name(transform.name)

    if name:
        segment_name += name

    parents = transforms[:-1]
    child = transforms[-1]

    if list(set([x.plugs['rotateOrder'].get_value() for x in transforms])) != 1:
        logging.getLogger('rig_build').critical(
            'create_matrix_constraint found mismatched rotate order values on : %s' % [x.name for x in transforms]
        )

    this = child.create_child(
        LocalConstraint,
        suffix='Mtc'
    )
    this.transform = child
    this.targets = parents

    add_weights = child.create_child(
        DependNode,
        segment_name='%sAddWeights' % segment_name,
        node_type='plusMinusAverage'
    )

    mult_matrix = child.create_child(
        DependNode,
        segment_name='%sAddWeightedMatrices' % segment_name,
        node_type='multMatrix'
    )

    for i, parent in enumerate(parents):
        weight_plug = this.create_plug(
            extract_segment_name(parent.name),
            at='double',
            dv=1.0,
            k=True,
            min=0.0
        )
        if maintain_offset:
            parent = parent.create_child(
                Transform,
                matrix=child.get_matrix(),
                segment_name='%s%sOffset' % (
                    extract_segment_name(parent.name),
                    segment_name
                )
            )
        out_plug = get_local_matrix_out_plug(
            common_ancestor,
            parent,
            name=name
        )

        decompose_matrix = parent.create_child(
            DependNode,
            segment_name='%s%sDecomposeMatrix' % (
                extract_segment_name(parent.name),
                segment_name
            ),
            node_type='decomposeMatrix'
        )
        pair_blend = parent.create_child(
            DependNode,
            segment_name='%s%sMatrixBlender' % (
                extract_segment_name(parent.name),
                segment_name
            ),
            node_type='pairBlend'
        )
        compose_matrix = child.create_child(
            DependNode,
            segment_name='%s%sComposeMatrix' % (
                extract_segment_name(parent.name),
                segment_name
            ),
            node_type='composeMatrix'
        )
        multiply = parent.create_child(
            DependNode,
            segment_name='%s%sWeightedMultiply' % (
                extract_segment_name(parent.name),
                segment_name
            ),
            node_type='multiplyDivide'
        )
        condition = parent.create_child(
            DependNode,
            segment_name='%s%sWeightedCondition' % (
                extract_segment_name(parent.name),
                segment_name
            ),
            node_type='condition'
        )
        out_plug.connect_to(decompose_matrix.plugs['inputMatrix'])
        weight_plug.connect_to(add_weights.plugs['input1D'].element(i))
        weight_plug.connect_to(multiply.plugs['input1X'])
        decompose_matrix.plugs['outputTranslate'].connect_to(pair_blend.plugs['inTranslate2'])
        decompose_matrix.plugs['outputRotate'].connect_to(pair_blend.plugs['inRotate2'])
        pair_blend.plugs['rotInterpolation'].set_value(interpolation_dict[interpolation])
        pair_blend.plugs['inTranslate1'].set_value([0.0, 0.0, 0.0])
        pair_blend.plugs['inRotate1'].set_value([0.0, 0.0, 0.0])
        add_weights.plugs['output1D'].connect_to(multiply.plugs['input2X'])
        multiply.plugs['operation'].set_value(2)
        multiply.plugs['outputX'].connect_to(condition.plugs['colorIfTrueR'])
        add_weights.plugs['output1D'].connect_to(condition.plugs['firstTerm'])
        condition.plugs['operation'].set_value(1)
        condition.plugs['secondTerm'].set_value(0.0)
        condition.plugs['colorIfFalseR'].set_value(0.0)
        condition.plugs['outColorR'].connect_to(pair_blend.plugs['weight'])
        pair_blend.plugs['outRotate'].connect_to(compose_matrix.plugs['inputRotate'])
        pair_blend.plugs['outTranslate'].connect_to(compose_matrix.plugs['inputTranslate'])
        compose_matrix.plugs['useEulerRotation'].set_value(False)
        """
        If useEulerRotation is off and input is euler, how does this still work??????
        """
        # compose_matrix.plugs['inputRotateOrder'].set_value(destination_rotate_order)
        compose_matrix.plugs['outputMatrix'].connect_to(mult_matrix.plugs['matrixIn'].element(i))

    result_choice = child.create_child(
        DependNode,
        segment_name='%sResultChoice' % segment_name,
        node_type='choice'
    )

    condition = child.create_child(
        DependNode,
        segment_name='%sResultCondition' % segment_name,
        node_type='condition'
    )
    default_position = Matrix()

    for transform in get_local_ancestors(common_ancestor, child, include_self=True):
        matrix = transform.get_matrix(world_space=False)
        default_position = default_position * matrix

    result_choice.plugs['input'].element(0).set_value(list(default_position))
    offset_plug = mult_matrix.create_plug('DefaultOffset', at='matrix')
    offset_plug.set_value(default_position)
    offset_plug.connect_to(result_choice.plugs['input'].element(0))
    mult_matrix.plugs['matrixSum'].connect_to(result_choice.plugs['input'].element(1))
    condition.plugs['operation'].set_value(1)
    add_weights.plugs['output1D'].connect_to(condition.plugs['firstTerm'])
    condition.plugs['secondTerm'].set_value(0.0)
    condition.plugs['colorIfFalseR'].set_value(0.0)
    condition.plugs['colorIfTrueR'].set_value(1.0)
    condition.plugs['outColorR'].connect_to(result_choice.plugs['selector'])

    in_plug = get_local_matrix_in_plug(
        common_ancestor,
        child,
        use_blend_weighted=use_blend_weighted,
        connect_scale=connect_scale,
        connect_translate=connect_translate,
        connect_rotate=connect_rotate,
        skip_rotate_x=skip_rotate_x,
        skip_rotate_y=skip_rotate_y,
        skip_rotate_z=skip_rotate_z,
        name=name
    )
    result_choice.plugs['output'].connect_to(in_plug)
    return this


def create_point_constraint(
    *transforms,
    **kwargs
):
    kwargs['connect_translate'] = True
    kwargs['connect_rotate'] = False
    kwargs['connect_scale'] = False
    kwargs['name'] = 'Point'
    return create_matrix_constraint(
        *transforms,
        **kwargs
    )

def create_orient_constraint(
    *transforms,
    **kwargs
):
    kwargs['connect_translate'] = False
    kwargs['connect_rotate'] = True
    kwargs['connect_scale'] = False
    kwargs['name'] = 'Orient'
    return create_matrix_constraint(
        *transforms,
        **kwargs
    )

def create_parent_constraint(
    *transforms,
    **kwargs
):
    kwargs['connect_translate'] = True
    kwargs['connect_rotate'] = True
    kwargs['name'] = 'Parent'
    return create_matrix_constraint(
        *transforms,
        **kwargs
    )


def create_local_parent_constraint(
    parent,
    child,
    maintain_offset=False,
    use_blend_weighted=False,
    connect_scale=False,
    skip_rotate_x=False,
    skip_rotate_y=False,
    skip_rotate_z=False,
):
    common_ancestor = get_common_ancestor(parent, child)
    if maintain_offset:
        parent = parent.create_child(
            Transform,
            segment_name='%s%sParentOffset' % (
                extract_segment_name(parent.name),
                extract_segment_name(child.name)
            ),
            matrix=child.get_matrix()
        )

    local_parent_plug = get_local_matrix_out_plug(common_ancestor, parent)
    local_child_in_plug = get_local_matrix_in_plug(
        common_ancestor,
        child,
        use_blend_weighted=use_blend_weighted,
        connect_scale=connect_scale,
        skip_rotate_x=skip_rotate_x,
        skip_rotate_y=skip_rotate_y,
        skip_rotate_z=skip_rotate_z,

    )
    local_parent_plug.connect_to(local_child_in_plug)


def create_local_point_constraint(parent, child, maintain_offset=False, use_blend_weighted=False):
    """
    "point constrains" one transform to another in local "part space"
    """
    common_ancestor = get_common_ancestor(parent, child)

    if maintain_offset:
        parent = parent.create_child(
            Transform,
            segment_name='%s%sPointOffset' % (
                extract_segment_name(parent.name),
                extract_segment_name(child.name)
            ),
            matrix=child.get_matrix()
        )

    local_parent_plug = get_local_matrix_out_plug(
        common_ancestor,
        parent,
        name='Point'
    )
    local_child_in_plug = get_local_matrix_in_plug(
        common_ancestor,
        child,
        connect_rotate=False,
        use_blend_weighted=use_blend_weighted,
        name='Point'
    )
    local_parent_plug.connect_to(local_child_in_plug)


def create_local_orient_constraint(
    parent,
    child,
    use_blend_weighted=False,
    maintain_offset=False,
    skip_rotate_x=False,
    skip_rotate_y=False,
    skip_rotate_z=False,
    connect_scale=False
):
    """
    "orient constrains" one transform to another in local "part space"
    """
    common_ancestor = get_common_ancestor(parent, child)

    if maintain_offset:
        parent = parent.create_child(
            Transform,
            segment_name='%s%sOrientOffset' % (
                extract_segment_name(parent.name),
                extract_segment_name(child.name)
            ),
            matrix=child.get_matrix()
        )

    local_parent_plug = get_local_matrix_out_plug(
        common_ancestor,
        parent,
        name='Orient'
    )
    local_child_in_plug = get_local_matrix_in_plug(
        common_ancestor,
        child,
        connect_translate=False,
        connect_scale=connect_scale,
        use_blend_weighted=use_blend_weighted,
        skip_rotate_x=skip_rotate_x,
        skip_rotate_y=skip_rotate_y,
        skip_rotate_z=skip_rotate_z,
        name='Orient'
    )
    local_parent_plug.connect_to(local_child_in_plug)

def create_local_scale_constraint(parent, child, maintain_offset=False, use_blend_weighted=False):
    """
    "parent constrains" one transform to another in local "part space"
    """
    common_ancestor = get_common_ancestor(parent, child)

    offset = list(child.get_matrix() * parent.get_matrix().invert_matrix()) if maintain_offset else None,

    local_parent_plug = get_local_matrix_out_plug(common_ancestor, parent, name='Scale')
    local_child_in_plug = get_local_matrix_in_plug(
        common_ancestor,
        child,
        connect_translate=False,
        connect_rotate=False,
        connect_scale=True,
        use_blend_weighted=use_blend_weighted,
        name='Scale'
    )
    local_parent_plug.connect_to(local_child_in_plug)

def create_blended_parent_constraint(part, parent1, parent2, child, blender, maintain_offset=False, rotate_type=0):
    """
    blended constraint between two transforms in local "part space"
    """
    camel_name = extract_segment_name(child.name)

    if maintain_offset:
        parent1 = parent1.create_child(
            Transform,
            segment_name='%sOffset1' % camel_name,
            matrix=child.get_matrix()
        )
        parent2 = parent2.create_child(
            Transform,
            segment_name='%sOffset1' % camel_name,
            matrix=child.get_matrix()
        )

    local_parent1_plug = get_local_matrix_out_plug(part, parent1)
    local_parent2_plug = get_local_matrix_out_plug(part, parent2)

    local_child_in_plug = get_local_matrix_in_plug(part, child)

    decompose_matrix_1 = child.create_child(
        DependNode,
        segment_name='%sDecomposeMatrix1' % camel_name,
        node_type='decomposeMatrix'
    )

    decompose_matrix_2 = child.create_child(
        DependNode,
        segment_name='%sDecomposeMatrix2' % camel_name,
        node_type='decomposeMatrix'
    )
    compose_matrix = child.create_child(
        DependNode,
        segment_name='%sComposeMatrix2' % camel_name,
        node_type='composeMatrix'
    )
    pair_blend = child.create_child(
        DependNode,
        segment_name='%sMatrixBlender' % camel_name,
        node_type='pairBlend'
    )
    pair_blend.plugs['rotInterpolation'].set_value(rotate_type)
    local_parent1_plug.connect_to(decompose_matrix_1.plugs['inputMatrix'])
    local_parent2_plug.connect_to(decompose_matrix_2.plugs['inputMatrix'])
    decompose_matrix_1.plugs['outputTranslate'].connect_to(pair_blend.plugs['inTranslate1'])
    decompose_matrix_2.plugs['outputTranslate'].connect_to(pair_blend.plugs['inTranslate2'])
    decompose_matrix_1.plugs['outputRotate'].connect_to(pair_blend.plugs['inRotate1'])
    decompose_matrix_2.plugs['outputRotate'].connect_to(pair_blend.plugs['inRotate2'])
    if isinstance(blender, Plug):
        blender.connect_to(pair_blend.plugs['weight'])
    elif isinstance(blender, (float, int)):
        pair_blend.plugs['weight'].set_value(blender)
    else:
        raise Exception('Invalid blender type: %s' % type(blender))
    decompose_matrix_2.plugs['outputTranslate'].connect_to(pair_blend.plugs['inTranslate2'])
    decompose_matrix_1.plugs['outputRotate'].connect_to(pair_blend.plugs['inRotate1'])
    pair_blend.plugs['outRotate'].connect_to(compose_matrix.plugs['inputRotate'])
    pair_blend.plugs['outTranslate'].connect_to(compose_matrix.plugs['inputTranslate'])
    compose_matrix.plugs['outputMatrix'].connect_to(local_child_in_plug)


def create_local_aim_constraint(
    aim_transform,
    driven_transform,
    aimVector='Y',
    upVector='-Z',
    upObject=None,
    use_blend_weighted=False,
    use_rotation_up=False,
    worldUpVector=None,
    common_ancestor=None,
    connect_translate=False,
    maintain_offset=False
):
    """
    "aim constrains" one transform to another in local "part space"
    """
    if worldUpVector is None:
        worldUpVector = [0.0, 0.0, -1.0]
    local_transforms = [aim_transform, driven_transform]
    if upObject:
        local_transforms.append(upObject)
    if common_ancestor is None:
        common_ancestor = get_common_ancestor(*local_transforms)

    aim_matrix_plug = create_local_aim_matrix_plug(
        aim_transform,
        driven_transform,
        aim_vector=aimVector,
        up_vector=upVector,
        use_rotation_up=use_rotation_up,
        world_up_vector=worldUpVector,
        up_object=upObject,
        common_ancestor=common_ancestor,
        maintain_offset=maintain_offset
    )
    in_plug = get_local_matrix_in_plug(
        common_ancestor,
        driven_transform,
        connect_translate=connect_translate,
        connect_rotate=True,
        connect_scale=False,
        use_blend_weighted=use_blend_weighted,
        name='Aim'
    )
    aim_matrix_plug.connect_to(in_plug)


def create_local_aim_matrix_plug(
    aim_transform,
    driven_transform,
    aim_vector='Y',
    up_vector='-Z',
    world_up_vector=None,
    use_rotation_up=False,
    up_object=None,
    common_ancestor=None,
    maintain_offset=False
):
    """
    returns a composeMatrix node that represents an "aim constraint" in local "part space"
    """

    local_transforms = [aim_transform, driven_transform]
    if up_object:
        local_transforms.append(up_object)
    if common_ancestor is None:
        common_ancestor = get_common_ancestor(*local_transforms)
    if world_up_vector is None:
        world_up_vector = [0.0, 0.0, -1.0]
    up_vector = up_vector.upper()
    aim_vector = aim_vector.upper()
    camel_name = extract_segment_name(driven_transform.name)

    if up_vector.strip('-') == aim_vector.strip('-'):
        raise Exception('Same axis provided for both up and aim vector: %s' % up_vector.strip('-'))

    invert_aim = '-' in aim_vector
    invert_up = '-' in up_vector
    aim_axis = aim_vector.strip('-')
    up_axis = up_vector.strip('-')
    cross_axis = [x for x in ['X', 'Y', 'Z'] if x not in [aim_axis, up_axis]][0]

    decompose_aim = aim_transform.create_child(
        DependNode,
        segment_name='%sDecomposeAim' % camel_name,
        node_type='decomposeMatrix'
    )

    decompose_up = aim_transform.create_child(
        DependNode,
        segment_name='%sDecomposeUp' % camel_name,
        node_type='decomposeMatrix'
    )
    get_aim_vector = driven_transform.create_child(
        DependNode,
        segment_name='%sGetAimVector' % camel_name,
        node_type='plusMinusAverage'
    )

    aim_normalize = driven_transform.create_child(
        DependNode,
        segment_name='%sAimNormalize' % camel_name,
        node_type='vectorProduct'
    )
    cross_product = driven_transform.create_child(
        DependNode,
        segment_name='%sCrossProduct' % camel_name,
        node_type='vectorProduct'
    )
    up_normalize = driven_transform.create_child(
        DependNode,
        segment_name='%sUpNormalize' % camel_name,
        node_type='vectorProduct'
    )
    up_product = driven_transform.create_child(
        DependNode,
        segment_name='%sUpProduct' % camel_name,
        node_type='vectorProduct'
    )
    get_up_vector = driven_transform.create_child(
        DependNode,
        segment_name='%sGetUpVector' % camel_name,
        node_type='plusMinusAverage'
    )
    build_matrix = driven_transform.create_child(
        DependNode,
        segment_name='%sBuildMatrix' % camel_name,
        node_type='fourByFourMatrix'
    )

    target_point = driven_transform.create_child(
        DependNode,
        segment_name='%sTargetPointMultMatrix' % camel_name,
        node_type='pointMatrixMult'
    )
    if common_ancestor == driven_transform.parent:
        aim_position_plug = driven_transform.plugs['translate']
    else:
        target_parent_matrix_plug = get_local_matrix_out_plug(common_ancestor, driven_transform.parent)
        target_parent_matrix_plug.connect_to(target_point.plugs['inMatrix'])
        driven_transform.plugs['translate'].connect_to(target_point.plugs['inPoint'])
        aim_position_plug = target_point.plugs['output']

    up_normalize.plugs['operation'].set_value(0)

    aim_matrix_plug = get_local_matrix_out_plug(common_ancestor, aim_transform)
    up_matrix_plug = get_local_matrix_out_plug(common_ancestor, up_object)
    aim_matrix_plug.connect_to(decompose_aim.plugs['inputMatrix'])
    up_matrix_plug.connect_to(decompose_up.plugs['inputMatrix'])

    get_up_vector.plugs['operation'].set_value(2)
    up_normalize.plugs['normalizeOutput'].set_value(True)

    if use_rotation_up:
        up_point_matrix_mult = driven_transform.create_child(
            DependNode,
            segment_name='%sUpPointMultMatrix' % camel_name,
            node_type='pointMatrixMult'
        )
        up_matrix_plug.connect_to(decompose_up.plugs['inputMatrix'])
        up_matrix_plug.connect_to(up_point_matrix_mult.plugs['inMatrix'])
        up_point_matrix_mult.plugs['inPoint'].set_value(world_up_vector)
        up_point_matrix_mult.plugs['output'].connect_to(get_up_vector.plugs['input3D'].element(0))
        decompose_up.plugs['outputTranslate'].connect_to(get_up_vector.plugs['input3D'].element(1))
    else:

        decompose_up.plugs['outputTranslate'].connect_to(get_up_vector.plugs['input3D'].element(0))
        aim_position_plug.connect_to(get_up_vector.plugs['input3D'].element(1))


    get_up_vector.plugs['output3D'].connect_to(up_normalize.plugs['input1'])



    # Aim
    get_aim_vector.plugs['operation'].set_value(2)
    decompose_aim.plugs['outputTranslate'].connect_to(get_aim_vector.plugs['input3D'].element(0))
    target_point.plugs['output'].connect_to(get_aim_vector.plugs['input3D'].element(1))


    aim_normalize.plugs['operation'].set_value(0)
    aim_normalize.plugs['normalizeOutput'].set_value(True)
    get_aim_vector.plugs['output3D'].connect_to(aim_normalize.plugs['input1'])

    cross_product.plugs['operation'].set_value(2)
    cross_product.plugs['normalizeOutput'].set_value(True)

    aim_vector_plug = aim_normalize.plugs['output']

    if invert_aim:
        invert_aim_multiply = driven_transform.create_child(
            DependNode,
            segment_name='%sInvertAim' % driven_transform.segment_name,
            node_type='multiplyDivide'
        )
        aim_vector_plug.connect_to(invert_aim_multiply.plugs['input1'])
        invert_aim_multiply.plugs['input2'].set_value([-1.0, -1.0, -1.0])
        aim_vector_plug = invert_aim_multiply.plugs['output']

    aim_vector_plug.connect_to(cross_product.plugs['input1'])

    up_vector_plug = up_normalize.plugs['output']
    if invert_up:
        invert_up_multiply = driven_transform.create_child(
            DependNode,
            segment_name='%sInvertUp' % driven_transform.segment_name,
            node_type='multiplyDivide'
        )
        up_vector_plug.connect_to(invert_up_multiply.plugs['input1'])
        invert_up_multiply.plugs['input2'].set_value([-1.0, -1.0, -1.0])
        up_vector_plug = invert_up_multiply.plugs['output']

    up_vector_plug.connect_to(cross_product.plugs['input2'])

    up_product.plugs['normalizeOutput'].set_value(False)
    up_product.plugs['operation'].set_value(2)

    cross_product.plugs['output'].connect_to(up_product.plugs['input1'])
    aim_vector_plug.connect_to(up_product.plugs['input2'])

    up_output_plug = up_product.plugs['output']
    aim_output_plug = aim_vector_plug

    matrix_vector_plugs = dict(
        X=['in00', 'in01', 'in02'],
        Y=['in10', 'in11', 'in12'],
        Z=['in20', 'in21', 'in22']
    )

    for i, plug_name in enumerate(matrix_vector_plugs[aim_axis]):
        aim_output_plug[i].connect_to(build_matrix.plugs[plug_name])

    for i, plug_name in enumerate(matrix_vector_plugs[up_axis]):
        up_output_plug[i].connect_to(build_matrix.plugs[plug_name])

    for i, plug_name in enumerate(matrix_vector_plugs[cross_axis]):
        cross_product.plugs['output'][i].connect_to(build_matrix.plugs[plug_name])  # Inverse??

    target_point.plugs['output'][0].connect_to(build_matrix.plugs['in30'])
    target_point.plugs['output'][1].connect_to(build_matrix.plugs['in31'])
    target_point.plugs['output'][2].connect_to(build_matrix.plugs['in32'])

    result_plug = build_matrix.plugs['output']

    if maintain_offset:
        offset_mult_matrix = driven_transform.create_child(
            DependNode,
            segment_name='%sOffsetMult' % driven_transform.segment_name,
            node_type='multMatrix'
        )
        result_plug.connect_to(offset_mult_matrix.plugs['matrixIn'].element(0))
        offset_matrix_plug = offset_mult_matrix.create_plug(
            'OffsetMatrix',
            at='matrix'
        )

        offset_matrix_plug.set_value(
            driven_transform.get_matrix() * Matrix(result_plug.get_value()).invert_matrix()
        )
        offset_matrix_plug.connect_to(offset_mult_matrix.plugs['matrixIn'].element(1))
        result_plug = offset_mult_matrix.plugs['matrixSum']

    return result_plug


def get_local_curve_matrix(
    part,
    nurbs_curve,
    up_transform,
    target_transform,
    paremeter_plug,
    aim_vector='Y',
    up_vector='-Z'
):
    """
    creates a matrix node that can be used to connect a transform to a curve in local "part space"
    """
    up_vector = up_vector.upper()
    aim_vector = aim_vector.upper()
    camel_name = extract_segment_name(target_transform.name)

    if up_vector.strip('-') == aim_vector.strip('-'):
        raise Exception('Same axis provided for both up and aim vector: %s' % up_vector.strip('-'))

    invert_aim = '-' in aim_vector
    invert_up = '-' in up_vector
    aim_axis = aim_vector.strip('-')
    up_axis = up_vector.strip('-')
    cross_axis = [x for x in ['X', 'Y', 'Z'] if x not in [aim_axis, up_axis]][0]

    up_transform_plug = get_local_double3_out_plug(part, up_transform)

    point_on_curve_info = target_transform.create_child(
        DependNode,
        segment_name='%sPointOnCurve' % camel_name,
        node_type='pointOnCurveInfo'
    )

    get_up_vector = target_transform.create_child(
        DependNode,
        segment_name='%sGetUpVector' % camel_name,
        node_type='plusMinusAverage'
    )

    up_normalize = target_transform.create_child(
        DependNode,
        segment_name='%sUpNormalize' % camel_name,
        node_type='vectorProduct'
    )

    cross_product = target_transform.create_child(
        DependNode,
        segment_name='%sCrossProduct' % camel_name,
        node_type='vectorProduct'
    )

    up_product = target_transform.create_child(
        DependNode,
        segment_name='%sUpProduct' % camel_name,
        node_type='vectorProduct'
    )

    build_matrix = target_transform.create_child(
        DependNode,
        segment_name='%sBuildMatrix' % camel_name,
        node_type='fourByFourMatrix'
    )
    point_on_curve_info.plugs['turnOnPercentage'].set_value(True)
    nurbs_curve.plugs['local'].connect_to(point_on_curve_info.plugs['inputCurve'])
    paremeter_plug.connect_to(point_on_curve_info.plugs['parameter'])

    get_up_vector.plugs['operation'].set_value(2)
    up_transform_plug.connect_to(get_up_vector.plugs['input3D'].element(0))
    point_on_curve_info.plugs['position'].connect_to(get_up_vector.plugs['input3D'].element(1))

    up_normalize.plugs['operation'].set_value(0)
    up_normalize.plugs['normalizeOutput'].set_value(True)
    get_up_vector.plugs['output3D'].connect_to(up_normalize.plugs['input1'])

    cross_product.plugs['operation'].set_value(2)
    cross_product.plugs['normalizeOutput'].set_value(True)

    aim_vector_plug = point_on_curve_info.plugs['normalizedTangent']
    if invert_aim:
        invert_aim_multiply = target_transform.create_child(
            DependNode,
            segment_name='%sInvertAim' % camel_name,
            node_type='multiplyDivide'
        )
        aim_vector_plug.connect_to(invert_aim_multiply.plugs['input1'])
        invert_aim_multiply.plugs['input2'].set_value([-1.0, -1.0, -1.0])
        aim_vector_plug = invert_aim_multiply.plugs['output']

    aim_vector_plug.connect_to(cross_product.plugs['input1'])

    up_vector_plug = up_normalize.plugs['output']
    if invert_up:
        invert_up_multiply = target_transform.create_child(
            DependNode,
            segment_name='%sInvertUp' % camel_name,
            node_type='multiplyDivide'
        )
        up_vector_plug.connect_to(invert_up_multiply.plugs['input1'])
        invert_up_multiply.plugs['input2'].set_value([-1.0, -1.0, -1.0])
        up_vector_plug = invert_up_multiply.plugs['output']

    up_vector_plug.connect_to(cross_product.plugs['input2'])

    up_product.plugs['normalizeOutput'].set_value(False)
    up_product.plugs['operation'].set_value(2)

    cross_product.plugs['output'].connect_to(up_product.plugs['input1'])
    aim_vector_plug.connect_to(up_product.plugs['input2'])

    up_output_plug = up_product.plugs['output']
    aim_output_plug = aim_vector_plug

    matrix_vector_plugs = dict(
        X=['in00', 'in01', 'in02'],
        Y=['in10', 'in11', 'in12'],
        Z=['in20', 'in21', 'in22']
    )

    for i, plug_name in enumerate(matrix_vector_plugs[aim_axis]):
        aim_output_plug[i].connect_to(build_matrix.plugs[plug_name])

    for i, plug_name in enumerate(matrix_vector_plugs[up_axis]):
        up_output_plug[i].connect_to(build_matrix.plugs[plug_name])

    for i, plug_name in enumerate(matrix_vector_plugs[cross_axis]):
        cross_product.plugs['output'][i].connect_to(build_matrix.plugs[plug_name])  # Inverse??

    point_on_curve_info.plugs['position'][0].connect_to(build_matrix.plugs['in30'])
    point_on_curve_info.plugs['position'][1].connect_to(build_matrix.plugs['in31'])
    point_on_curve_info.plugs['position'][2].connect_to(build_matrix.plugs['in32'])

    return build_matrix


def connect_to_local_curve(
    part,
    nurbs_curve,
    up_transform,
    target_transform,
    paremeter_plug,
    aim_vector='Y',
    up_vector='-Z',
    maintain_offset=False
):
    """
    connects a transform to a curve in local "part space"
    """
    camel_name = extract_segment_name(target_transform.name)
    curve_matrix = get_local_curve_matrix(
        part,
        nurbs_curve,
        up_transform,
        target_transform,
        paremeter_plug,
        aim_vector=aim_vector,
        up_vector=up_vector
    )
    matrix_plug = curve_matrix.plugs['output']
    if maintain_offset:
        multiply_offset_matrix = target_transform.create_child(
            DependNode,
            segment_name='%sMatrixCurveOffset' % camel_name,
            node_type='multMatrix'
        )
        offset_matrix_plug = multiply_offset_matrix.create_plug('OffsetFromCurveMatrix', at='matrix')
        matrix_plug.connect_to(multiply_offset_matrix.plugs['matrixIn'].element(0))
        # offset_matrix_plug.set_value(target_transform.get_matrix() * Matrix(matrix_plug.get_value()).invert_matrix())
        offset_matrix_plug.connect_to(multiply_offset_matrix.plugs['matrixIn'].element(1))
        matrix_plug = multiply_offset_matrix.plugs['matrixSum']
    decompose_matrix = target_transform.create_child(
        DependNode,
        segment_name='%sDecomposeMatrix' % camel_name,
        node_type='decomposeMatrix'
    )
    tangent_pair_blend = target_transform.create_child(
        DependNode,
        segment_name='%sTangentPairBlend' % target_transform.segment_name,
        node_type='pairBlend'
    )
    matrix_plug.connect_to(decompose_matrix.plugs['inputMatrix'])
    tangent_pair_blend.plugs['rotInterpolation'].set_value(1)
    tangent_pair_blend.plugs['inRotate1'].set_value(decompose_matrix.plugs['outputRotate'].get_value())
    decompose_matrix.plugs['outputRotate'].connect_to(tangent_pair_blend.plugs['inRotate2'])
    tangent_pair_blend.plugs['outRotate'].connect_to(target_transform.plugs['rotate'])
    decompose_matrix.plugs['outputTranslate'].connect_to(target_transform.plugs['translate'])
    return tangent_pair_blend


def get_common_ancestor(*transforms):
    for item in transforms:
        if not isinstance(item, Transform):
            raise Exception('Invalid type : %s' % type(item))
    if transforms[0] in transforms[1:]:
        raise Exception('Duplicate transform found : %s' % transforms[0])
    ancestor_lists = [get_ancestors(x, reverse=True) for x in transforms]
    for ancestor in ancestor_lists[0]:
        if all([ancestor in x for x in ancestor_lists[1:]]):
            return ancestor
    raise Exception('Common ancestor not found for : %s' % [x.name for x in transforms])


def get_ancestors(transform, include_self=False, reverse=False):
    """
    Gets all ancestor transforms up to (but not including) the root_transform
    Used to calculate transform positions in local "part" space
    """
    ancestors = []
    if include_self:
        ancestors.append(transform)
    parent = transform.parent
    while parent is not None:
        if reverse:
            ancestors.append(parent)
        else:
            ancestors.insert(0, parent)
        parent = parent.parent
    return ancestors


def get_local_ancestors(parent_group, transform, include_self=False, reverse=False):
    """
    Gets all ancestor transforms up to (but not including) the root_transform
    Used to calculate transform positions in local "part" space
    """
    ancestors = []
    if include_self:
        ancestors.append(transform)
    parent = transform.parent
    while parent != parent_group:
        if parent is None:
            raise Exception('%s does not seem to be a child of %s' % (transform.name, parent_group.name))
        if reverse:
            ancestors.append(parent)
        else:
            ancestors.insert(0, parent)
        parent = parent.parent
    return ancestors


def get_local_double3_out_plug(self, transform, plug_name='translate'):
    """
    returns a local (part) space plug that can be used to output a translate from a transform
    """
    if hasattr(self, 'local_translate_out_plugs') and transform.name in self.local_translate_out_plugs:
        up_transform_plug = self.local_translate_out_plugs[transform.name]
    else:
        camel_name = extract_segment_name(transform.name)
        sources = get_local_ancestors(
            self,
            transform,
            include_self=True
        )
        add_node = transform.create_child(
            DependNode,
            segment_name='%sAddTranslateOut' % camel_name,
            node_type='plusMinusAverage'
        )
        for i, source in enumerate(sources):
            source.plugs[plug_name].connect_to(add_node.plugs['input3D'].element(i))
        up_transform_plug = add_node.plugs['output3D']
        if hasattr(self, 'local_translate_out_plugs'):
            self.local_translate_out_plugs[transform.name] = up_transform_plug
    return up_transform_plug


def get_local_double3_in_plug(self, transform, plug_name='translate'):
    """
    returns a local (part) space plug that can be used to control a parented transforms translate values
    """
    if hasattr(self, 'local_translate_in_plugs') and transform.name in self.local_translate_in_plugs:
        raise Exception('Local translate in-plug already established for %s' % transform.name)
    else:
        camel_name = extract_segment_name(transform.name)
        sources = get_local_ancestors(transform)
        add_node = transform.create_child(
            DependNode,
            segment_name='%sAddLocalTranslates' % camel_name,
            node_type='plusMinusAverage'
        )
        for i, source in enumerate(sources):
            source.plugs[plug_name].connect_to(add_node.plugs['input3D'].element(i + 1))
        add_node.plugs['output3D'].connect_to(transform.plugs[plug_name])
        local_matrix_in_plug = add_node.plugs['input3D'].element(0)
        return local_matrix_in_plug


def get_local_matrix_out_plug(base_transform, transform, name=None):
    """
    returns a local (part) space plug that can be used to output a matrix from a transform
    """
    local_matrix_key = '%s_LOCAL_OUT_MATRIX' % base_transform.name
    if local_matrix_key in transform.relationships:
        return transform.relationships[local_matrix_key]
    elif base_transform == transform:
        return transform.plugs['matrix']
    else:
        parent_camel_name = extract_segment_name(base_transform.name)
        camel_name = extract_segment_name(transform.name)
        segment_name = '%s%sMultiplyLocalOutMatrices' % (
            parent_camel_name,
            camel_name
        )
        if name:
            segment_name = segment_name + name
        sources = get_local_ancestors(
            base_transform,
            transform,
            include_self=True,
            reverse=True
        )
        mult_matrix = transform.create_child(
            DependNode,
            segment_name=segment_name,
            node_type='multMatrix'
        )
        for i, source in enumerate(sources):
            source.plugs['matrix'].connect_to(mult_matrix.plugs['matrixIn'].element(i))
        local_matrix_out_plug = mult_matrix.plugs['matrixSum']
        transform.relationships[local_matrix_key] = local_matrix_out_plug
        return local_matrix_out_plug


def get_local_matrix_in_plug(
    self,
    transform,
    connect_translate=True,
    connect_rotate=True,
    connect_scale=False,
    use_blend_weighted=False,
    skip_rotate_x=False,
    skip_rotate_y=False,
    skip_rotate_z=False,
    name=None
):
    """
    returns a local (part) space plug that can be used to control a parented transforms matrix
    """

    if not self.controller.scene.mock:
        translate_in_connections = self.controller.scene.listConnections(
            transform.plugs['translate'].name,
            s=True,
            d=False
        )
        rotate_in_connections = self.controller.scene.listConnections(
            transform.plugs['rotate'].name,
            s=True,
            d=False
        )
        scale_in_connections = self.controller.scene.listConnections(
            transform.plugs['scale'].name,
            s=True,
            d=False
        )
        if connect_translate and translate_in_connections:
            raise Exception('%s is already connected' % transform.plugs['translate'].name)
        if connect_rotate and rotate_in_connections:
            raise Exception('%s is already connected' % transform.plugs['rotate'].name)
        if connect_scale and scale_in_connections:
            raise Exception('%s is already connected' % transform.plugs['scale'].name)

    camel_name = '%s%s' % (
        extract_segment_name(self.name),
        extract_segment_name(transform.name)
    )
    if name:
        camel_name = camel_name + name
    sources = get_local_ancestors(self, transform)
    mult_matrix = transform.create_child(
        DependNode,
        segment_name='%sMultiplyLocalInMatrices' % camel_name,
        node_type='multMatrix'
    )
    i = 0
    for source in sources:
        source.plugs['inverseMatrix'].connect_to(mult_matrix.plugs['matrixIn'].element(i + 1))
        i += 1

    connect_matrix_plug_to_transform(
        mult_matrix.plugs['matrixSum'],
        transform,
        connect_rotate=connect_rotate,
        connect_scale=connect_scale,
        connect_translate=connect_translate,
        use_blend_weighted=use_blend_weighted,
        skip_rotate_x=skip_rotate_x,
        skip_rotate_y=skip_rotate_y,
        skip_rotate_z=skip_rotate_z,
        name=name
    )

    local_matrix_in_plug = mult_matrix.plugs['matrixIn'].element(0)

    if hasattr(self, 'local_matrix_in_plug'):
        self.local_matrix_in_plugs[transform.name] = local_matrix_in_plug
    return local_matrix_in_plug


def connect_matrix_plug_to_transform(
    matrix_plug,
    transform,
    connect_rotate=True,
    connect_translate=True,
    connect_scale=False,
    use_blend_weighted=False,
    skip_rotate_x=False,
    skip_rotate_y=False,
    skip_rotate_z=False,
    name=None
):

    camel_name = extract_segment_name(transform.name)
    if name:
        camel_name = camel_name + name

    decompose_matrix = transform.create_child(
        DependNode,
        segment_name='%sDecomposeMatrix' % camel_name,
        node_type='decomposeMatrix'
    )

    matrix_plug.connect_to(decompose_matrix.plugs['inputMatrix'])
    translate_plug = decompose_matrix.plugs['outputTranslate']
    scale_plug = decompose_matrix.plugs['outputScale']

    rotate_plug_x = decompose_matrix.plugs['outputRotateX']
    rotate_plug_y = decompose_matrix.plugs['outputRotateY']
    rotate_plug_z = decompose_matrix.plugs['outputRotateZ']

    if isinstance(transform, Joint):

        euler_to_quat = transform.create_child(
            DependNode,
            segment_name='%sEulerToQuat' % camel_name,
            node_type='eulerToQuat'
        )
        quat_invert = transform.create_child(
            DependNode,
            segment_name='%sQuatInvert' % camel_name,
            node_type='quatInvert'
        )
        quat_prod = transform.create_child(
            DependNode,
            segment_name='%sQuatProd' % camel_name,
            node_type='quatProd'
        )
        quat_to_euler = transform.create_child(
            DependNode,
            segment_name='%sQuatToEuler' % camel_name,
            node_type='quatToEuler'
        )
        transform.plugs['jointOrient'].connect_to(euler_to_quat.plugs['inputRotate'])
        euler_to_quat.plugs['outputQuat'].connect_to(quat_invert.plugs['inputQuat'])
        decompose_matrix.plugs['outputQuat'].connect_to(quat_prod.plugs['input1Quat'])
        quat_invert.plugs['outputQuat'].connect_to(quat_prod.plugs['input2Quat'])
        quat_prod.plugs['outputQuat'].connect_to(quat_to_euler.plugs['inputQuat'])
        rotate_plug_x = quat_to_euler.plugs['outputRotateX']
        rotate_plug_y = quat_to_euler.plugs['outputRotateY']
        rotate_plug_z = quat_to_euler.plugs['outputRotateZ']
    if use_blend_weighted:
        # Inserting a blendWeighted node allows the target plug values to be changed while still being connected.
        # This is usefull in cases like the jaw when we want to drive sdks with a constrained transform
        if connect_rotate:
            if not skip_rotate_x:
                rotate_plug_x.blend_weighted().connect_to(transform.plugs['rotateX'])
            if not skip_rotate_y:
                rotate_plug_y.blend_weighted().connect_to(transform.plugs['rotateY'])
            if not skip_rotate_z:
                rotate_plug_z.blend_weighted().connect_to(transform.plugs['rotateZ'])
        if connect_translate:
            decompose_matrix.plugs['outputTranslateX'].blend_weighted().connect_to(transform.plugs['translateX'])
            decompose_matrix.plugs['outputTranslateX'].blend_weighted().connect_to(transform.plugs['translateY'])
            decompose_matrix.plugs['outputTranslateX'].blend_weighted().connect_to(transform.plugs['translateZ'])
        if connect_scale:
            decompose_matrix.plugs['outputScaleX'].blend_weighted().connect_to(transform.plugs['scaleX'])
            decompose_matrix.plugs['outputScaleY'].blend_weighted().connect_to(transform.plugs['scaleY'])
            decompose_matrix.plugs['outputScaleZ'].blend_weighted().connect_to(transform.plugs['scaleZ'])
    else:
        if connect_rotate:
            if not skip_rotate_x:
                rotate_plug_x.connect_to(transform.plugs['rotateX'])
            if not skip_rotate_y:
                rotate_plug_y.connect_to(transform.plugs['rotateY'])
            if not skip_rotate_z:
                rotate_plug_z.connect_to(transform.plugs['rotateZ'])
        if connect_translate:
            decompose_matrix.plugs['outputTranslate'].connect_to(transform.plugs['translate'])
        if connect_scale:
            decompose_matrix.plugs['outputScale'].connect_to(transform.plugs['scale'])


def extract_segment_name(word):
    new_word = ''.join(x.capitalize() or '_' for x in word.split(':')[-1].split('_'))
    while new_word[0].isdigit():
        new_word = new_word[1:] + new_word[0]
    return new_word

def create_joint_bubbles(joints, size=1.0):
    controller = joints[0].controller
    controller.scene.evaluationManager(mode='off')
    root = controller.root
    for joint in joints:
        transform_evaluator = joint.create_child(
            DependNode,
            node_type='transformEvaluator',
            segment_name='%sEvaluator' % joint.segment_name
        )
        group = joint.create_child(
            Transform,
            segment_name='%sEvaluator' % joint.segment_name
        )
        mesh = group.create_child(
            Mesh,
            segment_name='%sEvaluatorMesh' % joint.segment_name
        )
        sphere_node = joint.create_child(
            DependNode,
            node_type='polyPrimitiveMisc',
            segment_name='%sEvaluatorPrimitive' % joint.segment_name
        )
        condition = joint.create_child(
            DependNode,
            segment_name='%sEvaluatorCondition' % joint.segment_name,
            node_type='condition'
        )

        condition.plugs['colorIfTrueR'].set_value(1.0)
        condition.plugs['colorIfTrueG'].set_value(1.0)
        condition.plugs['colorIfTrueB'].set_value(1.0)

        condition.plugs['colorIfFalseR'].set_value(0.1)
        condition.plugs['colorIfFalseG'].set_value(0.1)
        condition.plugs['colorIfFalseB'].set_value(0.1)

        transform_evaluator.plugs['evaluatioinCount'].connect_to(condition.plugs['firstTerm'])
        condition.plugs['operation'].set_value(1)
        condition.plugs['secondTerm'].set_value(0.0)
        sphere_node.plugs['radius'].set_value(size)
        sphere_node.plugs['output'].connect_to(mesh.plugs['inMesh'])
        joint.plugs['translate'].connect_to(transform_evaluator.plugs['translateIn'])
        joint.plugs['rotate'].connect_to(transform_evaluator.plugs['rotateIn'])

        mesh.assign_shading_group(root.shaders['highlight'].shading_group)

        condition.plugs['outColor'].connect_to(group.plugs['scale'])
        reset_bubbles(controller)


def reset_bubbles(controller):
    for node in controller.scene.ls(type='transformEvaluator'):
        controller.scene.setAttr('%s.evaluatioinCount' % node, 0)


def blend_orients(
    source_1,
    source_2,
    destination,
    skip_rotate_x=False,
    skip_rotate_y=False,
    skip_rotate_z=False,
    interpolation='quaternions',
    common_ancestor=None
):
    """
    NOTE! This should be switched to quatSlerp
    """
    interpolation_dict = dict(
        euler=0,
        quaternions=1
    )
    if interpolation not in interpolation_dict:
        raise Exception('Invalid interpolation value: %s. Try one of the following : %s' % (
            interpolation,
            interpolation_dict.keys()
        )
                        )
    if not common_ancestor:
        common_ancestor = get_common_ancestor(
            source_1,
            source_2,
            destination
        )
    assert source_1 != common_ancestor
    assert source_2 != common_ancestor
    assert destination != common_ancestor
    source_1_rotate_order = source_1.plugs['rotateOrder'].get_value()
    source_2_rotate_order = source_2.plugs['rotateOrder'].get_value()
    destination_rotate_order = destination.plugs['rotateOrder'].get_value()
    if not source_1_rotate_order == source_2_rotate_order == destination_rotate_order:
        raise Exception('blend orients requires three transforms with teh same rotateOrder.')
    if not source_1 != source_2 != destination:
        raise Exception('blend orients requires three SEPARATE transforms')
    matrix_1 = get_local_matrix_out_plug(
        common_ancestor,
        source_1
    )
    matrix_2 = get_local_matrix_out_plug(
        common_ancestor,
        source_2
    )
    decompose_matrix_1 = destination.create_child(
        DependNode,
        segment_name='%s%sDecomposeMatrix1' % (
            extract_segment_name(destination.name),
            source_1.segment_name
        ),
        node_type='decomposeMatrix'
    )
    decompose_matrix_2 = destination.create_child(
        DependNode,
        segment_name='%s%sDecomposeMatrix2' % (
            extract_segment_name(destination.name),
            source_1.segment_name
        ),
        node_type='decomposeMatrix'
    )
    pair_blend = destination.create_child(
        DependNode,
        segment_name='%s%sMatrixBlender' % (
            extract_segment_name(destination.name),
            source_1.segment_name
        ),
        node_type='pairBlend'
    )
    compose_matrix = destination.create_child(
        DependNode,
        segment_name='%s%sCompose' % (
            extract_segment_name(destination.name),
            source_1.segment_name
        ),
        node_type='composeMatrix'
    )
    pair_blend.plugs['rotInterpolation'].set_value(interpolation_dict[interpolation])
    matrix_1.connect_to(decompose_matrix_1.plugs['inputMatrix'])
    matrix_2.connect_to(decompose_matrix_2.plugs['inputMatrix'])
    decompose_matrix_1.plugs['outputTranslate'].connect_to(pair_blend.plugs['inTranslate1'])
    decompose_matrix_1.plugs['outputRotate'].connect_to(pair_blend.plugs['inRotate1'])
    decompose_matrix_2.plugs['outputTranslate'].connect_to(pair_blend.plugs['inTranslate2'])
    decompose_matrix_2.plugs['outputRotate'].connect_to(pair_blend.plugs['inRotate2'])
    pair_blend.plugs['outRotate'].connect_to(compose_matrix.plugs['inputRotate'])
    pair_blend.plugs['outTranslate'].connect_to(compose_matrix.plugs['inputTranslate'])
    in_plug = get_local_matrix_in_plug(
        common_ancestor,
        destination,
        connect_translate=False,
        connect_scale=False,
        skip_rotate_x=skip_rotate_x,
        skip_rotate_y=skip_rotate_y,
        skip_rotate_z=skip_rotate_z
    )
    compose_matrix.plugs['useEulerRotation'].set_value(True)
    compose_matrix.plugs['inputRotateOrder'].set_value(destination_rotate_order)

    compose_matrix.plugs['outputMatrix'].connect_to(in_plug)
    return pair_blend.plugs['weight']


def create_twist_reader(transform, segment_name):

    mult_matrix = transform.create_child(
        DependNode,
        segment_name=segment_name,
        differentiation_name='MultMatrix',
        node_type='multMatrix'
    )
    decompose_matrix = transform.create_child(
        DependNode,
        segment_name=segment_name,
        differentiation_name='DecomposeInput',
        node_type='decomposeMatrix'
    )
    decompose_inverse_matrix = transform.create_child(
        DependNode,
        segment_name=segment_name,
        differentiation_name='DecomposeInverseInput',
        node_type='decomposeMatrix'
    )
    quat_product = transform.create_child(
        DependNode,
        segment_name=segment_name,
        differentiation_name='QuatProduct',
        node_type='quatProd'
    )
    quat_normalize = transform.create_child(
        DependNode,
        segment_name=segment_name,
        differentiation_name='EulerToQuat',
        node_type='quatNormalize'
    )
    quat_to_euler = transform.create_child(
        DependNode,
        segment_name=segment_name,
        differentiation_name='QuatToEuler',
        node_type='quatToEuler'
    )
    decompose_matrix.plugs['inputRotateOrder'].set_value(1)
    quat_to_euler.plugs['inputRotateOrder'].set_value(1)
    decompose_inverse_matrix.plugs['inputRotateOrder'].set_value(1)

    if not transform.plugs.exists('staticInvertedBindMatrix'):
        static_inverted_bind_matrix = transform.create_plug('staticInvertedBindMatrix', at='matrix')
        static_inverted_bind_matrix.set_value(transform.plugs['inverseMatrix'].get_value())
    if not transform.plugs.exists('staticBindMatrix'):
        static_bind_matrix = transform.create_plug('staticBindMatrix', at='matrix')
        static_bind_matrix.set_value(transform.plugs['matrix'].get_value())
    transform.plugs['matrix'].connect_to(mult_matrix.plugs['matrixIn'].element(0))
    transform.plugs['staticInvertedBindMatrix'].connect_to(mult_matrix.plugs['matrixIn'].element(1))
    mult_matrix.plugs['matrixSum'].connect_to(decompose_inverse_matrix.plugs['inputMatrix'])
    decompose_inverse_matrix.plugs['outputQuatY'].connect_to(quat_normalize.plugs['inputQuatY'])
    decompose_inverse_matrix.plugs['outputQuatW'].connect_to(quat_normalize.plugs['inputQuatW'])
    transform.plugs['staticBindMatrix'].connect_to(decompose_matrix.plugs['inputMatrix'])
    quat_normalize.plugs['outputQuat'].connect_to(quat_product.plugs['input1Quat'])
    decompose_matrix.plugs['outputQuat'].connect_to(quat_product.plugs['input2Quat'])
    quat_product.plugs['outputQuat'].connect_to(quat_to_euler.plugs['inputQuat'])
    # quat_to_euler.plugs['outputRotateY'].connect_to(reader.plugs['rotateY'])
    return quat_to_euler.plugs['outputRotateY']
