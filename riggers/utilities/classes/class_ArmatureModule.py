# Title: class_ArmatureModule.py
# Author: Sam Leheny
# Contact: samleheny@live.com

# Description:


###########################
##### Import Commands #####
import importlib
import ast
import numpy as np
import pymel.core as pm

import Snowman3.utilities.general_utils as gen_utils
importlib.reload(gen_utils)

import Snowman3.utilities.node_utils as node_utils
importlib.reload(node_utils)

import Snowman3.utilities.rig_utils as rig_utils
importlib.reload(rig_utils)

import Snowman3.dictionaries.nameConventions as nameConventions
importlib.reload(nameConventions)
nom = nameConventions.create_dict()

import Snowman3.riggers.dictionaries.control_colors as control_colors
importlib.reload(control_colors)
ctrl_colors = control_colors.create_dict()

import Snowman3.riggers.utilities.classes.class_Placer as classPlacer
import Snowman3.riggers.utilities.classes.class_PoleVectorPlacer as classPoleVectorPlacer
importlib.reload(classPlacer)
importlib.reload(classPoleVectorPlacer)
Placer = classPlacer.Placer
PoleVectorPlacer = classPoleVectorPlacer.PoleVectorPlacer

import Snowman3.riggers.utilities.classes.class_ArmatureModuleHandle as class_ArmatureModuleHandle
importlib.reload(class_ArmatureModuleHandle)
ArmatureModuleHandle = class_ArmatureModuleHandle.ArmatureModuleHandle

import Snowman3.riggers.utilities.directories.get_module_data as get_module_data
importlib.reload(get_module_data)
###########################
###########################


###########################
######## Variables ########
vis_switch_enum_strings = {
    "placers" : "PlacersVis",
    "controls" : "ControlsVis"
}
placers_attr_string = "PlacerNodes"
###########################
###########################





