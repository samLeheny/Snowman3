import os
import traceback
import logging
import Snowman3.rigger.rig_factory.environment as env
import Snowman3.rigger.rig_factory.utilities.dynamic_file_utilities as dfu
import Snowman3.rigger.rig_factory.build.utilities.controller_utilities as cut
from Snowman3.rigger.rig_factory.objects.node_objects.mesh import Mesh
from Snowman3.rigger.rig_factory.objects.node_objects.transform import Transform
from Snowman3.rigger.rig_factory.objects.node_objects.nurbs_surface import NurbsSurface
from Snowman3.rigger.rig_factory.objects.node_objects.nurbs_curve import NurbsCurve
from Snowman3.rigger.rig_math.matrix import Matrix
import Snowman3.rigger.rig_factory as rig_factory


DAG_SHAPE_TYPES = (Mesh, NurbsCurve, NurbsSurface)


def import_geometry_paths(entity_name, property_name, paths):
    controller = cut.get_controller()
    container = controller.root
    if not container:
        raise Exception('Rig Not Found.')
    new_geometry = dict()
    paths_property_name = '%s_paths' % property_name
    group_property_name = '%s_group' % property_name
    if not hasattr(container, paths_property_name):
        raise Exception('%s doesnt seem to have a property called "%s"' % (container, paths_property_name))
    if not hasattr(container, paths_property_name):
        raise Exception('%s doesnt seem to have a property called "%s"' % (container, group_property_name))
    parent = getattr(container, group_property_name)
    for i, path in enumerate(paths):
        if path.startswith('/'):
            if entity_name == os.environ['TT_ENTNAME']:
                build_directory = env.local_build_directory
            else:
                build_directory = dfu.get_latest_product_directory(  # Parent entity
                    os.environ['TT_PROJCODE'],
                    entity_name
                )
            path = '%s%s' % (build_directory, path)

        imported_geometry = import_container_geometry_path(
            controller.root,
            path,
            parent,
            property_name
        )

        new_geometry.update(imported_geometry)
    return new_geometry


def import_container_geometry_path(
        container,
        path,
        parent,
        property_name
):
    """
    Imports geometry from any arbitrary path for a container
    """
    logger = logging.getLogger('rig_build')
    controller = container.controller
    new_geometry = dict()
    if os.path.exists(path):
        new_geometry = import_geo_and_create_objects(
            controller,
            path,
            parent,
            property_name
        )
        if new_geometry and container.smooth_mesh_normals:
            for geo in new_geometry.values():
                if isinstance(geo, Mesh):
                    try:
                        controller.scene.smooth_normals([geo.name])
                    except Exception as e:
                        logger.error(traceback.format_exc())
                        controller.raise_warning(
                            'Something went wrong. Unable to smooth mesh normals. See script editor for details'
                        )

        if not hasattr(container, property_name):
            raise Exception('%s doesnt seem to have a property called "%s"' % (container, property_name))

        getattr(container, property_name).update(new_geometry)
        container.geometry.update(new_geometry)  # add to main geometry dict
        logger.info("Imported '%s' from : %s" % (property_name, path))

    else:
        logger.critical('The %s path does not exist: %s' % (property_name, path))
        controller.raise_warning('The %s path does not exist: %s' % (property_name, path))
    return new_geometry


def build_dag_objects(controller, dag_names, parent):
    logger = logging.getLogger('rig_build')
    new_objects = []
    for full_name in dag_names:
        target_name = full_name.split(':')[-1]
        if controller.namespace:
            target_name = '%s:%s' % (controller.namespace, target_name)

        if target_name in controller.named_objects:
            this = controller.named_objects[target_name]
            logger.info('Dag object already exists "%s" (skipping)' % this.name)

        else:
            logger.info('Attempting to create object "%s"' % full_name)
            this = generate_object_from_dag_node(
                controller,
                full_name,
                parent,
                target_name.split(':')[-1]
            )
            if this:
                new_objects.append(this)
                logger.info('Created new dag object "%s"' % this.name)

            logger.info('Attempting to copy materials "%s"' % this.name)
            # Try to copy material over if exists
            copy_materials(controller, full_name, target_name)
            logger.info('Finished copying materials "%s"' % this.name)

        if this:
            child_names = controller.scene.listRelatives(
                full_name,
                c=True,
                type='dagNode'
            )
            if child_names:
                logger.info('Building child dag objects: %s' % child_names)
                new_objects.extend(
                    build_dag_objects(
                        controller,
                        child_names,
                        this
                    )
                )
    return new_objects


