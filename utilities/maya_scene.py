import importlib
import maya.cmds as mc
import maya.api.OpenMaya as om
import pymel.core as pm
from Snowman3.utilities.decorators import check_simple_args

import Snowman3.riggers.managers.rig_manager as rig_manager_util
importlib.reload(rig_manager_util)
RigManager = rig_manager_util.RigManager

import Snowman3.riggers.managers.armature_manager as armature_manager_util
importlib.reload(armature_manager_util)
ArmatureManager = armature_manager_util.ArmatureManager

import Snowman3.riggers.utilities.curve_utils as curve_utils
importlib.reload(curve_utils)


class MayaScene:

    armature_manager = None
    rig_manager = None


    @check_simple_args
    def objExists(self, *args, **kwargs):
        return mc.objExists(*args, **kwargs)


    def create_armature_manager(self):
        self.armature_manager = ArmatureManager()


    def create_rig_manager(self):
        self.rig_manager = RigManager()


    def build_armature_from_blueprint(self, blueprint):
        self.armature_manager.build_armature_from_blueprint(blueprint=blueprint)


    def build_armature_from_latest_version(self, blueprint_manager):
        blueprint_manager.load_blueprint_from_latest_version()
        self.build_armature_from_blueprint(blueprint_manager.blueprint)


    def build_rig(self, blueprint_manager):
        self.rig_manager.build_rig_from_armature(blueprint_manager.blueprint)
        self.armature_manager.hide_armature()


    def create_nurbs_curve(self, **kwargs):
        return curve_utils.create_nurbs_curve(**kwargs)


    def initialize_plug(self, owner, key):
        node_functions = om.MFnDependencyNode(owner)
        m_attribute = node_functions.attribute(key)
        return node_functions.findPlug(m_attribute, False)


    def get_selection_string(self, m_object):
        sel_list = om.MSelectionList()
        sel_list.add(m_object)
        sel_strings = sel_list.getSelectionStrings(0)
        return pm.PyNode(sel_strings[0])


    def create_m_plug(self, owner, key, **kwargs):
        mc.addAttr( self.get_selection_string(owner), longName=key, **kwargs )
        return self.initialize_plug(owner, key)

