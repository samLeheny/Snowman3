# Title: animCurve_utils.py
# Author: Sam Leheny
# Contact: samleheny@live.com


###########################
##### Import Commands #####
import pymel.core as pm
import maya.cmds as mc
from dataclasses import dataclass
###########################
###########################


###########################
######## Variables ########
ANIM_CURVE_NODE_TYPE = ('animCurveUA', 'animCurveUL', 'animCurveUT', 'animCurveUU',
                         'animCurveTA', 'animCurveTL', 'animCurveTT', 'animCurveTU')
TRANSFORM_ATTRS = ('tx', 'ty', 'tz', 'rx', 'ry', 'rz')
###########################
###########################


########################################################################################################################
@dataclass
class KeyTangent:
    index: int
    inAngle: float
    outAngle: float
    inWeight: float
    outWeight: float
    inTangentType: str
    outTangentType: str
    weightedTangents: bool
    weightLock: bool
    stepAttributes: int
    lock: bool


# ----------------------------------------------------------------------------------------------------------------------
@dataclass
class AnimCurve:
    name: str
    node_type: str
    keyframe_count: int
    key_times: list
    key_values: list
    tangents: list
    tangentType: str
    weightedTangents: bool
    keyTanLocked: bool
    keyWeightLocked: bool
    keyTanInX: float
    keyTanInY: float
    keyTanOutX: float
    keyTanOutY: float
    keyTanInType: str
    keyTanOutType: str
    rotationInterpolation: bool
    preInfinity: str
    postInfinity: str
    stipplePattern: float
    outStippleThreshold: float
    outStippleRange: float
    inStippleRange: float
    stippleReverse: bool
    useCurveColor: bool
    curveColor: float
    curveColorR: float
    curveColorG: float
    curveColorB: float
    input: str
    output: list
    keyTimeValue: list