def generate_object_from_dag_node(controller, dag_name, parent, new_name):
    if not controller.root:
        raise Exception('Container must have a root to generate dag object (for shaders).')
    logger = logging.getLogger('rig_build')
    dag_type = controller.scene.nodeType(dag_name)
    dag_object = None

    # Use name minus suffix as segment name, for eg. parent constraint naming
    segment_name, chk, guess_suffix = new_name.rpartition('_')
    if not chk or len(guess_suffix) > 3:
        segment_name = new_name
    logger.info('Attempting to create %s object: %s' % (dag_type, new_name))
    if dag_type == 'transform':
        dag_object = parent.create_child(
            Transform,
            name=new_name,
            segment_name=segment_name
        )
        for attribute_name in [
            'rotatePivot',
            'rotatePivotTranslate',
            'rotateQuaternion',
            'scalePivot',
            'scalePivotTranslate'
        ]:
            dag_object.plugs[attribute_name].set_value(
                list(controller.scene.getAttr('%s.%s' % (dag_name, attribute_name))[0])
            )
        dag_object.set_matrix(controller.scene.xform(dag_name, q=True, ws=True, m=True))  # Needs to be set after pivots are loaded, to set correctly. Doesn't require Matrix object.

    elif dag_type == 'mesh':
        logger.info('Attempting to copy %s object: %s' % (dag_type, new_name))

        mesh_m_object = controller.scene.copy_mesh(
            dag_name,
            parent.m_object,
        )
        logger.info('Copied %s object: %s' % (dag_type, new_name))

        dag_object = parent.create_child(
            Mesh,
            name=new_name,
            segment_name=segment_name,
            m_object=mesh_m_object
        )

    elif dag_type == 'nurbsSurface':
        dag_object = parent.create_child(
            NurbsSurface,
            name=new_name,
            segment_name=segment_name,
            m_object=controller.scene.copy_nurbs_surface(
                dag_name,
                parent.m_object,
            )
        )
    elif dag_type == 'nurbsCurve':
        dag_object = parent.create_child(
            NurbsCurve,
            name=new_name,
            segment_name=segment_name,
            m_object=controller.scene.copy_nurbs_curve(
                dag_name,
                parent.m_object,
            )
        )
    else:
        logger.warning('Dag object "%s" is invalid type "%s" (skipping)' % (dag_name, dag_type))
    logger.info('Created %s object: %s' % (dag_type, new_name))
    logger.info('Attempting to assign shader to : %s' % new_name)
    if isinstance(dag_object, DAG_SHAPE_TYPES):
        dag_object.assign_shading_group(controller.root.shaders[None].shading_group)
    logger.info('Assigned shader to : %s' % new_name)

    return dag_object


def create_origin_geometry(origin_geometry_data):
    controller = cut.get_controller()
    logger = logging.getLogger('rig_build')
    container = controller.root
    error_messages = []
    invalid_geometry_names = []
    pre_existing_origin_geometry = []
    new_geometry = dict()
    new_origin_geometry_data = dict()
    for geo_name in origin_geometry_data:
        origin_data = origin_geometry_data[geo_name]
        if controller.namespace:
            geo_name = '%s:%s' % (controller.namespace, geo_name)
        if geo_name in controller.named_objects:
            new_origin_geometry_data[geo_name] = origin_data
        else:
            invalid_geometry_names.append(geo_name)
    del origin_geometry_data
    if controller.current_layer is None:
        container.origin_geometry_data = new_origin_geometry_data
    for name_string in new_origin_geometry_data:
        origin_data = new_origin_geometry_data[name_string]
        current_geometry = name_string
        faces = origin_data['faces']
        count = origin_data['count']
        if controller.scene.mock:
            #  If the controller is in mock mode, create dummy mesh
            mock_transform = container.origin_geometry_group.create_child(
                Transform,
                name=name_string
            )
            mock_transform.create_child(
                Mesh,
                name='%sShape' % name_string
            )
            continue
        if name_string not in controller.named_objects:
            continue
        geometry_transform = controller.named_objects[name_string]
        mesh_objects = [x for x in geometry_transform.children if isinstance(x, Mesh)]
        if len(mesh_objects) < 1:
            error_messages.append('No mesh children found under "%s"' % geometry_transform)
            continue
        elif len(mesh_objects) > 1:
            error_messages.append('more than one mesh children found under "%s"' % geometry_transform)
            continue
        for x in range(count):
            if x == 0:
                origin_geometry_name = '%s_Origin' % name_string
            else:
                origin_geometry_name = '%s_Origin%s' % (
                    name_string,
                    rig_factory.index_dictionary[x-1].upper()
                )
            full_origin_geometry_name = origin_geometry_name
            if controller.namespace:
                full_origin_geometry_name = '%s:%s' % (
                    controller.namespace,
                    full_origin_geometry_name
                )
            if full_origin_geometry_name in controller.named_objects:
                pre_existing_origin_geometry.append(full_origin_geometry_name)
                logger.warning('Origin Geometry seems to already exist and so must be skipped: %s' % full_origin_geometry_name)
            else:
                origin_geometry_transform = controller.create_object(
                    Transform,
                    name=origin_geometry_name,
                    parent=container.origin_geometry_group
                )
                logging.getLogger('rig_build').info(
                    'Copying mesh: %s %s' % (
                        mesh_objects[0].name,
                        mesh_objects[0].get_selection_string()
                    )
                )
                origin_mesh = controller.copy_mesh(
                    mesh_objects[0].name,
                    origin_geometry_transform,
                    name='%sShape' % origin_geometry_name,
                )
                origin_mesh.assign_shading_group(
                    container.shaders['origin'].shading_group
                )
                container.geometry[origin_mesh.name] = origin_mesh
                if faces:
                    start_index_str, end_index_str = faces.split('[')[-1].split(']')[0].split(':')
                    controller.scene.select('%s.f[*]' % origin_mesh)
                    controller.scene.select('%s.f[%s:%s]' % (origin_mesh, start_index_str, end_index_str), d=1)
                    controller.scene.delete(ch=False)
                blendshape_name = controller.scene.blendShape(
                    origin_mesh.name,
                    current_geometry,
                    tc=False
                )[0]
                blendshape_name = controller.scene.rename(
                    blendshape_name,
                    '%s_Bs' % origin_geometry_name
                )
                controller.scene.setAttr('%s.weight[0]' % blendshape_name, 1.0)
                logger.info('Created Origin Geometry: %s' % origin_geometry_transform)
                new_geometry[origin_mesh.name] = origin_mesh
                current_geometry = origin_mesh.name

    if invalid_geometry_names:
        return dict(
            status='warning',
            warning='Invalid orig geo tags found. the following will be removed: %s' % invalid_geometry_names
        )


