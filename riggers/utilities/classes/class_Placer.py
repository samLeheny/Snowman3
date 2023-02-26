# Title: class_Placer.py
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

import Snowman3.utilities.node_utils as node_utils
importlib.reload(node_utils)

import Snowman3.dictionaries.nameConventions as nameConventions
importlib.reload(nameConventions)
nom = nameConventions.create_dict()

import Snowman3.riggers.utilities.classes.class_VectorHandle as classVectorHandle
importlib.reload(classVectorHandle)
VectorHandle = classVectorHandle.VectorHandle

import Snowman3.riggers.utilities.classes.class_Orienter as classOrienter
importlib.reload(classOrienter)
Orienter = classOrienter.Orienter

import Snowman3.riggers.dictionaries.control_colors as ctrl_colors_dict
importlib.reload(ctrl_colors_dict)
ctrl_colors = ctrl_colors_dict.create_dict()
###########################
###########################


###########################
######## Variables ########
attr_strings = {"vector_handles_vis": "VectorHandlesVis",
                "orienter_vis": "OrienterVis"}
default_placer_shape_type = "sphere_placer"
###########################
###########################





########################################################################################################################
class Placer:
    def __init__(
        self,
        name: str,
        position = None,
        size = None,
        shape_type = None,
        side = None,
        color = None,
        parent = None,
        vector_handle_data = None,
        orienter_data = None,
        connect_targets = None,
    ):
        self.name = name
        self.position = position if position else (0, 0, 0)
        self.size = size if size else 1.0
        self.shape_type = shape_type if shape_type else default_placer_shape_type
        self.side = side
        self.side_tag = f'{self.side}_' if self.side else ''
        self.color = color if color else ctrl_colors[self.side] if self.side else ctrl_colors[nom.midSideTag]
        self.parent = parent
        self.up_vector_handle = None
        self.aim_vector_handle = None
        self.vector_handle_grp = None
        self.vector_handle_data = vector_handle_data
        self.connector_curve = None
        self.buffer_node = None
        self.orienter_data = orienter_data
        self.orienter = None
        self.connect_targets = connect_targets
        self.mobject = None





    """
    --------- METHODS --------------------------------------------------------------------------------------------------
    --------------------------------------------------------------------------------------------------------------------
    create_placer_in_scene
    create_mobject
    create_vector_handles
    dull_color
    position_placer
    create_connector_curve
    create_orienter
    position_vector_handles
    aim_orienter
    input_placer_metadata
    --------------------------------------------------------------------------------------------------------------------
    --------------------------------------------------------------------------------------------------------------------
    """




    ####################################################################################################################
    def create_placer_in_scene(self):
        self.create_mobject()
        self.input_placer_metadata()
        self.create_vector_handles() if self.vector_handle_data else None
        self.buffer_node = gen_utils.buffer_obj(self.mobject)
        self.position_placer() if self.position else None
        self.create_orienter()





    ####################################################################################################################
    def create_mobject(self):
        placer_name = f'{self.side_tag}{self.name}_{nom.placer}'
        self.mobject = gen_utils.prefab_curve_construct(
            prefab=self.shape_type, name=placer_name, color=self.color, scale=self.size, side=self.side)
        self.mobject.setParent(self.parent) if self.parent else None





    ####################################################################################################################
    def create_vector_handles(self):
        self.vector_handle_grp = pm.group(name='vectorHandlesVis', em=1, p=self.mobject)
        self.aim_vector_handle = VectorHandle(name=f'{self.side_tag}{self.name}', vector='aim', side=self.side,
                                              parent=self.vector_handle_grp, color=self.color, placer=self)
        self.up_vector_handle = VectorHandle(name=f'{self.side_tag}{self.name}', vector='up', side=self.side,
                                             parent=self.vector_handle_grp, color=self.color, placer=self)





    ####################################################################################################################
    def dull_color(self, hide=False):
        for shape in self.mobject.getShapes():
            shape.overrideEnabled.set(1)
            shape.overrideDisplayType.set(1)
            shape.visibility.set(0) if hide else None





    ####################################################################################################################
    def position_placer(self):
        self.mobject.translate.set(self.position)






    ####################################################################################################################
    def create_connector_curve(self, target, parent=None):

        parent = parent if parent else self.mobject

        self.connector_curve = rig_utils.connector_curve(name=f'{self.side_tag}{self.name}',
                                                         line_width=1.5, end_driver_1=self.mobject,
                                                         end_driver_2=target.mobject, override_display_type=2,
                                                         parent=parent, inheritsTransform=False,
                                                         use_locators=False)[0]

        source_attr_name = 'SourcePlacer'
        pm.addAttr(self.connector_curve, longName=source_attr_name, dataType='string', keyable=0)
        pm.connectAttr(f'{self.mobject}.Connectors', f'{self.connector_curve}.{source_attr_name}', lock=1)

        dest_attr_name = 'DestinationPlacer'
        pm.addAttr(self.connector_curve, longName=dest_attr_name, dataType='string', keyable=0)
        pm.connectAttr(f'{target.mobject}.ReceivedConnectors', f'{self.connector_curve}.{dest_attr_name}', lock=1)





    ####################################################################################################################
    def fill_out_orienter_data(self):

        if not self.orienter_data:
            self.orienter_data = {'world_up_type': None, 'aim_vector': None, 'up_vector': None, 'match_to': None}

        else:
            for key in ('world_up_type', 'aim_vector', 'up_vector', 'match_to'):
                if key not in self.orienter_data:
                    self.orienter_data[key] = None





    ####################################################################################################################
    def create_orienter(self):

        self.fill_out_orienter_data()

        self.orienter = Orienter(name=self.name,
                                 side=self.side,
                                 size=self.size,
                                 parent=self.mobject,
                                 aim_vector=self.orienter_data['aim_vector'],
                                 up_vector=self.orienter_data['up_vector'],
                                 match_to=self.orienter_data['match_to'],
                                 placer=self)

        #...Connect orienter to placer via message attr
        orienter_attr_name = 'OrienterNode'
        pm.addAttr(self.mobject, longName=orienter_attr_name, dataType='string', keyable=0)
        self.orienter.mobject.message.connect(f'{self.mobject}.{orienter_attr_name}')

        #...Drive orienter's visibility from placer attribute
        pm.addAttr(self.mobject, longName=attr_strings['orienter_vis'], attributeType='bool', keyable=0, defaultValue=0)
        pm.setAttr(f'{self.mobject}.{attr_strings["orienter_vis"]}', channelBox=1)
        pm.connectAttr(f'{self.mobject}.{attr_strings["orienter_vis"]}', self.orienter.mobject.visibility)





    ####################################################################################################################
    def position_vector_handles(self):

        for vector_string, vector_handle in (('aim', self.aim_vector_handle),
                                             ('up', self.up_vector_handle)):

            handle_data = self.vector_handle_data[vector_string]

            if 'obj' in handle_data:
                vector_handle.constrain_handle(handle_data['obj'])
            else:
                vector_handle.place_handle(handle_data['coord'])





    ####################################################################################################################
    def aim_orienter(self):
        if not self.vector_handle_data:
            return
        self.position_vector_handles()
        self.orienter.aim_orienter()





    ####################################################################################################################
    def get_data_dictionary(self):
        data_dict = {'name': self.name,
                     'position': self.position,
                     'size': self.size,
                     'shape_type': self.shape_type,
                     'side': self.side,
                     'color': self.color,
                     'parent': self.parent,
                     'vector_handle_data': self.vector_handle_data,
                     'orienter_data': self.orienter_data,
                     'connect_targets': self.connect_targets}
        return data_dict





    ####################################################################################################################
    def input_placer_metadata(self):

        #...Placer tag
        self.metadata_PlacerTag()
        #...Side
        self.metadata_Side()
        #...Size
        self.metadata_Size()
        #...Vector handle data
        self.metadata_VectorHandleData()
        #...Orienter data
        self.metadata_OrienterData()
        #...Connect targets
        self.metadata_ConnectorTargets()

        pm.addAttr(self.mobject, longName="ReceivedConnectors", dataType="string", keyable=0)



    ####################################################################################################################
    def metadata_PlacerTag(self):

        gen_utils.add_attr(self.mobject, long_name="PlacerTag", attribute_type="string", keyable=0,
                           default_value=self.name)

    ####################################################################################################################
    def metadata_Side(self):

        attr_input = self.side if self.side else "None"
        gen_utils.add_attr(self.mobject, long_name="Side", attribute_type="string", keyable=0, default_value=attr_input)

    ####################################################################################################################
    def metadata_Size(self):
        gen_utils.add_attr(self.mobject, long_name="Size", attribute_type="float", keyable=0,
                           default_value=float(self.size))

    ####################################################################################################################
    def metadata_VectorHandleData(self):

        gen_utils.add_attr(self.mobject, long_name="VectorHandleData", attribute_type="string", keyable=0,
                           default_value=str(self.vector_handle_data))

    ####################################################################################################################
    def metadata_OrienterData(self):

        gen_utils.add_attr(self.mobject, long_name="OrienterData", attribute_type="string", keyable=0,
                           default_value=str(self.orienter_data))

    ####################################################################################################################
    def metadata_ConnectorTargets(self):

        gen_utils.add_attr(self.mobject, long_name="ConnectorData", attribute_type="string", keyable=0,
                           default_value=str(self.connect_targets))