# ----------------------------------------------------------------------------------------------------------------------
class AnimCurveManager:

    ANIM_CURVE_NODE_TYPE = ANIM_CURVE_NODE_TYPE

    def __init__(
            self,
            node=None,
            anim_curve=None
    ):
        self.node = node
        self.anim_curve = anim_curve



    @classmethod
    def create_manager_from_node(cls, node):
        manager = AnimCurveManager(node=node)
        return manager



    @classmethod
    def create_manager_from_data(cls, data):
        manager = AnimCurveManager(anim_curve=data)
        return manager



    def node_from_data(self, data=None):
        data = data if data else self.anim_curve

        node = pm.shadingNode(data.node_type, name=data.name, au=1)
        data.name = node.nodeName()

        if data.input:
            pm.connectAttr(data.input, node.input)
        if data.output:
            [pm.connectAttr(node.output, plug, f=1) for plug in data.output]

        for i in range(data.keyframe_count):
            t = data.tangents[i]
            pm.setKeyframe(data.output[0], float=data.key_times[i], value=data.key_values[i])
            pm.keyTangent(data.output[0], e=1, index=(i, i), weightedTangents=int(t.weightedTangents))
            pm.keyTangent(data.output[0], e=1, index=(i, i), weightLock=t.weightLock)
            pm.keyTangent(data.output[0], e=1, index=(i, i), lock=t.lock)
            pm.keyTangent(data.output[0], e=1, index=(i, i), inWeight=t.inWeight)
            pm.keyTangent(data.output[0], e=1, index=(i, i), outWeight=t.outWeight)
            pm.keyTangent(data.output[0], e=1, index=(i, i), inAngle=t.inAngle)
            pm.keyTangent(data.output[0], e=1, index=(i, i), outAngle=t.outAngle)
            pm.keyTangent(data.output[0], e=1, index=(i, i), inTangentType=t.inTangentType)
            pm.keyTangent(data.output[0], e=1, index=(i, i), outTangentType=t.outTangentType)

        attrs = ('keyTanLocked', 'keyWeightLocked', 'keyTanInX', 'keyTanInY', 'keyTanOutX', 'keyTanOutY',
                 'keyTanInType', 'keyTanOutType', 'preInfinity', 'postInfinity', 'stipplePattern',
                 'outStippleThreshold', 'outStippleRange', 'useCurveColor', 'curveColor', 'curveColorR', 'curveColorG',
                 'curveColorB', 'keyTimeValue', 'stippleReverse')
        for attr in attrs:
            v = getattr(data, attr)
            pm.setAttr(f'{node}.{attr}', v)

        self.node = node
        return node



    def data_from_node(self, node=None):
        node = node if node else self.node

        output_plugs = pm.listConnections(node.output, s=0, d=1, plugs=1)
        output_plug = output_plugs[0] if output_plugs else None
        keyframe_count, key_times, key_values = 0, None, None
        node_input = pm.listConnections(node.input, s=1, d=0, plugs=1)[0]
        node_outputs = pm.listConnections(node.output, s=0, d=1, plugs=1)
        tangents = []
        if output_plug:
            keyframe_count = pm.keyframe(output_plug, q=1, keyframeCount=1)
            key_times = pm.keyframe(output_plug, q=1, index=(0, keyframe_count), floatChange=1)
            key_values = pm.keyframe(output_plug, q=1, index=(0, keyframe_count), valueChange=1)
            for i in range(keyframe_count):
                tangents.append(self.get_tangent(output_plug, i))

        attrs = ('tangentType', 'weightedTangents', 'keyTanLocked', 'keyWeightLocked', 'keyTanInX', 'keyTanInY',
                 'keyTanOutX', 'keyTanOutY', 'keyTanInType', 'keyTanOutType', 'rotationInterpolation', 'preInfinity',
                 'postInfinity', 'stipplePattern', 'outStippleThreshold', 'outStippleRange', 'inStippleRange',
                 'stippleReverse', 'useCurveColor', 'curveColor', 'curveColorR', 'curveColorG', 'curveColorB',
                 'keyTimeValue')
        inputs = {}
        for attr in attrs:
            inputs[attr] = pm.getAttr(f'{node.nodeName()}.{attr}')

        self.anim_curve = AnimCurve(
            name=node.nodeName(),
            node_type=node.nodeType(),
            keyframe_count=keyframe_count,
            key_times=key_times,
            key_values=key_values,
            tangents=tangents,
            input=node_input,
            output=node_outputs,
            **inputs
        )
        return self.anim_curve



    @staticmethod
    def get_tangent(plug, key_index):
        i = index = key_index
        lock = pm.keyTangent(plug, q=1, index=(i, i), lock=1)[0]
        inAngle = pm.keyTangent(plug, q=1, index=(i, i), inAngle=1)[0]
        outAngle = pm.keyTangent(plug, q=1, index=(i, i), outAngle=1)[0]
        inWeight = pm.keyTangent(plug, q=1, index=(i, i), inWeight=1)[0]
        outWeight = pm.keyTangent(plug, q=1, index=(i, i), outWeight=1)[0]
        weightLock = pm.keyTangent(plug, q=1, index=(i, i), weightLock=1)[0]
        stepAttributes = pm.keyTangent(plug, q=1, index=(i, i), stepAttributes=1)
        inTangentType = pm.keyTangent(plug, q=1, index=(i, i), inTangentType=1)[0]
        outTangentType = pm.keyTangent(plug, q=1, index=(i, i), outTangentType=1)[0]
        weightedTangents = pm.keyTangent(plug, q=1, index=(i, i), weightedTangents=1)[0]
        tangent = KeyTangent(index=index, inAngle=inAngle, outAngle=outAngle, inWeight=inWeight, outWeight=outWeight,
                             inTangentType=inTangentType, outTangentType=outTangentType,
                             weightedTangents=weightedTangents, weightLock=weightLock, stepAttributes=stepAttributes,
                             lock=lock)
        return tangent


