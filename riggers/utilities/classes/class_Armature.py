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
importlib.reload(class_ArmatureModule)
ArmatureModule = class_ArmatureModule.ArmatureModule

import Snowman3.utilities.general_utils as gen_utils
importlib.reload(gen_utils)
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
        root_size = None,
        symmetry_mode = None,
        modules = None,

    ):
        self.name = gen_utils.get_clean_name(name)
        self.mobject = None
        self.root_size = root_size if root_size else 1
        self.modules = modules if modules else {}
        self.sided_modules = {"L": {}, "R": {}}
        self.root_groups = {}
        self.symmetry_mode = symmetry_mode
        self.driver_side = gen_utils.symmetry_info(self.symmetry_mode)[1]





    """
    --------- METHODS --------------------------------------------------------------------------------------------------
    --------------------------------------------------------------------------------------------------------------------
    create_root_obj
    create_root_groups
    setup_realtime_symmetry
    connect_pair
    placer_symmetry
    setup_ctrl_symmetry
    drive_module_attrs
    build_armature_from_data
    assign_armature_metadata
    populate_armature
    --------------------------------------------------------------------------------------------------------------------
    --------------------------------------------------------------------------------------------------------------------
    """





    ####################################################################################################################
    def create_root_obj(self, size=None):
        """
        Creates the root node of the entire armature.
        Args:
            size (numeric): The size of the armature root's nurbs shape.
        Returns:
            (MObject): The created armature root object.
        """


        # ...Compose object name
        obj_name = "{}_ARMATURE".format(self.name)
        # ...If no size argument provided, derive scale from class attributes
        scale = size if size else self.root_size

        # ...Create root object
        self.mobject = gen_utils.prefab_curve_construct(prefab="COG",
                                                        name=obj_name,
                                                        color=[0.6, 0.6, 0.6],
                                                        up_direction=[0, 1, 0],
                                                        forward_direction=[0, 0, 1],
                                                        scale=scale)
        # ...Assign metadata in hidden attributes
        self.assign_armature_metadata()

        # ...Control root scale axes all at once with custom attribute
        for attr in ("sx", "sy", "sz"):
            pm.connectAttr(self.mobject + "." + "ArmatureScale", self.mobject + "." + attr)
            pm.setAttr(self.mobject + "." + attr, lock=1, keyable=0)

        # ...Create important groups under root object
        self.create_root_groups()


        return self.mobject





    ####################################################################################################################
    def create_root_groups(self):
        """
        Creates important groups under armature root object.
        """


        # ...Armature modules group
        self.root_groups["modules"] = pm.group(name="modules", p=self.mobject, em=1)





    ####################################################################################################################
    def setup_realtime_symmetry(self, driver_side=None):
        """
        Have one side of the armature mirror the other in real time.
        Args:
            driver_side (string): The side of the armature that is unlocked and free for manipulation by the user.
        """


        # ...If no driver side provided, get it from class attributes
        if not driver_side:
            driver_side = self.driver_side

        # ...Determine the following side as opposite to the driver side
        following_side = nom.rightSideTag
        if driver_side == nom.rightSideTag:
            following_side = nom.leftSideTag

        # ...Make symmetry connections in each pair of sided modules in the rig
        for module in self.sided_modules[driver_side].values():
            self.placer_symmetry(module)
            self.setup_ctrl_symmetry(module)

        # ...Visual indication of following side
        for module in self.sided_modules[following_side].values():
            if module.placers:
                for placer in module.placers.values():
                    placer.make_benign(hide=False)
            if module.setup_ctrls:
                for setup_ctrl in module.setup_ctrls.values():
                    setup_ctrl.make_benign(hide=True)





    ####################################################################################################################
    def connect_pair(self, obj, attrs=()):

        # ...Determine driver and follower placers in placer pair
        driver_obj = obj
        receiver_obj = gen_utils.get_opposite_side_obj(driver_obj)

        # ...Drive translation
        for attr in attrs:
            if not pm.attributeQuery(attr, node=driver_obj, exists=1):
                continue
            if not pm.getAttr(receiver_obj + "." + attr, lock=1):
                pm.connectAttr(driver_obj + "." + attr, receiver_obj + "." + attr, f=1)





    ####################################################################################################################
    def placer_symmetry(self, module):

        # ...For placers...
        if module.placers:

            for placer in module.placers.values():
                self.connect_pair(placer.mobject, attrs=("tx", "ty", "tz"))

                # ...Get placer's vector handles (if any)
                handles = []
                if placer.up_vector_handle:
                    handles.append(placer.up_vector_handle.mobject)
                if placer.aim_vector_handle:
                    handles.append(placer.aim_vector_handle.mobject)

                # ...Determine driver and follower handles in handle pairs
                for handle in handles:
                    self.connect_pair(handle, attrs=("tx", "ty", "tz"))





    ####################################################################################################################
    def setup_ctrl_symmetry(self, module):

        # ...For setup controls...
        if module.setup_ctrls:
            for setup_ctrl in module.setup_ctrls.values():
                self.connect_pair(setup_ctrl.mobject, attrs=("tx", "ty", "tz", "rx", "ry", "rz", "sx", "sy", "sz",
                                                             "ModuleScale"))





    ####################################################################################################################
    def drive_module_attrs(self):

        # ...Vis options
        attr_strings = ("PlacersVis", "VectorHandlesVis", "OrientersVis", "ControlsVis", "PlacerScale")
        default_vals = (1, 0, 0, 0, 1.0)
        attr_types = ("bool", "bool", "bool", "bool", "float")
        min_values = (0, 0, 0, 0, 0.001)

        for attr_string, default_val, attr_type, min_value in zip(attr_strings, default_vals, attr_types, min_values):

            pm.addAttr(self.mobject, longName=attr_string, attributeType=attr_type, defaultValue=default_val,
                       minValue=min_value, keyable=0)
            pm.setAttr(self.mobject + '.' + attr_string, channelBox=1)

            for module in self.modules.values():
                # ...Drive the same attrs on module placers
                pm.connectAttr(self.mobject + "." + attr_string, module.module_ctrl.mobject + "." + attr_string, f=1)
                pm.setAttr(module.module_ctrl.mobject + "." + attr_string, lock=1, channelBox=0)





    ####################################################################################################################
    def modules_from_data(self):

        data = self.modules

        # ...Make Armature Modules out of module dictionaries in data
        for key in data:
            m_data = data[key]

            # ...Fill in any missing properties with None values
            for property in ("rig_module_type", "name", "side", "is_driven_side", "position", "rotation", "scale",
                             "drive_target", "color", "draw_connections", "placers"):
                if not property in m_data:
                    m_data[property] = None


            new_module = ArmatureModule(
                rig_module_type=m_data["rig_module_type"],
                name=m_data["name"],
                side=m_data["side"],
                is_driven_side=m_data["is_driven_side"],
                position=m_data["position"],
                rotation=m_data["rotation"],
                scale=m_data["scale"],
                drive_target=m_data["drive_target"],
                draw_connections=m_data["draw_connections"],
                color=m_data["color"]
            )
            new_module.placers_from_data(m_data["placers"])

            data[key] = new_module

            if new_module.side in (nom.leftSideTag, nom.rightSideTag):
                self.sided_modules[new_module.side][key] = new_module





    ####################################################################################################################
    def assign_armature_metadata(self):

        target_obj = self.mobject

        pm.addAttr(target_obj, longName="ArmatureName", keyable=0, dataType="string")
        pm.setAttr(target_obj + "." + "ArmatureName", self.name, type="string", lock=1)

        if not pm.attributeQuery("ArmatureScale", node=target_obj, exists=1):
            pm.addAttr(target_obj, longName="ArmatureScale", attributeType=float, minValue=0.001, defaultValue=1,
                       keyable=0)
            pm.setAttr(target_obj + "." + "ArmatureScale", channelBox=1)

        pm.addAttr(target_obj, longName="SymmetryMode", keyable=0, dataType="string")
        pm.setAttr(target_obj + "." + "SymmetryMode", self.symmetry_mode, type="string", lock=1)

        pm.addAttr(target_obj, longName="DriverSide", keyable=0, dataType="string")
        pm.setAttr(target_obj + "." + "DriverSide", self.driver_side, type="string", lock=1)

        pm.addAttr(target_obj, longName="RootSize", keyable=0, attributeType="float")
        pm.setAttr(target_obj + "." + "RootSize", self.root_size, lock=1)





    ####################################################################################################################
    def populate_armature(self):

        self.mobject = self.create_root_obj()

        [module.populate_module() for module in self.modules.values()]

        for key in self.modules:
            module = self.modules[key]
            if module.side in (nom.leftSideTag, nom.rightSideTag):
                self.sided_modules[module.side][key] = module

        # ...Drive all module vis switches from armature root ------------------------------------------------------
        self.drive_module_attrs()

        # ...Connect modules to each other as specified in each module ---------------------------------------------
        [module.connect_modules() for module in self.modules.values()]

        # ...Enact live symmetry if needed -------------------------------------------------------------------------
        if self.symmetry_mode in ("Left drives Right", "Right drives Left"):
            self.setup_realtime_symmetry(driver_side=self.driver_side)
