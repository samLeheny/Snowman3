# Title: class_PrelimControl.py
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
###########################
###########################


###########################
######## Variables ########

###########################
###########################





########################################################################################################################
class AnimControl:
    def __init__(
        self,
        ctrl_name_tag,
        prelim_ctrl_name,
        side = None,
        match_transform = None,
        module_ctrl = None,
    ):
        self.ctrl_name_tag = ctrl_name_tag
        self.prelim_ctrl_name = prelim_ctrl_name if prelim_ctrl_name else self.ctrl_name_tag
        self.side = side
        self.match_transform = match_transform if match_transform else None

        self.side_tag = f'{self.side}_' if self.side else ''
        self.prelim_ctrl = None
        self.ctrl_transform = None
        self.module_ctrl_obj = module_ctrl if module_ctrl else None


    """
    --------- METHODS --------------------------------------------------------------------------------------------------
    --------------------------------------------------------------------------------------------------------------------
    get_prelim_ctrl
    initialize_anim_ctrl
    convert_existing_obj_to_ctrl
    new_ctrl_transform
    position_ctrl
    prep_center_ctrl_to_prelim_ctrl
    prep_center_ctrl_to_orienter
    copy_shape_from_prelim
    transfer_locks_from_prelim
    finalize_anim_ctrl
    assign_new_shape
    --------------------------------------------------------------------------------------------------------------------
    --------------------------------------------------------------------------------------------------------------------
    """



    ####################################################################################################################
    def get_prelim_ctrl(self):

        search_string = f'{self.side_tag}{self.prelim_ctrl_name}_{nom.nonAnimCtrl}'

        search = pm.ls(f'::{search_string}')
        if search:
            if len(search) == 1:
                self.prelim_ctrl = search[0]

        if not self.prelim_ctrl:
            print("Unable to find prelim control corresponding to: '{}'".format(self.ctrl_name_tag))

        return self.prelim_ctrl





    ####################################################################################################################
    def initialize_anim_ctrl(self, existing_obj=None, parent=None):

        #...If an existing object was provided, rename it and denote it as the initialized control object
        if existing_obj:
            self.convert_existing_obj_to_ctrl(existing_obj)
            return self.ctrl_transform

        #...Or -------------------
        #...Create an empty transform node to serve as control (it will get a shape later)
        self.new_ctrl_transform(parent=parent)
        return self.ctrl_transform





    ####################################################################################################################
    def convert_existing_obj_to_ctrl(self, obj):

        obj.rename(f'{self.side_tag}{self.ctrl_name_tag}_{nom.animCtrl}')
        self.ctrl_transform = obj





    ####################################################################################################################
    def new_ctrl_transform(self, parent):

        self.ctrl_transform = pm.shadingNode('transform',
                                             name=f'{self.side_tag}{self.ctrl_name_tag}_{nom.animCtrl}', au=1)
        self.ctrl_transform.setParent(parent) if parent else None

        #...Position control
        self.position_ctrl(self.ctrl_transform)





    ####################################################################################################################
    def position_ctrl(self, ctrl):

        temp_loc, match_transform_obj = None, None

        #...Get corresponding prelim ctrl if none was provided
        if not self.prelim_ctrl:
            self.prelim_ctrl = self.get_prelim_ctrl()

        if not self.match_transform:
            #...Get corresponding prelim control in scene
            match_transform_obj = self.prelim_ctrl if self.prelim_ctrl else None

        #...Matching ctrl -
        else:
            #... - to its module's root ctrl
            if self.match_transform == 'module_ctrl':
                match_transform_obj = self.module_ctrl_obj
            #... - to its prelim ctrl's shape's center
            elif self.match_transform == 'center to prelim':
                match_transform_obj = temp_loc = self.prep_center_ctrl_to_prelim_ctrl(ctrl)
            #... - to its orienter
            else:
                match_transform_obj = temp_loc = self.prep_center_ctrl_to_orienter(ctrl)

        #...Put ctrl into final position
        pm.matchTransform(ctrl, match_transform_obj)
        #...Do away with any temp locator
        pm.delete(temp_loc) if temp_loc else None





    ####################################################################################################################
    def prep_center_ctrl_to_prelim_ctrl(self, ctrl):

        #...Get center of prelim ctrl's shape
        center_coord = gen_utils.get_shape_center(self.prelim_ctrl)
        #...Create temporary locator that matches prelim ctrl's position
        temp_loc = pm.spaceLocator()
        temp_loc.setParent(self.prelim_ctrl)
        gen_utils.zero_out(temp_loc)
        temp_loc.setParent(world=1)
        #...Ensure locator is at the center of prelim ctrl's shape, while retaining prelim ctrl's rotate and scale
        temp_loc.translate.set(center_coord)
        #...Put locator alongside control
        temp_loc.setParent(ctrl.getParent())

        return temp_loc





    ####################################################################################################################
    def prep_center_ctrl_to_orienter(self, ctrl):

        #...Match temp locator to corresponding orienter
        ori = pm.ls(f'::{self.side_tag}{self.match_transform}_{nom.orienter}')[0]
        temp_loc = pm.spaceLocator()
        temp_loc.setParent(ori)
        gen_utils.zero_out(temp_loc)
        #...Put locator alongside ctrl and make loc the match transform object
        temp_loc.setParent(ctrl.getParent())

        return temp_loc





    ####################################################################################################################
    def copy_shape_from_prelim(self, delete_existing_shapes=False, keep_original=True):

        #...Get corresponding prelim control in scene
        self.get_prelim_ctrl() if not self.prelim_ctrl else None

        for attr in gen_utils.all_transform_attrs:
            gen_utils.break_connections(f'{self.prelim_ctrl}.{attr}')

        #...Copy shape across
        gen_utils.copy_shapes(self.prelim_ctrl, self.ctrl_transform, delete_existing_shapes=delete_existing_shapes,
                              keep_original=keep_original)





    ####################################################################################################################
    def transfer_locks_from_prelim(self):

        #...Get corresponding prelim control in scene
        self.get_prelim_ctrl() if not self.prelim_ctrl else None

        #...Transfer lock information from prelim control to final control
        attr = 'LockAttrData'
        if pm.attributeQuery(attr, node=self.prelim_ctrl, exists=1):
            pm.addAttr(self.ctrl_transform, longName=attr, keyable=0, attributeType='compound', numberOfChildren=4)
            for key in ('T', 'R', 'S', 'V'):
                pm.addAttr(self.ctrl_transform, longName=f'{attr}{key}', dataType='string', parent=attr)

        for attr in (f'{attr}T', f'{attr}R', f'{attr}S', f'{attr}V'):
            pm.setAttr(f'{self.ctrl_transform}.{attr}', pm.getAttr(f'{self.prelim_ctrl}.{attr}'), type='string')





    ####################################################################################################################
    def finalize_anim_ctrl(self, delete_existing_shapes=False):

        self.transfer_locks_from_prelim()
        self.copy_shape_from_prelim(delete_existing_shapes=delete_existing_shapes)





    ####################################################################################################################
    def assign_new_shape(self, new_shape, remove_existing_shape=True):

        gen_utils.copy_shapes(new_shape, self.ctrl_transform, keep_original=False,
                              delete_existing_shapes=remove_existing_shape)