# ----------------------------------------------------------------------------------------------------------------------
def combine_anim_curves(*anim_curve_nodes):
    if len(anim_curve_nodes) < 2:
        pm.warning("At least two anim curve nodes must be provided.")
        return False

    existing_blend_node = find_existing_blend_node(*anim_curve_nodes)
    blend_node = existing_blend_node if existing_blend_node else pm.shadingNode('blendWeighted', au=1)

    blend_anim_curves(blend_node, *anim_curve_nodes)

    return blend_node


# ----------------------------------------------------------------------------------------------------------------------
def blend_anim_curves(blend_node, *anim_curve_nodes):
    input_attr = blend_node.input
    for n, node in enumerate(anim_curve_nodes):
        if check_if_two_nodes_connected(node, blend_node):
            continue
        node.output.connect(input_attr[get_next_free_multi_index(input_attr)])


# ----------------------------------------------------------------------------------------------------------------------
def get_next_free_multi_index(attr_plug):
    start_index = 0
    max_index = 10000000
    while start_index < max_index:
        if len(pm.connectionInfo(f'{attr_plug}[{start_index}]', sourceFromDestination=True) or []) == 0:
            return start_index
        start_index += 1
    return 0


# ----------------------------------------------------------------------------------------------------------------------
def find_existing_blend_node(*nodes):
    for node in nodes:
        output_connections = pm.listConnections(node.output, d=1, s=0)
        if not output_connections:
            continue
        for connected_node in output_connections:
            if connected_node.nodeType() == 'blendWeighted':
                return connected_node
    return None


# ----------------------------------------------------------------------------------------------------------------------
def check_if_two_nodes_connected(*nodes):
    if not len(nodes) == 2:
        pm.warning("Must provide exactly two nodes.")
        return False
    if nodes[1] in pm.listConnections(nodes[0], d=1, s=1):
        return True
    return False


# ----------------------------------------------------------------------------------------------------------------------
def prune_empty_driven_keys_from_node(node, valid_node_types=ANIM_CURVE_NODE_TYPE):
    nodes_to_delete = []
    connected_nodes = pm.listConnections(node)
    if not connected_nodes:
        return False
    for node in connected_nodes:
        if not node.nodeType() in valid_node_types:
            continue
        if not check_if_curve_node_empty(node):
            continue
        nodes_to_delete.append(node)
    pm.delete(nodes_to_delete)


# ----------------------------------------------------------------------------------------------------------------------
def prune_unused_blend_nodes(node, valid_node_types=ANIM_CURVE_NODE_TYPE):
    anim_curve_nodes = []
    connected_nodes = pm.listConnections(node, s=0, d=1)
    for node in connected_nodes:
        if node.nodeType() in valid_node_types:
            anim_curve_nodes.append(node)
    blend_nodes = get_blend_nodes(anim_curve_nodes)
    if not blend_nodes:
        return False
    for node in blend_nodes:
        if check_if_blend_node_used(node):
            continue
        remove_blend_node(node)


# ----------------------------------------------------------------------------------------------------------------------
def get_blend_nodes(anim_curve_nodes):
    blend_nodes = []
    for node in anim_curve_nodes:
        outgoing_nodes = pm.listConnections(node.output, s=0, d=1)
        if not outgoing_nodes:
            continue
        for out_node in outgoing_nodes:
            if out_node.nodeType() == 'blendWeighted':
                blend_nodes.append(out_node)
    return blend_nodes


# ----------------------------------------------------------------------------------------------------------------------
def check_if_blend_node_used(node):
    if len(pm.listConnections(node.input, s=1, d=0, plugs=1)) < 2:
        return False
    return True


# ----------------------------------------------------------------------------------------------------------------------
def remove_blend_node(node):
    input_plug = pm.listConnections(node.input, s=1, d=0, plugs=1)[0]
    output_plug = pm.listConnections(node.output, s=0, d=1, plugs=1)[0]
    input_plug.connect(output_plug, f=1)
    pm.delete(node)


