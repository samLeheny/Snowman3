# Title: controls_IO.py
# Author: Sam Leheny
# Contact: samleheny@live.com

# Description:


###########################
##### Import Commands #####
import importlib
import pymel.core as pm
import json
import os
import Snowman3.utilities.general_utils as gen_utils
importlib.reload(gen_utils)

import Snowman3.dictionaries.nameConventions as nameConventions
importlib.reload(nameConventions)
nom = nameConventions.create_dict()
###########################
###########################

###########################
######## Variables ########

###########################
###########################





########################################################################################################################


dirpath = r'C:\Users\61451\Desktop' #...For testing purposes


class CtrlDataIO(object):

    def __init__(
        self,
        dirpath
    ):
        self.dirpath = dirpath
        self.filepath = f'{self.dirpath}/test_armature_data.json'
        self.scene_ctrls = None




    ####################################################################################################################
    def get_all_ctrls_in_scene(self):

        #...Get all transform nodes ending with control suffix
        transform_suffix_nodes = pm.ls(f'::*_{nom.animCtrl}', type='transform')
        #...Test each to confirm it has a nurbs curve(s) as an immediate child
        anim_ctrls = []
        for node in transform_suffix_nodes:
            for shape in node.getShapes():
                if shape.nodeType() == 'nurbsCurve':
                    anim_ctrls.append(node)
                    continue

        self.scene_ctrls = anim_ctrls