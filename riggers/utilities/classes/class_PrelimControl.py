# Title: class_PrelimControl.py
# Author: Sam Leheny
# Contact: samleheny@live.com

# Description:


###########################
##### Import Commands #####
import importlib
import pymel.core as pm

import Snowman3.utilities.general_utils as gen_utils
importlib.reload(gen_utils)

import Snowman3.utilities.rig_utils as rig_utils
importlib.reload(rig_utils)

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
class PrelimControl:
    def __init__(
        self,
        name = None,
        shape = None,
        size = None,
        shape_offset = None,
        color = None,
        position = None,
        position_weights = None,
        orientation = None,
        locks = None,
        forward_direction = None,
        up_direction = None,
        side = None,
        is_driven_side = None,
        body_module = None
    ):
        self.name = name
        self.shape = shape
        self.size = size if size else [1.0, 1.0, 1.0]
        self.shape_offset = shape_offset
        self.color = color
        self.position = position
        self.position_weights = position_weights
        self.orientation = orientation
        self.locks = locks if locks else {'v': 1}
        self.forward_direction = forward_direction if forward_direction else [0, 0, 1]
        self.up_direction = up_direction if up_direction else [0, 1, 0]
        self.side = side
        self.side_tag = f'{self.side}_' if self.side else ''
        self.is_driven_side = is_driven_side
        self.body_module = body_module

        self.ctrl_obj = None
        self.shape_data = None





    ####################################################################################################################
    def assemble_shape_data(self):

        #...Assemble data with which to build controls
        self.shape_data = {'name': self.name,
                           'shape': self.shape,
                           'color': self.color,
                           'locks': self.locks,
                           'forward_direction': self.forward_direction,
                           'up_direction': self.up_direction,
                           'scale': self.size,
                           'offset': self.shape_offset
                           }

        return self.shape_data





    ####################################################################################################################
    def create_prelim_ctrl_obj(self):

        #...Assemble shape data if needed
        self.assemble_shape_data() if not self.shape_data else None

        #...Create control object
        self.ctrl_obj = rig_utils.control(ctrl_info=self.shape_data, ctrl_type="prelim_ctrl", side=self.side)

        return self.ctrl_obj





    ####################################################################################################################
    def position_prelim_ctrl(self, body_module):


        if self.position:

            #...Ensure position_data is type: tuple
            self.position = (self.position,) if not isinstance(self.position, tuple) else self.position

            #...Use keys in position_data to get corresponding placers
            position_placers = tuple([body_module.placers[key].mobject for key in self.position])

            #...Constrain control's position between placers (or at placer if only one placer provided)
            position_constraint = pm.pointConstraint(position_placers, self.ctrl_obj)

            if len(self.position) > 1:
                if self.position_weights:

                    constraint_weights = pm.pointConstraint(position_constraint, q=1, weightAliasList=1)
                    [pm.setAttr(c, p) for c, p in zip(constraint_weights, self.position_weights)]





    ####################################################################################################################
    def orient_prelim_ctrl(self):


        if not self.orientation:
            return

        if 'match_to' in self.orientation:

            if self.orientation['match_to'] == 'module_ctrl':
                pm.setAttr(self.ctrl_obj.rotate, 0, 0, 0)
                pm.setAttr(self.ctrl_obj.scale, 1, 1, 1)

            else:

                match_key = self.orientation['match_to']

                if not isinstance(match_key, (list, tuple)):
                    match_key = (match_key,)

                match_objs = []
                for key in match_key:

                    ori_string = f'::{self.side_tag}{key}_{nom.orienter}'

                    if pm.objExists(ori_string):
                        ori = pm.ls(f'::{self.side_tag}{key}_{nom.orienter}')
                    else:
                        print(f'Could not find orienter "{ori_string}" in scene')

                    if ori:
                        match_objs.append(ori[0])

                pm.orientConstraint(tuple(match_objs), self.ctrl_obj)


        elif 'aim_vector' in self.orientation:

            aim_axis = self.orientation['aim_vector'][0]
            aim_vector = self.orientation['aim_vector'][1]

            up_axis = self.orientation['up_vector'][0]
            up_vector = self.orientation['up_vector'][1]

            self.ctrl_obj.setParent(world=1)

            rot_values = gen_utils.vectors_to_euler(aim_axis=aim_axis, aim_vector=aim_vector,
                                                    up_axis=up_axis, up_vector=up_vector,
                                                    rotation_order=self.ctrl_obj.rotateOrder.get())

            self.ctrl_obj.rotate.set(tuple(rot_values))
