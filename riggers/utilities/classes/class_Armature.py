# Title: class_Armature.py
# Author: Sam Leheny
# Contact: samleheny@live.com

# Description:


###########################
##### Import Commands #####
import importlib
import pymel.core as pm

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
        name = None,
        prefab_key = None,
        root_size = None,
        symmetry_mode = None,
        modules = None,

    ):
        self.name = gen_utils.get_clean_name(name)
        self.prefab_key = prefab_key if prefab_key else 'None'
        self.root_size = root_size if root_size else 1
        self.modules = modules if modules else {}
        self.sided_modules = {'L': {}, 'R': {}}
        self.root_groups = {}
        self.symmetry_mode = symmetry_mode
        self.driver_side = gen_utils.symmetry_info(self.symmetry_mode)[1]
        self.root_handle = ArmatureRootHandle(name=self.name, root_size=self.root_size)
        self.metadata_fields = self.compose_metadata_fields()





    """
    --------- METHODS --------------------------------------------------------------------------------------------------
    --------------------------------------------------------------------------------------------------------------------
    create_root_handle_in_scene
    create_root_groups
    setup_armature_realtime_symmetry
    placer_symmetry
    module_handle_symmetry
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
        self.root_groups["modules"] = pm.group(name="modules", p=self.root_handle.mobject, em=1)





    ####################################################################################################################
    def setup_armature_realtime_symmetry(self, driver_side=None):

        #...If no driver side provided, get it from class attributes
        if not driver_side: driver_side = self.driver_side

        #...Determine the following side as opposite to the driver side
        following_side = nom.rightSideTag
        if driver_side == nom.rightSideTag:
            following_side = nom.leftSideTag

        #...Make symmetry connections in each pair of sided modules in the rig
        for module in self.sided_modules[driver_side].values():
            self.placer_symmetry(module)
            self.module_handle_symmetry(module)

        #...Visual indication of following side
        for module in self.sided_modules[following_side].values():
            if module.placers:
                for placer in module.placers.values():
                    placer.make_benign(hide=False)
            if module.module_handles:
                for setup_ctrl in module.module_handles.values():
                    setup_ctrl.make_benign(hide=True)





    ####################################################################################################################
    def placer_symmetry(self, module):

        #...For placers...
        if module.placers:

            for placer in module.placers.values():
                amtr_utils.connect_pair(placer.mobject, attrs=("tx", "ty", "tz"))

                #...Get placer's vector handles (if any)
                handles = []
                if placer.up_vector_handle:
                    handles.append(placer.up_vector_handle.mobject)
                if placer.aim_vector_handle:
                    handles.append(placer.aim_vector_handle.mobject)

                #...Determine driver and follower handles in handle pairs
                for handle in handles:
                    amtr_utils.connect_pair(handle, attrs=("tx", "ty", "tz"))





    ####################################################################################################################
    def module_handle_symmetry(self, module):

        #...For setup controls...
        if module.module_handles:
            for setup_ctrl in module.module_handles.values():
                setup_ctrl.setup_symmetry()





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

        #...Make Armature Modules out of module dictionaries in data
        for key in data:
            m_data = data[key]

            #...Fill in any missing properties with None values
            for property in ("rig_module_type", "name", "side", "is_driven_side", "position", "rotation", "scale",
                             "drive_target", "color", "draw_connections", "placers"):
                if property not in m_data:
                    m_data[property] = None


            new_module = ArmatureModule(
                rig_module_type = m_data["rig_module_type"],
                name = m_data["name"],
                side = m_data["side"],
                is_driven_side = m_data["is_driven_side"],
                position = m_data["position"],
                rotation = m_data["rotation"],
                scale = m_data["scale"],
                drive_target = m_data["drive_target"],
                draw_connections = m_data["draw_connections"],
                color = m_data["color"]
            )
            new_module.placers_from_data(m_data["placers"])

            data[key] = new_module

            if new_module.side in (nom.leftSideTag, nom.rightSideTag):
                self.sided_modules[new_module.side][key] = new_module





    ####################################################################################################################
    def assign_armature_metadata(self):

        node = self.root_handle.mobject

        for data_field in self.metadata_fields:
            IO_key, attr_name, attr_type, attr_value = data_field

            if pm.attributeQuery(attr_name, node=node, exists=1):
                continue

            if attr_type == 'string':
                pm.addAttr(node, longName=attr_name, keyable=0, dataType=attr_type)
                pm.setAttr(f'{node}.{attr_name}', attr_value, type=attr_type, lock=1)
            else:
                pm.addAttr(node, longName=attr_name, keyable=0, attributeType=attr_type)
                pm.setAttr(f'{node}.{attr_name}', attr_value, lock=1)





    def compose_metadata_fields(self):

        data_fields = [('name', 'ArmatureName', 'string', self.name),
                       ('prefab_key', 'ArmaturePrefabKey', 'string', self.prefab_key),
                       ('symmetry_mode', 'SymmetryMode', 'string', self.symmetry_mode),
                       ('driver_side', 'DriverSide', 'string', self.driver_side),
                       ('root_size', 'RootSize', 'float', self.root_size)]
                       #('armature_scale', 'ArmatureScale', 'float', None)]
        return data_fields





    ####################################################################################################################
    def populate_armature(self):

        self.create_root_handle_in_scene()

        for module in self.modules.values():
            module.modules_parent = self.root_groups["modules"]
            module.populate_module()

        for key in self.modules:
            module = self.modules[key]
            if module.side in (nom.leftSideTag, nom.rightSideTag):
                self.sided_modules[module.side][key] = module

        #...Drive all module vis switches from armature root ------------------------------------------------------
        self.drive_module_attrs()

        #...Connect modules to each other as specified in each module ---------------------------------------------
        [module.connect_modules() for module in self.modules.values()]

        #...Enact live symmetry if needed -------------------------------------------------------------------------
        if self.symmetry_mode in ("Left drives Right", "Right drives Left"):
            self.setup_armature_realtime_symmetry(driver_side=self.driver_side)





    ####################################################################################################################
    def hibernate_armature(self):

        for module in self.modules.values():
            module.hibernate_module()
