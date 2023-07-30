import logging
import traceback
import copy
from Snowman3.rigger.rig_factory.objects.deformer_objects.lattice import Lattice
from Snowman3.rigger.rig_factory.objects.deformer_objects.skin_cluster import SkinCluster
from Snowman3.rigger.rig_factory.objects.deformer_objects.wire import Wire
from Snowman3.rigger.rig_factory.objects.node_objects.dag_node import DagNode
from Snowman3.rigger.rig_factory.objects.node_objects.object_set import ObjectSet
from Snowman3.rigger.rig_factory.objects.node_objects.transform import Transform


## Commented out as assumed Obsolete - but could be used externally somewhere?
# def get_deformer_data(rig, precision=None):
#     data = []
#     for deformer in rig.deformers:
#         if not isinstance(deformer, SkinCluster):
#             deformer_data = dict(
#                 klass=deformer.__class__.__name__,
#                 module=deformer.__module__,
#                 root_name=deformer.root_name,
#                 side=deformer.side,
#                 size=deformer.size,
#                 index=deformer.index,
#                 weights=deformer.get_weights(precision=precision),
#                 geometry=[str(x) for x in deformer.deformer_set.members]
#             )
#             data.append(deformer_data)
#     return data


def get_origin_weight_data(controller, ogd):
    geometries = [x for x in ogd]
    bs_weight_dict = dict((x, {}) for x in geometries)
    for geo in geometries:
        weights = controller.scene.get_blendshape_weights(geo)
        bs_weight_dict[geo]['weights'] = weights

    return bs_weight_dict


def create_lattice(controller, parent, *geometry, **kwargs):

    segment_name = kwargs.pop('segment_name', None)
    kwargs['parent'] = parent

    this = Lattice(
        controller=controller,
        segment_name=segment_name,
        **kwargs
    )

    lattice = Transform(
        controller=controller,
        segment_name=segment_name,
        **kwargs
    )
    lattice_shape = DagNode(
        controller=controller,
        node_type='lattice',
        segment_name=segment_name,
        **kwargs
    )

    base_lattice = Transform(
        controller=controller,
        segment_name='%sBase' % segment_name,
        **kwargs
    )
    lattice_base_shape = DagNode(
        controller=controller,
        segment_name='%sBase' % segment_name,
        **kwargs
    )

    deformer_set = ObjectSet(
        controller=controller,
        segment_name=segment_name,
        **kwargs
    )

    m_objects = controller.scene.create_lattice(*geometry)
    (
        this.m_object,
        lattice.m_object,
        base_lattice.m_object,
        lattice_shape.m_object,
        lattice_base_shape.m_object,
        deformer_set.m_object,
    ) = m_objects

    parent_name = controller.scene.get_selection_string(parent.m_object)
    controller.scene.parent(
        controller.scene.get_selection_string(lattice.m_object),
        parent_name,
    )
    controller.scene.parent(
        controller.scene.get_selection_string(base_lattice.m_object),
        parent_name,
    )

    this.deformer_set = deformer_set
    this.lattice_transform = lattice
    this.lattice_shape = lattice_shape
    this.lattice_base_transform = base_lattice
    this.base_lattice_shape = lattice_base_shape

    deformer_set.members = list(geometry)
    for x in geometry:
        x.deformers.append(this)

    controller.register_item(this)
    controller.register_item(lattice)
    controller.register_item(lattice_shape)
    controller.register_item(base_lattice)
    controller.register_item(lattice_base_shape)
    controller.register_item(deformer_set)

    def rename_node(node):
        controller.rename(
            node,
            controller.name_function(
                segment_name=segment_name,
                **kwargs
            )
        )
    rename_node(this)
    rename_node(lattice)
    rename_node(lattice_shape)
    rename_node(base_lattice)
    rename_node(lattice_base_shape)
    rename_node(deformer_set)

    return this


