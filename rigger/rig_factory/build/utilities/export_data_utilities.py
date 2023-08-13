import traceback
import logging
import json
import glob
import os
import Snowman3.rigger.rig_factory.build.utilities.controller_utilities as cut
from Snowman3.rigger.rig_factory.objects.node_objects.locator import Locator
from Snowman3.rigger.rig_factory.objects.node_objects.transform import Transform
import Snowman3.rigger.rig_factory.utilities.dynamic_file_utilities as dfu
from Snowman3.rigger.rig_math.matrix import Matrix


def load_export_data(
        namespace,
        export_data_path,
        fin_export_data_path,
        set_snap_locators_path,
        create_plugs=False
):
    controller = cut.get_controller()
    container = controller.root
    failed_json_paths = []
    plug_data = {
            'export_data_path': export_data_path,
            'fin_export_data_path': fin_export_data_path,
            'set_snap_locators_path': set_snap_locators_path,
        }
    if create_plugs:
        for plug_name, path in plug_data.items():
            plug = container.create_plug(plug_name, dt='string')
            plug.set_channel_box(True)
            if path:
                plug.set_value(path)

    fin_export_data = None
    export_data = None
    set_snap_data = None

    # get data and check if fin, set snap and export json file exists
    if fin_export_data_path:
        try:
            with open(fin_export_data_path, mode='r') as f:
                fin_export_data = json.load(f)
        except Exception as e:
            failed_json_paths.append(fin_export_data_path)
            logging.getLogger('rig_build').error(traceback.format_exc())

    if export_data_path:
        try:
            with open(export_data_path, mode='r') as f:
                export_data = json.load(f)
        except Exception as e:
            failed_json_paths.append(export_data_path)
            logging.getLogger('rig_build').error(traceback.format_exc())

    if set_snap_locators_path:
        try:
            with open(set_snap_locators_path, mode='r') as f:
                set_snap_data = json.load(f)
        except Exception as e:
            failed_json_paths.append(set_snap_locators_path)
            logging.getLogger('rig_build').error(traceback.format_exc())

    if fin_export_data and export_data:
        export_data['transform_data'].update(fin_export_data['transform_data'])
        export_data['node_data'].update(fin_export_data['node_data'])
        export_data['attr_data'].extend(fin_export_data['attr_data'])

    elif not export_data and fin_export_data:
        export_data = fin_export_data

    if not export_data:
        return dict(
            status='warning',
            warning='Unable to resolve export data.\n' + '\nFailed to parse: '.join(failed_json_paths)
        )

    # Builds all non-ATTR locator data items.
    if export_data:
        created_nodes = {}
        for node_name, matrix in export_data['transform_data'].iteritems():
            if namespace and namespace != os.environ['ENTITY_NAME']:
                node_name = '{0}:{1}'.format(namespace, node_name)

            if controller.scene.objExists(node_name):
                continue
            if controller.scene.objExists(node_name + '_ExportData'):
                continue
            if controller.scene.objExists(node_name + 'Shape'):
                continue

            locator = container.export_data_group.create_child(
                Transform,
                name=node_name + '_ExportData',
                matrix=Matrix(matrix)
            )
            locator.create_child(
                Locator,
                name=locator.name + 'Shape'
            )
            plug = locator.create_plug(
                'originalNode',
                dataType='string'
            )
            plug.set_value(node_name)

            created_nodes[node_name] = locator

        # Builds all ATTR locator data items.

        for attr_data in export_data['attr_data']:
            if namespace and namespace != os.environ['ENTITY_NAME']:
                node_name = '{0}:{1}'.format(namespace, attr_data['node'] + '_ExportData')
            else:
                node_name = attr_data['node'] + '_ExportData'
            logging.getLogger('rig_build').error(node_name)
            logging.getLogger('rig_build').error(export_data_path)
            logging.getLogger('rig_build').error(namespace)
            if node_name in container.controller.named_objects:
                locator = container.controller.named_objects[node_name]
            else:
                locator = container.export_data_group.create_child(
                    Transform,
                    name=node_name
                )

                locator.create_child(
                    Locator,
                    name=locator.name + 'Shape'
                )
                plug = locator.create_plug(
                    'originalNode',
                    dataType='string'
                )
                plug.set_value(attr_data['node'])
                created_nodes[node_name] = locator

            type = attr_data['type']
            value = attr_data['value']
            attribute = attr_data['attr']
            enum_names = attr_data.get('enum_names', None)

            if not locator.plugs.exists(attribute):
                if type == 'string':
                    plug = locator.create_plug(
                        attribute,
                        dataType=type
                    )
                elif type == 'enum':
                    plug = locator.create_plug(
                        attribute,
                        attributeType=type,
                        enumName=enum_names
                    )
                else:
                    plug = locator.create_plug(
                        attribute,
                        attributeType=type
                    )
                plug.set_value(value)

    if set_snap_data:

        created_nodes = {}
        for i in range(0, len(set_snap_data)):
            if namespace and namespace != os.environ['ENTITY_NAME']:
                node_name = '{0}:{1}'.format(namespace, set_snap_data[i][0])
            else:
                node_name = set_snap_data[i][0]
            matrix = set_snap_data[i][1]

            if controller.scene.objExists(node_name):
                continue
            if controller.scene.objExists(node_name + '_ExportData'):
                continue
            if controller.scene.objExists(node_name + 'Shape'):
                continue

            locator = container.export_data_group.create_child(
                Transform,
                name=node_name + '_ExportData',
                matrix=Matrix(matrix)
            )
            locator.create_child(
                Locator,
                name=locator.name + 'Shape'
            )
            plug = locator.create_plug(
                'originalNode',
                dataType='string'
            )
            plug.set_value(node_name)

            created_nodes[node_name] = locator

    for plug_name in plug_data:
        container.plugs[plug_name].set_locked(True)

    if failed_json_paths:
        return dict(
            status='warning',
            warning='\nFailed to parse: '.join(failed_json_paths)
        )
