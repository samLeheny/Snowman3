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
dir_string = {"module_build": "Snowman3.riggers.modules.{}.build.build"}
###########################
###########################





########################################################################################################################
class RigModule:
    def __init__(
        self,
        name = None,
        ctrl_data = None,
        side = None,
        rig_module_type = None,
        placer_data = None,
    ):
        self.name = gen_utils.get_clean_name(name)
        self.rig_module_type = rig_module_type
        self.side = side
        self.side_tag = f'{self.side}_' if self.side else ''
        self.placer_color = ctrl_colors[self.side] if self.side else ctrl_colors[nom.midSideTag]
        self.prefab_module_data = PrefabModuleData(prefab_key=self.rig_module_type, side=self.side)

        self.rig_module_grp = None
        self.no_transform_grp = None
        self.transform_grp = None
        self.bind_jnts = {}
        self.setup_module_ctrl = self.get_setup_module_ctrl()
        self.ctrl_data = ctrl_data if ctrl_data else self.prefab_module_data.ctrl_data
        self.placers = {}
        self.mConstruct = None
        self.placer_data = placer_data



    """
    --------- METHODS --------------------------------------------------------------------------------------------------
    --------------------------------------------------------------------------------------------------------------------
    create_rig_module_grp
    create_placers
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
    def create_placers(self):

        class Placer:
            def __init__(self, name, position, side=None):
                self.name = name
                self.side = side
                self.position = position
                self.world_position = None
                self.aim_vector = None
                self.up_vector = None
                self.orientation = None

            def get_orientation(self):
                side_tag = f'{self.side}_' if self.side else ''
                placer = pm.PyNode(f'::{side_tag}{self.name}_PLC')
                aim_handle_string = f'::{side_tag}{self.name}_AIM'
                if not pm.objExists(aim_handle_string):
                    return
                aim_handle = pm.PyNode(aim_handle_string)
                up_handle = pm.PyNode(f'::{side_tag}{self.name}_UP')
                self.world_position = pm.xform(placer, q=1, rotatePivot=1, worldSpace=1)
                aim_position = pm.xform(aim_handle, q=1, rotatePivot=1, worldSpace=1)
                up_position = pm.xform(up_handle, q=1, rotatePivot=1, worldSpace=1)
                self.aim_vector = [aim_position[i]-self.world_position[i] for i in range(3)]
                self.up_vector = [up_position[i]-self.world_position[i] for i in range(3)]
                self.orientation = gen_utils.vectors_to_euler(aim_vector=self.aim_vector, up_vector=self.up_vector,
                                                              aim_axis=(0, 0, 1), up_axis=(0, 1, 0), rotation_order=0)

        for placer_key, data in self.placer_data.items():
            self.placers[placer_key] = Placer(name=data['name'], side=data['side'], position=data['position'])
            self.placers[placer_key].get_orientation()



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

        self.create_rig_module_grp(parent=rig_parent)
        self.create_placers()
        self.get_setup_module_ctrl()
        self.mConstruct = build_script.build(rig_module=self, rig_parent=rig_parent)

        return self.mConstruct



    ####################################################################################################################
    def update_data_from_scene(self):
        pass
