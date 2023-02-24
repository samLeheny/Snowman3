# Title: root_setup.py
# Author: Sam Leheny
# Contact: samleheny@live.com

# Description: Builds setup module of character body rig's root controls.


###########################
##### Import Commands #####
import importlib

import Snowman3.utilities.general_utils as gen_utils
importlib.reload(gen_utils)

import Snowman3.dictionaries.nameConventions as nameConventions
importlib.reload(nameConventions)
nom = nameConventions.create_dict()

import Snowman3.riggers.modules.root.setup.subModules.ctrl_vis_conditions as vis_conditions
importlib.reload(vis_conditions)

import Snowman3.riggers.dictionaries.body_attributes as body_attributes
importlib.reload(body_attributes)
attrNom = body_attributes.create_dict()

import Snowman3.riggers.modules.root.data.placers as armature_module_placers
import Snowman3.riggers.modules.root.data.ctrl_data as root_prelimControls
importlib.reload(armature_module_placers)
importlib.reload(root_prelimControls)
###########################
###########################


###########################
######## Variables ########

###########################
###########################





########################################################################################################################
def build(armature_module):


    #armature_module.populate_module()

    #...Position module
    armature_module.position_module()


    #...Connect to another module if specified ------------------------------------------------------------------------
    armature_module.connect_modules()



    #...Preliminary controls -------------------------------------------------------------------------------------------
    armature_module.ctrl_data = root_prelimControls.create_ctrl_data(side=armature_module.side)

    armature_module.create_prelim_ctrls()




    return armature_module
