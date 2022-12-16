# Title: class_Orienter.py
# Author: Sam Leheny
# Contact: samleheny@live.com

# Description:


###########################
##### Import Commands #####
import pymel.core as pm

import Snowman.utilities.general_utils as gen_utils
reload(gen_utils)

import Snowman.utilities.rig_utils as rig_utils
reload(rig_utils)

import Snowman.dictionaries.nameConventions as nameConventions
reload(nameConventions)
nom = nameConventions.create_dict()
###########################
###########################


###########################
######## Variables ########
orientation_offset = (90, 0, 90)
###########################
###########################





########################################################################################################################
class Orienter:
    def __init__(
        self,
        name,
        side = None,
        size = None,
        parent = None,
        aim_target = None,
        up_target = None,
        aim_vector = (1, 0, 0),
        up_vector = (0, 1, 0),
        match_to = None,
        world_up_type = None,
        world_up_vector = None,
        placer = None,
    ):
        self.name = name
        self.side = side if side else None
        self.size = size if size else 1.0
        self.parent = parent if parent else None
        self.aim_vector = aim_vector
        self.up_vector = up_vector
        self.match_to = match_to if match_to else None
        self.placer = placer

        self.mobject = None
        self.buffer = None
        self.create()
        self.side_tag = "{}_".format(side) if self.side else ""




    '''
    create
    dull_color
    get_opposite_orienter
    match_to_obj
    aim_orient
    '''


    ####################################################################################################################
    def create(self):

        self.mobject = rig_utils.orienter(name=self.name, side=self.side, scale=self.size)

        self.buffer = gen_utils.buffer_obj(self.mobject)
        #self.mobject.rotate.set(orientation_offset)
        gen_utils.convert_offset(self.mobject)

        self.buffer.setParent(self.parent) if self.parent else None
        gen_utils.zero_out(self.buffer)


        return self.mobject





    ####################################################################################################################
    def dull_color(self, orienter=None, gray_out=True, hide=False):

        # ...If no specific orienter provided, default to using THIS orienter
        if not orienter:
            orienter = self.mobject

        for shape in orienter.getShapes():
            shape.overrideEnabled.set(1)
            shape.overrideDisplayType.set(1)
            if hide:
                shape.visibility.set(0)





    ####################################################################################################################
    def get_opposite_orienter(self):

        # ...Check that orienter is sided
        if not self.side:
            print "Orienter '{0}' has not assigned side, and therefore, has no opposite orienter".format(self.mobject)
            return None

        # ...Check that orienter's side is valid (left or right)
        if not self.side in (nom.leftSideTag, nom.rightSideTag):
            print "Side for orienter '{0}': {1}." \
                  "Can only find opposite orienters if assigned side is '{2}' or '{3}'".format(self.mobject,
                                                                                             self.side,
                                                                                             nom.leftSideTag,
                                                                                             nom.rightSideTag)

        # ...Find and get opposite orienter
        opposite_orienter = None
        opposite_orienter = gen_utils.get_opposite_side_obj(self.mobject)

        if not opposite_orienter:
            print "Unable to find opposite orienter for placer: '{0}'".format(self.mobject)
            return None

        return opposite_orienter





    ####################################################################################################################
    def match_to_obj(self, obj=None):

        if not obj:
            obj = self.match_to

        driver_orienter = None
        get_orienter_string = "::{}{}_{}".format(self.side_tag, obj, nom.orienter)
        if pm.ls(get_orienter_string):
            driver_orienter = pm.ls(get_orienter_string)[0]


        # ...Match orienter
        pm.orientConstraint(driver_orienter, self.mobject)





    ####################################################################################################################
    def aim_orienter(self):


        if self.match_to:
            self.match_to_obj()


        else:

            if self.placer.up_vector_handle:
                aim_target_obj = self.placer.aim_vector_handle.mobject
                up_target_obj = self.placer.up_vector_handle.mobject

                pm.aimConstraint(aim_target_obj, self.mobject, aimVector=self.aim_vector, upVector=self.up_vector,
                                 worldUpType="object", worldUpObject=up_target_obj)
