# Title: class_Armature.py
# Author: Sam Leheny
# Contact: samleheny@live.com

# Description:


###########################
##### Import Commands #####
import importlib
import pymel.core as pm
import os

import Snowman3.dictionaries.nameConventions as nameConventions
importlib.reload(nameConventions)
nom = nameConventions.create_dict()

import Snowman3.riggers.utilities.classes.class_ArmatureModule as class_ArmatureModule
import Snowman3.riggers.utilities.classes.class_ArmatureRootHandle as class_ArmatureRootHandle
importlib.reload(class_ArmatureModule)
importlib.reload(class_ArmatureRootHandle)
ArmatureModule = class_ArmatureModule.ArmatureModule
ArmatureRootHandle = class_ArmatureRootHandle.ArmatureRootHandle

import Snowman3.utilities.general_utils as gen_utils
import Snowman3.riggers.utilities.armature_utils as amtr_utils
importlib.reload(gen_utils)
importlib.reload(amtr_utils)

import Snowman3.riggers.IO.rig_module_IO as rigModule_IO
importlib.reload(rigModule_IO)
RigModuleDataIO = rigModule_IO.RigModuleDataIO

import Snowman3.riggers.IO.placerConnectors_IO as placerConnectors_IO
importlib.reload(placerConnectors_IO)
PlacerConnectorsDataIO = placerConnectors_IO.PlacerConnectorsDataIO

import Snowman3.riggers.utilities.classes.class_PlacerConnector as classPlacerConnector
importlib.reload(classPlacerConnector)
PlacerConnector = classPlacerConnector.PlacerConnector
###########################
###########################


###########################
######## Variables ########

###########################
###########################