########################################################################################################################
class ArmatureModule:
    def __init__(
        self,
        name = None,
        placer_data = None,
        prelim_ctrls = None,
        side = None,
        symmetry = None,
        is_driven_side = None,
        color = None,
        rig_module_type = None,
        position = None,
        rotation = None,
        scale = None,
        drive_target = None,
        draw_connections = None
    ):
        self.name = gen_utils.get_clean_name(name)
        self.side = side
        self.side_tag = f'{self.side}_' if self.side else ""
        self.name_tag = f'{self.side_tag}{self.name}'
        self.symmetry = symmetry
        self.is_driven_side = is_driven_side
        self.ordered_placer_keys = []
        self.rig_module_type = rig_module_type if rig_module_type else "-"
        self.position = position if position else (0, 0, 0)
        self.rotation = rotation if rotation else (0, 0, 0)
        self.scale = scale if scale else 1
        self.drive_target = drive_target
        self.draw_connections = draw_connections

        self.ctrls = {}
        self.placers = {}
        self.placer_data = placer_data if placer_data else get_module_data.placers(
            self.rig_module_type, side=side, is_driven_side=is_driven_side)
        self.prelim_ctrls = prelim_ctrls if prelim_ctrls else get_module_data.prelim_ctrls(
            self.rig_module_type, side=side, is_driven_side=is_driven_side)
        self.pv_placers = {}
        self.orienters = {}
        self.module_handles = {}
        self.objs_to_lock = []
        self.rig_root_grp = None
        self.rig_subGrps = None
        self.module_ctrl = None
        self.armature_container = None

        self.ctrl_color = color
        if not color:
            self.ctrl_color = ctrl_colors[self.side] if self.side else ctrl_colors[nom.midSideTag]




    """
    --------- METHODS --------------------------------------------------------------------------------------------------
    --------------------------------------------------------------------------------------------------------------------
    create_module_grps
    assign_module_metadata
    create_module_placers
    aim_module_orienters
    create_connector_curves
    create_module_ctrl_mobject
    aim_ctrl_at_placers
    flip_module
    position_module
    drive_module
    get_placer_from_tag
    make_obj_benign
    draw_module_connections
    connect_modules
    drive_module_handles_vis
    create_prelim_ctrls
    drive_vis_attrs_from_module_ctrl
    populate_module
    get_other_module
    get_scene_armature
    --------------------------------------------------------------------------------------------------------------------
    --------------------------------------------------------------------------------------------------------------------
    """




    ####################################################################################################################
    def create_module_grps(self):

        # ...
        self.rig_root_grp = pm.group(name=f'{self.side_tag}{self.name}_MODULE', w=1, em=1)

        self.rig_root_grp.setParent(self.armature_container)

        self.assign_module_metadata()

        # Sub groups
        self.rig_subGrps = {
            "placers": pm.group(name="placers", p=self.rig_root_grp, em=1),
            "prelim_ctrls": pm.group(name="prelimCtrls", p=self.rig_root_grp, em=1),
            "armature_ctrls": pm.group(name="armatureCtrls", p=self.rig_root_grp, em=1),
            "extra_systems": pm.group(name="extraSystems", p=self.rig_root_grp, em=1),
            "connector_curves": pm.group(name="connectorCrvs", p=self.rig_root_grp, em=1),
        }

        self.rig_subGrps["extra_systems"].visibility.set(0, lock=1)





    ####################################################################################################################
    def assign_module_metadata(self):

        target_obj = self.rig_root_grp

        # ...Rig Module Type............................................................................................
        pm.addAttr(target_obj, longName="ModuleType", keyable=0, dataType="string")
        pm.setAttr(f'{target_obj}.ModuleType', self.rig_module_type, type="string", lock=1)

        # ...Rig Module Name............................................................................................
        pm.addAttr(target_obj, longName="ModuleNameParticle", keyable=0, dataType="string")
        pm.setAttr(f'{target_obj}.ModuleNameParticle', self.name, type="string", lock=1)

        # ...Side.......................................................................................................
        pm.addAttr(target_obj, longName="Side", keyable=0, dataType="string")
        enter_value = self.side if self.side else None
        if enter_value:
            pm.setAttr(f'{target_obj}.Side', enter_value, type="string", lock=1)

        # ...Rig_Module_Tag.............................................................................................
        pm.addAttr(target_obj, longName="ModuleName", keyable=0, dataType="string")
        pm.setAttr(f'{target_obj}.ModuleName', self.name_tag, type="string", lock=1)

        # ...Is Driven Side.............................................................................................
        pm.addAttr(target_obj, longName="IsDrivenSide", keyable=0, attributeType="bool")
        enter_value = self.is_driven_side if self.is_driven_side else False
        pm.setAttr(f'{target_obj}.IsDrivenSide', enter_value, lock=1)
    
    
    
    
    
    ####################################################################################################################
    def create_module_ctrl_in_scene(self):

        # ...Create module placement control
        self.create_module_ctrl_mobject(name=self.name, side=self.side, parent=self.rig_root_grp)

        # ...Parent placers group to control
        mult_matrix = node_utils.multMatrix(matrixIn=(self.module_ctrl.mobject.worldMatrix,
                                                      self.rig_subGrps["placers"].parentInverseMatrix))

        node_utils.decomposeMatrix(inputMatrix=mult_matrix.matrixSum,
                                   outputTranslate=self.rig_subGrps["placers"].translate,
                                   outputRotate=self.rig_subGrps["placers"].rotate,
                                   outputScale=self.rig_subGrps["placers"].scale)





    ####################################################################################################################
    def create_placer(self, placer):

        self.placers[placer.name] = placer
        self.ordered_placer_keys.append(placer.name)

        placer.color = self.ctrl_color
        placer.parent = self.rig_subGrps["placers"]
        placer.create_placer_in_scene()

        # ...Lock and hide rotate, scale, and visibility. Placers only need translation
        attrs_to_lock = gen_utils.rotate_attrs + gen_utils.scale_attrs + gen_utils.vis_attrs
        [pm.setAttr(f'{placer.mobject}.{attr}', lock=1, keyable=0) for attr in attrs_to_lock]

        # ...Lock lateral placer translation if this is a center body module and symmetry is on
        placer.mobject.tx.set(lock=1, keyable=0) if self.symmetry else None

        # ...Add placer hook to module control
        pm.connectAttr(placer.mobject.message, f'{self.module_ctrl.mobject}.{placers_attr_string}.{placer.name}')

        pm.select(clear=1)

        # ...Drive placer scale with module root control attributes
        for attr in ("sx", "sy", "sz"):
            pm.setAttr(f'{placer.mobject}.{attr}', lock=0)
            pm.connectAttr(f'{self.module_ctrl.mobject}.PlacerScale', f'{placer.mobject}.{attr}')
            pm.setAttr(f'{placer.mobject}.{attr}', lock=1)





    ####################################################################################################################
    def create_module_placers(self):

        self.create_module_ctrl_in_scene()

        # ...Add placer hooks to module control
        pm.addAttr(self.module_ctrl.mobject, longName=placers_attr_string, attributeType="compound", keyable=0,
                   numberOfChildren=len(self.placer_data))
        for placer in self.placer_data:
            pm.addAttr(self.module_ctrl.mobject, longName=placer.name, keyable=0, dataType="string",
                       parent=placers_attr_string)

        for placer in self.placer_data:
            self.create_placer(placer)

        self.drive_vis_attrs_from_module_ctrl()





    ####################################################################################################################
    def aim_module_orienters(self):

        for key in self.ordered_placer_keys:
            placer = self.placers[key]
            orienter = placer.orienter

            if orienter:
                # ...Sort returned data
                self.orienters[key] = orienter
                # ...orienter.aim_orienter(orient_constrain_target=self.module_ctrl.mobject)
                placer.aim_orienter()





    ####################################################################################################################
    def create_connector_curves(self, parent=None):

        parent_obj = parent if parent else self.rig_subGrps["connector_curves"]

        for placer in self.placers.values():

            if placer.connect_targets:

                connectors_attr_name = "Connectors"
                pm.addAttr(placer.mobject, longName=connectors_attr_name, dataType="string", keyable=0)

                for target in placer.connect_targets:
                    placer.create_connector_curve(target=self.placers[target], parent=parent_obj)





    ####################################################################################################################
    def create_module_ctrl_mobject(self, name=None, shape="cube", locks=None, scale=None, side=None, parent=None,
                                   hide=False):


        if not locks: locks = {"v": 1}
        if not scale: scale = [1.2, 1.2, 1.2]

        # ...
        self.module_ctrl = self.module_handles["module_root"] = ArmatureModuleHandle(
            name = name,
            shape = shape,
            locks = locks,
            scale = scale,
            side = side,
            parent = parent,
            color = self.ctrl_color
        )
        self.module_ctrl.create()


        # ...Add Attributes. If module is part of a larger rig, the larger rig's setup root control will override these
        # ...attributes

        # ...Placer scale
        placer_scale_attr_string = "PlacerScale"

        pm.addAttr(self.module_ctrl.mobject, longName=placer_scale_attr_string, attributeType=float, minValue=0.001,
                   defaultValue=1, keyable=0)
        pm.setAttr(f'{self.module_ctrl.mobject}.{placer_scale_attr_string}', channelBox=1)

        # ...Module scale
        pm.addAttr(self.module_ctrl.mobject, longName="ModuleScale", attributeType=float, minValue=0.001,
                   defaultValue=1, keyable=0)
        pm.setAttr(f'{self.module_ctrl.mobject}.ModuleScale', channelBox=1)
        for attr in gen_utils.scale_attrs:
            pm.connectAttr(f'{self.module_ctrl.mobject}.ModuleScale', f'{self.module_ctrl.mobject}.{attr}', f=1)
            pm.setAttr(f'{self.module_ctrl.mobject}.{attr}', lock=1, keyable=0)

        # ...Vis options
        attr_strings = ("PlacersVis", "VectorHandlesVis", "OrientersVis", "ControlsVis")
        default_vals = (1, 0, 0, 0)
        for attr_string, default_val in zip(attr_strings, default_vals):
            pm.addAttr(self.module_ctrl.mobject, longName=attr_string, attributeType="bool", defaultValue=default_val,
                       keyable=0)
            pm.setAttr(f'{self.module_ctrl.mobject}.{attr_string}', channelBox=1)


        if hide:
            [shape.visibility.set(0, lock=1) for shape in self.module_ctrl.mobject.getShapes()]


        # ...Hook module control to root group
        hook_string = "ModuleRootCtrl"
        pm.addAttr(self.rig_root_grp, longName=hook_string, dataType="string", keyable=0)
        pm.connectAttr(self.module_ctrl.mobject.message, f'{self.rig_root_grp}.{hook_string}')

        # ...Hook root group to parent Armature
        attr_prefix = "Module_"
        attr_name = f'{attr_prefix}{self.side_tag}{self.name}'
        pm.addAttr(self.armature_container, longName=attr_name, keyable=0, dataType="string")
        pm.connectAttr(self.rig_root_grp.message, f'{self.armature_container}.{attr_name}')





    ####################################################################################################################
    def aim_ctrl_at_placers(self):

        snapped_vector = [0, 1, 0]

        # ...Get positions of all placers in modules
        placer_positions = []
        for placer in self.placers.values():
            placer_positions.append(np.array(placer.position))

        average_placer_position = list(np.average(placer_positions, axis=0))

        if average_placer_position == [0, 0, 0]:
            return snapped_vector

        normalized_vector = gen_utils.normalize_vector(average_placer_position)

        vector_lengths = (abs(normalized_vector[0]), abs(normalized_vector[1]), abs(normalized_vector[2]))
        longest_place = vector_lengths.index(max(vector_lengths))

        snapped_vector = [0, 0, 0]
        if average_placer_position[longest_place] > 0:
            snapped_vector[longest_place] = 1
        elif average_placer_position[longest_place] < 0:
            snapped_vector[longest_place] = -1
        else:
            snapped_vector[longest_place] = 0


        return snapped_vector





    ####################################################################################################################
    def flip_module(self):

        connection = None
        connections = pm.listConnections(f'{self.rig_root_grp}.sz', source=1, plugs=1)
        if connections:
            connection = connections[0]
            gen_utils.break_connections(f'{self.rig_subGrps["module"]}.sz', incoming=True)

        pm.setAttr(f'{self.rig_root_grp}.sz', -1)
        pm.setAttr(f'{self.rig_root_grp}.ry', 180)
        gen_utils.convert_offset(self.rig_root_grp)

        # ...Reconnect
        if connection:
            pm.connectAttr(connection, self.rig_root_grp + ".sz")





    ####################################################################################################################
    def position_module(self):

        # ...Flip module if this is on the right
        self.flip_module() if self.side == nom.rightSideTag else None
        # ...Position module
        self.module_ctrl.mobject.translate.set(self.position)
        self.module_ctrl.mobject.rotate.set(self.rotation)
        pm.setAttr(f'{self.module_ctrl.mobject}.ModuleScale', self.scale)





    ####################################################################################################################
    def drive_module(self, hide_target=True):
        """
        Drives position of a placer from one armature module with a placer from another armature module. Good for making
            two modules act as if they're connected. e.g. Driving the end of an Arm armature module with the start of a
            Hand armature module.
        Args:
            hide_target (bool): If true, hides target node.
        Returns:
            (bool): Success state.
        """

        if not self.drive_target:
            return None

        if not isinstance(self.drive_target, dict):
            return None

        for key in self.drive_target:

            compare_keys = [pair[1] for pair in self.drive_target[key]]

            # ...Get source nodes
            source_placer = self.placers[key].mobject

            for target_key in self.drive_target[key]:

                # ...Get target placer from target key
                target_node = self.get_placer_from_tag(module_tag=target_key[0], placer_tag=target_key[1])

                # ...Constrain target nodes to source nodes
                [pm.setAttr(f'{target_node}.{attr}', lock=0) for attr in gen_utils.keyable_attrs]
                pm.parentConstraint(source_placer, target_node, mo=1)

                # ...Hide and disconnect target_node
                if not hide_target:
                    continue

                # ...Hide shape
                self.make_obj_benign(target_node)
                # ...Hide any connectors relating to placer
                if not pm.attributeQuery("Connectors", node=target_node, exists=1):
                    continue

                connectors = pm.listConnections(f'{target_node}.Connectors', d=1, s=0)
                for obj in connectors:
                    dest_placer = pm.listConnections(f'{obj}.DestinationPlacer', s=1, d=0)[0]
                    dest_placer_tag = pm.getAttr(f'{dest_placer}.PlacerTag')

                    if dest_placer_tag not in compare_keys:
                        continue

                    if obj.getShape().visibility.get() == 1:
                        obj.getShape().visibility.set(0, lock=1)


                # ...NOTE: If target_node is a placer, does something more need to be done with its orienter and
                #    vector handles?
        return True





    ####################################################################################################################
    def get_placer_from_tag(self, module_tag, placer_tag):

        target_module_ctrl = self.get_other_module(name=module_tag, return_module_ctrl=True)
        target_node = pm.listConnections(target_module_ctrl + "." + "PlacerNodes" + "." + placer_tag, s=1, d=0)[0]

        return target_node





    ####################################################################################################################
    def make_obj_benign(self, obj):

        for shape in obj.getShapes():
            shape.visibility.set(lock=0)
            shape.visibility.set(0, lock=1)
            [pm.setAttr(f'{obj}.{attr}', lock=1, keyable=0) for attr in ("tx", "ty", "tz",
                                                                         "rx", "ry", "rz",
                                                                         "sx", "sy", "sz")]





    ####################################################################################################################
    def draw_module_connections(self, parent=None):


        if self.draw_connections:

            # ...Create an attribute to keep track of these extra drawn connections
            pm.addAttr(self.rig_root_grp, longName="ExtraDrawnConnections", dataType="string", keyable=0)


        for key in self.draw_connections:

            for placer_info in self.draw_connections[key]:

                end_1_node = self.placers[key].mobject

                target_module_key = placer_info[0]
                target_module_ctrl = self.get_other_module(name=target_module_key, return_module_ctrl=True)

                end_2_node = pm.listConnections(f'{target_module_ctrl}.PlacerNodes.{placer_info[1]}', source=1)[0]


                parent_obj = parent if parent else self.rig_subGrps["connector_curves"]

                connector = rig_utils.connector_curve(
                    name=key, line_width=1.5, end_driver_1=end_1_node, end_driver_2=end_2_node,
                    override_display_type=2, parent=parent_obj, inheritsTransform=False)[0]

                # ...Connect curve to module attribute
                pm.addAttr(connector, longName="Module", dataType="string", keyable=0)
                pm.connectAttr(f'{self.rig_root_grp}.ExtraDrawnConnections', f'{connector}.Module')





    ####################################################################################################################
    def connect_modules(self):

        if self.drive_target:
            self.drive_module()

        if self.draw_connections:
            self.draw_module_connections()





    ####################################################################################################################
    def drive_module_handles_vis(self, drive_plug):

        for ctrl in self.module_handles.values():
            ctrl.visibility.set(lock=0)
            pm.connectAttr(drive_plug, ctrl.visibility)
            ctrl.visibility.set(lock=1, keyable=0, channelBox=0)





    ####################################################################################################################
    def create_prelim_ctrls(self, parent=None):

        parent = parent if parent else self.rig_subGrps["prelim_ctrls"]

        # ...Operate on each control in dictionary
        for key in self.prelim_ctrls:

            prelim_ctrl = self.prelim_ctrls[key]
            ctrl = prelim_ctrl.create_prelim_ctrl_obj()
            # ...Position ctrl
            prelim_ctrl.position_prelim_ctrl(body_module=self)
            # ...Orient ctrl
            prelim_ctrl.orient_prelim_ctrl()

            self.prelim_ctrls[key].ctrl_obj.setParent(parent)
            self.prelim_ctrls[key].ctrl_obj.rotate.set(0, 0, 0)
            self.prelim_ctrls[key].ctrl_obj.scale.set(1, 1, 1)

            pm.orientConstraint(self.module_ctrl.mobject, parent)





    ####################################################################################################################
    def drive_vis_attrs_from_module_ctrl(self):

        # ...Vis options
        attr_strings = ("PlacersVis", "VectorHandlesVis", "OrientersVis", "ControlsVis")

        # ...Drive the same attrs on module placers
        pm.connectAttr(f'{self.module_ctrl.mobject}.PlacersVis', self.rig_subGrps["placers"].visibility)
        pm.connectAttr(f'{self.module_ctrl.mobject}.ControlsVis', self.rig_subGrps["prelim_ctrls"].visibility)

        for placer in self.placers.values():
            for attr_out, attr_in in (("VectorHandlesVis", "VectorHandlesVis"), ("OrientersVis", "OrienterVis")):
                if pm.attributeQuery(attr_in, node=placer.mobject, exists=1):
                    pm.connectAttr(self.module_ctrl.mobject + "." + attr_out, placer.mobject + "." + attr_in, f=1)
                    pm.setAttr(f'{placer.mobject}.{attr_in}', channelBox=0)





    ####################################################################################################################
    def populate_module(self):

        # ...Get scene armature
        self.get_scene_armature()
        # ...Structural groups
        self.create_module_grps()
        # ...Placers
        self.create_module_placers()
        # ...Connector curves
        self.create_connector_curves()
        # ...Orienters
        self.aim_module_orienters()

        # ...Run any required bespoke setup
        get_module_data.bespokeSetup(self.rig_module_type).build(self)





    ####################################################################################################################
    def get_other_module(self, name, return_module_ctrl):

        return_node = None

        target_module = return_node = pm.listConnections(
            f'{self.armature_container}.Module_{name}', source=1)[0]

        if return_module_ctrl:
            return_node = pm.listConnections(f'{target_module}.ModuleRootCtrl', source=1)[0]

        return return_node





    ####################################################################################################################
    def get_scene_armature(self):

        search = pm.ls("::*_ARMATURE", type="transform")
        self.armature_container = search[0] if search else None





    ####################################################################################################################
    def placers_from_data(self, data):

        self.placer_data = []

        # ...Certain inputs needs to be converted from string representations of python expressions
        for p_dict in data:
            for key in ("vectorHandleData", "orienterData", "connectorTargets"):
                v = p_dict[key]
                if isinstance(v, str):
                    p_dict[key] = ast.literal_eval(v)

            if "ikDistance" in p_dict:
                self.placer_data.append(
                    PoleVectorPlacer(name=p_dict["name"],
                                     side=p_dict["side"],
                                     position=p_dict["position"],
                                     size=p_dict["size"],
                                     vector_handle_data=p_dict["vectorHandleData"],
                                     orienter_data=p_dict["orienterData"],
                                     connect_targets=p_dict["connectorTargets"],
                                     pv_distance=p_dict["ikDistance"])
                )

            else:
                self.placer_data.append(
                    Placer(name = p_dict["name"],
                           side = p_dict["side"],
                           position = p_dict["position"],
                           size = p_dict["size"],
                           vector_handle_data = p_dict["vectorHandleData"],
                           orienter_data = p_dict["orienterData"],
                           connect_targets = p_dict["connectorTargets"])
                )
