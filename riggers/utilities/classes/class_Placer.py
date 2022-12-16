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

import Snowman3.riggers.dictionaries.control_colors as ctrl_colors_dict
importlib.reload(ctrl_colors_dict)
ctrl_colors = ctrl_colors_dict.create_dict()

import Snowman3.riggers.utilities.classes.class_Orienter as classOrienter
importlib.reload(classOrienter)
Orienter = classOrienter.Orienter
###########################
###########################


###########################
######## Variables ########
attr_strings = {"vector_handles_vis": "VectorHandlesVis",
                "orienter_vis": "OrienterVis"}
default_placer_shape_type = "sphere_curve_obj"
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
        aim_obj = None,
        up_obj = None,
        has_vector_handles = True,
        get = False,
        placer_data = None,
        orienter_data = None,
        ik_distance = None,
        connect_targets = None,
    ):
        self.name = name
        self.position = position if position else (0, 0, 0)
        self.size = size if size else 1.0
        self.shape_type = shape_type if shape_type else default_placer_shape_type
        self.side = side if side else None
        self.side_tag = "{}_".format(self.side) if self.side else ""
        self.color = color if color else ctrl_colors[self.side] if self.side else ctrl_colors[nom.midSideTag]
        self.parent = parent if parent else None
        self.up_vector_handle = None
        self.aim_vector_handle = None
        self.vector_handle_grp = None
        self.has_vector_handles = has_vector_handles
        self.aim_obj = aim_obj
        self.up_obj = up_obj
        self.connector_curve = None
        self.placer_data = placer_data
        self.buffer_node = None
        self.orienter_data = orienter_data
        self.orienter = None
        self.get = get
        self.ik_distance = ik_distance
        self.connect_targets = connect_targets if connect_targets else None

        if self.orienter_data:
            for key in ("world_up_type",
                        "aim_vector",
                        "up_vector",
                        "match_to"):
                if key not in self.orienter_data.keys():
                    self.orienter_data[key] = None
        else:
            self.orienter_data = {
                "world_up_type": None,
                "aim_vector": None,
                "up_vector": None,
                "match_to": None
            }

        if self.placer_data:
            for key in ("aim_target",
                        "up_target"):
                if key not in self.placer_data.keys():
                    self.placer_data[key] = None
            for key in ("has_vector_handles",):
                if key not in self.placer_data.keys():
                    self.placer_data[key] = True

        self.mobject = None
        if self.get:
            self.get_placer()




    '''
    create_mobject
    get_placer
    create_vector_handles
    dull_color
    set_position
    get_opposite_placer
    setup_live_symmetry
    create_connector_curve
    make_benign
    create_orienter
    aim_orienter
    install_reverse_ik
    placer_metadata
    '''




    ####################################################################################################################
    def create_mobject(self):

        # ...Create placer
        self.mobject = gen_utils.placer(name = self.name,
                                        size = self.size,
                                        placer_type = self.shape_type,
                                        side = self.side,
                                        parent = self.parent,
                                        color = self.color)
        # ...Metadata
        self.placer_metadata()
        # ...Vector handles. Aim Handle and Up Handle
        self.create_vector_handles() if self.has_vector_handles else None
        # ...Buffer group
        self.buffer_node = gen_utils.buffer_obj(self.mobject)
        # ...Position placer
        self.set_position() if self.position else None
        # ...Orienter
        self.create_orienter()


        return self.mobject





    ####################################################################################################################
    def get_placer(self):

        placer_search_string = "::{0}{1}_{2}".format(self.side_tag, self.name, nom.placer)

        placer = pm.ls(placer_search_string)
        if not placer:
            print("Unable to find placer from string: '{}'".format(placer_search_string))
        else:
            self.mobject = placer[0]

            self.color = gen_utils.get_color(self.mobject)

            # ...Find orienter
            self.orienter = None

            for child in pm.listRelatives(self.mobject, allDescendents=1):
                if child.nodeType() == "transform":
                    if str(child).endswith(nom.orienter):
                        self.orienter = child
                        break





    ####################################################################################################################
    def create_vector_handles(self):

        # ...A group to house vector handles
        self.vector_handle_grp = pm.group(name="vectorHandlesVis", em=1, p=self.mobject)

        # ...Create vector handles
        self.aim_vector_handle = VectorHandle(name="{}{}".format(self.side_tag, self.name), vector="aim",
                                              side=self.side, parent=self.vector_handle_grp, color=self.color,
                                              placer=self)
        self.up_vector_handle = VectorHandle(name="{}{}".format(self.side_tag, self.name), vector="up",
                                             side=self.side, parent=self.vector_handle_grp, color=self.color,
                                             placer=self)





    ####################################################################################################################
    def dull_color(self, placer=None, gray_out=True, hide=False):

        # ...If no specific placer provided, default to using THIS placer
        if not placer:
            placer = self.mobject

        for shape in placer.getShapes():
            shape.overrideEnabled.set(1)
            shape.overrideDisplayType.set(1)
            if hide:
                shape.visibility.set(0)





    ####################################################################################################################
    def set_position(self, position=None):

        # ...If no position specified, fall back on placer's inbuilt position variable
        placer_pos = position if position else self.position
        # ...Position placer
        self.buffer_node.translate.set(placer_pos)





    ####################################################################################################################
    def get_opposite_placer(self):

        # ...Check that placer is sided
        if not self.side:
            print("Placer '{0}' has not assigned side, and therefore, has no opposite placer".format(self.mobject))
            return None

        # ...Check that placer's side is valid (left or right)
        if not self.side in (nom.leftSideTag, nom.rightSideTag):
            print("Side for placer '{0}': {1}." \
                  "Can only find opposite placers if assigned side is '{2}' or '{3}'".format(self.mobject, self.side,
                                                                                    nom.leftSideTag, nom.rightSideTag))

        # ...Find and get opposite placer
        opposite_placer = None
        opposite_placer = gen_utils.get_opposite_side_obj(self.mobject)

        if not opposite_placer:
            print("Unable to find opposite placer for placer: '{0}'".format(self.mobject))
            return None


        return opposite_placer





    ####################################################################################################################
    def setup_live_symmetry(self, reverse_relationship=False, dull_follower=True):

        # ...Get opposite placer
        opposite_placer = self.get_opposite_placer()

        if not opposite_placer:
            print("No opposite placer found. Cannot setup live symmetry for placer '{0}'".format(self.mobject))
            return None


        # Determine - based on reverse_relationship arg - if THIS placer leads, or follows
        leader = opposite_placer
        follower = self.mobject
        if reverse_relationship:
            leader = self.mobject
            follower = opposite_placer


        for attr in ("tx", "ty", "tz", "rx", "ry", "rz"):
            if not pm.listConnections(follower + "." + attr, source=1):
                pm.connectAttr(leader + "." + attr, follower + "." + attr)
                pm.setAttr(follower + "." + attr, lock=1, keyable=0, channelBox=1)

        if dull_follower:
            self.dull_color(follower)





    ####################################################################################################################
    def create_connector_curve(self, target, parent=None):

        target_obj = target.mobject

        par = parent if parent else self.mobject

        self.connector_curve = rig_utils.connector_curve( name = "{}{}".format(self.side_tag, self.name),
                                                          line_width = 1.5,
                                                          end_driver_1 = self.mobject,
                                                          end_driver_2 = target.mobject,
                                                          override_display_type = 2,
                                                          parent = par,
                                                          inheritsTransform = False,
                                                          use_locators = False)[0]

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
            # ...Hide placer shape
            for shape in self.mobject.getShapes():
                shape.visibility.set(0, lock=1) if not shape.visibility.get(lock=1) else None

        # ...Lock attributes
        [pm.setAttr(self.mobject + "." + attr, lock=1, keyable=0) for attr in gen_utils.keyable_attrs]

        # ...Dull placer color
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
    def create_orienter(self):


        self.orienter = Orienter(name=self.name,
                                 side=self.side,
                                 size=self.size,
                                 parent=self.mobject,
                                 aim_vector=self.orienter_data["aim_vector"],
                                 up_vector=self.orienter_data["up_vector"],
                                 match_to=self.orienter_data["match_to"],
                                 placer=self)

        # ...Connect orienter to placer via message attr
        orienter_attr_name = "OrienterNode"
        pm.addAttr(self.mobject, longName=orienter_attr_name, dataType="string", keyable=0)
        self.orienter.mobject.message.connect(self.mobject + "." + orienter_attr_name)

        # ...Drive orienter's visibility from placer attribute
        pm.addAttr(self.mobject, longName=attr_strings["orienter_vis"], attributeType="bool", keyable=0, defaultValue=0)
        pm.setAttr(self.mobject + '.' + attr_strings["orienter_vis"], channelBox=1)

        pm.connectAttr(self.mobject + "." + attr_strings["orienter_vis"], self.orienter.mobject.visibility)

        pm.select(clear=1)
        return self.orienter





    ####################################################################################################################
    def aim_orienter(self):

        # Constrain placer's up vector and aim vector handles
        if self.aim_obj:

            if type(self.aim_obj) in (list, tuple):

                self.aim_vector_handle.mobject.translate.set(self.aim_obj)

            else:

                aim_target_obj = None
                get_placer_string = "::{}{}_{}".format(self.side_tag, self.aim_obj, nom.placer)
                if pm.ls(get_placer_string):
                    aim_target_obj = pm.ls(get_placer_string)[0]
                else:
                    print("Unable to find object: '{}'".format(get_placer_string))

                offset = gen_utils.buffer_obj(self.aim_vector_handle.mobject, suffix="MOD")
                pm.pointConstraint(aim_target_obj, offset)

        if self.up_obj:

            if type(self.up_obj) in (list, tuple):

                self.up_vector_handle.mobject.translate.set(self.up_obj)

            else:

                up_target_obj = None
                get_placer_string = "::{}{}_{}".format(self.side_tag, self.up_obj, nom.placer)
                if pm.ls(get_placer_string):
                    up_target_obj = pm.ls(get_placer_string)[0]
                else:
                    print("Unable to find object: '{}'".format(get_placer_string))

                offset = gen_utils.buffer_obj(self.up_vector_handle.mobject, suffix="MOD")
                pm.pointConstraint(up_target_obj, offset)

        self.orienter.aim_orienter()





    ####################################################################################################################
    def install_reverse_ik(self, pv_chain_mid=None, limb_start=None, limb_end=None, scale_node=None,
                           connector_crv_parent=None, module=None, hide=False):

        # ...Variable initializations
        pv_chain_start = limb_start
        pv_chain_end = limb_end


        # ...Take note of placer's current parent (this placer will receive a new parent,
        # ...which itself will end up back here)
        placer_orig_parent = self.mobject.getParent()

        # ...Get lengths of limb segments
        seg_1_dist = node_utils.distanceBetween(inMatrix1=pv_chain_start.worldMatrix,
                                                inMatrix2=pv_chain_mid.worldMatrix)
        seg_2_dist = node_utils.distanceBetween(inMatrix1=pv_chain_mid.worldMatrix,
                                                inMatrix2=pv_chain_end.worldMatrix)

        # ...Create and position midway locator
        sum = node_utils.floatMath(floatA=seg_1_dist + ".distance", floatB=seg_2_dist + ".distance", operation="add")
        div_1 = node_utils.floatMath(operation="divide", floatA=seg_2_dist + ".distance", floatB=sum.outFloat)
        div_2 = node_utils.floatMath(operation="divide", floatA=seg_1_dist + ".distance", floatB=sum.outFloat)

        mid_point_loc = pm.spaceLocator(name='{}pvMidpoint_{}_{}'.format(self.side_tag, self.name, nom.locator))
        mid_point_loc_shape = mid_point_loc.getShape()
        mid_point_loc_shape.visibility.set(0)

        # ...Keep midway locator between start and end of limb
        constraint = pm.pointConstraint(pv_chain_start, pv_chain_end, mid_point_loc)
        weights = pm.pointConstraint(constraint, query=1, weightAliasList=1)
        pm.connectAttr(div_1.outFloat, weights[0])
        pm.connectAttr(div_2.outFloat, weights[1])

        # ...Aim midway locator at mid-limb placer
        pm.aimConstraint(pv_chain_mid, mid_point_loc, worldUpType="object", worldUpObject=pv_chain_end,
                         aimVector=[0, 0, 1], upVector=[1, 0, 0])

        # ...Position pole vector placer
        pv_end_loc = pm.spaceLocator(name="{}pvEnd_{}_{}".format(self.side_tag, self.name, nom.locator))
        pv_end_loc.setParent(mid_point_loc)
        gen_utils.zero_out(pv_end_loc)

        # ...Make pole vector offset relative to limb length
        add = node_utils.addDoubleLinear(input1=seg_1_dist.distance, input2=seg_2_dist.distance)
        div_1 = node_utils.floatMath(floatA=add.output, floatB=add.output.get(), operation="divide")
        decomp = node_utils.decomposeMatrix(inputMatrix=module.module_ctrl.mobject.worldMatrix)
        div_2 = node_utils.floatMath(floatA=div_1.outFloat, floatB=decomp.outputScale.outputScaleX, operation="divide")
        mult = node_utils.multDoubleLinear(input1=div_2.outFloat, input2=self.ik_distance)
        mult.output.connect(pv_end_loc.tz)

        pm.matchTransform(self.buffer_node, pv_end_loc)
        gen_utils.convert_offset(self.buffer_node)

        mult_matrix = node_utils.multMatrix(matrixIn=(pv_end_loc.worldMatrix, self.buffer_node.parentInverseMatrix))
        decomp = node_utils.decomposeMatrix(inputMatrix=mult_matrix.matrixSum,
                                            outputTranslate=self.buffer_node.translate,
                                            outputRotate=self.buffer_node.rotate)

        module.pv_placers[self.name] = self



        # ...Make connector curve linking ik placers to limb
        crv = rig_utils.connector_curve(line_width=1, end_driver_1=pv_chain_mid, end_driver_2=self.mobject,
                                        override_display_type=1, parent=connector_crv_parent,
                                        inheritsTransform=False, use_locators=False)[0]


        # ...Hide reverse IK system (optional)
        if hide:
            for node in (crv, self.mobject):
                gen_utils.break_connections(node.visibility)
                node.visibility.set(lock=0)
                node.visibility.set(0, lock=1)

            # ...Lock down PV placer's transforms
            [pm.setAttr(self.mobject + "." + attr,
                        lock=1, keyable=0) for attr in gen_utils.keyable_transform_attrs]



        [pm.setAttr(self.mobject + "." + attr, lock=1, keyable=0) for attr in ("tx", "ty")]

        pm.select(clear=1)



        return mid_point_loc





    ####################################################################################################################
    def placer_metadata(self):

        obj = self.mobject
        print(1)
        # ...Placer tag
        placer_tag_attr_name = "PlacerTag"
        pm.addAttr(obj, longName=placer_tag_attr_name, dataType="string", keyable=0)
        pm.setAttr(obj + "." + placer_tag_attr_name, self.name, type="string")
        print(2)
        # ...Side
        placer_side_attr_name = "Side"
        pm.addAttr(obj, longName=placer_side_attr_name, dataType="string", keyable=0)
        attr_input = self.side if self.side else "None"
        pm.setAttr(obj + "." + placer_side_attr_name, attr_input, type="string")
        print(3)
        # ...Aim object
        placer_aimObj_attr_name = "AimObj"
        if isinstance(self.aim_obj, str) or not self.aim_obj:
            pm.addAttr(obj, longName=placer_aimObj_attr_name, dataType="string", keyable=0)
            if self.aim_obj:
                pm.setAttr(obj + "." + placer_aimObj_attr_name, self.aim_obj, type="string")
            else:
                pm.setAttr(obj + "." + placer_aimObj_attr_name, "None", type="string")
        elif type(self.aim_obj) in (tuple, list):
            pm.addAttr(obj, longName=placer_aimObj_attr_name, attributeType="compound", keyable=0, numberOfChildren=3)
            letters = ("x", "y", "z")
            for i in range(3):
                letter = letters[i]
                pm.addAttr(obj, longName=letter, keyable=0, attributeType="double", parent=placer_aimObj_attr_name)
        print(4)
        # ...Up object
        '''placer_upObj_attr_name = "UpObj"
        if isinstance(self.up_obj, str) or not self.up_obj:
            pm.addAttr(obj, longName=placer_upObj_attr_name, dataType="string", keyable=0)
            if self.up_obj:
                pm.setAttr(obj + "." + placer_upObj_attr_name, self.up_obj, type="string")
            else:
                pm.setAttr(obj + "." + placer_upObj_attr_name, "None", type="string")
        elif type(self.up_obj) in (tuple, list):
            pm.addAttr(obj, longName=placer_upObj_attr_name, attributeType="compound", keyable=0, numberOfChildren=3)
            letters = ("x", "y", "z")
            for i in range(3):
                letter = letters[i]
                pm.addAttr(obj, longName=letter, keyable=0, attributeType="double", parent=placer_upObj_attr_name)'''
        print(5)
        # ...Has vector handles
        placer_hasVectorHandles_attr_name = "HasVectorHandles"
        pm.addAttr(obj, longName=placer_hasVectorHandles_attr_name, attributeType="bool", keyable=0,
                   defaultValue=self.has_vector_handles)
        print(6)
        # ...IK distance
        if self.ik_distance:
            placer_ikDist_attr_name = "IkDistance"
            pm.addAttr(obj, longName=placer_ikDist_attr_name, attributeType="float", keyable=0,
                       defaultValue=self.ik_distance)
        print(7)
        # ...Orienter data
        # ...Connect targets
        # ...


        pm.addAttr(self.mobject, longName="ReceivedConnectors", dataType="string", keyable=0)
        print(8)