########################################################################################################################
class Armature:
    def __init__(
        self,
        name: str = None,
        prefab_key: str = None,
        root_size: float = None,
        modules: dict = None,
        armature_scale: float = None,
        data: dict = None
    ):
        self.name = name
        self.prefab_key = prefab_key if prefab_key else 'None'
        self.root_size = root_size if root_size else 55.0
        self.modules = modules if modules else {}
        self.sided_modules = {'L': {}, 'R': {}}
        self.root_groups = {}
        self.armature_scale = armature_scale if armature_scale else 1.0
        self.root_handle = ArmatureRootHandle(name=self.name, root_size=self.root_size)
        self.metadata_fields = self.compose_metadata_fields()
        self.data = data





    """
    --------- METHODS --------------------------------------------------------------------------------------------------
    --------------------------------------------------------------------------------------------------------------------
    create_root_handle_in_scene
    create_root_groups
    drive_module_attrs
    build_armature_from_data
    assign_armature_metadata
    populate_armature
    --------------------------------------------------------------------------------------------------------------------
    --------------------------------------------------------------------------------------------------------------------
    """





    ####################################################################################################################
    def create_root_handle_in_scene(self):

        #...Create root object
        self.root_handle.create_mobject()
        #...Assign metadata in hidden attributes
        self.assign_armature_metadata()
        #...Control root scale axes all at once with custom attribute
        self.armature_scale_attr()
        #...Create important groups under root object
        self.create_root_groups()





    ####################################################################################################################
    def armature_scale_attr(self):

        attr_name = "ArmatureScale"
        pm.addAttr(self.root_handle.mobject, longName=attr_name, attributeType=float, minValue=0.001, defaultValue=1,
                   keyable=0)
        pm.setAttr(f'{self.root_handle.mobject}.{attr_name}', channelBox=1)
        for attr in ("sx", "sy", "sz"):
            pm.connectAttr(f'{self.root_handle.mobject}.{attr_name}', f'{self.root_handle.mobject}.{attr}')
            pm.setAttr(f'{self.root_handle.mobject}.{attr}', lock=1, keyable=0)





    ####################################################################################################################
    def create_root_groups(self):

        #...Armature modules group
        self.root_groups["modules"] = pm.group(name="modules", parent=self.root_handle.mobject, empty=True)



    ####################################################################################################################
    def drive_module_attrs(self):

        #...Vis options
        attr_strings = ("PlacersVis", "VectorHandlesVis", "OrientersVis", "ControlsVis", "PlacerScale")
        default_vals = (1, 0, 0, 0, 1.0)
        attr_types = ("bool", "bool", "bool", "bool", "float")
        min_values = (0, 0, 0, 0, 0.001)

        for attr_string, default_val, attr_type, min_value in zip(attr_strings, default_vals, attr_types, min_values):

            pm.addAttr(self.root_handle.mobject, longName=attr_string, attributeType=attr_type,
                       defaultValue=default_val, minValue=min_value, keyable=0)
            pm.setAttr(self.root_handle.mobject + '.' + attr_string, channelBox=1)

            for module in self.modules.values():
                #...Drive the same attrs on module placers
                pm.connectAttr(f'{self.root_handle.mobject}.{attr_string}',
                               f'{module.module_ctrl.mobject}.{attr_string}', f=1)
                pm.setAttr(f'{module.module_ctrl.mobject}.{attr_string}', lock=1, channelBox=0)





    ####################################################################################################################
    def modules_from_data(self):

        data = self.modules

        armature_modules = {}

        #...Make Armature Modules out of module dictionaries in data
        for key in data:
            m_data = data[key]

            #...Fill in any missing properties with None values
            for field in ("rig_module_type", "name", "side", "position", "rotation", "scale",
                             "draw_connections", "placers"):
                if field not in m_data:
                    m_data[field] = None

            new_module = ArmatureModule(
                rig_module_type = m_data["rig_module_type"],
                name = m_data["name"],
                side = m_data["side"],
                position = m_data["position"],
                rotation = m_data["rotation"],
                scale = m_data["scale"],
                draw_connections = m_data["draw_connections"]
            )

            armature_modules[key] = new_module

            if new_module.side in (nom.leftSideTag, nom.rightSideTag):
                self.sided_modules[new_module.side][key] = new_module

        self.modules = armature_modules





    ####################################################################################################################
    def assign_armature_metadata(self):

        node = self.root_handle.mobject

        for data_field in self.metadata_fields:
            IO_key, attr_name, attr_type, attr_value = data_field

            if pm.attributeQuery(attr_name, node=node, exists=1):
                continue

            if attr_type == 'string':
                pm.addAttr(node, longName=attr_name, keyable=0, dataType=attr_type)
                attr_value = attr_value if attr_value else 'None'
                pm.setAttr(f'{node}.{attr_name}', attr_value, type=attr_type, lock=1)
            else:
                pm.addAttr(node, longName=attr_name, keyable=0, attributeType=attr_type)
                pm.setAttr(f'{node}.{attr_name}', attr_value, lock=1)



    ####################################################################################################################
    def compose_metadata_fields(self):

        data_fields = [('name', 'ArmatureName', 'string', self.name),
                       ('prefab_key', 'ArmaturePrefabKey', 'string', self.prefab_key),
                       ('root_size', 'RootSize', 'float', self.root_size)]
                       #('armature_scale', 'ArmatureScale', 'float', None)]
        return data_fields





    ####################################################################################################################
    '''
    def draw_module_connectors(self):

        for connector_data in self.placer_connectors:
            connector = PlacerConnector(
                source_module_key = connector_data['source_module_key'],
                source_placer_key = connector_data['source_placer_key'],
                destination_module_key = connector_data['destination_module_key'],
                destination_placer_key =connector_data['destination_placer_key']
            )
            connector.create_connector(source_module=self.modules[connector.source_module_key],
                                       parent=self.modules[connector.source_module_key].rig_subGrps["connector_curves"])
    '''



    ####################################################################################################################
    def populate_armature(self):

        self.create_root_handle_in_scene()

        for key, module in self.modules.items():
            module_IO = RigModuleDataIO(module_key=key, rig_module=module)
            module.modules_parent = self.root_groups['modules']
            module.populate_module(key)

        for key in self.modules:
            module = self.modules[key]
            if module.side in (nom.leftSideTag, nom.rightSideTag):
                self.sided_modules[module.side][key] = module

        #...Drive all module vis switches from armature root ------------------------------------------------------
        self.drive_module_attrs()