def delete_objects(objects):
    controller = cut.get_controller()
    controller.schedule_objects_for_deletion(objects)
    del objects
    controller.delete_scheduled_objects()


def import_abc_product(key, path, store_path=False):
    if not os.path.exists(path):
        logging.getLogger('rig_build').warning('Path not found: %s' % path)
        return {}
    controller = cut.get_controller()
    group = controller.root.geometry_group
    new_geometry = import_geo_and_create_objects(
        controller,
        path,
        group,
        property_name=key
    )
    if new_geometry and controller.root.smooth_mesh_normals:
        for geo in new_geometry.values():
            if isinstance(geo, Mesh):
                try:
                    controller.scene.smooth_normals([geo.name])
                except Exception as e:
                    logging.getLogger('rig_build').error(traceback.format_exc())
                    controller.raise_warning(
                        'Something went wrong. Unable to smooth mesh normals. See script editor for details'
                    )
    if new_geometry:
        controller.root.geometry.update(new_geometry)  # add to main geometry dict
    logging.getLogger('rig_build').info("Imported '%s' from : %s" % (key, path))
    if store_path:
        controller.root.product_paths[key] = path
    return new_geometry


def import_geo_and_create_objects(controller, path, parent, property_name='import_geometry'):
    new_geometry = dict()
    temp_namespace = property_name
    if controller.namespace:
        temp_namespace = '%s:%s' % (controller.namespace, temp_namespace)
    root_names = controller.scene.import_geometry(
        path,
        namespace=temp_namespace
    )
    if root_names:
        new_dag_objects = build_dag_objects(controller, root_names, parent)
        controller.scene.delete(root_names)
        new_geometry.update(dict((x.name, x) for x in new_dag_objects if isinstance(x, DAG_SHAPE_TYPES)))
        controller.scene.select(cl=True)
    else:
        logging.getLogger('rig_build').info('Warning ! No geometry roots found in %s' % path)
        controller.scene.delete(controller.scene.ls('%s:*' % temp_namespace))

    controller.scene.namespace(
        rm=':%s' % temp_namespace,
        mergeNamespaceWithParent=True
    )
    return new_geometry


def gather_mesh_children(transform):
    mesh_children = []
    for child in transform.children:
        if isinstance(child, Mesh):
            mesh_children.append(child)
        else:
            mesh_children.extend(gather_mesh_children(child))
    return mesh_children


def smooth_normals(controller, geometries):
    logger = logging.getLogger('rig_build')
    try:
        controller.scene.select([x.name for x in geometries])
        controller.scene.polyNormalPerVertex(ufn=True)
        for geo in [x.name for x in geometries]:
            controller.scene.polySoftEdge(
                geo,
                a=180,
                ch=False
            )
    except Exception as e:
        logger.error(traceback.format_exc())
        controller.raise_warning(
            'Something went wrong. Unable to smooth mesh normals. See script editor for details'
        )


def copy_materials(controller, source_geo, target_geo):
    ignore_shaders = ['Blank_Shd', 'lambert1']
    shade_engine = controller.scene.listConnections(source_geo, type='shadingEngine')
    if shade_engine:
        material = controller.scene.ls(controller.scene.listConnections(shade_engine), materials=True)

        # Connect material
        if material and material[-1] not in ignore_shaders:
            controller.scene.sets(target_geo, forceElement=shade_engine[-1])

        # Connect to uvChooser node if exist
        dag_type = controller.scene.nodeType(source_geo)
        if dag_type == 'mesh':
            uvchooser = controller.scene.ls(
                controller.scene.listConnections(source_geo, destination=True),
                type='uvChooser'
            )
            if uvchooser:
                target_plug = controller.scene.listConnections('{0}.uvSet'.format(source_geo), plugs=True)[0]
                source_plug = controller.scene.listConnections(target_plug, source=True, plugs=True)[0]

                controller.scene.connectAttr(
                    source_plug.replace(source_geo, target_geo),
                    target_plug,
                    force=True
                )
