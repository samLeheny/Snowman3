# Title: class_VectorHandle.py
# Author: Sam Leheny
# Contact: samleheny@live.com

# Description:


###########################
##### Import Commands #####
import importlib
import pymel.core as pm

import Snowman3.utilities.general_utils as gen_utils
import Snowman3.utilities.rig_utils as rig_utils
importlib.reload(gen_utils)
importlib.reload(rig_utils)

import Snowman3.dictionaries.nameConventions as nameConventions
importlib.reload(nameConventions)
nom = nameConventions.create_dict()

import Snowman3.riggers.dictionaries.control_colors as ctrl_colors_dict
importlib.reload(ctrl_colors_dict)
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
        name: str,
        vector = None,
        position = None,
        size = None,
        side = None,
        color = None,
        parent = None,
        placer = None
    ):
        self.name = name
        self.handle_name = None
        self.vector = vector if vector else 'aim'
        self.position = position if position else (0, 0, 0)
        self.size = size if size else 0.25
        self.side = side
        self.side_tag = f'{self.side}_' if self.side else ''
        self.color = color if color else ctrl_colors[self.side] if self.side else ctrl_colors[nom.midSideTag]
        self.parent = parent
        self.connector_crv = None
        self.placer = placer
        self.mobject = None

        self.create_in_scene()





    ####################################################################################################################
    def create_in_scene(self):
        self.create_mobject()
        self.mobject.setParent(self.parent) if self.parent else None
        self.set_position()
        self.create_connector_curve()
        self.connect_to_placer_metadata()
        self.drive_handle_visibility()





    ####################################################################################################################
    def create_mobject(self):

        vector_type, handle_shape = 'AIM', 'cube'

        if self.vector == 'aim':
            vector_type, handle_shape = 'AIM', 'cube'
        elif self.vector == 'up':
            vector_type, handle_shape = 'UP', 'sphere'

        self.handle_name = f'{self.name}_{vector_type}'

        #...Create handle
        self.mobject = gen_utils.prefab_curve_construct(prefab=handle_shape, name=self.handle_name, side=self.side,
                                                        scale=self.size, color=self.color)





    ####################################################################################################################
    def drive_handle_visibility(self):
        if not pm.attributeQuery('VectorHandlesVis', node=self.placer.mobject, exists=1):
            pm.addAttr(self.placer.mobject, longName='VectorHandlesVis', attributeType="bool", defaultValue=0)
            pm.setAttr(f'{self.placer.mobject}.VectorHandlesVis', channelBox=1)
        for obj in (self.mobject, self.connector_crv):
            pm.connectAttr(f'{self.placer.mobject}.VectorHandlesVis', obj.visibility)





    ####################################################################################################################
    def create_connector_curve(self):
        self.connector_crv = rig_utils.connector_curve(name=f'{self.side_tag}{self.name}_{self.vector}',
                                                       end_driver_1=self.parent, end_driver_2=self.mobject,
                                                       parent=self.mobject, override_display_type=1,
                                                       inheritsTransform=False, use_locators=False)[0]





    ####################################################################################################################
    def set_position(self, convert_offset=False):

        dist_mult = 2
        init_placement_vector = (0, 0, 0)

        if self.vector == 'aim':
            init_placement_vector = (1*dist_mult, 0, 0)
        elif self.vector == 'up':
            init_placement_vector = (0, 1*dist_mult, 0)

        self.mobject.translate.set(init_placement_vector)

        #...Keep transforms clean by moving translate values into offsetParentMatrix (optional)
        if convert_offset:
            gen_utils.convert_offset(self.mobject)





    ####################################################################################################################
    def connect_to_placer_metadata(self):
        obj = self.placer.mobject
        attr_name = {'aim': 'AimVectorNode', 'up': 'UpVectorNode'}
        pm.addAttr(obj, longName=attr_name[self.vector], dataType='string', keyable=0)
        self.mobject.message.connect(f'{obj}.{attr_name[self.vector]}')





    ####################################################################################################################
    def place_handle(self, coordinate):
        self.mobject.translate.set(coordinate)





    ####################################################################################################################
    def constrain_handle(self, placer_tag):
        # ...Find constraint target placer
        target_obj = None
        get_placer_string = f'::{self.side_tag}{placer_tag}_{nom.placer}'
        if pm.ls(get_placer_string):
            target_obj = pm.ls(get_placer_string)[0]
        else:
            print(f"Unable to find placer: '{get_placer_string}'")
        pm.pointConstraint(target_obj, self.mobject)
