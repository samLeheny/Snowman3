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

import Snowman3.riggers.utilities.armature_utils as amtr_utils
importlib.reload(amtr_utils)

import Snowman3.riggers.utilities.directories.get_armature_data as get_armature_data
importlib.reload(get_armature_data)

import Snowman3.riggers.utilities.classes.class_RigModule as class_RigModules
importlib.reload(class_RigModules)
RigModule = class_RigModules.RigModule

import Snowman3.riggers.IO.attr_handoffs_IO as attrHandoffs_IO
importlib.reload(attrHandoffs_IO)
AttrHandoffsDataIO = attrHandoffs_IO.AttrHandoffsDataIO
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
        armature_has_prefab_key = pm.attributeQuery("ArmaturePrefabKey", node=self.armature, exists=1)

        if armature_has_prefab_key:
            rig_prefab_type = pm.getAttr(f'{self.armature}.ArmaturePrefabKey')

        return rig_prefab_type





    ####################################################################################################################
    def get_armature_module_mObj(self, module_key):

        armature_module = None

        #...Look for Armature module attribute on provided armature node
        attr_string = f'Module_{module_key}'
        module_in_armature = pm.attributeQuery(attr_string, node=self.armature, exists=1)

        if module_in_armature:
            source_nodes = pm.listConnections(f'{self.armature}.{attr_string}', s=1, d=0)
            armature_module = source_nodes[0] if source_nodes else None

        return armature_module





    ####################################################################################################################
    def create_root_groups(self):

        self.character_grp = pm.group(name=f'{self.name}CHAR', world=1, empty=1)
        self.rig_grp = pm.group(name='rig', parent=self.character_grp, empty=1)
        self.geo_grp = pm.group(name='geo', parent=self.character_grp, empty=1)





    ####################################################################################################################
    def get_armature_modules(self):

        self.armature_modules = amtr_utils.get_modules_in_armature(self.armature)





    ####################################################################################################################
    def get_module_types(self):

        for key in self.armature_modules:
            self.module_types[key] = amtr_utils.get_module_type(self.armature_modules[key])





    ####################################################################################################################
    def perform_module_attr_handoffs(self):

        self.attr_handoffs = get_armature_data.attr_handoffs(self.rig_prefab_type, self.modules)

        dirpath = r'C:\Users\User\Desktop\test_build'
        attr_handoffs_IO = AttrHandoffsDataIO(attr_handoffs=self.attr_handoffs, dirpath=dirpath)
        attr_handoffs_IO.save()

        for handoff in self.attr_handoffs:
            handoff.perform_attr_handoff()





    ####################################################################################################################
    def attach_modules(self):

        connection_pairs = get_armature_data.module_connections(self.rig_prefab_type, self.modules)

        for pair in connection_pairs:
            #...Create a locator to hold transforms
            loc = pm.spaceLocator(name=f'{gen_utils.get_clean_name(pair[1])}_SPACE')
            #...Match locator to rotate + scale of DRIVEN node (to account for modules in flipped space)
            loc.setParent(pair[1])
            gen_utils.zero_out(loc)
            #...Match locator to translate of DRIVER node (so scaling the driver won't offset the pivot position)
            loc.setParent(pair[0])
            loc.translate.set(0, 0, 0)
            #...Constraint DRIVEN node to locator (with offset!)
            pm.parentConstraint(loc, pair[1], mo=1)





    ####################################################################################################################
    def install_space_blends(self):

        get_armature_data.space_blends(self.rig_prefab_type, self.modules)





    ####################################################################################################################
    def populate_rig(self):

        #...Get information from armature
        self.create_root_groups()
        self.get_armature_modules()
        self.get_module_types()

        #...Get modules data from armature
        for module_key in self.armature_modules:
            armature_module = self.get_armature_module_mObj(module_key=module_key)
            self.modules[module_key] = RigModule(
                name = pm.getAttr(f'{armature_module}.ModuleNameParticle'),
                rig_module_type = self.module_types[module_key],
                armature_module = armature_module,
                side = pm.getAttr(f'{armature_module}.Side'),
                piece_keys = amtr_utils.get_piece_keys_from_module(armature_module))

        #...Build modules in scene
        [module.populate_rig_module(rig_parent=self.rig_grp) for module in self.modules.values()]

        #...Compose dictionary of sided modules (left and right)
        for key, module in self.modules.items():
            if module.side in (nom.leftSideTag, nom.rightSideTag):
                self.sided_modules[module.side][key] = module


        #...Transfer attributes between nodes in the rig as specified in the attr_handoffs data
        self.perform_module_attr_handoffs()
        #...Attach modules to each other in accordance with prefab's connection pairs data
        self.attach_modules()
        #...Install space blends
        self.install_space_blends()
