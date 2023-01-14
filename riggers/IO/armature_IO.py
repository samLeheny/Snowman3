# Title: armature_IO.py
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
importlib.reload(amtr_utils)
importlib.reload(gen_utils)

import Snowman3.riggers.dictionaries.IO_data_fields as IO_data_fields_dict
importlib.reload(IO_data_fields_dict)
IO_data_fields = IO_data_fields_dict.get_dict('armature')
###########################
###########################

###########################
######## Variables ########
decimal_count = 9
###########################
###########################





########################################################################################################################


dirpath = r'C:\Users\61451\Desktop'


class ArmatureDataIO(object):

    def __init__(
        self,
        dirpath,
        IO_data_fields = IO_data_fields
    ):

        #...vars
        self.armature_data = {}
        self.dirpath = dirpath
        self.data_fields = IO_data_fields





    ####################################################################################################################
    def find_armature_in_scene(self):

        found_armatures = pm.ls("::*_ARMATURE", type="transform")
        scene_armature = found_armatures[0] if found_armatures else None
        return scene_armature





    ####################################################################################################################
    def get_modules_data(self, armature):

        self.armature_data['modules'] = {}
        #...Get all modules in armature
        modules = amtr_utils.get_modules_in_armature(armature)
        #...Get data from each module
        [self.get_data_from_module(modules[key], key) for key in modules]





    ####################################################################################################################
    def get_armature_data_from_scene(self):

        #...Find armature container in scene
        scene_armature = self.find_armature_in_scene()

        #...Fill in armature data based on values stored in hidden armature attributes
        for data_field in self.data_fields:
            self.armature_data[data_field.IO_key] = pm.getAttr(f'{scene_armature}.{data_field.attr_name}')

        #...Get data from armature modules
        self.get_modules_data(scene_armature)

        return self.armature_data





    ####################################################################################################################
    def get_data_from_module(self, module, module_key):

        module_ctrl = pm.listConnections(f'{module}.ModuleRootCtrl', s=1, d=0)[0]

        init_data = {
            'rig_module_type' : pm.getAttr(f'{module}.ModuleType'),
            'name' : pm.getAttr(f'{module}.ModuleNameParticle'),
            'side' : pm.getAttr(f'{module}.Side'),
            'is_driven_side' : pm.getAttr(f'{module}.IsDrivenSide'),
            'drive_target' : self.get_driver_placers_in_module(module),
            'draw_connections' : self.get_drawn_connections(module),
            'position' : [round(i, decimal_count) for i in mc.getAttr(f'{module_ctrl}.translate')[0]],
            'rotation' : [round(i, decimal_count) for i in mc.getAttr(f'{module_ctrl}.rotate')[0]],
            'scale' : round(mc.getAttr(f'{module_ctrl}.ModuleScale'), decimal_count),
            'color' : gen_utils.get_color(module_ctrl)
        }

        #...Populate module's placers data
        self.get_module_placers_data(init_data, module)

        self.armature_data['modules'][module_key] = init_data





    ####################################################################################################################
    def get_module_placers_data(self, module_data, module):

        #...Get module placement control. It has the attributes whose values we need
        module_ctrl = pm.listConnections(f'{module}.ModuleRootCtrl', s=1, d=0)[0]

        module_data['placers'] = []

        attr_string = 'PlacerNodes'
        for attr_name in pm.listAttr(f'{module_ctrl}.{attr_string}'):
            if attr_name != attr_string:
                placer = pm.listConnections(f'{module_ctrl}.{attr_string}.{attr_name}', s=1, d=0)[0]
                module_data['placers'].append(self.get_placer_data(placer))





    ####################################################################################################################
    def get_placer_data(self, placer):

        out_dict = {
            #...Name
            'name' : pm.getAttr(f'{placer}.PlacerTag'),
            #...Side
            'side' : pm.getAttr(f'{placer}.Side'),
            #...Position
            'position' : [round(i, decimal_count) for i in mc.getAttr(f'{placer}.translate')[0]],
            #...Size
            'size' : pm.getAttr(f'{placer}.Size'),
            #...Vector Handle Data
            'vectorHandleData' : pm.getAttr(f'{placer}.VectorHandleData'),
            #...Orienter Data
            'orienterData' : pm.getAttr(f'{placer}.OrienterData'),
            #...Connector targets
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
    def get_driver_placers_in_module(self, module):

        #...Placers
        placers = amtr_utils.get_placers_in_module(module)

        #...Check which placers (if any) drive constraints
        constraining_placers = {}
        for key in placers:
            if amtr_utils.get_outgoing_constraints(placers[key]):
                constraining_placers[key] = placers[key]

        #...Check which constraining placers are driving other placers
        driver_placers = {}
        for driver_key in constraining_placers:
            constraint_nodes = amtr_utils.get_outgoing_constraints(placers[driver_key])
            connected_nodes = []
            for constraint_node in constraint_nodes:
                for attr in ("constraintTranslate", "constraintRotate", "constraintScale"):
                    if pm.attributeQuery(attr, node=constraint_node, exists=1):
                        for letter in ("X", "Y", "Z"):
                            connections = pm.listConnections(constraint_node + "." + attr + letter, d=1, s=0)
                            if connections:
                                for node in connections:
                                    connected_nodes.append(node) if node not in connected_nodes else None

            for node in connected_nodes:
                if amtr_utils.check_if_placer(node):

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
                if module_placer in driver_placers:

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
    def save(self):

        self.get_armature_data_from_scene() if not self.armature_data else None
        filepath = '{}/{}.json'.format(self.dirpath, 'test_armature_data')
        with open(filepath, 'w') as fh:
            json.dump(self.armature_data, fh, indent=5)





    ####################################################################################################################
    def load(self, filepath):

        data = None

        #...
        if not os.path.exists(filepath):
            print('ERROR: Provided file path not found on disk.')
            return False

        #...Read data
        with open(filepath, 'r') as fh:
            data = json.load(fh)

        return data