'''
import os
import traceback
import logging

import maya.OpenMaya as om
import maya.OpenMayaAnim as oma
import maya.cmds as mc
import maya.mel as mel

import maya_tools.deformer_utilities.blendshape as btl

import maya_tools.deformer_utilities.delta_mush as dmu
import maya_tools.deformer_utilities.general as dtl
import maya_tools.deformer_utilities.lattice as lut
import maya_tools.deformer_utilities.softMod as sut
import maya_tools.deformer_utilities.non_linear as ntl
import maya_tools.deformer_utilities.skin_cluster as sku
import maya_tools.deformer_utilities.wire as wir
import maya_tools.deformer_utilities.wrap as wru
import maya_tools.deformer_utilities.cvwrap as cvw
import maya_tools.deformer_utilities.squish_utils as sqt
import maya_tools.utilities.animation_curve_utils as atl
import maya_tools.utilities.ik_handle_utilities as itl
import maya_tools.utilities.mesh_utilities as mtl
import maya_tools.utilities.nurbs_surface_utilities as nsl
import maya_tools.utilities.nurbs_utils as ctl
import maya_tools.utilities.plug_utilities as ptl
import maya_tools.utilities.ribbon_utilities as rtl
import maya_tools.utilities.selection_utilities as stl
import maya_tools.utilities.cloth_utilities as clthutils

import maya_tools.utilities.skin_utils as sss
from maya_tools.utilities.decorators import flatten_args, check_simple_args, m_object_args, m_dag_path_args
import maya_tools.utilities.nurbs_curve_utilities as ncu
import rig_factory.common_modules as com
from iRig.iRig_maya.lib import deformLib

global MAYA_CALLBACKS
MAYA_CALLBACKS = []

NURBS_CURVE_FORMS = [
    om.MFnNurbsCurve.kOpen,
    om.MFnNurbsCurve.kClosed,
    om.MFnNurbsCurve.kPeriodic
]
NURBS_SURFACE_FORMS = [
    om.MFnNurbsSurface.kOpen,
    om.MFnNurbsSurface.kClosed,
    om.MFnNurbsSurface.kPeriodic,
    om.MFnNurbsSurface.kLast
]

mc.setNodeTypeFlag(
    'shardMatrix',
    threadSafe=False
)

CURVE_FUNCTIONS = oma.MFnAnimCurve

try:
    mc.setAttr('hardwareRenderingGlobals.lineAAEnable', 1)
    mc.setAttr('hardwareRenderingGlobals.multiSampleEnable', 1)
except Exception:
    logging.getLogger('rig_build').error(traceback.format_exc())


def pre_file_new_or_opened_callback(*args):
    com.system_signals.maya_callback_signals['pre_file_new_or_opened'].emit()


def selection_changed_callback(*args):
    com.system_signals.maya_callback_signals['selection_changed'].emit()


pre_file_new_or_opened_callback = om.MEventMessage.addEventCallback(
    'PreFileNewOrOpened',
    pre_file_new_or_opened_callback
)

selection_changed_callback = om.MEventMessage.addEventCallback(
    'SelectionChanged',
    selection_changed_callback
)
MAYA_CALLBACKS.append(pre_file_new_or_opened_callback)
MAYA_CALLBACKS.append(selection_changed_callback)


class MayaScene(object):
    callback_types = {
        'connection_made': om.MNodeMessage.kConnectionMade,
        'connection_broken': om.MNodeMessage.kConnectionBroken,
        'attribute_evaluated': om.MNodeMessage.kAttributeEval,
        'attribute_set': om.MNodeMessage.kAttributeSet,
        'attribute_locked': om.MNodeMessage.kAttributeLocked,
        'attribute_unlocked': om.MNodeMessage.kAttributeUnlocked,
        'attribute_added': om.MNodeMessage.kAttributeAdded,
        'attribute_removed': om.MNodeMessage.kAttributeRemoved,
        'attribute_renamed': om.MNodeMessage.kAttributeRenamed,
        'other_plug_set': om.MNodeMessage.kOtherPlugSet
    }
    tangents = {
        'auto': CURVE_FUNCTIONS.kTangentAuto,
        'clamped': CURVE_FUNCTIONS.kTangentClamped,
        'fast': CURVE_FUNCTIONS.kTangentFast,
        'fixed': CURVE_FUNCTIONS.kTangentFixed,
        'flat': CURVE_FUNCTIONS.kTangentFlat,
        'global': CURVE_FUNCTIONS.kTangentGlobal,
        'linear': CURVE_FUNCTIONS.kTangentLinear,
        'plateau': CURVE_FUNCTIONS.kTangentPlateau,
        'slow': CURVE_FUNCTIONS.kTangentSlow,
        'smooth': CURVE_FUNCTIONS.kTangentSmooth,
        'step': CURVE_FUNCTIONS.kTangentStep,
        'step_next': CURVE_FUNCTIONS.kTangentStepNext,
    }

    curve_types = {
        'time_to_angular': CURVE_FUNCTIONS.kAnimCurveTA,
        'time_to_linear': CURVE_FUNCTIONS.kAnimCurveTL,
        'time_to_time': CURVE_FUNCTIONS.kAnimCurveTT,
        'time_to_unitless': CURVE_FUNCTIONS.kAnimCurveTU,
        'unitless_to_angular': CURVE_FUNCTIONS.kAnimCurveUA,
        'unitless_to_linear': CURVE_FUNCTIONS.kAnimCurveUL,
        'unitless_to_time': CURVE_FUNCTIONS.kAnimCurveUT,
        'unitless_to_unitless': CURVE_FUNCTIONS.kAnimCurveUU,
        'unknown': CURVE_FUNCTIONS.kAnimCurveUnknown
    }

    infinity_types = {
        'constant': CURVE_FUNCTIONS.kConstant,
        'linear': CURVE_FUNCTIONS.kLinear,
        'cycle': CURVE_FUNCTIONS.kCycle,
        'cycle_relative': CURVE_FUNCTIONS.kCycleRelative,
        'oscilate': CURVE_FUNCTIONS.kOscillate,
    }

    def __init__(self):
        super(MayaScene, self).__init__()
        self.standalone = False
        self.mock = False
        self.loaded_plugins = []
        self.maya_version = mc.about(version=True)
        self.logger = logging.getLogger('rig_build')

    def get_predicted_curve_length(self, *args, **kwargs):
        return ncu.get_predicted_curve_length(*args, **kwargs)

    def get_predicted_params_at_cvs(self, *args, **kwargs):
        return ncu.get_predicted_params_at_cvs(*args, **kwargs)

    def get_closest_predicted_point_on_curve(self, *args, **kwargs):
        return ncu.get_closest_predicted_point_on_curve(*args, **kwargs)

    def get_closest_predicted_points_on_curve(self, *args, **kwargs):
        return ncu.get_closest_predicted_points_on_curve(*args, **kwargs)

    def get_predicted_points_on_curve(self, *args, **kwargs):
        return ncu.get_predicted_points_on_curve(*args, **kwargs)

    def get_evenly_distributed_points_on_curve(self, *args, **kwargs):
        return ncu.get_evenly_distributed_points_on_curve(*args, **kwargs)

    def get_evenly_distributed_curve_parameters(self, *args, **kwargs):
        return ncu.get_evenly_distributed_curve_parameters(*args, **kwargs)

    def create_cloth_origin_geo(self, *args, **kwargs):
        return clthutils.create_cloth_origin_geo(*args, **kwargs)

    def create_cloth(self, *args, **kwargs):
        return clthutils.create_cloth(*args, **kwargs)

    def create_rigid(self, *args, **kwargs):
        return clthutils.create_rigid(*args, **kwargs)

    def remove_rigid(self, *args, **kwargs):
        return clthutils.remove_rigid(*args, **kwargs)

    def get_cloth_mesh_names(self, *args, **kwargs):
        return clthutils.get_cloth_mesh_names(*args, **kwargs)

    def get_rigid_mesh_names(self, *args, **kwargs):
        return clthutils.get_rigid_mesh_names(*args, **kwargs)

    def get_cloth_node_names(self, *args, **kwargs):
        return clthutils.get_cloth_node_names(*args, **kwargs)

    def get_rigid_node_names(self, *args, **kwargs):
        return clthutils.get_rigid_node_names(*args, **kwargs)

    def polyNormalPerVertex(self, *args, **kwargs):
        return mc.polyNormalPerVertex(*args, **kwargs)

    def polySoftEdge(self, *args, **kwargs):
        return mc.polySoftEdge(*args, **kwargs)

    @staticmethod
    def get_file_info():
        """
        Get info stored in the scene
        :return: dict
        """

        def chunks(l, n):
            """
            splits a list into chunks
            """
            for i in range(0, len(l), n):
                yield l[i:i + n]

        data = dict()
        for chunk in chunks(mc.fileInfo(q=True), 2):
            data[chunk[0]] = chunk[1]
        return data

    @staticmethod
    def update_file_info(**kwargs):
        for key in kwargs:
            mc.fileInfo(key, kwargs[key])

    def select(self, *items, **kwargs):
        mc.select(*items, **kwargs)

    def reorderDeformers(self, *args, **kwargs):
        mc.reorderDeformers(*args, **kwargs)

    def add_node_delete_callback(self, m_object, function):
        return om.MNodeMessage.addNodePreRemovalCallback(
            m_object,
            function
        )

    def add_attribute_delete_callback(self, m_object, function):
        return om.MNodeMessage.addAttributeChangedCallback(
            m_object,
            function
        )

    def remove_callback(self, event_id):
        om.MMessage.removeCallback(event_id)

    def reorder_deformers_by_type(self, nodes, deformer_level):
        """
        Reorders history for the given geometries. Reordering is based
        on each deformers type.
        :param nodes:
            Names of geometries to reorder history for.
        :param deformer_level:
            Specifies how soon each deformer type should appear in the
            stack. The lower the value the sooner {TYPE: LEVEL}.
        """

        for node in mc.ls(*nodes):
            deformers = mc.listHistory(
                node,
                pruneDagObjects=True,
                interestLevel=2,
            )

            deformer_stack = []
            for deformer in deformers:

                node_type = mc.nodeType(deformer)
                if node_type not in deformer_level:
                    continue

                stack_level = deformer_level[node_type]
                deformer_stack.append((stack_level, deformer))

            deformer_stack.sort(
                key=lambda x: x[0],
                reverse=True,
            )

            upper_lower = zip(
                deformer_stack[:-1],
                deformer_stack[1:],
            )
            for (_, upper), (_, lower) in upper_lower:
                mc.reorderDeformers(upper, lower, node)

    def keyframe(self, *args, **kwargs):
        return mc.keyframe(*args, **kwargs)

    def select_keyframes(self, curve_names, in_value=None):
        self.select(*curve_names, add=True)
        if in_value is not None:
            mc.selectKey(curve_names, replace=False, add=True, f=(in_value,))
        else:
            mc.selectKey(curve_names, replace=False, add=True)

    def create_ik_spline_handle(self, *args, **kwargs):
        return itl.create_ik_spline_handle(*args, **kwargs)

    def fit_view(self, *args):
        try:
            if args:
                self.select(*args)
            mc.viewFit()
        except Exception as e:
            self.logger.error(traceback.format_exc())

    def get_selected_attribute_names(self):
        get_channelbox = mc.channelBox(
            'mainChannelBox',
            q=True,
            selectedMainAttributes=True
        )
        if not get_channelbox:
            return []
        return [str(x) for x in get_channelbox]

    def get_selected_nodes(self):
        nodes = []
        selection_list = om.MSelectionList()
        om.MGlobal.getActiveSelectionList(selection_list)
        for i in range(0, selection_list.length()):
            m_object = om.MObject()
            selection_list.getDependNode(i, m_object)
            nodes.append(m_object)
        return nodes

    def get_selected_node_names(self):
        return [self.get_selection_string(x) for x in self.get_selected_nodes()]

    def get_dag_path(self, dag_node):
        return om.MDagPath.getAPathTo(dag_node)

    def delete(self, *args, **kwargs):
        mc.delete(*args, **kwargs)

    def initialize_plug(self, owner, name):
        return ptl.initialize_plug(owner, name)

    def create_plug(self, owner, key, **kwargs):
        return ptl.create_plug(owner, key, **kwargs)

    def get_plug_compound_children_count(self, plug):
        if not plug.m_plug.isCompound:
            raise Exception('Plug {} is not a compound attribute!'.format(plug.name))
        return plug.m_plug.numChildren()

    def get_plug_locked(self, plug):
        return plug.m_plug.isLocked()

    def set_plug_keyable(self, plug, value):
        mc.setAttr(plug.name, keyable=value)

    def get_plug_keyable(self, plug):
        return mc.getAttr(plug.name, keyable=True)

    def set_plug_locked(self, plug, value):
        mc.setAttr(plug.name, lock=value)

    def get_plug_hidden(self, plug):
        return mc.getAttr(plug.name, keyable=True)

    def set_plug_hidden(self, plug, value):
        if value is True:
            mc.setAttr(plug.name, keyable=False, channelBox=False)
        else:
            mc.setAttr(plug.name, keyable=True)

    def set_plug_value(self, plug, value):
        ptl.set_plug_value(plug, value)

    def get_plug_value(self, plug, *args):
        return ptl.get_plug_value(plug)

    def get_next_avaliable_plug_index(self, plug):
        return ptl.get_next_avaliable_plug_index(plug)

    def get_next_blendshape_weight_index(self, blendshape_name):
        node_functions = om.MFnDependencyNode(self.get_m_object(blendshape_name))
        m_attribute = node_functions.attribute('weight')
        weights_m_plug = node_functions.findPlug(m_attribute, False)
        return self.get_next_avaliable_plug_index(weights_m_plug)

    def listHistory(self, *args, **kwargs):
        return mc.listHistory(*args, **kwargs)

    def list_deformers(self, *args, **kwargs):
        return mc.ls(
            mc.listHistory(
                *args,
                il=2,
                pdo=True
            ),
            typ='geometryFilter'
        )

    def hide(self, *objects):
        mc.hide(*objects)

    def showHidden(self, *objects):
        mc.showHidden(*objects)

    def parent(self, *args, **kwargs):
        mc.parent(*args, **kwargs)

    def move(self, *args, **kwargs):
        return mc.move(*args, **kwargs)

    def rename(self, *args, **kwargs):
        return mc.rename(*args, **kwargs)

    def renameAttr(self, *args, **kwargs):
        return mc.renameAttr(*args, **kwargs)

    def get_m_object(self, node_name):
        if isinstance(node_name, om.MObject):
            return node_name
        selection_list = om.MSelectionList()
        selection_list.add(node_name)
        m_object = om.MObject()
        selection_list.getDependNode(0, m_object)
        return m_object

    def create_loft_ribbon(self, positions, vector, parent, degree=2):
        return rtl.create_loft_ribbon(positions, vector, parent, degree=degree)

    def create_extrude_ribbon(self, positions, vector, parent, degree=2):
        return rtl.create_extrude_ribbon(positions, vector, parent, degree=degree)

    def get_m_object_type(self, m_object):
        dependency_node = om.MFnDependencyNode(m_object)
        return str(dependency_node.typeName())

    def is_dag_node(self, m_object):
        if 'dagNode' in mc.nodeType(self.get_selection_string(m_object), inherited=True):
            return True
        return False

    def nodeType(self, *args, **kwargs):
        return mc.nodeType(*args, **kwargs)

    def xform(self, *args, **kwargs):
        return mc.xform(*args, **kwargs)

    def assign_shading_group(self, shading_group_name, *node_names):
        for node_name in node_names:
            mc.sets(
                node_name,
                e=True,
                forceElement=shading_group_name
            )

    def sets(self, *args, **kwargs):
        mc.sets(*args, **kwargs)

    def deleteAttr(self, plug, **kwargs):
        mc.deleteAttr(plug, **kwargs)

    def listAttr(self, *args, **kwargs):
        return mc.listAttr(*args, **kwargs)

    def ls(self, *args, **kwargs):
        return mc.ls(*args, **kwargs)

    def file(self, *args, **kwargs):
        return mc.file(*args, **kwargs)

    def keyTangent(self, *args, **kwargs):
        return mc.keyTangent(*args, **kwargs)

    def setDrivenKeyframe(self, *args, **kwargs):
        return mc.setDrivenKeyframe(*args, **kwargs)

    def parentConstraint(self, *args, **kwargs):
        return mc.parentConstraint(*args, **kwargs)

    def orientConstraint(self, *args, **kwargs):
        return mc.orientConstraint(*args, **kwargs)

    def pointConstraint(self, *args, **kwargs):
        return mc.pointConstraint(*args, **kwargs)

    def scaleConstraint(self, *args, **kwargs):
        return mc.scaleConstraint(*args, **kwargs)

    def aimConstraint(self, *args, **kwargs):
        return mc.aimConstraint(*args, **kwargs)

    def setKeyframe(self, *args, **kwargs):
        return mc.setKeyframe(*args, **kwargs)

    def get_curve_data(self, node):
        return ctl.get_shape_data(node)

    def get_curve_cv_positions(self, node):
        return ctl.get_curve_cv_positions(node)

    def get_surface_data(self, node):
        return ctl.get_surface_shape_data(node)

    def update_surface(self, surface):
        om.MFnNurbsSurface(surface).updateSurface()

    def listRelatives(self, *args, **kwargs):
        return mc.listRelatives(*args, **kwargs)

    @check_simple_args
    def addAttr(self, *args, **kwargs):
        return mc.addAttr(*args, **kwargs)

    def get_selected_mesh_names(self):
        mesh_names = [self.get_selection_string(x) for x in self.get_selected_mesh_objects()]
        mesh_transforms = [mc.listRelatives(x, p=True)[0] for x in mesh_names]
        valid_mesh_names = []
        for transform in mesh_transforms:
            mesh_children = mc.listRelatives(transform, c=True, type='mesh')
            if mesh_children:
                meshs = [x for x in mesh_children if not mc.getAttr('%s.intermediateObject' % x)]
                if len(meshs) == 1:
                    valid_mesh_names.append(meshs[0])
        return valid_mesh_names

    def get_selected_nurbs_surface_names(self):
        surface_names = [self.get_selection_string(x) for x in self.get_selected_nurbs_surface_objects()]
        surface_transforms = [mc.listRelatives(x, p=True)[0] for x in surface_names]
        valid_surface_names = []
        for transform in surface_transforms:
            surface_children = mc.listRelatives(transform, c=True, type='nurbsSurface')
            if surface_children:
                surfaces = [x for x in surface_children if not mc.getAttr('%s.intermediateObject' % x)]
                if len(surfaces) == 1:
                    valid_surface_names.append(surfaces[0])
        return valid_surface_names

    def get_selected_nurbs_curve_names(self):
        curve_names = [self.get_selection_string(x) for x in self.get_selected_nurbs_curve_objects()]
        surface_transforms = [mc.listRelatives(x, p=True)[0] for x in curve_names]
        valid_surface_names = []
        for transform in surface_transforms:
            curve_children = mc.listRelatives(transform, c=True, type='nurbsCurve')
            if curve_children:
                surfaces = [x for x in curve_children if not mc.getAttr('%s.intermediateObject' % x)]
                if len(surfaces) == 1:
                    valid_surface_names.append(surfaces[0])
        return valid_surface_names

    def convert_selection(self, **kwargs):
        mc.select(mc.polyListComponentConversion(mc.ls(sl=1), **kwargs))

    def namespace(self, *args, **kwargs):
        return mc.namespace(*args, **kwargs)

    def namespaceInfo(self, *args, **kwargs):
        return mc.namespaceInfo(*args, **kwargs)

    def refresh(self, *args, **kwargs):
        return mc.refresh(*args, **kwargs)

    def dg_dirty(self):
        mel.eval('dgdirty -a')

    def dgdirty(self, *args, **kwargs):
        mc.dgdirty(*args, **kwargs)

    @check_simple_args
    def dgeval(self, nodes_or_attributes):
        """ Refresh only the specified node(s) or attribute(s)
        Eg. refresh an output mesh plug to ensure the node retains shape data after being disconnected """
        mc.dgeval(nodes_or_attributes)

    def lock_node(self, *nodes, **kwargs):
        mc.lockNode(*nodes, **kwargs)

    def lockNode(self, *nodes, **kwargs):
        mc.lockNode(*nodes, **kwargs)

    def set_deformer_weights(self, m_deformer, weights):
        dtl.set_deformer_weights(m_deformer, weights)

    def set_deformer_mesh_weights(self, deformer, mesh, weights):
        dtl.set_deformer_mesh_weights(
            self.get_m_object(deformer),
            mesh,
            weights
        )

    def get_deformer_mesh_weights(self, deformer, mesh):
        return dtl.get_deformer_mesh_weights(
            self.get_m_object(deformer),
            mesh
        )

    def get_deformer_weights(self, m_deformer, precision=None, skip_if_default_weights=False):
        return dtl.get_deformer_weights(
            m_deformer, precision=precision, skip_if_default_weights=skip_if_default_weights)

    def get_deformer_members(self, m_deformer, object_if_all_points=False):
        return dtl.get_deformer_members(m_deformer, object_if_all_points=object_if_all_points)

    def set_deformer_members(self, m_deformer, members):
        return dtl.set_deformer_members(m_deformer, members)

    def add_deformer_members(self, m_deformer, members):
        return dtl.add_deformer_members(m_deformer, members)

    def create_nonlinear_deformer(self, deformer_type, geometry, **kwargs):
        return ntl.create_nonlinear_deformer(deformer_type, geometry, **kwargs)

    @staticmethod
    def get_animcurve_data(driven_plug_name, tolerance=0.00001):
        """
        Get data for create_animcurve_from_data

        driven_plug: can be an animcurve instead of a driven attribute
        """

        # Get the points and tangents from the given animCurve or driven attribute
        key_coords = mc.keyframe(driven_plug_name, q=1, floatChange=True, valueChange=True)
        key_tangents = mc.keyTangent(driven_plug_name, q=1, ix=True, iy=True, ox=True, oy=True)
        curve_data = []
        for i in range(mc.keyframe(driven_plug_name, q=1, keyframeCount=True)):
            pt_x, pt_y = key_coords[i * 2: i * 2 + 2]
            in_tangent_x, out_tangent_x, in_tangent_y, out_tangent_y = key_tangents[i * 4: i * 4 + 4]
            if abs(in_tangent_x - out_tangent_x) > tolerance or abs(in_tangent_y - out_tangent_y) > tolerance:
                raise TypeError("Key {} has broken tangents, but this code only saves one tangent!".format(i))
            curve_data.append(((round(pt_x, 6), round(pt_y, 6)), (round(out_tangent_x, 6), round(out_tangent_y, 6))))

        return curve_data

    @staticmethod
    def create_animcurve_from_data(driver_plug_name, driven_plug_name, curve_data, subrange=None):
        """
        Plot the given points and tangents on an animcurve node (driven key, not time based)

        driven_plug: can be an animcurve instead - in which case, driver_plug is ignored (use animcurve as arg for both)
        subrange: If specified eg. (range_min, range_max), the data is scaled to fit between these values,
         assuming the initial range is 0.0 to 1.0

        # TODO: put as a util somewhere
        """
        if subrange:
            range_min, range_max = subrange
            range_width = range_max - range_min

        # Check for a provided animCurve, otherwise use driver and driven plugs
        animcurve = None
        if '.' not in driven_plug_name and mc.objectType(driven_plug_name).startswith('animCurveU'):
            animcurve = driven_plug_name

        # Create an animCurve with the given points and tangents
        for i, ((point_x, point_y), (tangent_x, tangent_y)) in enumerate(curve_data):
            if subrange:
                point_x = point_x * range_width + range_min
                tangent_x *= range_width

            if animcurve:
                mc.setKeyframe(
                    animcurve,
                    f=point_x, value=point_y,
                    inTangentType="spline", outTangentType="spline")

            else:
                mc.setDrivenKeyframe(
                    driven_plug_name, cd=driver_plug_name,
                    driverValue=point_x, value=point_y,
                    inTangentType="spline", outTangentType="spline")
            mc.keyTangent(
                driven_plug_name, e=1,
                index=(i, i),
                ix=tangent_x, iy=tangent_y, ox=tangent_x, oy=tangent_y)

        return animcurve or mc.listConnections(driven_plug_name, d=False)[0]

    @check_simple_args
    def copy_key(self, *args, **kwargs):
        """ Maya key clipboard """
        mc.copyKey(*args, **kwargs)

    @check_simple_args
    def paste_key(self, *args, **kwargs):
        """ Maya key clipboard """
        mc.pasteKey(*args, **kwargs)

    def add_deformer_geometry(self, deformer, geometry):
        dtl.add_deformer_members(deformer, geometry)

    def remove_deformer_geometry(self, deformer, geometry):
        dtl.remove_deformer_geometry(deformer, geometry)

    def find_skin_cluster(self, node):
        for history_node in mc.listHistory(self.get_selection_string(node)):
            if mc.nodeType(history_node) == 'skinCluster':
                return self.get_m_object(history_node)

    def find_skin_clusters(self, node):
        geometry_name = self.get_selection_string(node)
        skin_clusters = []
        for history_node in mc.listHistory(geometry_name, ):
            if mc.nodeType(history_node) == 'skinCluster':
                get_skin = mc.skinCluster(history_node, q=True, geometry=True)
                if get_skin:
                    if geometry_name in get_skin:
                        skin_clusters.append(history_node)
        return skin_clusters

    def get_skin_weights(self, node, precision=None):
        return sss.getWeights(node, precision)

    def get_skin_blend_weights(self, node, precision=None):
        return sss.get_skin_blend_weights(node, precision)

    def set_skin_blend_weights(self, node, weights):
        return sss.set_skin_blend_weights(node, weights)

    #
    # def set_skin_weights(self, node, weights):
    #     return sss.setWeights(node, weights)

    def get_skin_influences(self, node):
        return sss.get_skin_influences(node)

    def set_skin_as(self, skin, target_mesh):
        return sss.skin_as(skin, target_mesh)

    @flatten_args
    def skinCluster(self, *args, **kwargs):
        return mc.skinCluster(*[str(x) for x in args], **kwargs)

    def skinPercent(self, *args, **kwargs):
        return mc.skinPercent(*[str(x) for x in args], **kwargs)

    @flatten_args
    def rebuildSurface(self, *args, **kwargs):
        return mc.rebuildSurface(*[str(x) for x in args], **kwargs)

    def create_corrective_geometry(self, *args, **kwargs):
        return mtl.create_corrective_geometry(*args, **kwargs)

    def get_closest_vertex_index(self, mesh, point):
        return mtl.get_closest_vertex_index(mesh, om.MPoint(*point))

    def get_closest_vertex_uv(self, mesh, point):
        return mtl.get_closest_vertex_uv(mesh, om.MPoint(*point))

    def get_closest_face_index(self, mesh, position):
        return mtl.get_closest_face_index(mesh, position)

    def get_vertex_count(self, mesh):
        return mtl.get_vertex_count(mesh)

    def get_vertex_positions(self, mesh):
        return mtl.get_vertex_positions(mesh)

    def get_closest_face_center_point(self, mesh):
        return mtl.get_closest_face_center_point(mesh)

    def get_meshs(self, node_name):
        return mtl.get_meshs(node_name)

    def create_shard_mesh(self, mesh_name, parent_m_object):
        if not mesh_name:
            raise Exception('you must provide a name for the mesh')
        return mtl.create_shard_mesh(mesh_name, parent_m_object)

    def get_blendshape_weights(self, *args, **kwargs):
        btl.get_blendshape_weights(*args, **kwargs)

    def set_blendshape_weights(self, *args, **kwargs):
        btl.set_blendshape_weights(*args, **kwargs)

    def flip_blendshape_weights(self, *args, **kwargs):
        btl.flip_blend_shape_weights(*args, **kwargs)

    def get_blendshape_target_index_list(self, blendshape, mesh, index):
        funcs = oma.MFnBlendShapeDeformer(blendshape)
        result = om.MIntArray()
        funcs.targetItemIndexList(index, mesh, result)
        return [result[x] for x in range(result.length())]

    def get_blendshape_weight_index_list(self, blendshape):
        funcs = oma.MFnBlendShapeDeformer(blendshape)
        result = om.MIntArray()
        funcs.weightIndexList(result)
        return [result[x] for x in range(result.length())]

    def create_blendshape(self, mesh_name, **kwargs):
        return btl.create_blendshape(mesh_name, **kwargs)

    def copy_vertex_positions(self, source_mesh, destination_mesh):
        points = om.MPointArray()
        om.MFnMesh(source_mesh).getPoints(points)
        om.MFnMesh(destination_mesh).setPoints(points)
        # assert source_iterator.count() == destination_iterator.count()
        # while not source_iterator.isDone():
        #     destination_iterator.setPosition(source_iterator.position(om.MSpace.kObject))
        #     source_iterator.next()
        #     destination_iterator.next()
        #

    def create_parallel_blendshape(self, mesh_name, **kwargs):
        return btl.create_parallel_blendshape(mesh_name, **kwargs)

    def add_blendshape_base_geometry(self, blendshape, *geometry):
        return btl.add_base_geometry(blendshape, *geometry)

    def create_blendshape_target(self, *args, **kwargs):
        btl.add_target(*args, **kwargs)

    def remove_blendshape_target(self, *args):
        btl.remove_target(*args)

    def remove_blendshape_group(self, *args):
        btl.remove_group(*args)

    def removeMultiInstance(self, *args, **kwargs):
        mc.removeMultiInstance(*args, **kwargs)

    def clear_blendshape_group_targets(self, *args):
        btl.clear_group_targets(*args)

    def clear_blendshape_targets(self, *args):
        btl.clear_targets(*args)

    def list_selected_vertices(self):
        component_selection = mc.filterExpand(sm=(31, 32, 34))
        if component_selection:
            return mc.ls(mc.polyListComponentConversion(
                component_selection,
                toVertex=True),
                fl=True
            )
        return []

    def polyListComponentConversion(self, *args, **kwargs):
        return mc.polyListComponentConversion(*args, **kwargs)

    def get_selected_mesh_objects(self):
        return mtl.get_selected_mesh_objects()

    def get_selected_nurbs_surface_objects(self):
        return nsl.get_selected_nurbs_surface_objects()

    def get_nurbs_surface_objects(self, x):
        return nsl.get_nurbs_surface_objects(x)

    def get_selected_nurbs_curve_objects(self):
        return ncu.get_selected_nurbs_curve_objects()

    def get_nurbs_curve_objects(self, x):
        return ncu.get_nurbs_curve_objects(x)

    def get_selected_transform_names(self):
        return stl.get_selected_transform_names()

    def get_selected_joint_names(self):
        return stl.get_selected_joint_names()

    def get_selected_transforms(self):
        return stl.get_selected_transforms()

    def get_mesh_objects(self, x):
        return mtl.get_mesh_objects(x)

    def get_mesh_points(self, mesh_name):
        mesh_iterator = om.MItMeshVertex(om.MDagPath.getAPathTo(self.get_m_object(mesh_name)))
        point_count = mesh_iterator.count()
        vectors = om.MVectorArray()
        for i in range(point_count):
            vectors.append(om.MVector(mesh_iterator.position(om.MSpace.kWorld)))
            mesh_iterator.next()
        return vectors

    def update_mesh(self, mesh):
        mesh_functions = om.MFnMesh(self.get_m_object(mesh))
        mesh_functions.updateSurface()

    def copy_mesh_in_place(self, source_mesh, target_mesh):
        mesh_functions_2 = om.MFnMesh(self.get_m_object(target_mesh))
        mesh_functions_2.copyInPlace(self.get_m_object(source_mesh))
        mesh_functions_2.updateSurface()

    def copy_mesh_from_plug(self, plug, mesh):
        plug_m_object = plug.asMObject()
        mf = om.MFnMesh(mesh)
        mf.copyInPlace(plug_m_object)
        mf.updateSurface()

    @m_object_args
    def copy_mesh(self, mesh, parent_transform):
        mesh = om.MFnMesh().copy(mesh, parent_transform)
        mesh_functions = om.MFnMesh(mesh)
        mesh_functions.updateSurface()
        return mesh

    def copy_mesh_by_name(self, mesh, parent_transform, name=None):
        """
        This is temporary untill i refactor copy_mesh  -pax
        """
        mesh = om.MFnMesh().copy(self.get_m_object(mesh), self.get_m_object(parent_transform))
        mesh_name = self.get_selection_string(mesh)
        if name:
            mesh_name = mc.rename(mesh_name, name)
        mesh_functions = om.MFnMesh(mesh)
        mesh_functions.updateSurface()
        return mesh_name

    def get_skin_data(self, node, precision=4):
        node_name = self.get_selection_string(node)
        return dict(
            geometry=mc.skinCluster(node_name, geometry=True, q=True)[0],
            method=mc.skinCluster(node_name, skinMethod=True, q=True),
            joints=mc.skinCluster(node_name, influence=True, q=True),
            weights=self.get_skin_weights(node_name, precision),
            blend_weights=self.get_skin_blend_weights(node_name, precision)

        )

    def remove_deformer(self, deformer, geometry):
        return mc.deformer(deformer, e=True, rm=True, g=geometry)

    def get_delta_mush_nodes(self, *geometry):
        return dmu.get_delta_mush_nodes(*geometry)

    def create_delta_mush(self, data, namespace=None):
        return dmu.create_delta_mush(data, namespace=namespace)

    def get_delta_mush_data(self, delta_mush_node, precision=None):
        return dmu.get_delta_mush_data(delta_mush_node, precision=precision)

    def find_deformer_node(self, *args, **kwargs):
        return dtl.find_deformer_node(*args, **kwargs)

    def find_deformer_nodes(self, *args, **kwargs):
        return dtl.find_deformer_nodes(*args, **kwargs)

    def get_wrap_data(self, node):
        return wru.get_wrap_data(node)

    def create_wrap(self, data, namespace=None):
        return wru.create_wrap(data, namespace=namespace)

    def get_cvwrap_data(self, node):
        return cvw.get_cvwrap_data(node)

    def create_cvwrap(self, data, namespace=None):
        return cvw.create_cvwrap(data, namespace=namespace)

    def export_alembic(self, path, *roots):
        self.loadPlugin('AbcExport')
        mc.AbcExport(j="-writeUVSets -frameRange 1 1 %s -file %s" % (
            ' '.join(['-root %s' % x for x in roots]),
            path,

        ))

    def AbcImport(self, path, **kwargs):
        kwargs.setdefault('mode', 'import')
        self.loadPlugin('AbcImport')
        mc.AbcImport(
            path,
            **kwargs
        )

    def AbcExport(self, path, *roots):
        self.loadPlugin('AbcExport')
        mc.AbcExport(j="-writeUVSets -fitTimeRange %s -file %s" % (
            ' '.join(['-root %s' % x for x in roots]),
            path,

        ))

    def polyReduce(self, *args, **kwargs):
        return mc.polyReduce(args, **kwargs)

    def import_geometry(self, path, namespace=None):

        if not os.path.exists(path):
            raise IOError('Geometry file does not exist: %s' % path)
        current_namespace = mc.namespaceInfo(currentNamespace=True)
        if not current_namespace == ':':
            current_namespace = ':%s' % current_namespace
        if not namespace:
            namespace = 'IMPORTGEOMETRY'

        if not mc.namespace(exists=':%s' % namespace):
            mc.namespace(add=':%s' % namespace)
        mc.namespace(set=':%s' % namespace)
        if path.endswith('.abc'):
            self.loadPlugin('AbcImport')
            mc.AbcImport(
                path,
                mode='import'
            )
        elif path.endswith('.ma'):
            if not os.environ.get('DO_NOT_LOAD_ARNOLD', False):
                mc.file(
                    path,
                    i=True,
                    type="mayaAscii",
                    ignoreVersion=True,
                    mergeNamespacesOnClash=False,
                    rpr="CLASHING_NODE_NAME",
                    options="v=0;p=17;f=0",
                    importTimeRange="override",
                    importFrameRate=True
                )
        elif path.endswith('.mb'):
            if not os.environ.get('DO_NOT_LOAD_ARNOLD', False):
                mc.file(
                    path,
                    i=True,
                    type="mayaBinary",
                    ignoreVersion=True,
                    mergeNamespacesOnClash=False,
                    rpr="CLASHING_NODE_NAME",
                    options="v=0;p=17;f=0",
                    importTimeRange="override",
                    importFrameRate=True
                )
        else:
            raise Exception('Invalid file type "%s"' % path.split('.')[-1])
        mc.namespace(set=current_namespace)
        assemblies = mc.ls('%s:*' % namespace, assemblies=True) or []
        root_m_objects = [self.get_m_object(x) for x in assemblies]
        return [self.get_selection_string(x) for x in root_m_objects]

    def remove_namespace(self, name_space):
        if mc.namespace(exists=':%s' % name_space):
            mc.namespace(rm=':%s' % name_space, mergeNamespaceWithParent=True)

    def create_from_skin_data(self, data):
        existing_skin = mel.eval('findRelatedSkinCluster %s' % data['geometry'])
        method = data.get('method', None)
        if existing_skin:
            logging.getLogger('rig_build').warning(
                'Found existing skin on %s. attempting do delete the old skin: %s' % (
                    data['geometry'],
                    existing_skin
                )
            )
            mc.skinCluster(data['geometry'], e=True, ub=True)
            if mc.objExists(existing_skin):
                raise Exception('Unable to delete existing skin: %s' % data['geometry'])
        skin_name = mc.skinCluster(
            data['geometry'],
            data['joints'],
            tsb=True
        )[0]
        if method is not None:
            mc.skinCluster(skin_name, edit=1, skinMethod=method)

        new_skin_name = data['geometry'].replace('Shape', '') + '_Skn'

        # rename skincluster
        skin_name = mc.rename(
            skin_name,
            new_skin_name
        )

        m_object = self.get_m_object(skin_name)
        weights = data.get('weights', None)
        blend_weights = data.get('blend_weights', None)
        if weights:
            # TEMP UNTILL WE SWITCH OVER TO NEW WEIGHT FORMAT

            self.set_skin_weights(skin_name, weights)

        if blend_weights:
            sss.set_skin_blend_weights(skin_name, blend_weights)

        return m_object

    def set_skin_weights(self, skin_name, weights):
        geometry = mc.skinCluster(skin_name, q=True, geometry=True)
        influences = mc.skinCluster(skin_name, q=True, influence=True)
        if geometry:
            for itr in range(len(geometry)):
                # poly mesh and skinCluster name
                shapeName = geometry[itr]
                # unlock influences used by skincluster
                for influence in influences:
                    mc.setAttr('%s.liw' % influence, False)
                # normalize needs turned off for the prune to work
                skinNorm = mc.getAttr('%s.normalizeWeights' % skin_name)
                if skinNorm != 0:
                    mc.setAttr('%s.normalizeWeights' % skin_name, 0)
                mc.skinPercent(skin_name, shapeName, nrm=False, prw=100)
                # restore normalize setting
                if skinNorm != 0:
                    mc.setAttr('%s.normalizeWeights' % skin_name, skinNorm)
                for vertId, weightData in weights[itr].items():
                    wlAttr = '%s.weightList[%s]' % (skin_name, vertId)
                    for infIndex, infValue in weightData.items():
                        wAttr = '.weights[%s]' % infIndex
                        mc.setAttr(wlAttr + wAttr, infValue)

    def find_related_skin_cluster(self, geometry_name):
        existing_skin = mel.eval('findRelatedSkinCluster %s' % geometry_name)
        if existing_skin:
            return existing_skin

    def get_selected_vertex_indices(self, *args):
        return mtl.get_selected_vertex_indices(*args)

    def get_key_value(self, animation_curve, in_value):
        anim_curve_functions = oma.MFnAnimCurve(animation_curve)
        index_utility = om.MScriptUtil()
        index_utility.createFromInt(0)
        index_pointer = index_utility.asUintPtr()
        anim_curve_functions.find(in_value, index_pointer)
        index = om.MScriptUtil.getUint(index_pointer)
        return anim_curve_functions.value(index)

    def get_animation_curve_value_at_index(self, animation_curve, current_in_value):
        return atl.get_value_at_index(
            animation_curve,
            current_in_value
        )

    def change_keyframe(self, animation_curve, current_in_value, **kwargs):
        atl.change_keyframe(animation_curve, current_in_value, **kwargs)

    def delete_keyframe(self, animation_curve, in_value):
        atl.delete_keyframe(animation_curve, in_value)

    def add_keyframe(self, animation_curve, in_value, out_value, **kwargs):
        atl.add_keyframe(animation_curve, in_value, out_value, **kwargs)

    def selectKey(self, *args, **kwargs):
        mc.selectKey(*args, **kwargs)

    def cutKey(self, *args, **kwargs):
        return mc.cutKey(*args, **kwargs)

    def aliasAttr(self, *args, **kwargs):
        return mc.aliasAttr(*args, **kwargs)

    def create_animation_curve(self, m_plug, **kwargs):
        return atl.create_animation_curve(m_plug, **kwargs)

    def create_dag_node(self, *args):
        return om.MFnDagNode().create(*args)

    def create_depend_node(self, *args):
        return om.MFnDependencyNode().create(*args)

    def create_keyframe(self, curve, *args):
        animation_curve = oma.MFnAnimCurve(curve)
        animation_curve.addKey(*args)

    def create_ik_handle(self, start_joint, end_effector, solver='ikSCsolver', name=None, parent=None):
        return itl.create_ik_handle(
            start_joint,
            end_effector,
            solver=solver,
            name=name.split(':'),
            parent=parent
        )

    def get_constrained_node(self, constraint):
        constraint_string = constraint
        constraint_type = self.nodeType(constraint_string)

        if constraint_type == 'pointConstraint':
            out_attributes = [
                'constraintTranslateX', 'constraintTranslateY', 'constraintTranslateZ'
            ]
        elif constraint_type == 'parentConstraint':
            out_attributes = [
                'constraintTranslateX', 'constraintTranslateY', 'constraintTranslateZ',
                'constraintRotateX', 'constraintRotateY', 'constraintRotateZ'
            ]
        elif constraint_type == 'orientConstraint':
            out_attributes = [
                'constraintRotateX', 'constraintRotateY', 'constraintRotateZ'
            ]
        elif constraint_type == 'scaleConstraint':
            out_attributes = [
                'constraintScaleX', 'constraintScaleY', 'constraintScaleZ'
            ]
        elif constraint_type == 'aimConstraint':
            out_attributes = [
                'constraintRotateX', 'constraintRotateY', 'constraintRotateZ'
            ]
        elif constraint_type == 'geometryConstraint':
            out_attributes = [
                'constraintGeometry'
            ]

        else:
            raise Exception('Unsupported constraint type "%s"' % constraint_type)

        connected_nodes = set()
        for attribute in out_attributes:
            nodes = self.listConnections('%s.%s' % (constraint_string, attribute), d=True, s=False, scn=True, p=False)
            if nodes:
                connected_nodes.update(nodes)

        if len(connected_nodes) > 1:
            raise Exception('Multiple constrained nodes not supported.')

        if len(connected_nodes) < 1:
            raise Exception('No node was controlled by the constraint')

        return list(connected_nodes)[0]

    # @m_object_arg
    def get_constraint_data(self, constraint):
        """Queries the info related to a constraint object inside a Maya scene.

        Args:
            constraint (str): The name of a constraint object.

        Returns:
            dict: A dictionary containing the following info:

            dict = {
                    name: (str) constraint_object_name,

                    constraint_type: (str) constraint_type ('parentConstraint', 'pointConstraint'...),

                    mo: (bool) maintain_offset,

                    target_list: (list) list of targets names as strings,

                    constrained_node: (str) driven_object_name,

                    parent: (str) constraint_parent_node

                    interpType: (int) Only for parent and orient constraints, this gets their interpolation type
                                 according to the enum value.
                                 (0 = No flip, 1 = Average, 2 = Shortest, 3 = Longest, 4 = Cache)

                    worldUpType: (int) For aim constraints. Int that matches the worldUp type attr.

                    worldUpVector: (list) For aim constraints. A list containing a 3-floats tuple describing a vector.

                    upVector: (list) For aim constraints. A list containing a 3-floats tuple describing the vector.

                    aimVector: (list) For aim constraints. A list containing a 3-floats tuple describing the vector.
                    }
        """
        # consraint_name = self.get_selection_string(constraint)
        consraint_name = constraint
        constraint_type = self.nodeType(consraint_name)
        parent = None
        get_parent = mc.listRelatives(consraint_name, p=True)
        if get_parent:
            parent = get_parent[0]
        if constraint_type == 'pointConstraint':
            return dict(
                name=consraint_name,
                constraint_type=constraint_type,
                mo=True,
                target_list=mc.pointConstraint(consraint_name, q=True, tl=True),
                constrained_node=self.get_constrained_node(constraint),
                parent=parent
            )
        elif constraint_type == 'parentConstraint':
            return dict(
                name=consraint_name,
                constraint_type=constraint_type,
                mo=True,
                target_list=mc.parentConstraint(consraint_name, q=True, tl=True),
                constrained_node=self.get_constrained_node(constraint),
                interpType=mc.getAttr(consraint_name + '.interpType'),
                parent=parent
            )
        elif constraint_type == 'orientConstraint':
            return dict(
                name=consraint_name,
                constraint_type=constraint_type,
                mo=True,
                target_list=mc.orientConstraint(consraint_name, q=True, tl=True),
                constrained_node=self.get_constrained_node(constraint),
                interpType=mc.getAttr(consraint_name + '.interpType'),
                parent=parent
            )
        elif constraint_type == 'scaleConstraint':
            return dict(
                name=consraint_name,
                constraint_type=constraint_type,
                mo=True,
                target_list=mc.scaleConstraint(consraint_name, q=True, tl=True),
                interpType=None,
                constrained_node=self.get_constrained_node(constraint),
                parent=parent
            )
        elif constraint_type == 'geometryConstraint':
            return dict(
                name=consraint_name,
                constraint_type=constraint_type,
                target_list=mc.geometryConstraint(consraint_name, q=True, tl=True),
                interpType=None,
                constrained_node=self.get_constrained_node(constraint),
                parent=parent
            )
        elif constraint_type == 'aimConstraint':

            data = dict(
                name=consraint_name,
                constraint_type=constraint_type,
                mo=True,
                target_list=mc.aimConstraint(consraint_name, q=True, tl=True),
                interpType=None,
                constrained_node=self.get_constrained_node(constraint),
                worldUpType=mc.getAttr('%s.worldUpType' % consraint_name),
                worldUpVector=mc.getAttr('%s.worldUpVector' % consraint_name)[0],
                upVector=mc.getAttr('%s.upVector' % consraint_name)[0],
                aimVector=mc.getAttr('%s.aimVector' % consraint_name)[0],
                parent=parent
            )

            connected = mc.listConnections(
                '%s.worldUpMatrix' % consraint_name,
                s=True,
                d=False,
                scn=True,
                plugs=False
            )
            if connected:
                data['worldUpObject'] = connected[0]
            return data

        else:
            self.logger.info('Warning: Constraint type "%s" not supported. skipping...' % constraint_type)

    def create_constraint(self, constraint_type, *transforms, **kwargs):
        """Handles the constraint creation. It picks the type of constraint and calls methods to set its attributes.

        Args:
            constraint_type: (str) The type of constraint.

            *transforms: (list) A list of transform objects.

            **kwargs: (list) A list of parameters related to the constraint creation and behaviour settings. You can
                find an example on the *get_constraint_data* method.

        Returns:
            The created constraint Maya object.

        """
        name = kwargs.pop('name', None)
        parent = kwargs.pop('parent', None)
        interpolation_type = kwargs.pop('interpType', None)
        targets = [self.get_selection_string(x) for x in transforms]
        clean_kwargs = dict()

        for key in kwargs:
            clean_kwargs[str(key)] = kwargs[key]
        short_name = mc.__dict__[constraint_type](
            *targets,
            **clean_kwargs
        )[-1]
        long_names = mc.ls(short_name, long=True)
        constraint_name = long_names[-1]
        m_object = self.get_m_object(constraint_name)
        constraint_name = mc.rename(constraint_name, name)
        if parent:
            parent_name = self.get_selection_string(parent)
            get_parents = mc.listRelatives(constraint_name, p=True)
            if get_parents is None or get_parents[0] != parent_name:
                mc.parent(
                    constraint_name,
                    parent_name
                )
        if interpolation_type:
            mc.setAttr(constraint_name + '.interpType', interpolation_type)

        return m_object

    @staticmethod
    def draw_nurbs_surface(positions, knots_u, knots_v, degree_u, degree_v, form_u, form_v, name, parent):
        create_2d = False
        rational = False
        point_array = om.MPointArray()
        knots_array_u = om.MDoubleArray()
        knots_array_v = om.MDoubleArray()
        for p in positions:
            point_array.append(om.MPoint(*p))
        for k in knots_u:
            knots_array_u.append(k)
        for k in knots_v:
            knots_array_v.append(k)
        args = [
            point_array,
            knots_array_u,
            knots_array_v,
            degree_u,
            degree_v,
            form_u,
            form_v,
            rational,
            parent
        ]
        m_object = om.MFnNurbsSurface().create(*args)
        om.MFnDependencyNode(m_object).setName(name)
        return m_object

    def update_surface_shape(self, surface, positions, knots_u, knots_v, degree_u, degree_v, form_u, form_v):
        """
        FIND A WAY TO DO WITH MAYA API>> THIS IS MESSY

        @param surface:
        @param positions:
        @param knots_u:
        @param knots_v:
        @param degree_u:
        @param degree_v:
        @param form_u:
        @param form_v:
        @return:
        """
        surface_transform = mc.createNode('transform', name='temporary_surface')
        try:
            transform_m_object = self.get_m_object(surface_transform)
            surface_m_object = self.draw_nurbs_surface(
                positions,
                knots_u,
                knots_v,
                degree_u,
                degree_v,
                form_u,
                form_v,
                'temporary_surfaceShape',
                transform_m_object
            )
            temp_surface = self.get_selection_string(surface_m_object)
            target_surface = self.get_selection_string(surface)
            mc.connectAttr(
                '%s.worldSpace[0]' % temp_surface,
                '%s.create' % target_surface
            )
            self.update_surface(surface)
            mc.disconnectAttr(
                '%s.worldSpace[0]' % temp_surface,
                '%s.create' % target_surface
            )
        except Exception as e:
            mc.delete(surface_transform)
            raise e
        mc.delete(surface_transform)

    @staticmethod
    def draw_nurbs_curve(
            positions,
            degree,
            form,
            name,
            parent,
            create_2d=False,
            rational=False
    ):
        spans = len(positions) - degree
        point_array = om.MPointArray()
        knots_array = om.MDoubleArray()
        for p in positions:
            point_array.append(om.MPoint(*p))
        for k in calculate_knots(spans, degree, form):
            knots_array.append(k)
        args = [
            point_array,
            knots_array,
            degree,
            NURBS_CURVE_FORMS[form],
            create_2d,
            rational,
            parent
        ]
        m_object = om.MFnNurbsCurve().create(*args)
        om.MFnDependencyNode(m_object).setName(name)
        return m_object

    def create_shader(self, node_type):
        node_name = mc.shadingNode(
            node_type,
            asShader=True
        )
        return self.get_m_object(node_name)

    def create_shading_group(self, name):
        node_name = mc.sets(
            name=name,
            empty=True,
            renderable=True,
            noSurfaceShader=True
        )
        return self.get_m_object(node_name)

    def connect_plugs(self, plug_1, plug_2):
        graph_modifier = om.MDGModifier()
        graph_modifier.connect(
            plug_1,
            plug_2
        )
        graph_modifier.doIt()

    def disconnect_plugs(self, plug_1, plug_2):
        graph_modifier = om.MDGModifier()
        graph_modifier.disconnect(
            plug_1,
            plug_2
        )
        graph_modifier.doIt()

    @flatten_args
    def get_bounding_box_center(self, *nodes):
        bbox = mc.exactWorldBoundingBox(*[str(x) for x in nodes])
        center_x = (bbox[0] + bbox[3]) / 2.0
        center_y = (bbox[1] + bbox[4]) / 2.0
        center_z = (bbox[2] + bbox[5]) / 2.0
        return round(center_x, 5), round(center_y, 5), round(center_z, 5)

    @flatten_args
    def get_bounding_box_scale(self, *nodes):
        bbox = mc.exactWorldBoundingBox(*[str(x) for x in nodes])
        scale_x = bbox[3] - bbox[0]
        scale_y = bbox[4] - bbox[1]
        scale_z = bbox[5] - bbox[2]
        return round(scale_x, 5), round(scale_y, 5), round(scale_z, 5)

    @flatten_args
    def get_bounding_box(self, *nodes):
        nodes = mc.ls([str(x) for x in nodes])
        if nodes:
            return mc.exactWorldBoundingBox(nodes)
        else:
            return [-1, -1, -1, 1, 1, 1]

    def get_selection_string(self, item):
        if isinstance(item, basestring):
            item = self.get_m_object(item)
        if isinstance(item, om.MObject):
            m_object = item
            selection_list = om.MSelectionList()
            selection_list.add(m_object)
            selection_strings = []
            selection_list.getSelectionStrings(0, selection_strings)
            return selection_strings[0]
        else:
            raise Exception('Cannot get_selection_string for type: "%s"' % type(item))

    def set_xray_panel(self, value):
        panels = mc.getPanel(type='modelPanel')
        if panels:
            for p in panels:
                if value:
                    mc.modelEditor(p, jointXray=True, e=True)
                    mel.eval('setXrayOption true %s' % p)
                else:
                    mel.eval('setXrayOption false %s' % p)
                    mc.modelEditor(p, jointXray=False, e=True)

        else:
            self.logger.info('No panels to isolate')

    def set_xray_joints_panel(self, value):
        panels = mc.getPanel(type='modelPanel')
        if panels:
            for p in panels:
                if value:
                    mel.eval('setXrayOption false %s' % p)
                    mc.modelEditor(p, jointXray=True, e=True)
                else:
                    mel.eval('setXrayOption false %s' % p)
                    mc.modelEditor(p, jointXray=False, e=True)

        else:
            self.logger.info('No panels to isolate')

    def isolate(self, *objects):
        panels = mc.getPanel(type='modelPanel')
        if panels:
            mc.select(*objects)
            for p in panels:
                mel.eval('enableIsolateSelect %s 1' % p)
            # mel.eval('fitPanel - selectedNoChildren;')

        else:
            self.logger.info('No panels to isolate')

    def deisolate(self):
        panels = mc.getPanel(type='modelPanel')
        if panels:
            for p in panels:
                mc.isolateSelect(p, state=0)
        else:
            self.logger.info('No panels to deisolate')

    def get_mirror_mesh_data(self, meshs):
        return mtl.get_mirror_mesh_data(meshs)

    def create_mirrored_geometry(self, *args, **kwargs):
        return mtl.create_mirrored_geometry(*args, **kwargs)

    @m_object_args
    def copy_nurbs_surface(self, surface, parent_transform):
        return om.MFnNurbsSurface().copy(surface, parent_transform)

    @m_object_args
    def copy_nurbs_curve(self, curve, parent_transform):
        return om.MFnNurbsCurve().copy(curve, parent_transform)

    @check_simple_args
    def attributeQuery(self, *args, **kwargs):
        return mc.attributeQuery(*args, **kwargs)

    @check_simple_args
    def getAttr(self, *args, **kwargs):
        return mc.getAttr(*args, **kwargs)

    @check_simple_args
    def setAttr(self, *args, **kwargs):
        return mc.setAttr(*args, **kwargs)

    @check_simple_args
    def objExists(self, *args, **kwargs):
        return mc.objExists(*args, **kwargs)

    @check_simple_args
    def objectType(self, *args, **kwargs):
        return mc.objectType(*args, **kwargs)

    @check_simple_args
    def listConnections(self, *args, **kwargs):
        return mc.listConnections(*args, **kwargs)

    @check_simple_args
    def disconnectAttr(self, *args, **kwargs):
        return mc.disconnectAttr(*args, **kwargs)

    @check_simple_args
    def connectAttr(self, *args, **kwargs):
        return mc.connectAttr(*args, **kwargs)

    def loadPlugin(self, plugin_name):
        if plugin_name not in self.loaded_plugins:
            mc.loadPlugin(plugin_name)
            self.loaded_plugins.append(plugin_name)

    def unloadPlugin(self, *args, **kwargs):
        mc.unloadPlugin(*args, **kwargs)

    def pluginInfo(self, *args, **kwargs):
        mc.pluginInfo(*args, **kwargs)

    def check_visibility(self, node):
        """
        check if obj is a dagNode
        check if obj is visible by...
        --visible attribute of item and it's ancestors
        --item's display layer's visibility
        --checks if panels' Show>Polygons is checked on or off
        """
        visible_status = False
        try:
            if mc.objectType(node, isAType='dagNode'):
                visible_status = mc.getAttr(str(node) + '.visibility')
                if mc.getAttr(str(node) + '.overrideEnabled'):
                    visible_status = visible_status and mc.getAttr(str(node) + '.overrideVisibility')
                if (mc.listRelatives(node, parent=True)[0] is not None) is True:
                    node_parent = mc.listRelatives(node, parent=True)[0]
                    visible_status = visible_status and self.check_visibility(node_parent)
                panels = mc.getPanel(type='modelPanel')
                if panels:
                    panel_polymesh_list = []
                    for panel_name in panels:
                        visible_status = visible_status and mc.modelEditor(panel_name, q=True, polymeshes=True)
                        panel_polymesh_list.append(visible_status)
                    visible_status = visible_status and any(panel_polymesh_list)
        except Exception as e:
            self.logger.error(traceback.format_exc())
        return visible_status

    def lock_all_plugs(self, node, skip=None):
        get_keyable = mc.listAttr(node, keyable=True)
        if get_keyable:
            for attr in get_keyable:
                plug_string = node + '.' + attr
                if not skip or plug_string not in skip:
                    if mc.objExists(plug_string):
                        mc.setAttr(
                            plug_string,
                            lock=True,
                            keyable=False,
                            channelBox=False
                        )

    def warning(self, *args, **kwargs):
        mc.warning(*args, **kwargs)

    def get_user_plugs(self, node):
        attrs = mc.listAttr(node, ud=True) or []
        plugs = [node + '.' + attr for attr in attrs]
        return plugs

    def set_skincluster_influence_weights(self, node, index, weights, **kwargs):
        return sku.set_influence_weights(
            node,
            index,
            weights,
            **kwargs
        )

    def get_skincluster_influence_weights(self, node, index, **kwargs):
        return sku.get_influence_weights(
            node,
            index,
            **kwargs
        )

    def get_skincluster_weights(self, node, **kwargs):
        return sku.get_weights(
            node,
            **kwargs
        )

    def set_skincluster_weights(self, node, weights, **kwargs):
        return sku.set_weights(
            node,
            weights,
            **kwargs
        )

    @staticmethod
    def create_text_curve(*args):
        return ctl.create_text_curve(*args)

    @staticmethod
    def get_closest_curve_parameter(surface, point):
        return ncu.get_closest_point(surface, point)

    @staticmethod
    def get_closest_surface_uv(surface, point):
        return nsl.get_closest_uv(surface, point)

    @staticmethod
    def get_closest_surface_point(surface, point):
        point = nsl.get_closest_point(surface, point)
        return point[0], point[1], point[2]

    @staticmethod
    def get_closest_mesh_uv(mesh, point):
        return mtl.get_closest_mesh_uv(mesh, point)

    def delete_unused_nodes(self):
        mel.eval('MLdeleteUnused()')

    def remove_namespaces(self):
        mc.namespace(setNamespace=':')
        all_namespaces = [x for x in mc.namespaceInfo(listOnlyNamespaces=True, recurse=True) if
                          x != "UI" and x != "shared"]
        if all_namespaces:
            all_namespaces.sort(key=len, reverse=True)
            for namespace in all_namespaces:
                if mc.namespace(exists=namespace) is True:
                    mc.namespace(removeNamespace=namespace, mergeNamespaceWithRoot=True)

    def remove_unused_influences(self, skin):
        allInfluences = mc.skinCluster(skin, q=True, inf=True)
        weightedInfluences = mc.skinCluster(skin, q=True, wi=True)
        if allInfluences and weightedInfluences:
            unusedInfluences = [inf for inf in allInfluences if inf not in weightedInfluences]
            mc.skinCluster(skin, e=True, removeInfluence=unusedInfluences)

    def create_lattice(self, *args, **kwargs):
        return lut.create_lattice(*args, **kwargs)

    def create_softMod(self, softMod_vert, softMod_distance, softMod_falloff):
        return sut.create_softMod(softMod_vert, softMod_distance, softMod_falloff)

    def create_wire_deformer(self, curve, *geometry, **kwargs):
        return wir.create_wire_deformer(curve, *geometry, **kwargs)

    def create_squish_deformer(self, *args, **kwargs):
        return sqt.create_squish_deformer(*args, **kwargs)

    def undoInfo(self, *args, **kwargs):
        mc.undoInfo(*args, **kwargs)

    def create_curve_from_vertices(self, curve_from_surface):

        """
        This can all be done from create function using objects..
        doesnt need to use scene, cmds or OpenMaya
        """
        parent = curve_from_surface.parent
        vertices = curve_from_surface.vertices
        points = [component.split('.')[-1] for component in vertices]
        mesh_name = curve_from_surface.mesh_name

        poly_edge_to_curve_name = mc.createNode('polyEdgeToCurve')
        nurbs_curve_name = mc.createNode('nurbsCurve', parent=parent)

        connections = [
            (
                mesh_name + '.displaySmoothMesh',
                poly_edge_to_curve_name + '.displaySmoothMesh',
            ), (
                mesh_name + '.outMesh',
                poly_edge_to_curve_name + '.inputPolymesh',
            ), (
                mesh_name + '.outSmoothMesh',
                poly_edge_to_curve_name + '.inputSmoothPolymesh',
            ), (
                mesh_name + '.smoothLevel',
                poly_edge_to_curve_name + '.smoothLevel',
            ), (
                mesh_name + '.worldMatrix[0]',
                poly_edge_to_curve_name + '.inputMat',
            ), (
                poly_edge_to_curve_name + '.outputcurve',
                nurbs_curve_name + '.create',
            ),
        ]
        for connection in connections:
            mc.connectAttr(*connection)

        mc.setAttr(
            poly_edge_to_curve_name + '.inputComponents',
            len(points),
            *points,
            type='componentList'
        )

        mc.setAttr(poly_edge_to_curve_name + '.form', curve_from_surface.form)
        mc.setAttr(poly_edge_to_curve_name + '.degree', curve_from_surface.degree)

        m_object = self.get_m_object(nurbs_curve_name)
        construction_history = self.get_m_object(poly_edge_to_curve_name)

        om.MFnDependencyNode(m_object).setName(
            curve_from_surface.name,
        )
        om.MFnDependencyNode(construction_history).setName(
            curve_from_surface.name + 'polyEdgeToCurve',
        )

        curve_from_surface.m_object = m_object
        curve_from_surface.construction_history = [construction_history]

    def createNode(self, *args, **kwargs):
        return mc.createNode(*args, **kwargs)

    def autoKeyframe(self, *args, **kwargs):
        return mc.autoKeyframe(*args, **kwargs)

    def evaluationManager(self, *args, **kwargs):
        return mc.evaluationManager(*args, **kwargs)

    def displaySmoothness(self, *args, **kwargs):
        return mc.displaySmoothness(*args, **kwargs)

    def callbacks(self, *args, **kwargs):
        return mc.callbacks(*args, **kwargs)

    def blendShape(self, *args, **kwargs):
        return mc.blendShape(*args, **kwargs)

    def sculptTarget(self, *args, **kwargs):
        return mc.sculptTarget(*args, **kwargs)

    def setNodeTypeFlag(self, *args, **kwargs):
        return mc.setNodeTypeFlag(*args, **kwargs)

    def update_mesh_deltas(self, *args, **kwargs):
        return mtl.update_mesh_deltas(*args, **kwargs)

    def fitBspline(self, *args, **kwargs):
        return mc.fitBspline(*args, **kwargs)

    def transformLimits(self, *args, **kwargs):
        return mc.transformLimits(*args, **kwargs)

    def reverseSurface(self, *args, **kwargs):
        return mc.reverseSurface(*args, **kwargs)

    def smooth_normals(self, geometries, *args, **kwargs):
        mc.select(geometries)
        mc.polyNormalPerVertex(ufn=True)
        for geo in geometries:
            mc.polySoftEdge(
                geo,
                a=180,
                ch=False
            )

    def get_lattice_point(self, lattice, s, t, u):
        return lut.get_lattice_point(lattice, s, t, u)

    def reset_lattice(self, lattice):
        lut.reset_lattice(lattice)

    def create_weight_constraint(self, *args, **kwargs):
        """
        constraints and sets weights for drivers
        :usage:
            create_weight_constraint(
                'pCube1',
                'pCube2',
                'pSphere',
                type='parentConstraint',
                weights=[0.2, 0.8],
            )

        :param type: type of constraint to create eg: parentConstraint
        :param weights: list of weights
        """
        typ = kwargs.pop('type', 'parentConstraint')
        weights = kwargs.pop('weights')
        cnsCmd = getattr(mc, typ)
        cns = cnsCmd(*args, **kwargs)[0]
        if typ == 'parentConstraint':
            mc.setAttr(cns + '.interpType', 2)
        attrs = cnsCmd(cns, q=True, weightAliasList=True)
        for a, w in zip(attrs, weights):
            mc.setAttr(cns + '.' + a, w)
        return cns

    def label_joints(self):
        for jnt in mc.ls(type='joint'):
            tokens = jnt.split(":")[-1].split("_", 1)

            # if there's no "_" in the name, skip
            if len(tokens) <= 1:
                continue

            # find side and label from name
            side, label = tokens[0], tokens[1]
            side_label = {'L': 1, 'R': 2}.get(side, 0)

            # set joint label attrs
            mc.setAttr(jnt + ".side", side_label)
            mc.setAttr(jnt + ".type", 18)
            mc.setAttr(jnt + ".otherType", label, type="string")

    def window(self, *args, **kwargs):
        return mc.window(*args, **kwargs)

    def deleteUI(self, *args, **kwargs):
        return mc.deleteUI(*args, **kwargs)

    def polyExtrudeEdge(self, *args, **kwargs):
        return mtl.create_poly_extrude_edge(*args, **kwargs)

    def invert_matrix(self, matrix_values):
        """

        :param matrix_values:
        :return:
        """
        matrix = om.MMatrix()
        om.MScriptUtil.setDoubleArray(matrix[0], 0, matrix_values[0])
        om.MScriptUtil.setDoubleArray(matrix[0], 1, matrix_values[1])
        om.MScriptUtil.setDoubleArray(matrix[0], 2, matrix_values[2])
        om.MScriptUtil.setDoubleArray(matrix[0], 3, matrix_values[3])

        om.MScriptUtil.setDoubleArray(matrix[1], 0, matrix_values[4])
        om.MScriptUtil.setDoubleArray(matrix[1], 1, matrix_values[5])
        om.MScriptUtil.setDoubleArray(matrix[1], 2, matrix_values[6])
        om.MScriptUtil.setDoubleArray(matrix[1], 3, matrix_values[7])

        om.MScriptUtil.setDoubleArray(matrix[2], 0, matrix_values[8])
        om.MScriptUtil.setDoubleArray(matrix[2], 1, matrix_values[9])
        om.MScriptUtil.setDoubleArray(matrix[2], 2, matrix_values[10])
        om.MScriptUtil.setDoubleArray(matrix[2], 3, matrix_values[11])

        om.MScriptUtil.setDoubleArray(matrix[3], 0, matrix_values[12])
        om.MScriptUtil.setDoubleArray(matrix[3], 1, matrix_values[13])
        om.MScriptUtil.setDoubleArray(matrix[3], 2, matrix_values[14])
        om.MScriptUtil.setDoubleArray(matrix[3], 3, matrix_values[15])

        inverted_matrix = matrix.inverse()
        matrix_values = []
        for c in range(4):
            for r in range(4):
                matrix_values.append(om.MScriptUtil.getDoubleArrayItem(inverted_matrix[r], c))
        return matrix_values

    def polyEvaluate(self, *args, **kwargs):
        return mc.polyEvaluate(*args, **kwargs)

    def setDrivenKeyframe(self, *args, **kwargs):
        return mc.setDrivenKeyframe(*args, **kwargs)

    def setInfinity(self, *args, **kwargs):
        return mc.setInfinity(*args, **kwargs)

    def exactWorldBoundingBox(self, *args, **kwargs):
        return mc.exactWorldBoundingBox(*args, **kwargs)

    def optionVar(self, *args, **kwargs):
        mc.optionVar(*args, **kwargs)

    def objectType(self, *args, **kwargs):
        return mc.objectType(*args, **kwargs)


def calculate_knots(spans, degree, form):
    knots = []
    knot_count = spans + 2 * degree - 1
    if form == 2:
        pit = (degree - 1) * -1
        for itr in range(knot_count):
            knots.append(pit)
            pit += 1
        return knots

    for itr in range(degree):
        knots.append(0)
    for itr in range(knot_count - (degree * 2)):
        knots.append(itr + 1)
    for kit in range(degree):
        knots.append(itr + 2)
    return knots


cvs = [
    [-0.5, 0.0, 0.5],
    [-0.5, 0.0, -0.5],
    [0.5, 0.0, 0.5],
    [0.5, 0.0 - 0.5]
]

knots_u = [0.0, 1.0]
knots_v = [0.0, 1.0]
degree_u = 1
degree_v = 1
spans_u = 1
spans_v = 1
'''
