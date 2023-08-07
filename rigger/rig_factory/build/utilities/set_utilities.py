# python modules
import os
import logging
import traceback

# iRig Modules
import Snowman3.rigger.rig_factory.objects as obs
import Snowman3.rigger.rig_factory.utilities.dynamic_file_utilities as dfu
import Snowman3.rigger.rig_factory.build.utilities.controller_utilities as cut


# Placements & Standins
def import_placement_nodes(placements_file, create_plug=False):
    controller = cut.get_controller()
    logger = logging.getLogger('rig_build')
    container = controller.root
    if not placements_file:
        return dict(
            status='info',
            info='placements_file not found: %s' % placements_file
        )
    if not os.path.exists(placements_file):
        return dict(
            status='warning',
            warning='placements_file not found: %s' % placements_file
        )
    if not container.import_placement_path:
        return dict(
            status='warning',
            warning='Container.import_placement_path set to False'
        )
    if not isinstance(container, obs.Container):
        return dict(
            status='warning',
            warning='No valid rig found'
        )
    if not container.placement_group:
        return dict(
            status='warning',
            warning='Container had no placements group'
        )
    current_namespace = controller.scene.namespaceInfo(currentNamespace=True)
    logger.info('Importing placements from: %s' % placements_file)
    temp_namespace = 'import_geometry'
    if not controller.scene.namespace(exists=':%s' % temp_namespace):
        controller.scene.namespace(add=':%s' % temp_namespace)
    controller.scene.namespace(set=':%s' % temp_namespace)
    controller.scene.file(
        placements_file,
        i=True,
        type="mayaAscii",
        ignoreVersion=True,
        mergeNamespacesOnClash=False,
        options="v=0;p=17;f=0",
        importTimeRange="override",
        importFrameRate=True
    )
    roots = controller.scene.ls('%s:*' % temp_namespace, assemblies=True) or []
    if not roots:
        container.standin_group = []
        return dict(
            status='warning',
            warning='Unable to find any original valid dag nodes in: %s' % placements_file
        )
    delete_nodes = []
    for node_name in controller.scene.ls('%s:*' % temp_namespace, type='transform'):
        existing_node_name = node_name.split(':')[-1]
        if controller.scene.objExists(existing_node_name):
            delete_nodes.append(node_name)
            for child_name in controller.scene.listRelatives(node_name, c=True, type='transform'):
                existing_child_name = child_name.split(':')[-1]
                if not controller.scene.objExists(existing_child_name):
                    controller.scene.parent(child_name, existing_node_name)
    controller.scene.delete(delete_nodes)
    new_roots = controller.scene.ls('%s:*' % temp_namespace, assemblies=True) or []

    if new_roots:
        logger.info('Found imported geometry roots to parent: %s' % new_roots)
        controller.scene.parent(
            roots,
            container.placement_group
        )
        # add geo path to group so we can track which model the rig is using
        if create_plug:
            utility_geometry_path_plug = container.create_plug(
                'placements_path',
                dt='string'
            )
            utility_geometry_path_plug.set_value(placements_file)
            roots.extend(container.standin_group)
            container.standin_group = list(set([x.split(':')[-1] for x in roots]))
            # Update placement_path, since we only have one file, will just create the list from scratch
            utility_geometry_path_plug.set_channel_box(True)
            utility_geometry_path_plug.set_locked(True)

    if controller.namespace:
        controller.scene.namespace(
            moveNamespace=(':%s' % temp_namespace, ':%s' % controller.namespace))
    controller.scene.namespace(
        rm=':%s' % temp_namespace,
        mergeNamespaceWithParent=True
    )
    controller.scene.namespace(set=current_namespace)
    set_placement_attributes(controller)


def set_placement_attributes(controller):
    logger = logging.getLogger('rig_build')
    environment_group = 'Placements_Grp'
    if controller.scene.objExists(environment_group):
        descendants = controller.scene.listRelatives(environment_group, ad=True, type='transform')
        if descendants:
            for x in controller.scene.listRelatives(environment_group, ad=True, type='transform'):
                plug = '%s.Proxy' % x
                if controller.scene.objExists(plug):
                    try:
                        controller.scene.setAttr(plug, lock=False)
                        controller.scene.setAttr(plug, 1)
                    except Exception as e:
                        logger.error(traceback.format_exc())
                plug = '%s.Render' % x
                if controller.scene.objExists(plug):
                    try:
                        controller.scene.setAttr(plug, lock=False)
                        controller.scene.setAttr(plug, 0)
                    except Exception as e:
                        logger.info('failed to set attr: %s' % plug)

    else:
        logger.info('set_placement_attributes : Unable to find {0}.'.format(environment_group))


# Previs Lights
def import_previs_lights(project, entity):

    controller = cut.get_controller()

    logger = logging.getLogger('rig_build')
    container = controller.root
    try:
        import maya.cmds as mc
        if isinstance(container, obs.Container):
            previs_lights_directory = '%s/previs_lights' % dfu.get_products_directory(project, entity)
            logger.info('Attempting to import previs_lights from: %s' % previs_lights_directory)
            if os.path.exists(previs_lights_directory):
                sorted_files = sorted(os.listdir(previs_lights_directory))
                if sorted_files:
                    file_path = '%s/%s' % (previs_lights_directory, sorted_files[-1])
                    roots = controller.scene.import_geometry(file_path)
                    if roots:
                        if container.root_geometry_group:
                            mc.parent(roots, container.root_geometry_group)

                            # add geo path to group so we can track which model the rig is using
                            utility_geometry_path_plug = container.create_plug(
                                'previs_lights_path',
                                dt='string'
                            )
                            utility_geometry_path_plug.set_value(file_path)
                            utility_geometry_path_plug.set_channel_box(True)
                            utility_geometry_path_plug.set_locked(True)

                        else:
                            controller.raise_warning('import_previs_lights_nodes: No placement_group found')
                    else:
                        controller.raise_warning('import_previs_lights_nodes: No previs_lights roots found')
                else:
                    logger.info('import_previs_lights_nodes: No previs_lights scenes found in : %s' % previs_lights_directory)
        else:
            controller.raise_warning('import_placement_nodes: no valid rig found ')
    except Exception:
        logger.error(traceback.format_exc())
        controller.raise_warning('Import previs_lights failed. See script editor for details')


def set_previs_lights_attributes(controller):
    previs_lights_Grp = 'PreVis_Light_Grp'
    driver = None

    if controller.scene.objExists(previs_lights_Grp):

        if controller.scene.objExists('C_Main_Cog_Jnt'):
            driver = 'C_Main_Cog_Jnt'
        elif controller.scene.objExists(previs_lights_Grp):
            driver = 'Cog_Jnt'
        else:
            controller.scene.error('Could not find Cog_Jnt or C_Main_Cog_Jnt')

        if driver:
            controller.scene.parentConstraint(driver, previs_lights_Grp, mo=True)
            controller.scene.scaleConstraint(driver, previs_lights_Grp, mo=True)
