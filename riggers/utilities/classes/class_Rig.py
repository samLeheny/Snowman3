# Title: class_Rig.py
# Author: Sam Leheny
# Contact: samleheny@live.com

# Description:


###########################
##### Import Commands #####
import os
import json
import importlib
import pymel.core as pm

import Snowman3.dictionaries.nameConventions as nameConventions
importlib.reload(nameConventions)
nom = nameConventions.create_dict()

import Snowman3.utilities.general_utils as gen_utils
importlib.reload(gen_utils)

import Snowman3.riggers.utilities.armature_utils as amtr_utils
importlib.reload(amtr_utils)

import Snowman3.riggers.utilities.classes.class_RigModule as class_RigModules
importlib.reload(class_RigModules)
RigModule = class_RigModules.RigModule

import Snowman3.riggers.IO.attr_handoffs_IO as attrHandoffs_IO
import Snowman3.riggers.IO.space_blends_IO as spaceBlends_IO
import Snowman3.riggers.IO.connection_pairs_IO as connectionPairs_IO
importlib.reload(attrHandoffs_IO)
importlib.reload(spaceBlends_IO)
importlib.reload(connectionPairs_IO)
AttrHandoffsDataIO = attrHandoffs_IO.AttrHandoffsDataIO
SpaceBlendsDataIO = spaceBlends_IO.SpaceBlendsDataIO
ConnectionPairsDataIO = connectionPairs_IO.ConnectionPairsDataIO

import Snowman3.riggers.utilities.classes.class_PrefabArmatureData as classPrefabArmature
importlib.reload(classPrefabArmature)
PrefabArmature = classPrefabArmature.PrefabArmatureData

import Snowman3.riggers.IO.rig_module_IO as rigModule_IO
importlib.reload(rigModule_IO)
RigModuleIO = rigModule_IO.RigModuleDataIO
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
        self.space_blends = None
        self.connection_pairs = None
        self.prefab_data = None





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
    def get_armature_modules(self, dirpath):

        filepath = dirpath+'/module_roster.json'

        # ...
        if not os.path.exists(filepath):
            print(f'ERROR: Provided file path "{filepath}" not found on disk.')
            return False

        # ...Read data
        with open(filepath, 'r') as fh:
            module_roster = json.load(fh)

        self.armature_modules = {}
        for module_name in module_roster:
            io = RigModuleIO(dirpath=dirpath+'/rig_modules/'+module_name)
            module = io.get_module_data_from_file()
            self.armature_modules[list(module.keys())[0]] = list(module.values())[0]

        ###self.armature_modules = amtr_utils.get_modules_in_armature(self.armature)



    ####################################################################################################################
    def get_module_types(self):
        for key in self.armature_modules:
            self.module_types[key] = amtr_utils.get_module_type(self.armature_modules[key])



    ####################################################################################################################
    def perform_module_attr_handoffs(self):

        self.attr_handoffs = self.prefab_data.get_attr_handoffs()

        attr_handoffs_IO = AttrHandoffsDataIO(attr_handoffs=self.attr_handoffs, dirpath=dirpath)
        attr_handoffs_IO.save()

        for handoff in self.attr_handoffs:
            print(handoff.old_attr_node)
            handoff.perform_attr_handoff()



    ####################################################################################################################
    def attach_modules(self):

        self.connection_pairs = self.prefab_data.get_module_connections()

        connection_pairs_IO = ConnectionPairsDataIO(connection_pairs=self.connection_pairs, dirpath=dirpath)
        connection_pairs_IO.save()
        [pair.connect_sockets() for pair in self.connection_pairs]



    ####################################################################################################################
    def install_space_blends(self):

        self.space_blends = self.prefab_data.get_space_blends()

        space_blends_IO = SpaceBlendsDataIO(space_blends=self.space_blends, dirpath=dirpath)
        space_blends_IO.save()
        [b.install_blend()for b in self.space_blends]



    ####################################################################################################################
    def populate_rig(self, dirpath):

        print('*'*120)
        print(f"Building rig modules...\n")

        #...Get information from armature
        self.create_root_groups()
        self.get_armature_modules(dirpath)
        ###self.get_module_types()

        #...Get modules data from armature
        for module_key in self.armature_modules:
            print(f"CREATE MODULE: {module_key}")

            '''armature_module = self.get_armature_module_mObj(module_key=module_key)
            self.modules[module_key] = RigModule(
                name = pm.getAttr(f'{armature_module}.ModuleNameParticle'),
                rig_module_type = self.module_types[module_key],
                armature_module = armature_module,
                side = pm.getAttr(f'{armature_module}.Side'),
                piece_keys = amtr_utils.get_piece_keys_from_module(armature_module))'''

        #...Build modules in scene
        '''[module.populate_rig_module(rig_parent=self.rig_grp) for module in self.modules.values()]'''

        #...Compose dictionary of sided modules (left and right)
        '''for key, module in self.modules.items():
            if module.side in (nom.leftSideTag, nom.rightSideTag):
                self.sided_modules[module.side][key] = module'''

        '''self.prefab_data = PrefabArmature(prefab_key=self.rig_prefab_type, rig_modules=self.modules)'''

        '''
        #...Transfer attributes between nodes in the rig as specified in the attr_handoffs data
        self.perform_module_attr_handoffs()
        #...Attach modules to each other in accordance with prefab's connection pairs data
        self.attach_modules()
        #...Install space blends
        self.install_space_blends()
        '''