def create_wire_deformer(controller, curve, *geometry, **kwargs):

    root_name = kwargs.pop('root_name', None)

    this = Wire(
        controller=controller,
        root_name=root_name,
        **kwargs
    )

    base_wire = Transform(
        controller=controller,
        root_name='%s_base_wire' % root_name,
        **kwargs
    )
    base_wire_shape = DagNode(
        controller=controller,
        root_name='%s_base_wire' % root_name,
        **kwargs
    )

    deformer_set = ObjectSet(
        controller=controller,
        root_name=root_name,
        **kwargs
    )

    m_objects = controller.scene.create_wire_deformer(curve, *geometry)
    (
        this.m_object,
        base_wire.m_object,
        base_wire_shape.m_object,
        deformer_set.m_object,
    ) = m_objects

    this.deformer_set = deformer_set
    this.base_wire = base_wire
    this.base_wire_shape = base_wire_shape

    deformer_set.members = list(geometry)
    for x in geometry:
        x.deformers.append(this)

    def get_name(node):

        return controller.name_function(
            node.__class__.__name__,
            root_name=node.root_name,
            **kwargs
        )

    items = (
        this,
        base_wire,
        base_wire_shape,
        deformer_set
    )
    for item in items:

        controller.register_item(item)
        controller.rename(item, get_name(item))

    return this


def create_skin_cluster(controller, geometry, influences, **kwargs):
    return controller.scene.create_from_skin_data(
        dict(
            geometry=geometry,
            joints=influences,
            weights=dict()
        )
    )


def get_skin_cluster_data(controller, rig, precision=4):
    data = []
    skin_clusters = []
    layer = controller.current_layer
    for key in rig.geometry:
        geometry = rig.geometry[key]
        skin_cluster = controller.find_skin_clusters(geometry)
        if skin_cluster:
            named_obs = controller.named_objects
            joints = [named_obs[x] for x in controller.scene.skinCluster(key, q=True, influence=True) if x in named_obs]
            if layer == geometry.layer or any([layer == joint.layer for joint in joints]):
                skin_clusters.extend(skin_cluster)
    for skin_cluster in list(set(skin_clusters)):
        data.append(controller.scene.get_skin_data(skin_cluster, precision=precision))
    return data


def set_skin_cluster_data(controller, rig, data):
    logger = logging.getLogger('rig_build')
    if data:
        all_missing_joints = []
        missing_geometry = []

        for i, skin_data in enumerate(data or []):

            if controller.namespace:
                skin_data = copy.deepcopy(skin_data)  # Avoid changing input
                for i in range(len(skin_data['joints'])):
                    skin_data['joints'][i] = '%s:%s' % (
                        controller.namespace,
                        skin_data['joints'][i]
                    )
                skin_data['geometry'] = '%s:%s' % (
                    controller.namespace,
                    skin_data['geometry']
                )
            missing_joints = []
            for joint in skin_data['joints']:
                if not controller.objExists(joint):
                    missing_joints.append(joint)
            if missing_joints:
                all_missing_joints.extend(missing_joints)
                continue
            if not controller.objExists(skin_data['geometry']):
                missing_geometry.append(skin_data['geometry'])
                continue
            try:
                controller.scene.create_from_skin_data(skin_data)
                logger.info('Loaded Skincluster for : %s' % skin_data['geometry'])

            except Exception as e:
                logger.error(traceback.format_exc())

        all_missing_joints = [all_missing_joints[x] for x in range(len(all_missing_joints)) if x < 8]
        missing_geometry = [missing_geometry[x] for x in range(len(missing_geometry)) if x < 8]

        if all_missing_joints:
            controller.raise_warning_signal.emit(
                'Failed skin report: missing joints:\n%s' % '\n'.join(all_missing_joints)
            )
            logger.critical('Failed skin report: missing joints:\n%s' % '\n'.join(all_missing_joints))

        if missing_geometry:
            controller.raise_warning_signal.emit(
                'Failed Skin report: missing geometry:\n%s' % '\n'.join(missing_geometry)
            )
            logger.critical('Failed Skin report: missing geometry:\n%s' % '\n'.join(missing_geometry))


