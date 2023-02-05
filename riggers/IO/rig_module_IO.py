# Title: armature_module_IO.py
# Author: Sam Leheny
# Contact: samleheny@live.com

# Description:


###########################
##### Import Commands #####
import importlib
import pymel.core as pm
import maya.cmds as mc
import json
import os
import Snowman3.riggers.utilities.armature_utils as amtr_utils
import Snowman3.utilities.general_utils as gen_utils
import Snowman3.utilities.general_utils as rig_utils
importlib.reload(amtr_utils)
importlib.reload(gen_utils)
importlib.reload(rig_utils)

import Snowman3.riggers.utilities.classes.class_PrefabModuleData as class_prefabModuleData
importlib.reload(class_prefabModuleData)
PrefabModuleData = class_prefabModuleData.PrefabModuleData

import Snowman3.riggers.IO.placer_IO as placer_IO
importlib.reload(placer_IO)
PlacerDataIO = placer_IO.PlacerDataIO

import Snowman3.riggers.IO.controls_IO as controls_IO
importlib.reload(controls_IO)
ControlsDataIO = controls_IO.ControlsDataIO
###########################
###########################

###########################
######## Variables ########
decimal_count = 9
###########################
###########################





########################################################################################################################


default_dirpath = r'C:\Users\61451\Desktop\test_build' #...For testing purposes


