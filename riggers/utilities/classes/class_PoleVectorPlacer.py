# Title: class_PoleVectorPlacer.py
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
importlib.reload(classVectorHandle)
VectorHandle = classVectorHandle.VectorHandle

import Snowman3.riggers.utilities.classes.class_Orienter as classOrienter
importlib.reload(classOrienter)
Orienter = classOrienter.Orienter

import Snowman3.riggers.dictionaries.control_colors as ctrl_colors_dict
importlib.reload(ctrl_colors_dict)
ctrl_colors = ctrl_colors_dict.create_dict()

import Snowman3.riggers.utilities.classes.class_Placer as classPlacer
importlib.reload(classPlacer)
Placer = classPlacer.Placer
###########################
###########################


###########################
######## Variables ########

###########################
###########################





########################################################################################################################
class PoleVectorPlacer(Placer):

    def __init__(
        self,
        name,
        pv_distance,
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
        self.pv_distance = pv_distance
        self.pv_curve = None
        self.mid_point_loc = None

        super().__init__(
            name,
            position=position,
            size=size,
            shape_type=shape_type,
            side=side,
            color=color,
            parent=parent,
            vector_handle_data=vector_handle_data,
            orienter_data=orienter_data,
            connect_targets=connect_targets,
        )





    """
    --------- METHODS --------------------------------------------------------------------------------------------------
    --------------------------------------------------------------------------------------------------------------------
    install_reverse_ik
    hide_reverse_ik
    mid_chain_locator
    pv_placer_metadata
    metadata_IkDistance
    --------------------------------------------------------------------------------------------------------------------
    --------------------------------------------------------------------------------------------------------------------
    """





    ####################################################################################################################
    def install_reverse_ik(self, pv_chain_mid=None, limb_start=None, limb_end=None,  connector_crv_parent=None,
                           module=None, hide=False):

        # ...Variable initializations
        pv_chain_start, pv_chain_end = limb_start, limb_end

        # ...Get lengths of limb segments
        seg_1_dist = node_utils.distanceBetween(inMatrix1=pv_chain_start.worldMatrix,
                                                inMatrix2=pv_chain_mid.worldMatrix)
        seg_2_dist = node_utils.distanceBetween(inMatrix1=pv_chain_mid.worldMatrix,
                                                inMatrix2=pv_chain_end.worldMatrix)

        # ...Create and position midway locator
        self.mid_chain_locator(seg_1_dist, seg_2_dist, pv_chain_start, pv_chain_end, pv_chain_mid)
        # ...Position pole vector locator
        pv_end_loc = pm.spaceLocator(name="{}pvEnd_{}_{}".format(self.side_tag, self.name, nom.locator))
        pv_end_loc.setParent(self.mid_point_loc)
        gen_utils.zero_out(pv_end_loc)

        # ...Make pole vector offset relative to limb length
        add = node_utils.addDoubleLinear(input1=seg_1_dist.distance, input2=seg_2_dist.distance)
        div_1 = node_utils.floatMath(floatA=add.output, floatB=add.output.get(), operation="divide")
        decomp = node_utils.decomposeMatrix(inputMatrix=module.module_ctrl.mobject.worldMatrix)
        div_2 = node_utils.floatMath(floatA=div_1.outFloat, floatB=decomp.outputScale.outputScaleX,
                                     operation="divide")
        mult = node_utils.multDoubleLinear(input1=div_2.outFloat, input2=self.pv_distance)
        mult.output.connect(pv_end_loc.tz)

        # ...Match placer buffer, then zero out placer to avoid double transforms
        pm.matchTransform(self.buffer_node, pv_end_loc)
        gen_utils.convert_offset(self.buffer_node)

        mult_matrix = node_utils.multMatrix(matrixIn=(pv_end_loc.worldMatrix, self.buffer_node.parentInverseMatrix))
        decomp = node_utils.decomposeMatrix(inputMatrix=mult_matrix.matrixSum,
                                            outputTranslate=self.buffer_node.translate,
                                            outputRotate=self.buffer_node.rotate)

        module.pv_placers[self.name] = self

        [pm.setAttr(f'{self.mobject}.{a}', lock=0) for a in ("tx", "ty")]
        [pm.setAttr(f'{self.mobject}.{a}', 0) for a in ("tx", "ty", "tz")]
        [pm.setAttr(f'{self.mobject}.{a}', lock=1) for a in ("tx", "ty")]

        self.mobject.tz.set(self.position[2])

        # ...Make connector curve linking ik placers to limb
        self.pv_curve = rig_utils.connector_curve(line_width=1, end_driver_1=pv_chain_mid, end_driver_2=self.mobject,
                                                  override_display_type=1, parent=connector_crv_parent,
                                                  inheritsTransform=False, use_locators=False)[0]

        # ...Hide reverse IK system (optional)
        self.hide_reverse_ik() if hide else None

        [pm.setAttr(self.mobject + "." + attr, lock=1, keyable=0) for attr in ("tx", "ty")]

        pm.select(clear=1)


        # ...Install PoleVectorPlacer-unique metadata
        self.pv_placer_metadata()

        return self.mid_point_loc





    ####################################################################################################################
    def hide_reverse_ik(self):

        for node in (self.pv_curve, self.mobject):
            gen_utils.break_connections(node.visibility)
            node.visibility.set(lock=0)
            node.visibility.set(0, lock=1)

            # ...Lock down PV placer's transforms
        [pm.setAttr(self.mobject + "." + attr, lock=1, keyable=0) for attr in gen_utils.keyable_transform_attrs]





    ####################################################################################################################
    def mid_chain_locator(self, seg_1_dist, seg_2_dist, pv_chain_start, pv_chain_end, pv_chain_mid):

        sum = node_utils.floatMath(floatA=f'{seg_1_dist}.distance', floatB=f'{seg_2_dist}.distance',
                                   operation="add")
        div_1 = node_utils.floatMath(operation="divide", floatA=f'{seg_2_dist}.distance', floatB=sum.outFloat)
        div_2 = node_utils.floatMath(operation="divide", floatA=f'{seg_1_dist}.distance', floatB=sum.outFloat)

        self.mid_point_loc = pm.spaceLocator(name=f'{self.side_tag}pvMidpoint_{self.name}_{nom.locator}')
        self.mid_point_loc.getShape().visibility.set(0)

        # ...Keep midway locator between start and end of limb
        constraint = pm.pointConstraint(pv_chain_start, pv_chain_end, self.mid_point_loc)
        weights = pm.pointConstraint(constraint, query=1, weightAliasList=1)
        div_1.outFloat.connect(weights[0])
        div_2.outFloat.connect(weights[1])

        # ...Aim midway locator at mid-limb placer
        pm.aimConstraint(pv_chain_mid, self.mid_point_loc, worldUpType="object", worldUpObject=pv_chain_end,
                         aimVector=[0, 0, 1], upVector=[1, 0, 0])





    ####################################################################################################################
    def pv_placer_metadata(self):

        # ...IK distance
        self.metadata_IkDistance()





    ####################################################################################################################
    def metadata_IkDistance(self):

        # ...IK distance
        gen_utils.add_attr(self.mobject, long_name="IkDistance", attribute_type="float", keyable=0,
                           default_value=self.pv_distance)