def remap_skin_data(controller, source_skin_data, new_mesh,
                    joint_prefixes=('C_Lip_', 'L_Lip_', 'R_Lip_'),
                    search_replace_joints=(('Upper', 'UpperZip'), ('Lower', 'LowerZip')),
                    holder_joint='Face_Container_Bind_Jnt',
                    weight_check_threshold=0.003,
                    prune_small_weights=0.002,
                    check_joints_exist=False):  # can't check existence if not yet built
    logger = logging.getLogger('rig_build')
    if not source_skin_data:
        message = 'Failed remap skin: no skin data found to remap to %s' % new_mesh
        controller.raise_warning_signal.emit(message)
        logger.error(message)
        return {}

    # Copy data before masking weight values
    skin_data = copy.deepcopy(source_skin_data)
    skin_data['geometry'] = new_mesh  # Replace old geo

    # Filter the joint names to only keep the prefixed ones and the placeholder joint;
    # Keep track of the old joint ids for the sake of loading the right weights.
    excluded_joint_ids = []
    included_joints = [holder_joint]  # Leave out existence check to avoid using mc
    joint_id_map = {}
    holder_joint_weights_id = None
    for i, joint in enumerate(skin_data['joints']):
        if not any(joint.startswith(pref) for pref in joint_prefixes):
            excluded_joint_ids.append(i)
        else:
            for search, replace in search_replace_joints:
                joint = joint.replace(search, replace)
            if check_joints_exist and not controller.objExists(joint):
                message = 'Warning - masked skin: missing joint after search/replace %s' % joint
                controller.raise_warning_signal.emit(message)
                logger.warning(message)
                excluded_joint_ids.append(i)
            elif joint == holder_joint:
                holder_joint_weights_id = i
            else:
                joint_id_map[i] = len(included_joints)
                included_joints.append(joint)
    if len(included_joints) == 1:
        # No joints found with the prefix - no point in copying weights
        message = 'Warning - remap skin: no joints found in the skin from %s ' \
                  'matching the pattern %s after search/replace' % (
                      source_skin_data['geometry'], str(joint_prefixes))
        controller.raise_warning_signal.emit(message)
        logger.error(message)
        return {}
    skin_data['joints'] = included_joints

    # Process the skin weights; all weight on excluded joints will be transferred to the holder joint.
    # _Note that the skin_data saves int ids as strings_
    weights = skin_data['weights']
    if not weights:
        message = 'Failed remap skin: no skin weights found to apply to %s' % new_mesh
        controller.raise_warning_signal.emit(message)
        logger.error(message)
        return {}
    weight_dict = weights[0]  # Only one mesh but weight format supports multiple
    weight_on_relevant_joints = False  # Whether any weights were left after transferring weights to the holder joint
    for vertId, weightData in weight_dict.items():
        masked_weights = {}
        non_holder_weight_sum = 0.0
        for joint_id_str, value in weightData.items():
            joint_id = int(joint_id_str)
            if joint_id != holder_joint_weights_id and joint_id not in excluded_joint_ids:
                # Adjust joint index due to reduced joint list
                new_id = joint_id_map[joint_id]
                if value < prune_small_weights:
                    continue
                masked_weights[str(new_id)] = value
                non_holder_weight_sum += value

                if not weight_on_relevant_joints and value > weight_check_threshold:
                    weight_on_relevant_joints = True
        masked_weights["0"] = 1.0 - non_holder_weight_sum  # Avoids precision error of adding excluded joint weights

        weight_dict[vertId] = masked_weights  # Modifying skin_data (copy)

    if not weight_on_relevant_joints:
        message = 'Warning - masked skin: The geometry %s had no influence from the prefixed joints' % (skin_data['geometry'])
        controller.raise_warning_signal.emit(message)
        logger.warning(message)
        return {}

    return skin_data


def set_deformer_stack(controller, item_name, stack):
    # type - ('ObjectController', AnyStr, List) -> None
    """
    Applies the given deformer stack to the given mesh name.
    :param controller:
        Rig controller.
    :param item_name:
        Name of the target item to reorder deformers for.
    :param stack:
        New deformer stack for the mesh. Should only contain deformers
        that are actually attached to the given item.
    """
    for deformer_1, deformer_2 in zip(stack[:-1], stack[1:]):
        try:
            controller.scene.reorderDeformers(
                deformer_1,
                deformer_2,
                item_name
            )
        except RuntimeError:
            controller.raise_warning_signal.emit(
                f'could not reorder: `{deformer_1}` with `{deformer_2}` on `{item_name}`'
            )