# ----------------------------------------------------------------------------------------------------------------------
def check_if_curve_node_empty(node):
    outgoing_connection = pm.listConnections(node.output, plugs=1, s=0, d=1)
    if not outgoing_connection:
        return False
    key_frame_count = pm.keyframe(outgoing_connection[0], q=1, keyframeCount=1)
    if key_frame_count == 0:
        pm.delete(node)
        return True
    key_values = pm.keyframe(outgoing_connection[0], q=1, index=(0, key_frame_count), valueChange=1)
    if all(v == 0 for v in key_values):
        return True
    return False


# ----------------------------------------------------------------------------------------------------------------------
class BlendposeManager:

    def __init__(self):
        self.blendposes = {}
        self.blendpose_order = []



    def populate_manager_from_scene(self):
        all_hook_nodes = self.get_hook_nodes_in_scene()
        [self.add_existing_blendpose(hook_node=node) for node in all_hook_nodes]



    def add_blendpose(self, name=None):
        if not name:
            name = self.generate_new_blendpose_name()
        new_blendpose = Blendpose(name)
        if name not in self.blendpose_order:
            self.blendpose_order.append(name)
        self.blendposes[name] = new_blendpose
        new_blendpose.create_hook_node()



    def generate_new_blendpose_name(self):
        first_part = 'blendpose'
        existing_named_nodes = pm.ls(f'{first_part}*')
        numerically_named_nodes = []
        for node_name in existing_named_nodes:
            end_particle = node_name.split(first_part)[1]
            if end_particle.isnumeric():
                numerically_named_nodes.append(end_particle)
        first_available_number = 1
        for i in range(1, len(numerically_named_nodes)):
            if i not in numerically_named_nodes:
                first_available_number = i
                break
        return f'{first_part}{first_available_number}'



    def add_existing_blendpose(self, name=None, hook_node=None):
        if not name:
            if hook_node:
                name = hook_node.nodeName()
        if name not in self.blendpose_order:
            self.blendpose_order.append(name)
        self.blendposes[name] = Blendpose.create_blendpose(name=name, hook_node=hook_node)



    def add_target_pose(self, blendpose_key, new_target_pose_key=None):
        blendpose = self.blendposes[blendpose_key]
        if not new_target_pose_key:
            new_target_pose_key = self.generate_new_target_pose_name(blendpose)
        blendpose.add_target_pose(new_target_pose_key)



    def rename_blendpose(self, new_name, blendpose_key):
        old_name = blendpose_key
        blendpose = self.blendposes[blendpose_key]
        new_name = blendpose.rename(new_name)
        self.blendpose_order[self.blendpose_order.index(old_name)] = new_name
        self.blendposes[new_name] = blendpose
        del self.blendposes[old_name]
        return new_name



    def rename_target_pose(self, current_target_name, new_target_name, blendpose_key):
        blendpose = self.blendposes[blendpose_key]
        new_name = blendpose.rename_target_pose(current_target_name, new_target_name)
        return new_name


    def add_output_objs(self, blendpose_key, *objs):
        blendpose = self.blendposes[blendpose_key]
        blendpose.add_output_objs(*objs)
        print(f'Output objects update for blendpose: {blendpose_key}')



    def add_output_objs_from_selection(self, blendpose_key):
        sel = pm.ls(sl=1)
        if not sel:
            return False
        self.add_output_objs(blendpose_key, *sel)



    def new_sub_target_from_transforms(self, blendpose_key, target_pose_key):
        blendpose = self.blendposes[blendpose_key]
        blendpose.new_sub_target_from_transforms(target_pose_key)



    @staticmethod
    def generate_new_target_pose_name(blendpose):
        first_part = 'targetPose'
        existing_named_targets = blendpose.get_target_poses_from_node(blendpose.hook_node)
        if not existing_named_targets:
            return f'{first_part}1'
        numerically_named_targets = []
        for target_name in existing_named_targets:
            if first_part not in target_name:
                continue
            end_particle = target_name.split(first_part)[1]
            if end_particle.isnumeric():
                numerically_named_targets.append(end_particle)
        first_available_number = 0
        i = 1
        while first_available_number == 0:
            if str(i) not in numerically_named_targets:
                first_available_number = i
            i += 1
        return f'{first_part}{first_available_number}'



    @staticmethod
    def get_hook_nodes_in_scene():
        blendpose_identifier = 'IsBlendposeNode'
        all_nodes = pm.ls(dependencyNodes=1)
        hook_nodes = []
        for node in all_nodes:
            if pm.attributeQuery(blendpose_identifier, node=node, exists=1):
                hook_nodes.append(node)
        return hook_nodes



