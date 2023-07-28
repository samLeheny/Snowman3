###import os
###import rig_factory
import itertools

###DEBUG = os.getenv('PIPE_DEV_MODE') == 'TRUE'

side_prefixes = {
    'left': 'L',
    'right': 'R',
    'center': 'C'
}
DEFAULT_SEGMENT_NAME = 'root'


def create_alpha_dictionary(depth=4):
    ad = {}
    mit = 0
    for its in range(1, depth):
        for combo in itertools.product('abcdefghijklmnopqrstuvwxyz', repeat=its):
            ad[mit] = ''.join(combo)
            mit += 1
    return ad


index_dictionary = create_alpha_dictionary()
index_list = list(value for key, value in index_dictionary.items())


def create_name_string(**kwargs):
    """
    This function names all objects in Snowman
    @param kwargs: Data used to construct name
    @return: str
    """
    if 'name' in kwargs:
        if len(kwargs['name'].split(':')) > 2:
            raise Exception('Double namespaces not supported: %s' % kwargs['name'])
    functionality_name = kwargs.get('functionality_name', None)
    differentiation_name = kwargs.get('differentiation_name', None)
    subsidiary_name = kwargs.get('subsidiary_name', None)
    side = kwargs.get('side', None)
    segment_name = kwargs.get('segment_name', None)
    curve_segment_name = kwargs.get('curve_segment_name', None)  # Specifically for control shapes(nurbsCurve)
    namespace = kwargs.pop('namespace', None)
    allow_underscores = kwargs.get('allow_underscores', False)
    name = kwargs.get('name', None)
    if name:
        if namespace and ':' not in name:
            return f'{namespace}:{name}'
        return name
    root_name = kwargs.get('root_name', None)
    base_name = kwargs.get('base_name', None)

    if root_name is not None:
        if not allow_underscores and '_' in root_name:
            raise Exception(f"Invalid character in root_name : '{root_name}'")
        if not allow_underscores and ' ' in root_name:
            raise Exception(f"Invalid character in root_name : '{root_name}'")
        if len(root_name) == 0:
            raise Exception('Empty string "" is not a valid root name')
        if not root_name[0].isupper():
            raise Exception(f"root_name '{root_name}' must be PascalCase")

    if side is not None:
        if root_name:
            name = f'{side}_{root_name}'
        elif base_name:
            name = f'{side}_{base_name}'
        else:
            name = side
    elif root_name:
        name = root_name
    elif base_name:
        name = base_name
    if isinstance(segment_name, basestring):
        if ':' in segment_name:
            raise Exception(f'segment_name "{segment_name}" contained invalid character: ":"')
        if not segment_name[0].isupper():
            raise Exception(f'segment_name "{segment_name}" must be PascalCase')
        if name:
            name = f'{name}_{segment_name}'
        else:
            name = segment_name
    else:
        raise Exception(f'Invalid segment_name type: {segment_name}')
    if differentiation_name is not None:
        if not differentiation_name[0].isupper():
            raise Exception(f'differentiation_name "{differentiation_name}" must be PascalCase')
        if '_' in differentiation_name:
            raise Exception(f'Invalid character in differentiation_name : "{differentiation_name}"')
        name = f'{name}_{differentiation_name}'
    if subsidiary_name is not None:
        if not subsidiary_name[0].isupper():
            raise Exception(f'subsidiary_name "{subsidiary_name}" must be PascalCase')
        if '_' in subsidiary_name:
            raise Exception(f'Invalid character in subsidiary_name : "{subsidiary_name}"')
        name = f'{name}_{subsidiary_name}'
    if functionality_name is not None:
        if not functionality_name[0].isupper():
            raise Exception(f'functionality_name "{functionality_name}" must be PascalCase')
        if '_' in functionality_name:
            raise Exception(f'Invalid character in functionality_name : "{functionality_name}"')
        name = f'{name}_{functionality_name}'
    if curve_segment_name is not None:
        if not curve_segment_name[0].isupper():
            raise Exception(f"subsidiary_name '{curve_segment_name}' must be PascalCase")
        if '_' in curve_segment_name:
            raise Exception(f"Invalid character in subsidiary_name : '{curve_segment_name}'")
        name = f'{name}_{curve_segment_name}'
    node_type = kwargs.get('node_type', None)
    suffix = kwargs.get('suffix', None)
    if not suffix:
        if node_type and node_type in type_suffixes:
            suffix = type_suffixes[node_type]
    if suffix:
        if not suffix.istitle():
            raise Exception(f"Invalid character in suffix : '{suffix}'")
        name = f'{name}_{suffix}'
    if namespace:
        name = f'{namespace}:{name}'
    if len(name.split(':')) > 3:
        raise Exception(f"Double namespaces are not supported: '{name}'")
    return name


type_suffixes = dict(
    addDoubleLinear='Adl',
    blendWeighted='Bwt',
    clamp='Clp',
    composeMatrix='Cmx',
    condition='Cnd',
    decomposeMatrix='Dcm',
    distanceBetween='Dst',
    eulerToQuat='Euq',
    follicle='Flc',
    ikEffector='Ike',
    joint='Jnt',
    locator='Loc',
    mesh='Msh',
    multMatrix='Mmx',
    multiplyDivide='Mlt',
    nurbsCurve='Ncv',
    nurbsSurface='Nsf',
    pairBlend='Pbl',
    plusMinusAverage='Pma',
    polyCone='Pcn',
    polyCube='Pcb',
    polyCylinder='Pcy',
    polyPrimitiveMisc='Sps',
    polySphere='Psp',
    quatInvert='Qiv',
    quatProd='Qpd',
    quatToEuler='Qte',
    remapValue='Rmp',
    reverse='Rvs',
    setRange='Srg',
    shadingEngine='Shg',
    shardMatrix='Smx',
    transformGeometry='Tgm',
    HIKCharacterNode='Hik',
    rebuildCurve='Rbc',
    hairSystem='Hys',
    nucleus='Nuc',
    polyEdgeToCurve='Pec',
    pointOnSurfaceInfo='Psi',
    pointOnCurveInfo='Pci',
    multDoubleLinear='Mdl',
    fitBspline='Fbs',
    projectCurve='Pjc',
    curveVarGroup='Cvg',
    curveFromSurfaceCoS='Cfs',
    arcLengthDimension='Acd',
    floatMath='Fmh',
    closestPointOnSurface='Cps',
    nearestPointOnCurve='Npoc',
    combinationShape='Cmbo',
    rigSpline='Spln',
    rigFollicle='Rflc',
    polyExtrudeEdge='Pxe'
)
