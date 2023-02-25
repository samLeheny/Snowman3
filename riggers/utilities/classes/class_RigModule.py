# Title: class_RigModule.py
# Author: Sam Leheny
# Contact: samleheny@live.com

# Description:


###########################
##### Import Commands #####
import importlib
import importlib
import pymel.core as pm

import Snowman3.utilities.general_utils as gen_utils
importlib.reload(gen_utils)

import Snowman3.riggers.utilities.armature_utils as amtr_utils
importlib.reload(amtr_utils)

import Snowman3.dictionaries.nameConventions as nameConventions
importlib.reload(nameConventions)
nom = nameConventions.create_dict()

import Snowman3.riggers.dictionaries.control_colors as control_colors
importlib.reload(control_colors)
ctrl_colors = control_colors.create_dict()

import Snowman3.riggers.utilities.classes.class_PrefabModuleData as classPrefabModuleData
importlib.reload(classPrefabModuleData)
PrefabModuleData = classPrefabModuleData.PrefabModuleData
###########################
###########################


###########################
######## Variables ########
vis_switch_enum_strings = {
    "placers" : "PlacersVis",
    "orienters" : "OrientersVis",
    "controls" : "ControlsVis"
}
dir_string = {"module_build": "Snowman3.riggers.modules.{}.build.build"}
###########################
###########################





########################################################################################################################
class RigModule:
    def __init__(
        self,
        name = None,
        module_tag = None,
        body_pieces = None,
        ctrl_data = None,
        side = None,
        piece_keys = None,
        rig_module_type = None,
        placer_data = None,
    ):
        self.name = gen_utils.get_clean_name(name)
        self.body_pieces = body_pieces
        self.rig_module_type = rig_module_type
        self.side = side
        self.side_tag = f'{self.side}_' if self.side else ''
        self.module_tag = module_tag if module_tag else self.side_tag+self.name
        self.placer_color = ctrl_colors[self.side] if self.side else ctrl_colors[nom.midSideTag]
        self.piece_keys = piece_keys
        self.prefab_module_data = PrefabModuleData(
            prefab_key=self.rig_module_type,
            side=self.side
        )

        self.rig_module_grp = None
        self.no_transform_grp = None
        self.transform_grp = None
        self.bind_jnts = {}
        self.setup_module_ctrl = self.get_setup_module_ctrl()
        self.ctrl_data = ctrl_data if ctrl_data else self.prefab_module_data.ctrl_data
        self.placers = {}
        self.pv_placers = {}
        self.orienters = {}
        self.settings_ctrl = None
        self.mConstruct = None
        self.socket = {}
        self.placer_data = placer_data





    """
    --------- METHODS --------------------------------------------------------------------------------------------------
    --------------------------------------------------------------------------------------------------------------------
    create_rig_module_grp
    get_armature_placers
    create_orienters
    get_setup_module_ctrl
    populate_rig_module
    --------------------------------------------------------------------------------------------------------------------
    --------------------------------------------------------------------------------------------------------------------
    """





    ####################################################################################################################
    def create_rig_module_grp(self, parent=None):

        self.rig_module_grp = pm.group(name=f'{self.side_tag}{self.name}_RIG', world=1, em=1)

        pm.addAttr(self.rig_module_grp, longName='RigScale', attributeType='float', defaultValue=1.0, keyable=0)

        self.transform_grp = pm.group(name='transform', p=self.rig_module_grp, em=1)
        self.no_transform_grp = pm.group(name='no_transform', p=self.rig_module_grp, em=1)
        self.no_transform_grp.inheritsTransform.set(0, lock=1)

        self.rig_module_grp.setParent(parent) if parent else None

        if self.side == nom.rightSideTag:
            grps_to_flip = (self.rig_module_grp, self.no_transform_grp)
            [gen_utils.flip(grp) for grp in grps_to_flip]


        # --------------------------------------------------------------------------------------------------------------
        pm.select(clear=1)
        return self.rig_module_grp





    ####################################################################################################################
    def create_orienters(self):

        orienters = []
        placers = {}

        class Placer:
            def __init__(self, name, position, side=None):
                name=name,
                side=side,
                position=position

        for placer_key, data in self.placer_data.items():
            placers[placer_key] = Placer(name=data['name'], side=data['side'], position=data['position'])

        for p in placers.items():
            print(p)


        '''armature_placers = amtr_utils.get_placers_in_module(self.armature_module)

        for placer in armature_placers.values():
            key = pm.getAttr(f'{placer}.PlacerTag')
            self.orienters[key] = pm.listConnections(f'{placer}.OrienterNode', s=1, d=0)[0]'''





    ####################################################################################################################
    def get_setup_module_ctrl(self):

        search_string = f'::{self.side_tag}{self.name}_{nom.setupCtrl}'

        if pm.ls(search_string):
            self.setup_module_ctrl = pm.ls(search_string)[0]
        else:
            self.setup_module_ctrl = None

        return self.setup_module_ctrl





    ####################################################################################################################
    def populate_rig_module(self, rig_parent=None):

        build_script = importlib.import_module(dir_string['module_build'].format(self.rig_module_type))
        importlib.reload(build_script)

        '''exception_types = ['root']
        if self.module_tag not in exception_types:'''

        #...Create rig group
        self.create_rig_module_grp(parent=rig_parent)
        #...Get orienters from armature
        self.create_orienters()
        '''self.get_setup_module_ctrl()'''

        self.mConstruct = build_script.build(rig_module=self, rig_parent=rig_parent)

        return self.mConstruct
