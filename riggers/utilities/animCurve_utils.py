# Title: animCurve_utils.py
# Author: Sam Leheny
# Contact: samleheny@live.com


###########################
##### Import Commands #####
import pymel.core as pm
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
class KeyTangent:
    def __init__(
        self,
        index: int,
        inAngle: float,
        outAngle: float,
        inWeight: float,
        outWeight: float,
        inTangentType: str,
        outTangentType: str,
        weightedTangents: bool,
        weightLock: bool,
        stepAttributes: int,
        lock: bool
    ):
        self.index = index
        self.inAngle = inAngle
        self.outAngle = outAngle
        self.inWeight = inWeight
        self.outWeight = outWeight
        self.inTangentType = inTangentType
        self.outTangentType = outTangentType
        self.weightedTangents = weightedTangents
        self.weightLock = weightLock
        self.stepAttributes = stepAttributes
        self.lock = lock



    @classmethod
    def create_from_data(cls, **kwargs):
        inst_inputs = KeyTangent._get_inst_inputs(**kwargs)
        return KeyTangent(**inst_inputs)



    @classmethod
    def _get_inst_inputs(cls, **kwargs):
        class_params = cls.__init__.__code__.co_varnames
        inst_inputs = {name: kwargs[name] for name in kwargs if name in class_params}
        return inst_inputs



    def data_dict(self):
        return vars(self).copy()



