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
        self.filepath = f'{self.dirpath}/test_ctrlShape_data.json'
        self.scene_ctrls = None
        self.ctrl_shapes_data = {}




    ####################################################################################################################
    def get_all_ctrls_in_scene(self):

        scene_ctrls = []

        #...Get all transform nodes ending with control suffix
        transform_suffix_nodes = pm.ls(f'::*_{nom.animCtrl}', type='transform')
        #...Test each to confirm it has a nurbs curve(s) as an immediate child
        for node in transform_suffix_nodes:
            for shape in node.getShapes():
                if shape.nodeType() == 'nurbsCurve':
                    scene_ctrls.append(node)
                    continue

        # ...Get all transform nodes ending with control suffix
        transform_suffix_nodes = pm.ls(f'::*_{nom.prelimCtrl}', type='transform')
        # ...Test each to confirm it has a nurbs curve(s) as an immediate child
        for node in transform_suffix_nodes:
            for shape in node.getShapes():
                if shape.nodeType() == 'nurbsCurve':
                    scene_ctrls.append(node)
                    continue

        self.scene_ctrls = scene_ctrls





    ####################################################################################################################
    def ctrl_compose_shape_data(self):

        unwanted_suffixes = [f'_{nom.prelimCtrl}', f'_{nom.animCtrl}']

        for ctrl in self.scene_ctrls:

            ctrl_key = gen_utils.get_clean_name(str(ctrl))
            for suffix in unwanted_suffixes:
                if not ctrl_key.endswith(suffix):
                    continue
                ctrl_key = ctrl_key.split(suffix)[0]
                break

            self.ctrl_shapes_data[ctrl_key] = gen_utils.get_shape_data_from_obj(ctrl)





    ####################################################################################################################
    def save(self):

        with open(self.filepath, 'w') as fh:
            json.dump(self.ctrl_shapes_data, fh, indent=5)
