# Title: class_Placer.py
# Author: Sam Leheny
# Contact: samleheny@live.com

# Description:


###########################
##### Import Commands #####
import importlib
import pymel.core as pm

import Snowman3.utilities.general_utils as gen_utils
import Snowman3.utilities.rig_utils as rig_utils
import Snowman3.utilities.node_utils as node_utils
importlib.reload(gen_utils)
importlib.reload(rig_utils)
importlib.reload(node_utils)

import Snowman3.dictionaries.nameConventions as nameConventions
importlib.reload(nameConventions)
nom = nameConventions.create_dict()

import Snowman3.riggers.utilities.classes.class_VectorHandle as classVectorHandle
import Snowman3.riggers.utilities.classes.class_Orienter as classOrienter
importlib.reload(classVectorHandle)
importlib.reload(classOrienter)
VectorHandle = classVectorHandle.VectorHandle
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
        name,
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
    set_position
    get_opposite_placer
    setup_live_symmetry
    create_connector_curve
    make_benign
    create_orienter
    aim_orienter
    placer_metadata
    --------------------------------------------------------------------------------------------------------------------
    --------------------------------------------------------------------------------------------------------------------
    """




    ####################################################################################################################
    def create_placer_in_scene(self):
        """
        - Creates the placer mobject in the scene.
            - Assigns metadata to placer in hidden attributes.
            - Installs vector handles.
            - Installs orienter.
            - Wraps placer in offset group.
            - Positions placer.
        Returns:
            (mObj): Placer.
        """

        #...Create placer
        self.create_mobject()
        #...Metadata
        self.placer_metadata()
        #...Vector handles. Aim Handle and Up Handle
        self.create_vector_handles() if self.vector_handle_data else None
        #...Buffer group
        self.buffer_node = gen_utils.buffer_obj(self.mobject)
        #...Position placer
        self.set_position() if self.position else None
        #...Orienter
        self.create_orienter()

        return self.mobject





    ####################################################################################################################
    def create_mobject(self):
        """
        Creates placer MObject in scene based on class properties.
        """

        #...Compose placer name
        placer_name = "{0}{1}_{2}".format(self.side_tag, self.name, nom.placer)
        #...Create placer MObject
        self.mobject = gen_utils.prefab_curve_construct(prefab=self.shape_type, name=placer_name, color=self.color,
                                                        scale=self.size, side=self.side)
        #...Parent placer
        self.mobject.setParent(self.parent) if self.parent else None





    ####################################################################################################################
    def create_vector_handles(self):

        #...A group to house vector handles
        self.vector_handle_grp = pm.group(name="vectorHandlesVis", em=1, p=self.mobject)
        #...Create handles for Aim vector and Up vector
        self.aim_vector_handle = VectorHandle(name="{}{}".format(self.side_tag, self.name), vector="aim",
                                              side=self.side, parent=self.vector_handle_grp, color=self.color,
                                              placer=self)
        self.up_vector_handle = VectorHandle(name="{}{}".format(self.side_tag, self.name), vector="up",
                                             side=self.side, parent=self.vector_handle_grp, color=self.color,
                                             placer=self)





    ####################################################################################################################
    def dull_color(self, hide=False):

        for shape in self.mobject.getShapes():
            shape.overrideEnabled.set(1)
            shape.overrideDisplayType.set(1)
            if hide:
                shape.visibility.set(0)





    ####################################################################################################################
    def set_position(self):

        #...Position placer
        self.mobject.translate.set(self.position)





    ####################################################################################################################
    def get_opposite_placer(self):

        if self.side not in (nom.leftSideTag, nom.rightSideTag):
            return

        #...Find and get opposite placer
        opposite_placer = gen_utils.get_opposite_side_obj(self.mobject)
        if not opposite_placer:
            print("Unable to find opposite placer for placer: '{0}'".format(self.mobject))
            return None

        return opposite_placer





    ####################################################################################################################
    def setup_live_symmetry(self, reverse=False):

        #...Get opposite placer
        opposite_placer = self.get_opposite_placer()
        if not opposite_placer:
            print("No opposite placer found. Cannot setup live symmetry for placer '{0}'".format(self.mobject))
            return None

        # Determine - based on reverse_relationship arg - if THIS placer leads, or follows
        leader, follower = opposite_placer, self.mobject
        if reverse:
            leader, follower = self.mobject, opposite_placer

        gen_utils.drive_attr(leader, follower, ("tx", "ty", "tz", "rx", "ry", "rz"))
        self.dull_color(follower)





    ####################################################################################################################
    def create_connector_curve(self, target, parent=None):

        par = parent if parent else self.mobject

        self.connector_curve = rig_utils.connector_curve(name="{}{}".format(self.side_tag, self.name),
                                                         line_width=1.5, end_driver_1=self.mobject,
                                                         end_driver_2=target.mobject, override_display_type=2,
                                                         parent=par, inheritsTransform=False,
                                                         use_locators=False)[0]

        source_attr_name = "SourcePlacer"
        pm.addAttr(self.connector_curve, longName=source_attr_name, dataType="string", keyable=0)
        pm.connectAttr(self.mobject + "." + "Connectors", self.connector_curve + "." + source_attr_name, lock=1)

        dest_attr_name = "DestinationPlacer"
        pm.addAttr(self.connector_curve, longName=dest_attr_name, dataType="string", keyable=0)
        pm.connectAttr(target.mobject + "." + "ReceivedConnectors", self.connector_curve + "." + dest_attr_name, lock=1)

        self.connector_curve.selectionChildHighlighting.set(0, lock=1)





    ####################################################################################################################
    def make_benign(self, hide=True):

        if hide:
            #...Hide placer shape
            for shape in self.mobject.getShapes():
                shape.visibility.set(0, lock=1) if not shape.visibility.get(lock=1) else None

        #...Lock attributes
        [pm.setAttr(self.mobject + "." + attr, lock=1, keyable=0) for attr in gen_utils.keyable_attrs]

        #...Dull placer color
        self.dull_color()

        handles = []
        if self.up_vector_handle:
            handles.append(self.up_vector_handle)
        if self.aim_vector_handle:
            handles.append(self.aim_vector_handle)

        for handle in handles:
            for shape in handle.mobject.getShapes():
                shape.overrideEnabled.set(1)
                shape.overrideDisplayType.set(1)
                shape.visibility.set(0)
            handle.connector_crv.getShape().visibility.set(0)





    ####################################################################################################################
    def fill_out_orienter_data(self):

        if self.orienter_data:
            for key in ("world_up_type", "aim_vector", "up_vector", "match_to"):
                if key not in self.orienter_data:
                    self.orienter_data[key] = None
        else:
            self.orienter_data = {"world_up_type": None, "aim_vector": None, "up_vector": None, "match_to": None}





    ####################################################################################################################
    def create_orienter(self):

        self.fill_out_orienter_data()

        self.orienter = Orienter(name=self.name,
                                 side=self.side,
                                 size=self.size,
                                 parent=self.mobject,
                                 aim_vector=self.orienter_data["aim_vector"],
                                 up_vector=self.orienter_data["up_vector"],
                                 match_to=self.orienter_data["match_to"],
                                 placer=self)

        #...Connect orienter to placer via message attr
        orienter_attr_name = "OrienterNode"
        pm.addAttr(self.mobject, longName=orienter_attr_name, dataType="string", keyable=0)
        self.orienter.mobject.message.connect(self.mobject + "." + orienter_attr_name)

        #...Drive orienter's visibility from placer attribute
        pm.addAttr(self.mobject, longName=attr_strings["orienter_vis"], attributeType="bool", keyable=0, defaultValue=0)
        pm.setAttr(self.mobject + '.' + attr_strings["orienter_vis"], channelBox=1)
        pm.connectAttr(self.mobject + "." + attr_strings["orienter_vis"], self.orienter.mobject.visibility)





    ####################################################################################################################
    def aim_orienter(self):

        if not self.vector_handle_data:
            return

        # Constrain placer's up vector and aim vector handles
        for vector_string, vector_handle in (("aim", self.aim_vector_handle),
                                             ("up", self.up_vector_handle)):

            handle_data = self.vector_handle_data[vector_string]

            if "obj" not in handle_data:
                vector_handle.mobject.translate.set(handle_data["coord"])
                continue

            target_obj = None
            get_placer_string = f'::{self.side_tag}{handle_data["obj"]}_{nom.placer}'
            if pm.ls(get_placer_string):
                target_obj = pm.ls(get_placer_string)[0]
            else:
                print(f'Unable to find placer: "{get_placer_string}"')

            offset = gen_utils.buffer_obj(vector_handle.mobject, suffix="MOD")
            pm.pointConstraint(target_obj, offset)

        self.orienter.aim_orienter()





    ####################################################################################################################
    def placer_metadata(self):

        obj = self.mobject

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

