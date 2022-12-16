# Title: class_PrelimControl.py
# Author: Sam Leheny
# Contact: samleheny@live.com

# Description:


###########################
##### Import Commands #####
import pymel.core as pm

import Snowman.dictionaries.nameConventions as nameConventions
reload(nameConventions)
nom = nameConventions.create_dict()

import Snowman.utilities.general_utils as gen_utils
reload(gen_utils)
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

        self.side_tag = "{}_".format(self.side) if self.side else ""
        self.prelim_ctrl = None
        self.ctrl_transform = None
        self.module_ctrl_obj = module_ctrl if module_ctrl else None





    ####################################################################################################################
    def get_prelim_ctrl(self):

        search_string = "{}{}_{}".format(self.side_tag, self.prelim_ctrl_name, nom.nonAnimCtrl)

        search = pm.ls("::" + search_string)
        if search:
            if len(search) == 1:
                self.prelim_ctrl = search[0]

        if not self.prelim_ctrl:
            print "Unable to find prelim control corresponding to: '{}'".format(self.ctrl_name_tag)

        return self.prelim_ctrl





    ####################################################################################################################
    def initialize_anim_ctrl(self, existing_obj=None, parent=None):

        ctrl = None
        if not self.prelim_ctrl:
            self.prelim_ctrl = self.get_prelim_ctrl()


        if existing_obj:
            ctrl = existing_obj
            ctrl.rename("{}{}_{}".format(self.side_tag, self.ctrl_name_tag, nom.animCtrl))


        if not existing_obj:

            temp_loc = None

            # Create an empty transform node to serve as control (it will get a shape later)
            ctrl = pm.shadingNode("transform", name="{}{}_{}".format(self.side_tag, self.ctrl_name_tag, nom.animCtrl),
                                  au=1)

            ctrl.setParent(parent) if parent else None

            if self.match_transform:

                if self.match_transform == "module_ctrl":
                    match_transform_obj = self.module_ctrl_obj

                elif self.match_transform == "center to prelim":

                    center_coord = gen_utils.get_shape_center(self.prelim_ctrl)

                    temp_loc = pm.spaceLocator()
                    temp_loc.setParent(self.prelim_ctrl)
                    gen_utils.zero_out(temp_loc)
                    temp_loc.setParent(world=1)
                    temp_loc.translate.set(center_coord)
                    temp_loc.setParent(ctrl.getParent())

                    match_transform_obj = temp_loc

                else:
                    ori = pm.ls("::{}{}_{}".format(self.side_tag, self.match_transform, nom.orienter))[0]
                    temp_loc = pm.spaceLocator()
                    temp_loc.setParent(ori)
                    gen_utils.zero_out(temp_loc)
                    temp_loc.setParent(world=1)
                    temp_loc.setParent(ctrl.getParent())

                    match_transform_obj = temp_loc

            else:
                # ...Get corresponding prelim control in scene
                match_transform_obj = self.prelim_ctrl if self.prelim_ctrl else None



            pm.matchTransform(ctrl, match_transform_obj)


            pm.delete(temp_loc) if temp_loc else None



        self.ctrl_transform = ctrl
        return ctrl





    ####################################################################################################################
    def copy_shape_from_prelim(self, delete_existing_shapes=False, keep_original=True):

        # ...Get corresponding prelim control in scene
        self.get_prelim_ctrl() if not self.prelim_ctrl else None

        for attr in gen_utils.all_transform_attrs:
            gen_utils.break_connections(self.prelim_ctrl+"."+attr)

        # ...Copy shape across
        gen_utils.copy_shapes(self.prelim_ctrl, self.ctrl_transform, parent_offset_matrix_mode=False,
                              delete_existing_shapes=delete_existing_shapes, keep_original=keep_original)





    ####################################################################################################################
    def transfer_locks_from_prelim(self):

        # ...Get corresponding prelim control in scene
        self.get_prelim_ctrl() if not self.prelim_ctrl else None

        # ...Transfer lock information from prelim control to final control
        for attr in ("lock_info_translate", "lock_info_rotate", "lock_info_scale", "lock_info_visibility"):

            if pm.attributeQuery(attr, node=self.prelim_ctrl, exists=1):

                pm.addAttr(self.ctrl_transform, longName=attr, keyable=0, dataType="string")

                pm.setAttr('{}.{}'.format(self.ctrl_transform, attr),
                           pm.getAttr('{}.{}'.format(self.prelim_ctrl, attr)), type="string")





    ####################################################################################################################
    def finalize_anim_ctrl(self, delete_existing_shapes=False):

        self.transfer_locks_from_prelim()
        self.copy_shape_from_prelim(delete_existing_shapes=delete_existing_shapes)