class RigModuleDataIO(object):

    def __init__(
        self,
        dirpath = None,
        module_key = None,
        rig_module = None
    ):

        self.rig_module = rig_module
        self.dirpath = dirpath if dirpath else default_dirpath
        self.module_key = module_key
        self.file = f'{self.module_key}_module.json'
        self.folder = 'rig_modules'
        self.prefab_module_data = PrefabModuleData(
            prefab_key=self.rig_module.rig_module_type,
            side=self.rig_module.side,
            is_driven_side=self.rig_module.is_driven_side
        )
        self.module_data = None





    ####################################################################################################################
    def get_data_from_module_in_scene(self):

        module_node = amtr_utils.get_modules_in_armature(self.rig_module.armature_container)[self.module_key]

        module_ctrl = pm.listConnections(f'{module_node}.ModuleRootCtrl', s=1, d=0)[0]

        init_data = {
            'rig_module_type': pm.getAttr(f'{module_node}.ModuleType'),
            'name': pm.getAttr(f'{module_node}.ModuleNameParticle'),
            'side': pm.getAttr(f'{module_node}.Side'),
            'is_driven_side': pm.getAttr(f'{module_node}.IsDrivenSide'),
            'drive_target': self.get_driver_placers_in_module(module_node),
            'draw_connections': self.get_drawn_connections(module_node),
            'position': [round(i, decimal_count) for i in mc.getAttr(f'{module_ctrl}.translate')[0]],
            'rotation': [round(i, decimal_count) for i in mc.getAttr(f'{module_ctrl}.rotate')[0]],
            'scale': round(mc.getAttr(f'{module_ctrl}.ModuleScale'), decimal_count),
            'color': gen_utils.get_color(module_ctrl)
        }

        # ...Populate module's placers data
        self.get_module_placers_data(init_data, module_node)

        self.module_data = init_data





    ####################################################################################################################
    def prep_data_for_export(self):

        self.module_data = {}
        data_dict = self.rig_module.get_data_dictionary()
        self.module_data[self.module_key] = data_dict

        '''self.module_data = {}

        #...
        IO_data_fields = (('rig_module_type', self.rig_module.rig_module_type),
                          ('name', self.rig_module.name),
                          ('side', self.rig_module.side),
                          ('is_driven_side', self.rig_module.is_driven_side),
                          ('drive_target', self.rig_module.drive_target),
                          ('position', self.rig_module.position),
                          ('rotation', self.rig_module.rotation),
                          ('scale', self.rig_module.scale),
                          ('color', self.rig_module.ctrl_color))
        for IO_key, input_attr in IO_data_fields:
            self.module_data[IO_key] = input_attr'''





    ####################################################################################################################
    def get_driver_placers_in_module(self, module):

        #...Placers
        placers = amtr_utils.get_placers_in_module(module)

        #...Check which placers (if any) drive constraints
        constraining_placers = {}
        for key in placers:
            if amtr_utils.get_outgoing_constraints(placers[key]):
                constraining_placers[key] = placers[key]

        #...Check which constraining placers are driving other placers
        constraint_nodes = {}
        connected_nodes = {}
        check_attr_data = {}
        attrs = {}
        connections = {}
        for dict in (constraint_nodes, connected_nodes, check_attr_data, attrs, connections):
            for driver_key in constraining_placers:
                dict[driver_key] = []

        for driver_key in constraining_placers:
            constraint_nodes[driver_key] = amtr_utils.get_outgoing_constraints(placers[driver_key])

        for driver_key, nodes in constraint_nodes.items():
            for node in nodes:
                for attr in ('constraintTranslate', 'constraintRotate', 'constraintScale'):
                    check_attr_data[driver_key].append((node, attr))

        for driver_key, attr_data_package in check_attr_data.items():
            for attr_data in attr_data_package:
                constraint_node, attr = attr_data
                if not pm.attributeQuery(attr, node=constraint_node, exists=1):
                    continue
                for letter in ('X', 'Y', 'Z'):
                    attrs[driver_key].append(f'{constraint_node}.{attr}{letter}')

        for driver_key, attr in attrs.items():
            connections = pm.listConnections(attr, d=1, s=0)
            if not connections:
                continue
            for node in connections:
                connected_nodes[driver_key].append(node) if node not in connected_nodes[driver_key] else None

        driver_placers = {}

        for driver_key, nodes in connected_nodes.items():
            for node in nodes:
                if not amtr_utils.check_if_placer(node):
                    continue
                driven_placer_module_tag = amtr_utils.get_module_from_placer(node)
                module_tag = str(pm.getAttr(f'{driven_placer_module_tag}.ModuleName'))
                placer_tag = pm.getAttr(f'{node}.PlacerTag')

                if driver_key in driver_placers:
                    driver_placers[str(driver_key)].append((module_tag, str(placer_tag)))
                else:
                    driver_placers[str(driver_key)] = [(module_tag, str(placer_tag))]


        return driver_placers





    ####################################################################################################################
    def get_drawn_connections(self, module):

        #...Placers in this module
        module_placers = amtr_utils.get_placers_in_module(module)

        if not pm.attributeQuery('ExtraDrawnConnections', node=module, exists=1):
            return None

        connector_data = {}

        #...Get connectors in modules
        connectors = pm.listConnections(f'{module}.ExtraDrawnConnections', d=1, s=0)


        for connector in connectors:
            shape = connector.getShape()

            driver_placers = []
            for loc in pm.listConnections(f'{shape}.controlPoints', s=1, d=0):
                driver_placers.append(loc.getParent())

            for key in module_placers:
                module_placer = module_placers[key]
                if module_placer not in driver_placers:
                    continue

                this_module_placer_key = key

                driver_placers.remove(module_placer)
                remaining_placer = driver_placers[0]

                remaining_placer_tag = pm.getAttr(f'{remaining_placer}.PlacerTag')
                remaining_placer_module_tag = amtr_utils.get_module_from_placer(remaining_placer, return_tag=True)

                if this_module_placer_key in connector_data:
                    connector_data[str(this_module_placer_key)].append(str(remaining_placer_module_tag),
                                                                       str(remaining_placer_tag))
                else:
                    connector_data[str(this_module_placer_key)] = [(str(remaining_placer_module_tag),
                                                                    str(remaining_placer_tag)),]

                break


            return connector_data





    ####################################################################################################################
    def get_module_placers_data(self, module_data, module):

        # ...Get module placement control. It has the attributes whose values we need
        module_ctrl = pm.listConnections(f'{module}.ModuleRootCtrl', s=1, d=0)[0]

        module_data['placers'] = []

        attr_string = 'PlacerNodes'
        for attr_name in pm.listAttr(f'{module_ctrl}.{attr_string}'):
            if attr_name == attr_string:
                continue
            placer = pm.listConnections(f'{module_ctrl}.{attr_string}.{attr_name}', s=1, d=0)[0]
            module_data['placers'].append(self.get_placer_data(placer))





    ####################################################################################################################
    def get_placer_data(self, placer):

        out_dict = {
            'name' : pm.getAttr(f'{placer}.PlacerTag'),
            'side' : pm.getAttr(f'{placer}.Side'),
            'position' : [round(i, decimal_count) for i in mc.getAttr(f'{placer}.translate')[0]],
            'size' : pm.getAttr(f'{placer}.Size'),
            'vectorHandleData' : pm.getAttr(f'{placer}.VectorHandleData'),
            'orienterData' : pm.getAttr(f'{placer}.OrienterData'),
            'connectorTargets' : pm.getAttr(f'{placer}.ConnectorData'),
        }

        #...Pole vector distance
        if pm.attributeQuery('IkDistance', node=placer, exists=1):
            out_dict['ikDistance'] = pm.getAttr(f'{placer}.IkDistance')

        for key, val in out_dict.items():
            if val == 'None':
                out_dict[key] = None

        return out_dict



    ####################################################################################################################
    def save(self):

        filepath = os.path.join(self.dirpath, self.folder)

        path_exists = os.path.exists(filepath)
        if not path_exists:
            os.mkdir(filepath)

        filepath = os.path.join(filepath, self.module_key)
        path_exists = os.path.exists(filepath)
        if not path_exists:
            os.mkdir(filepath)

        self.export_module_data(filepath=filepath)
        self.export_placers_data(filepath=filepath)
        self.export_ctrls_data(filepath=filepath)



    ####################################################################################################################
    def export_module_data(self, filepath):

        # self.get_data_from_module() if not self.module_data else None
        self.prep_data_for_export() if not self.module_data else None
        with open(f'{filepath}/{self.file}', 'w') as fh:
            json.dump(self.module_data, fh, indent=5)



    ####################################################################################################################
    def export_placers_data(self, filepath):

        placers = self.prefab_module_data.get_placers()
        placers_IO = PlacerDataIO(placers=placers, dirpath=filepath)
        placers_IO.save()



    ####################################################################################################################
    def export_ctrls_data(self, filepath):

        ctrls = self.prefab_module_data.get_ctrl_data()
        ctrls_IO = ControlsDataIO(ctrls=ctrls, dirpath=filepath)
        ctrls_IO.save()



    ####################################################################################################################
    def load(self):

        #...
        filepath = os.path.join(self.dirpath, self.folder)
        if not os.path.exists(filepath):
            print('ERROR: Provided file path not found on disk.')
            return False

        #...Read data
        with open(filepath, 'r') as fh:
            data = json.load(fh)

        return data



    ####################################################################################################################
    def build_module_data_from_file(self):

        data = self.load()
        print('-'*150)
        print(data)
        print('-'*150)