class Blendpose:

    ANIM_CURVE_NODE_TYPES = ANIM_CURVE_NODE_TYPE

    def __init__(
        self,
        name,
        hook_node = None,
        target_poses = None,
        output_objs = None
    ):
        self.name = name
        self.hook_node = hook_node
        self.target_poses = target_poses if target_poses else {}
        self.output_objs = output_objs if output_objs else []



    @classmethod
    def create_blendpose(cls, name=None, hook_node=None):
        if isinstance(hook_node, str):
            hook_node = pm.PyNode(hook_node)
        if not name and not hook_node:
            print("Must provide a name or a hook_node when creating a Blendpose instance.")
        if not name:
            name = cls.get_blendpose_name_from_hook_node(hook_node)
        elif not hook_node:
            hook_node = cls.get_hook_node_from_blendpose_name(name)
        blendpose = Blendpose(name=name, hook_node=hook_node)
        blendpose.target_poses = blendpose.get_target_poses_from_node(hook_node)
        blendpose.output_objs = blendpose.get_output_objs_from_connections(hook_node)
        return blendpose



    @classmethod
    def get_hook_node_from_blendpose_name(cls, name):
        hook_node_name = name
        if not pm.objExists(hook_node_name):
            pm.error(f"Node: '{hook_node_name}' not found in scene")
        return pm.PyNode(hook_node_name)



    @classmethod
    def get_blendpose_name_from_hook_node(cls, node):
        return node.shortName()



    def get_output_objs_from_connections(self, node):
        output_attr_name = 'OutputObjs'
        output_objs = pm.listConnections(f'{self.hook_node}.{output_attr_name}', s=0, d=1)
        return output_objs



    def get_target_pose_range(self, target_pose_name):
        default_pose_range = (0, 1)
        if target_pose_name not in self.target_poses:
            return False
        target_pose_attr = f'{self.hook_node.nodeName()}.{target_pose_name}'
        out_connections = pm.listConnections(target_pose_attr, s=0, d=1)
        anim_curve = None
        for node in out_connections:
            if node.nodeType() in self.ANIM_CURVE_NODE_TYPES:
                anim_curve = node
                break
        if not anim_curve:
            return default_pose_range
        pose_range = self.get_anim_curve_float_range(anim_curve)
        return pose_range



    def get_anim_curve_float_range(self, anim_curve):
        keyframe_count = pm.keyframe(anim_curve, q=1, keyframeCount=1)
        float_range = pm.keyframe(anim_curve, q=1, index=(0, keyframe_count), floatChange=1)
        return min(float_range), max(float_range)



    def create_hook_node(self):
        node_type = 'transform'
        node_name = self.name
        self.hook_node = pm.shadingNode(node_type, name=node_name, au=1)
        self.add_attrs_to_hook_node()
        self.mark_hook_node()



    def add_attrs_to_hook_node(self):
        attr_names = {'weight': 'Weight',
                      'output objs': 'OutputObjs'}
        pm.addAttr(self.hook_node, longName=attr_names['weight'], attributeType='float', multi=1, keyable=1)
        pm.addAttr(self.hook_node, longName=attr_names['output objs'], dataType='string', keyable=0)



    def mark_hook_node(self):
        attr_name = 'IsBlendposeNode'
        pm.addAttr(self.hook_node, longName=attr_name, attributeType=bool, keyable=0)
        pm.setAttr(f'{self.hook_node}.{attr_name}', 1, lock=1)



    def add_target_pose(self, name):
        weight_attr_name = 'Weight'
        self.target_poses[name] = []
        indices = pm.getAttr(f'{self.hook_node}.{weight_attr_name}', multiIndices=1)
        next_index = max(indices) + 1 if indices else 0
        pm.aliasAttr(name, f'{self.hook_node}.{weight_attr_name}[{next_index}]')
        pm.setAttr(f'{self.hook_node}.{weight_attr_name}[{next_index}]', 1)



    def add_output_objs(self, *objs):
        self.output_objs = self.output_objs + list(objs)
        for obj in objs:
            self.connect_output_obj(obj)



    def connect_output_obj(self, obj):
        input_attr_name = 'BlendposeDriver'
        output_attr_name = 'OutputObjs'
        pm.addAttr(obj, longName=input_attr_name, dataType='string', keyable=0)
        pm.connectAttr(f'{self.hook_node}.{output_attr_name}', f'{obj}.{input_attr_name}')



    def get_output_objs_from_anim_curve(self, anim_curve_node):
        output_objs = []
        output_connections = pm.listConnections(anim_curve_node.output, s=0, d=1)
        for obj in output_connections:
            if obj.nodeType() in self.ANIM_CURVE_NODE_TYPES:
                output_objs.append(obj)
            elif obj.nodeType() == 'blendWeighted':
                found_objs = self.get_output_objs_from_blend_node(obj)
                if found_objs:
                    output_objs += found_objs
        return output_objs



    def get_target_poses_from_node(self, node):
        empty = {}
        pose_weight_attr_name = 'Weight'
        pose_weight_attr = f'{node}.{pose_weight_attr_name}'
        indices = pm.getAttr(pose_weight_attr, multiIndices=1)
        if not indices:
            return empty
        pose_attrs = {}
        for i in indices:
            attr_alias = pm.aliasAttr(f'{pose_weight_attr}[{i}]', q=1)
            pose_attrs[attr_alias] = []
        return pose_attrs



    def get_output_objs_from_blend_node(self, blend_node):
        output_objs = []
        output_connections = pm.listConnections(blend_node.output, s=0, d=1)
        for obj in output_connections:
            if obj.nodeType() in self.ANIM_CURVE_NODE_TYPES:
                output_objs.append(obj)
        return output_objs


    # Obsolete? --------------------------------------------------------------------------------------------------------------------------------------
    def get_anim_curve_nodes_from_hook_node(self, hook_node):
        target_poses = self.get_target_poses_from_node(hook_node)
        hook_node_output_plugs = [f'{hook_node}.{pose_name}' for pose_name in target_poses]
        anim_curve_nodes = []
        for output_plug in hook_node_output_plugs:
            connected_nodes = pm.listConnections(output_plug, s=0, d=1)
            for node in connected_nodes:
                if node.nodeType() in self.ANIM_CURVE_NODE_TYPES:
                    anim_curve_nodes.append(node)
        return anim_curve_nodes


    def new_sub_target_from_transforms(self, target_pose_key):
        driver_node = self.hook_node
        driver_attr_name = target_pose_key
        driver_plug = f'{driver_node}.{driver_attr_name}'
        blend_val = pm.getAttr(driver_plug)
        self.new_sub_target_at_blend_val(target_pose_key, blend_val)
        self.update_sub_target_from_transforms(driver_plug)



    def new_sub_target_at_blend_value(self, target_pose_key, blend_val):
        self.target_poses[target_pose_key].append(blend_val)



    def update_sub_target_from_transforms(self, source_plug):
        for obj in self.output_objs:
            self.bake_obj_to_sub_target(obj, source_plug)



    def bake_obj_to_sub_target(self, obj, source_plug, cull_zeroes=False):
        transform_vals = {attr: pm.getAttr(f'{obj}.{attr}') for attr in TRANSFORM_ATTRS}
        if self.all_transforms_are_zero(transform_vals):
            return False
        for key, val in transform_vals.items():
            #transform_value = pm.getAttr(f'{obj}.{attr}')
            if cull_zeroes and -0.00001 < val < 0.00001:
                continue
            self.bake_transform_attr_to_sub_target(obj, key, source_plug, val)



    def all_transforms_are_zero(self, transform_vals):
        for v in list(transform_vals.values()):
            if not -0.00001 < v < 0.00001:
                return False
        return True



    def bake_transform_attr_to_sub_target(self, destination_obj, destination_attr, source_plug, transform_value):
        transform_attr = destination_attr
        new_destination_obj = destination_obj.getParent()
        destination_plug = f'{new_destination_obj}.{destination_attr}'
        destination_inputs = pm.listConnections(destination_plug, s=1, d=0)
        destination_has_inputs = True if destination_inputs else False
        if destination_has_inputs:
            self.process_connected_destination_plug(
                destination_input=destination_inputs[0], destination_plug=destination_plug, source_plug=source_plug,
                transform_value=transform_value, transform_attr=transform_attr)
        else:
            self.initialize_anim_curve(new_destination_obj, destination_attr, source_plug, transform_value,
                                       transform_attr)
        self.reset_plug(f'{destination_obj}.{destination_attr}')



    def process_connected_destination_plug(self, destination_input, destination_plug, source_plug, transform_value,
                                           transform_attr):
        destination_input_node_type = destination_input.nodeType()
        if destination_input_node_type in self.ANIM_CURVE_NODE_TYPES:
            self.process_connection_from_anim_curve(destination_plug, source_plug, destination_input, transform_value,
                                                    transform_attr)
        elif destination_input_node_type == 'blendWeighted':
            self.process_connection_from_blend_node(destination_input, source_plug, transform_value, transform_attr)



    def process_connection_from_blend_node(self, destination_input, source_plug, transform_value, transform_attr):
        blend_node = destination_input
        blend_node_input = pm.listConnections(blend_node.input, s=1, d=0)
        if blend_node_input:
            self.process_connection_to_blend_node(blend_node, source_plug, transform_value, blend_node_input,
                                                  transform_attr)
        else:
            self.initialize_anim_curve(blend_node, get_next_free_multi_index(blend_node.input), source_plug,
                                       transform_value, transform_attr)



    def process_connection_to_blend_node(self, blend_node, source_plug, transform_value, blend_node_input,
                                         transform_attr):
        needed_anim_curve = None
        input_index = None
        for i in range(pm.getAttr(blend_node.input, size=1)):
            if self.needed_anim_curve_node_exists(blend_node.input[i], source_plug):
                needed_anim_curve = pm.listConnections(blend_node.input[i], s=1, d=0)[0]
                input_index = i
        if needed_anim_curve:
            self.update_anim_curve_node(needed_anim_curve, blend_node.input[input_index], source_plug, transform_value,
                                        needed_anim_curve)
        else:
            existing_anim_curves = blend_node_input
            new_anim_curve_node = self.new_anim_curve(source_plug, transform_attr)
            combine_anim_curves(*existing_anim_curves, new_anim_curve_node)
            source_float = pm.getAttr(source_plug)
            destination_plug = pm.listConnections(new_anim_curve_node.output, s=0, d=1, plugs=1)[0]
            self.set_key_on_anim_curve(destination_plug, 0, 0, new_anim_curve_node)
            self.set_key_on_anim_curve(destination_plug, source_float, transform_value, new_anim_curve_node)



    def process_connection_from_anim_curve(self, destination_plug, source_plug, destination_input, transform_value,
                                           transform_attr):
        if self.needed_anim_curve_node_exists(destination_plug, source_plug):
            anim_curve_node = pm.listConnections(destination_plug, s=1, d=0)[0]
            self.update_anim_curve_node(destination_input, destination_plug, source_plug, transform_value,
                                        anim_curve_node)
        else:
            existing_anim_curve = destination_input
            new_anim_curve_node = self.new_anim_curve(source_plug, transform_attr)
            blend_node = combine_anim_curves(existing_anim_curve, new_anim_curve_node)
            blend_node.output.connect(destination_plug, f=1)
            source_float = pm.getAttr(source_plug)
            self.set_key_on_anim_curve(blend_node.input[1], 0, 0, new_anim_curve_node)
            self.set_key_on_anim_curve(blend_node.input[1], source_float, transform_value, new_anim_curve_node)



    def update_anim_curve_node(self, node, destination_plug, source_plug, transform_value, anim_curve_node):
        source_float = pm.getAttr(source_plug)
        total_transform_value = transform_value + pm.getAttr(node.output)
        self.set_key_on_anim_curve(destination_plug, source_float, total_transform_value, anim_curve_node)



    def initialize_anim_curve(self, destination_obj, destination_attr, source_plug, transform_value, transform_attr):
        destination_plug = f'{destination_obj}.{destination_attr}'
        anim_curve_node = self.new_anim_curve(source_plug, transform_attr)
        anim_curve_node.output.connect(destination_plug)
        source_float = pm.getAttr(source_plug)
        self.set_key_on_anim_curve(destination_plug, 0, 0, anim_curve_node)
        self.set_key_on_anim_curve(destination_plug, source_float, transform_value, anim_curve_node)



    def new_anim_curve(self, source_plug, transform_attr):
        new_anim_curve_node = self.create_anim_curve_node(transform_attr)
        pm.connectAttr(source_plug, new_anim_curve_node.input)
        return new_anim_curve_node



    def set_key_on_anim_curve(self, destination_plug, source_float, key_value, anim_curve_node):
        pm.setKeyframe(anim_curve_node, float=source_float, value=key_value)
        self.jump_start_connection(destination_plug)



    def rename(self, new_name):
        actual_new_name = self.hook_node.rename(new_name).nodeName()
        self.name = actual_new_name
        return actual_new_name



    def rename_target_pose(self, old_name, new_name):
        this_target_attr = None
        weight_attr = f'{self.hook_node}.{"Weight"}'
        weight_indices = pm.getAttr(weight_attr, multiIndices=1)
        for i in weight_indices:
            attr_alias = pm.aliasAttr(f'{weight_attr}[{i}]', q=1)
            if not attr_alias == old_name:
                continue
            this_target_attr = f'{weight_attr}[{i}]'
            break
        if not this_target_attr:
            return False
        pm.aliasAttr(new_name, this_target_attr)
        self.target_poses[new_name] = self.target_poses[old_name]
        del(self.target_poses[old_name])
        return new_name



    @staticmethod
    def jump_start_connection(destination_plug):
        anim_curve_node_output_plug = pm.listConnections(destination_plug, s=1, d=0, plugs=1)[0]
        pm.disconnectAttr(anim_curve_node_output_plug, destination_plug)
        pm.connectAttr(anim_curve_node_output_plug, destination_plug)



    @staticmethod
    def reset_plug(plug):
        pm.setAttr(plug, 0)



    @staticmethod
    def create_anim_curve_node(transform_attr):
        node_type = {'t': 'animCurveUL', 'r': 'animCurveUA'}
        anim_curve_node = pm.shadingNode(node_type[transform_attr[0]], au=1)
        return anim_curve_node



    @staticmethod
    def needed_anim_curve_node_exists(destination_plug, source_plug):
        anim_curve_node = pm.listConnections(destination_plug, s=1, d=0)[0]
        node_inputs = pm.listConnections(anim_curve_node.input, s=1, d=0, plugs=1)
        if not node_inputs:
            return False
        if node_inputs[0] == source_plug:
            return True
        return False