# ----------------------------------------------------------------------------------------------------------------------
class AnimCurve:
    def __init__(
        self,
        name: str = None,
        node_type: str = None,
        keyframe_count: int = None,
        key_times: list = None,
        key_values: list = None,
        tangents: list = None,
        tangentType: str = None,
        weightedTangents: bool = None,
        keyTanLocked: bool = None,
        keyWeightLocked: bool = None,
        keyTanInX: float = None,
        keyTanInY: float = None,
        keyTanOutX: float = None,
        keyTanOutY: float = None,
        keyTanInType: str = None,
        keyTanOutType: str = None,
        rotationInterpolation: bool = None,
        preInfinity: str = None,
        postInfinity: str = None,
        stipplePattern: float = None,
        outStippleThreshold: float = None,
        outStippleRange: float = None,
        inStippleRange: float = None,
        stippleReverse: bool = None,
        useCurveColor: bool = None,
        curveColor: float = None,
        curveColorR: float = None,
        curveColorG: float = None,
        curveColorB: float = None,
        input: str = None,
        output: list = None,
        keyTimeValue: list = None
    ):
        self.name = name
        self.node_type = node_type
        self.keyframe_count = keyframe_count
        self.key_times = key_times
        self.key_values = key_values
        self.tangents = tangents
        self.tangentType = tangentType
        self.weightedTangents = weightedTangents
        self.keyTanLocked = keyTanLocked
        self.keyWeightLocked = keyWeightLocked
        self.keyTanInX = keyTanInX
        self.keyTanInY = keyTanInY
        self.keyTanOutX = keyTanOutX
        self.keyTanOutY = keyTanOutY
        self.keyTanInType = keyTanInType
        self.keyTanOutType = keyTanOutType
        self.rotationInterpolation = rotationInterpolation
        self.preInfinity = preInfinity
        self.postInfinity = postInfinity
        self.stipplePattern = stipplePattern
        self.outStippleThreshold = outStippleThreshold
        self.outStippleRange = outStippleRange
        self.inStippleRange = inStippleRange
        self.stippleReverse = stippleReverse
        self.useCurveColor = useCurveColor
        self.curveColor = curveColor
        self.curveColorR = curveColorR
        self.curveColorG = curveColorG
        self.curveColorB = curveColorB
        self.input = input
        self.output = output
        self.keyTimeValue = keyTimeValue

        self.node = None



    @classmethod
    def create_from_node(cls, node=None):

        output_plugs = pm.listConnections(node.output, s=0, d=1, plugs=1, scn=1)
        output_plug = output_plugs[0] if output_plugs else None
        keyframe_count, key_times, key_values = 0, None, None
        node_input = pm.listConnections(node.input, s=1, d=0, plugs=1, scn=1)[0].name()
        node_outputs = [c.name() for c in get_final_anim_curve_destinations(node.output)]
        tangents = []
        if output_plug:
            keyframe_count = pm.keyframe(output_plug, q=1, keyframeCount=1)
            key_times = pm.keyframe(output_plug, q=1, index=(0, keyframe_count), floatChange=1)
            key_values = pm.keyframe(output_plug, q=1, index=(0, keyframe_count), valueChange=1)
            for i in range(keyframe_count):
                tangents.append(cls._get_tangent(output_plug, i))

        attrs = ('tangentType', 'weightedTangents', 'keyTanLocked', 'keyWeightLocked', 'keyTanInX', 'keyTanInY',
                 'keyTanOutX', 'keyTanOutY', 'keyTanInType', 'keyTanOutType', 'rotationInterpolation', 'preInfinity',
                 'postInfinity', 'stipplePattern', 'outStippleThreshold', 'outStippleRange', 'inStippleRange',
                 'stippleReverse', 'useCurveColor', 'curveColor', 'curveColorR', 'curveColorG', 'curveColorB',
                 'keyTimeValue')
        inputs = {}
        for attr in attrs:
            inputs[attr] = pm.getAttr(f'{node.nodeName()}.{attr}')

        return AnimCurve(
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



    @classmethod
    def create_from_data(cls, **kwargs):
        inst_inputs = AnimCurve._get_inst_inputs(**kwargs)

        if inst_inputs['tangents']:
            inst_inputs['tangents'] = [ KeyTangent.create_from_data(**data) for data in inst_inputs['tangents'] ]

        return AnimCurve(**inst_inputs)



    @classmethod
    def _get_inst_inputs(cls, **kwargs):
        class_params = cls.__init__.__code__.co_varnames
        inst_inputs = {name: kwargs[name] for name in kwargs if name in class_params}
        return inst_inputs



    def node_from_data(self, data=None):

        if not data:
            data = self

        node = pm.shadingNode(data.node_type, name=data.name, au=1)
        data.name = node.nodeName()

        if data.input:
            self._find_connect_input(data.input, node)
        if data.output:
            self._find_connect_output(data.output, node)

        for i in range(data.keyframe_count):
            t = data.tangents[i]
            pm.setKeyframe(node, float=data.key_times[i], value=data.key_values[i])
            pm.keyTangent(node, e=1, index=(i, i), weightedTangents=int(t.weightedTangents))
            if not pm.keyTangent(node, q=1, index=(i, i), weightedTangents=1):
                pm.keyTangent(node, e=1, index=(i, i), weightLock=t.weightLock)
            pm.keyTangent(node, e=1, index=(i, i), lock=t.lock)
            pm.keyTangent(node, e=1, index=(i, i), inWeight=t.inWeight)
            pm.keyTangent(node, e=1, index=(i, i), outWeight=t.outWeight)
            pm.keyTangent(node, e=1, index=(i, i), inAngle=t.inAngle)
            pm.keyTangent(node, e=1, index=(i, i), outAngle=t.outAngle)
            pm.keyTangent(node, e=1, index=(i, i), inTangentType=t.inTangentType)
            pm.keyTangent(node, e=1, index=(i, i), outTangentType=t.outTangentType)

        attrs = ('keyTanLocked', 'keyWeightLocked', 'keyTanInX', 'keyTanInY', 'keyTanOutX', 'keyTanOutY',
                 'keyTanInType', 'keyTanOutType', 'preInfinity', 'postInfinity', 'stipplePattern',
                 'outStippleThreshold', 'outStippleRange', 'useCurveColor', 'curveColor', 'curveColorR', 'curveColorG',
                 'curveColorB', 'keyTimeValue', 'stippleReverse')
        [pm.setAttr(f'{node}.{attr}', getattr(data, attr)) for attr in attrs]

        self.node = node
        return node



    def data_dict(self):
        attrs = vars(self).copy()
        attrs['tangents'] = [tangent.data_dict() for tangent in self.tangents]
        return attrs



    @staticmethod
    def _get_tangent(plug, key_index):
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



    @staticmethod
    def _find_connect_input(input_plug, node):
        attr = input_plug
        obj_name, plug = attr.split('.')
        if pm.objExists(obj_name):
            if not pm.attributeQuery(plug, node=obj_name, exists=1):
                pm.connectAttr(input_plug, node.input)



    @staticmethod
    def _find_connect_output(output_plugs, node):
        for attr in output_plugs:
            obj_name, plug = attr.split('.')
            if not pm.objExists(obj_name):
                continue
            if not pm.attributeQuery(plug, node=obj_name, exists=1):
                continue
            connect_anim_curve(node, attr)



'''
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
        if not data:
            data = self.anim_curve

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
        node = node or self.node

        output_plugs = pm.listConnections(node.output, s=0, d=1, plugs=1, scn=1)
        output_plug = output_plugs[0] if output_plugs else None
        keyframe_count, key_times, key_values = 0, None, None
        node_input = pm.listConnections(node.input, s=1, d=0, plugs=1, scn=1)[0]
        node_outputs = pm.listConnections(node.output, s=0, d=1, plugs=1, scn=1)
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
'''



# ----------------------------------------------------------------------------------------------------------------------
def get_true_transform_value(attr):
    apparent_value = pm.getAttr(attr)
    possible_driver_plugs = pm.listConnections(attr, s=1, d=0, plugs=1, scn=1)
    if not possible_driver_plugs:
        return apparent_value
    else:
        true_value = pm.getAttr(possible_driver_plugs[0])
        return apparent_value - true_value


# ----------------------------------------------------------------------------------------------------------------------
def get_node_from_attr(attr):
    if isinstance(attr, str):
        return pm.PyNode(attr.split('.')[0])
    else:
        return attr._node


# ----------------------------------------------------------------------------------------------------------------------
def connect_anim_curve(anim_curve, dest_plug):
    dest_plug_inputs = pm.listConnections(dest_plug, s=1, d=0, scn=1)
    if not dest_plug_inputs:
        anim_curve.output.connect(dest_plug)
        return
    else:
        dest_plug_input = dest_plug_inputs[0]
        if dest_plug_input.type() in ANIM_CURVE_NODE_TYPE:
            blend_node = combine_anim_curves(anim_curve, dest_plug_input)
            blend_node.output.connect(dest_plug, f=1)
        elif dest_plug_input.type() == 'blendWeighted':
            blend_anim_curves(dest_plug_input, anim_curve)


# ----------------------------------------------------------------------------------------------------------------------
def disconnect_anim_curve(anim_curve, dest_plug):

    def get_blend_node_input_plug(node, blend_node):
        for input_plug in pm.listConnections(node, s=0, d=1, plugs=1, scn=1):
            if get_node_from_attr(input_plug) == blend_node:
                return input_plug
        return None

    def main(dest_plug):
        dest_plug_input_nodes = pm.listConnections(dest_plug, s=1, d=0, scn=1)
        if not dest_plug_input_nodes:
            return
        dest_plug_input_node = dest_plug_input_nodes[0]
        if dest_plug_input_node == anim_curve:
            pm.disconnectAttr(anim_curve.output, dest_plug)
            return
        if not dest_plug_input_node.nodeType() == 'blendWeighted':
            return
        blend_node = dest_plug_input_node
        blend_node_inputs = pm.listConnections(blend_node.input, s=1, d=0, scn=1)
        if anim_curve not in blend_node_inputs:
            return
        pm.disconnectAttr(anim_curve.output, get_blend_node_input_plug(anim_curve, blend_node))
        if not check_if_blend_node_used(blend_node):
            remove_blend_node(blend_node)

    dest_node = get_node_from_attr(dest_plug)
    if dest_node.nodeType() == 'blendWeighted':
        dest_node_out_plugs = pm.listConnections(dest_node.output, s=0, d=1, plugs=1, scn=1)
        if not dest_node_out_plugs:
            return
        for plug in dest_node_out_plugs:
            main(plug)
        return

    main(dest_plug)


# ----------------------------------------------------------------------------------------------------------------------
def redirect_curve_connection(curve, old_attr, new_attr):
    disconnect_anim_curve(curve, old_attr)
    connect_anim_curve(curve, new_attr)


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
    unconnected_nodes = []
    for node in anim_curve_nodes:
        if blend_node not in pm.listConnections(node, s=0, d=1, scn=1):
            unconnected_nodes.append(node)
    input_attr = blend_node.input
    for node in unconnected_nodes:
        next_index = get_next_free_multi_index(input_attr)
        node.output.connect(input_attr[next_index])


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
def find_existing_anim_curve(source_plug, dest_plug):
    downstream_connections = pm.listConnections(source_plug, s=0, d=1)
    upstream_connections = pm.listConnections(dest_plug, s=1, d=0)
    if not all((downstream_connections, upstream_connections)):
        return None
    downstream_nodes = get_downstream_nodes(source_plug)
    upstream_nodes = pm.listHistory(upstream_connections[0])
    for node in downstream_nodes:
        if node not in upstream_nodes:
            continue
        if node.nodeType() not in ANIM_CURVE_NODE_TYPE:
            continue
        return node
    return None



# ----------------------------------------------------------------------------------------------------------------------
def get_downstream_nodes(source_plug):
    downstream_nodes = []
    downstream_connections = pm.listConnections(source_plug, s=0, d=1)
    for node in downstream_connections:
        downstream_nodes += pm.listHistory(node, future=1)
    return downstream_nodes



# ----------------------------------------------------------------------------------------------------------------------
def find_existing_blend_node(*nodes):
    for node in nodes:
        output_connections = pm.listConnections(node.output, d=1, s=0, scn=1)
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
    if nodes[1] in pm.listConnections(nodes[0], d=1, s=1, scn=1):
        return True
    return False


# ----------------------------------------------------------------------------------------------------------------------
def prune_empty_driven_keys_from_node(node, valid_node_types=ANIM_CURVE_NODE_TYPE):
    nodes_to_delete = []
    connected_nodes = pm.listConnections(node, scn=1)
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
    connected_nodes = pm.listConnections(node, s=0, d=1, scn=1)
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
        outgoing_nodes = pm.listConnections(node.output, s=0, d=1, scn=1)
        if not outgoing_nodes:
            continue
        for out_node in outgoing_nodes:
            if out_node.nodeType() == 'blendWeighted':
                blend_nodes.append(out_node)
    return blend_nodes


# ----------------------------------------------------------------------------------------------------------------------
def check_if_blend_node_used(node):
    if len(pm.listConnections(node.input, s=1, d=0, plugs=1, scn=1)) < 2:
        return False
    return True


# ----------------------------------------------------------------------------------------------------------------------
def remove_blend_node(node):
    input_plug = pm.listConnections(node.input, s=1, d=0, plugs=1, scn=1)[0]
    output_plug = pm.listConnections(node.output, s=0, d=1, plugs=1, scn=1)[0]
    input_plug.connect(output_plug, f=1)
    pm.delete(node)


# ----------------------------------------------------------------------------------------------------------------------
def check_if_curve_node_empty(node):
    outgoing_connection = pm.listConnections(node.output, plugs=1, s=0, d=1, scn=1)
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
def create_anim_curve_node(transform_attr):
    node_type = {'t': 'animCurveUL', 'r': 'animCurveUA'}
    anim_curve_node = pm.shadingNode(node_type[transform_attr[0]], au=1)
    return anim_curve_node


# ----------------------------------------------------------------------------------------------------------------------
def new_anim_curve(source_plug, transform_attr):
    new_anim_curve_node = create_anim_curve_node(transform_attr)
    pm.connectAttr(source_plug, new_anim_curve_node.input)
    return new_anim_curve_node


# ----------------------------------------------------------------------------------------------------------------------
def jump_start_connection(destination_plug):
    anim_curve_node_output_plug = pm.listConnections(destination_plug, s=1, d=0, plugs=1, scn=1)[0]
    pm.disconnectAttr(anim_curve_node_output_plug, destination_plug)
    pm.connectAttr(anim_curve_node_output_plug, destination_plug)


# ----------------------------------------------------------------------------------------------------------------------
def set_key_on_anim_curve(destination_plug, source_float, key_value, anim_curve_node):
    pm.setKeyframe(anim_curve_node, float=source_float, value=key_value)
    jump_start_connection(destination_plug)


# ----------------------------------------------------------------------------------------------------------------------
def update_anim_curve_node(node, destination_plug, source_plug, transform_value):
    source_float = pm.getAttr(source_plug)
    total_transform_value = transform_value + pm.getAttr(node.output)
    set_key_on_anim_curve(destination_plug, source_float, total_transform_value, node)


# ----------------------------------------------------------------------------------------------------------------------
def initialize_anim_curve(destination_plug, source_plug, transform_value, transform_attr):
    anim_curve_node = new_anim_curve(source_plug, transform_attr)
    connect_anim_curve(anim_curve_node, destination_plug)
    source_float = pm.getAttr(source_plug)
    set_key_on_anim_curve(destination_plug, 0, 0, anim_curve_node)
    set_key_on_anim_curve(destination_plug, source_float, transform_value, anim_curve_node)


# ----------------------------------------------------------------------------------------------------------------------
def get_final_anim_curve_destinations(starting_node_out_plug):
    final_plugs = []
    starting_node_output_nodes = pm.listConnections(starting_node_out_plug, s=0, d=1, scn=1)
    starting_node_output_plugs = pm.listConnections(starting_node_out_plug, s=0, d=1, scn=1, plugs=1)
    for i, node in enumerate(starting_node_output_nodes):
        if not node.nodeType() == 'blendWeighted':
            final_plugs.append(starting_node_output_plugs[i])
        else:
            x = get_final_anim_curve_destinations(node.output)
            if x:
                final_plugs += x
    return final_plugs