def get_deformer_stack(controller, item_name):
    # type - ('ObjectController', AnyStr) -> List
    """
    :param controller:
        Rig controller.
    :param item_name:
        Name of the target item to get deformer stack from.
    :return:
        Deformer stack for the given item.
    """
    return [
        x for x in (
            controller.scene.listHistory(
                item_name,
                pruneDagObjects=True,
                interestLevel=1
            )
            or []
        )
        if 'geometryFilter' in controller.scene.nodeType(x, inherited=True)
    ]


def get_deformer_stack_data(controller, rig):
    data = {
        mesh: [
            [deformer, controller.scene.nodeType(deformer)]
            for deformer in get_deformer_stack(controller, mesh)
        ]
        for mesh in rig.geometry if rig.geometry[mesh].layer == controller.current_layer
    }
    return data


def set_deformer_stack_to_default(
        controller,
        item_name,
        custom_stack_order=None
):
    # type - ('ObjectController', AnyStr, Dict[AnyStr: int]) -> None
    """
    Sets the deformer stack for the given item to a default order.
    :param controller:
        Rig controller.
    :param item_name:
        Name of the target item to reorder deformer stack for.
    :param custom_stack_order:
        Custom stack order.
    :return:
    """

    default_order = {
        'lattice': 1,
        'skinCluster': 2,
        'blendShape': 3,
    }

    stack_order = custom_stack_order or default_order

    # Reorderes the items current stack based on `stack_order`
    weighted_stack = [
        (x, stack_order.get(controller.scene.nodeType(x), 0))
        for x in get_deformer_stack(controller, item_name)
    ]
    sorted_stack = [x[0] for x in sorted(weighted_stack, key=lambda x: x[1])]

    set_deformer_stack(controller, item_name, sorted_stack)


def set_deformer_stack_data(controller, rig, data):
    # type - ('ObjectController', 'BaseContainer', Dict) -> None
    """
    Applies given deformer stack data to geometries in the given rig.
    :param controller:
        Rig controller.
    :param rig:
        Root/container object.
    :param data:
        Deformer stack data.
    """

    data_meshes = []
    for mesh_name, deformer_data in (data or {}).items():

        if mesh_name not in rig.geometry:
            continue

        data_meshes.append(mesh_name)

        # All deformers currently attached to the target geometry.
        current_stack = get_deformer_stack(controller, mesh_name)

        # Finds any pre existing skinCluster on the current mesh.
        skin_cluster, = [
            x for x in current_stack
            if controller.scene.nodeType(x) == 'skinCluster'
        ][:1] or [None]

        # Replaces untrackable node types from data with their pre
        # existing node type counterparts.
        # (data slincluster -> existing skincluster).
        subbed_stack = (
            deformer_type == 'skinCluster' and skin_cluster
            or deformer
            for deformer, deformer_type in deformer_data
        )

        # Removes deformers not present in meshes current stack.
        filtered_stack = [
            deformer for deformer in subbed_stack
            if deformer in current_stack
        ]

        # Applies the filtered stack to the given mesh.
        set_deformer_stack(controller, mesh_name, filtered_stack)

    # Reorders remaining geometry in the scene to the default order. (On current blueprint layer only)
    for mesh_name, mesh in rig.geometry.iteritems():
        if mesh.layer != controller.current_layer or mesh_name in data_meshes:
            continue

        set_deformer_stack_to_default(controller, mesh_name)


def initialize_deformers(mesh):
    controller = mesh.controller
    scene = controller.scene
    mesh_history = mesh.controller.scene.listHistory(mesh)
    deformers = []
    if mesh_history:
        for deformer_name in [x for x in mesh_history if 'geometryFilter' in scene.nodeType(x, inherited=True)]:
            deformer_type = scene.nodeType(deformer_name)
            if deformer_type == 'skinCluster':
                m_object = scene.get_m_object(deformer_name)
                skin_cluster = SkinCluster(m_object=m_object)
                deformers.append(skin_cluster)
    return deformers
