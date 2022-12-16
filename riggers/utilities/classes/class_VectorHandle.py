# Title: class_VectorHandle.py
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

import Snowman.riggers.dictionaries.control_colors as ctrl_colors_dict
reload(ctrl_colors_dict)
ctrl_colors = ctrl_colors_dict.create_dict()
###########################
###########################


###########################
######## Variables ########

###########################
###########################





########################################################################################################################
class VectorHandle:
    def __init__(
        self,
        name,
        vector = "aim",
        position = None,
        size = None,
        side = None,
        color = None,
        parent = None,
        placer = None
    ):
        self.name = name
        self.handle_name = None
        self.vector = vector
        self.position = position if position else (0, 0, 0)
        self.size = size if size else 0.25
        self.side = side if side else None
        self.side_tag = "{}_".format(self.side) if self.side else ""
        self.color = color if color else ctrl_colors[self.side] if self.side else ctrl_colors[nom.midSideTag]
        self.parent = parent if parent else None
        self.connector_crv = None
        self.placer = placer

        self.mobject = None

        self.create()





    ####################################################################################################################
    def create(self):


        vector_type, handle_shape = "AIM", "cube"
        if self.vector == "aim":
            vector_type, handle_shape = "AIM", "cube"
        elif self.vector == "up":
            vector_type, handle_shape = "UP", "sphere"

        self.handle_name = "{}_{}".format(self.name, vector_type)

        # ...Create handle
        self.mobject = gen_utils.prefab_curve_construct(prefab=handle_shape, name=self.handle_name, side=self.side,
                                                        scale=self.size, color=self.color)

        # ...
        self.mobject.setParent(self.parent) if self.parent else None


        # ...Position handle
        self.set_position()

        # ...
        self.create_connector_curve()

        # ...
        self.connect_to_placer_metadata()

        # ...Drive vector handles visibility from placer attribute
        if not pm.attributeQuery("VectorHandlesVis", node=self.placer.mobject, exists=1):
            pm.addAttr(self.placer.mobject, longName="VectorHandlesVis", attributeType="bool", defaultValue=0)
            pm.setAttr(self.placer.mobject + '.' + "VectorHandlesVis", channelBox=1)
        for obj in (self.mobject, self.connector_crv):
            pm.connectAttr(self.placer.mobject + "." + "VectorHandlesVis", obj.visibility)


        return self.mobject





    ####################################################################################################################
    def create_connector_curve(self):

        self.connector_crv = rig_utils.connector_curve(name="{}{}_{}".format(self.side_tag, self.name, self.vector),
                                                       end_driver_1=self.parent, end_driver_2=self.mobject,
                                                       parent=self.mobject, override_display_type=1,
                                                       inheritsTransform=False, use_locators=False)[0]





    ####################################################################################################################
    def dull_color(self, handle=None, gray_out=True, hide=False):

        # ...If no specific handle provided, default to using THIS placer
        if not handle:
            handle = self.mobject

        for shape in handle.getShapes():
            shape.overrideEnabled.set(1)
            shape.overrideDisplayType.set(1)
            if hide:
                shape.visibility.set(0)





    ####################################################################################################################
    def set_position(self, convert_offset=False):


        dist_mult = 2

        init_placement_vector = (0, 0, 0)

        if self.vector == "aim":
            init_placement_vector = (1*dist_mult, 0, 0)
        elif self.vector == "up":
            init_placement_vector = (0, 1*dist_mult, 0)


        self.mobject.translate.set(init_placement_vector)


        # ...Keep transforms clean by moving translate values into offsetParentMatrix (optional)
        if convert_offset:
            gen_utils.convert_offset(self.mobject)





    ####################################################################################################################
    def connect_to_placer_metadata(self):

        obj = self.placer.mobject
        attr_name = {"aim": "AimVectorNode", "up": "UpVectorNode"}

        pm.addAttr(obj, longName=attr_name[self.vector], dataType="string", keyable=0)
        self.mobject.message.connect(obj + "." + attr_name[self.vector])