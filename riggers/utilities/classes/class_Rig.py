# Title: class_Rig.py
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

import Snowman3.utilities.general_utils as gen_utils
importlib.reload(gen_utils)

import Snowman3.riggers.utilities.armature_utils as arm_utils
importlib.reload(arm_utils)

import Snowman3.riggers.utilities.directories.get_armature_data as get_armature_data
importlib.reload(get_armature_data)

import Snowman3.riggers.utilities.classes.class_RigModule as class_RigModules
importlib.reload(class_RigModules)
RigModule = class_RigModules.RigModule
###########################
###########################


###########################
######## Variables ########

###########################
###########################





########################################################################################################################
class Rig:
    def __init__(
        self,
        name,
        armature,

    ):
        self.name = gen_utils.get_clean_name(name)
        self.armature = armature
        self.modules = {}
        self.armature_modules = None
        self.module_types = {}
        self.sided_modules = {nom.leftSideTag: {}, nom.rightSideTag: {}}
        self.character_grp = None
        self.rig_grp = None
        self.geo_grp = None
        self.attr_handoffs = {}
        self.rig_prefab_type = self.get_rig_prefab_type()





    """
    --------- METHODS --------------------------------------------------------------------------------------------------
    --------------------------------------------------------------------------------------------------------------------
    get_rig_prefab_type
    get_armature_module_mObj
    create_root_groups
    get_armature_modules
    get_module_types
    perform_module_attr_handoffs
    populate_rig
    --------------------------------------------------------------------------------------------------------------------
    --------------------------------------------------------------------------------------------------------------------
    """





    ####################################################################################################################
    def get_rig_prefab_type(self):

        rig_prefab_type = None
        if pm.attributeQuery("ArmaturePrefabKey", node=self.armature, exists=1):
            rig_prefab_type = pm.getAttr(f'{self.armature}.ArmaturePrefabKey')

        return rig_prefab_type





    ####################################################################################################################
    def get_armature_module_mObj(self, key):
        """
        Given an armature, will look through its connections to find the armature module of the specified key.
        Args:
            key (str): The name of the string attribute that is connected to the desired module.
        Returns:
            (mObj): Armature module root object.
        """

        armature_module = None

        # ...Look for Armature modules attributes on provided armature node
        attr_string = f'Module_{key}'
        if pm.attributeQuery(attr_string, node=self.armature, exists=1):
            # ...Find the string attribute that matches provided key
            in_connections = pm.listConnections(f'{self.armature}.{attr_string}', s=1, d=0)
            if in_connections:
                armature_module = in_connections[0]

        return armature_module





    ####################################################################################################################
    def create_root_groups(self):

        self.character_grp = pm.group(name=f'{self.name}CHAR', world=1, em=1)
        self.rig_grp = pm.group(name='rig', p=self.character_grp, em=1)
        self.geo_grp = pm.group(name='geo', p=self.character_grp, em=1)





    ####################################################################################################################
    def get_armature_modules(self):

        self.armature_modules = arm_utils.get_modules_in_armature(self.armature)





    ####################################################################################################################
    def get_module_types(self):

        if not self.armature_modules:
            self.get_armature_modules()

        for key in self.armature_modules:
            self.module_types[key] = arm_utils.get_module_type(self.armature_modules[key])





    ####################################################################################################################
    def perform_module_attr_handoffs(self):

        attr_exceptions = ("LockAttrData", "LockAttrDataT", "LockAttrDataR", "LockAttrDataS", "LockAttrDataV")

        self.attr_handoffs = get_armature_data.attr_handoffs(self.rig_prefab_type)

        for key, data in self.attr_handoffs.items():
            for handoff in data:
                if key in ("root", "spine", "neck", "L_clavicle", "R_clavicle", "L_arm", "R_arm"):
                    module = self.modules[key]

                    old_ctrl_key, new_ctrl_data, delete_old_ctrl = handoff
                    old_ctrl = module.ctrls[old_ctrl_key]
                    new_ctrl = self.modules[new_ctrl_data[0]].ctrls[new_ctrl_data[1]]

                    attrs = pm.listAttr(old_ctrl, userDefined=1)
                    [attrs.remove(a) if a in attrs else None for a in attr_exceptions]
                    for attr in attrs:
                        gen_utils.migrate_attr(old_ctrl, new_ctrl, attr)

                    if delete_old_ctrl:
                        pm.delete(old_ctrl)





    ####################################################################################################################
    def attach_modules(self):

        connection_pairs = get_armature_data.module_connections(self.rig_prefab_type, self.modules)

        for pair in connection_pairs:
            # ...Create a locator to hold transforms
            loc = pm.spaceLocator(name=f'{gen_utils.get_clean_name(pair[1])}_SPACE')
            # ...Match locator to rotate + scale of DRIVEN node (to account for modules in flipped space)
            loc.setParent(pair[1])
            gen_utils.zero_out(loc)
            # ...Match locator to translate of DRIVER node (so scaling the driver won't offset the pivot position)
            loc.setParent(pair[0])
            loc.translate.set(0, 0, 0)
            # ...Constraint DRIVEN node to locator (with offset!)
            pm.parentConstraint(loc, pair[1], mo=1)





    ####################################################################################################################
    def populate_rig(self):

        # ...Get information from armature
        self.create_root_groups()
        self.get_module_types()

        #for key in armature_modules:
        for key in ('root', 'spine', 'neck', 'L_clavicle', 'R_clavicle', 'L_arm', 'R_arm', 'L_hand', 'R_hand', 'L_leg',
                    'R_leg', 'L_foot', 'R_foot'):

            armature_module = self.get_armature_module_mObj(key)

            self.modules[key] = RigModule(
                name=pm.getAttr(f'{armature_module}.ModuleNameParticle'),
                rig_module_type=self.module_types[key],
                armature_module=armature_module,
                side=pm.getAttr(f'{armature_module}.Side'),
                piece_keys=arm_utils.get_piece_keys_from_module(armature_module)
            )

        # ...Build modules in scene
        [module.populate_rig_module(rig_parent=self.rig_grp) for module in self.modules.values()]

        # ...Populate sided modules dictionary
        for key, module in self.modules.items():
            if module.side in (nom.leftSideTag, nom.rightSideTag):
                self.sided_modules[module.side][key] = module

        # ...Connect modules to each other as specified in each module
        self.perform_module_attr_handoffs()

        # ...
        self.attach_modules()



