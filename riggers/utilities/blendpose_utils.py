# Title: blendpose_utils.py
# Author: Sam Leheny
# Contact: samleheny@live.com


###########################
##### Import Commands #####
import pymel.core as pm
import Snowman3.utilities.general_utils as gen
import Snowman3.riggers.utilities.animCurve_utils as acrv
###########################
###########################


###########################
######## Variables ########
ANIM_CURVE_NODE_TYPE = ('animCurveUA', 'animCurveUL', 'animCurveUT', 'animCurveUU',
                        'animCurveTA', 'animCurveTL', 'animCurveTT', 'animCurveTU')
TRANSFORM_ATTRS = ('tx', 'ty', 'tz', 'rx', 'ry', 'rz')
###########################
###########################



# ----------------------------------------------------------------------------------------------------------------------
class BlendposeManager:

    def __init__(self):
        self.blendposes = {}
        self.blendpose_order = []



    @classmethod
    def populate_manager_from_scene(cls):
        manager = BlendposeManager()
        all_hook_nodes = manager.get_hook_nodes_in_scene()
        [manager.add_existing_blendpose(hook_node=node) for node in all_hook_nodes]
        return manager



    def create_blendpose(self, name=None):
        if not name:
            name = self.generate_new_blendpose_name()
        new_blendpose = Blendpose(name)
        if name not in self.blendpose_order:
            self.blendpose_order.append(name)
        self.blendposes[name] = new_blendpose



    def generate_new_blendpose_name(self):
        first_part = 'blendpose'
        existing_named_nodes = pm.ls(f'{first_part}*')
        numerically_named_nodes = []
        for node_name in existing_named_nodes:
            end_particle = node_name.split(first_part)[1]
            if end_particle.isnumeric():
                numerically_named_nodes.append(end_particle)
        first_available_number = 1
        for i in range(len(numerically_named_nodes)+1):
            n = i + 1
            if str(n) not in numerically_named_nodes:
                first_available_number = n
                break
        return f'{first_part}{first_available_number}'



    def add_existing_blendpose(self, name=None, hook_node=None):
        if hook_node and not name:
            name = hook_node.nodeName()
        if name not in self.blendpose_order:
            self.blendpose_order.append(name)
        self.blendposes[name] = Blendpose.create_blendpose_from_scene(name=name)



    def add_target_pose(self, blendpose_key, new_target_pose_key=None):
        blendpose = self.blendposes[blendpose_key]
        if not new_target_pose_key:
            new_target_pose_key = self.generate_new_target_pose_name(blendpose_key)
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
        print(f'Output objects updated for blendpose: {blendpose_key}')



    def remove_output_objs(self, blendpose_key, *objs):
        blendpose = self.blendposes[blendpose_key]
        blendpose.remove_output_objs(*objs)
        print(f'Output objects updated fr blendpose: {blendpose_key}')



    def add_output_objs_from_selection(self, blendpose_key):
        sel = pm.ls(sl=1)
        if not sel:
            return False
        self.add_output_objs(blendpose_key, *sel)



    def new_anim_key_from_transforms(self, blendpose_key, target_pose_key):
        blendpose = self.blendposes[blendpose_key]
        blendpose.new_anim_key_from_transforms(target_pose_key)



    def update_target_pose_value(self, value, blendpose_key, blend_target_key):
        self.blendposes[blendpose_key].update_target_pose_value(value, blend_target_key)



    def toggle_blendpose_collapsed(self, blendpose_key, collapsed_status):
        self.blendposes[blendpose_key].isExpanded = collapsed_status



    def initialize_slider_range(self, blendpose_key, blend_target_attr):
        blendpose = self.blendposes[blendpose_key]
        pose_range = blendpose.get_target_pose_range(blend_target_attr)
        return pose_range



    def generate_new_target_pose_name(self, blendpose_key):
        first_part = 'targetPose'
        blendpose = self.blendposes[blendpose_key]
        existing_named_targets = blendpose.get_target_poses_from_node()
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



    def get_target_shape_current_value(self, blendpose_key, target_pose_key):
        return self.blendposes[blendpose_key].target_poses[target_pose_key].current_weight_value



    def set_target_shape_current_value(self, blendpose_key, target_pose_key, new_value):
        self.blendposes[blendpose_key].target_poses[target_pose_key].current_weight_value = new_value



    def get_target_pose(self, target_pose_key, blendpose_key):
        blendpose = self.blendposes[blendpose_key]
        target_pose = blendpose.get_target_pose(target_pose_key)
        return target_pose



    def duplicate_target_pose(self, target_pose_key, blendpose_key):
        blendpose = self.blendposes[blendpose_key]
        blendpose.duplicate_target_pose(target_pose_key)



    def delete_target_pose(self, target_pose_key, blendpose_key):
        blendpose = self.blendposes[blendpose_key]
        blendpose.delete_target_pose(target_pose_key)



    def delete_blendpose(self, blendpose_key):
        #
        blendpose = self.blendposes[blendpose_key]
        blendpose.delete_hook_node()
        #
        del(self.blendposes[blendpose_key])
        self.blendpose_order.remove(blendpose_key)



    def flip_target_pose(self, blendpose_key, target_pose_key):
        blendpose = self.blendposes[blendpose_key]
        blendpose.flip_target_pose(target_pose_key)



    def mirror_target_pose(self, blendpose_key, target_pose_key):
        blendpose = self.blendposes[blendpose_key]
        blendpose.mirror_target_pose(target_pose_key)



    @staticmethod
    def get_hook_nodes_in_scene():
        blendpose_identifier = 'IsBlendposeNode'
        all_nodes = pm.ls(dependencyNodes=1)
        hook_nodes = []
        for node in all_nodes:
            if pm.attributeQuery(blendpose_identifier, node=node, exists=1):
                hook_nodes.append(node)
        return hook_nodes



# ----------------------------------------------------------------------------------------------------------------------
class Blendpose:

    ANIM_CURVE_NODE_TYPES = ANIM_CURVE_NODE_TYPE
    WEIGHT_ATTR_NAME = 'Weight'
    OUTPUT_ATTR_NAME = 'OutputObjs'
    TRANSFORM_ATTRS = TRANSFORM_ATTRS

    def __init__(
        self,
        name = None,
        target_poses = None,
        output_objs = None,
    ):
        self.name = name
        self.hook_node = HookNode.produce(name)
        self.target_poses = target_poses if target_poses else {}
        self.output_objs = output_objs if output_objs else []
        self.key_frames = []
        self.isExpanded = True
        self.target_pose_order = []



    @classmethod
    def create_blendpose_from_scene(cls, name=None):
        blendpose = Blendpose(name=name)
        blendpose.target_poses = blendpose.get_target_poses_from_node()
        for key in blendpose.target_poses:
            blendpose.target_pose_order.append(key)
        blendpose.output_objs = blendpose.get_output_objs_from_connections()
        return blendpose



    def get_output_objs_from_connections(self):
        return self.hook_node.get_output_objs_from_connections()



    def get_target_pose_range(self, target_pose_name):
        if target_pose_name not in self.target_poses:
            return False
        target_pose = self.target_poses[target_pose_name]
        float_range = target_pose.get_float_range()
        return float_range



    def add_target_pose(self, name):
        #
        index = self.hook_node.get_next_available_weight_index()
        self.target_poses[name] = TargetPose(name=name, weight_attr_index=index)
        self.isExpanded = True
        self.target_pose_order.append(name)
        #
        self.hook_node.add_target_pose(name, index)



    def add_output_objs(self, *objs):
        self.output_objs = self.output_objs + list(objs)
        for obj in objs:
            self.hook_node.connect_output_obj(obj)



    def remove_output_objs(self, *objs):
        for obj in objs:
            if obj not in self.output_objs:
                continue
            self.output_objs.remove(obj)
            self.hook_node.disconnect_output_obj(obj)



    '''def get_output_objs_from_anim_curve(self, anim_curve_node):
        output_objs = []
        output_connections = pm.listConnections(anim_curve_node.output, s=0, d=1, scn=1)
        for obj in output_connections:
            if obj.nodeType() in self.ANIM_CURVE_NODE_TYPES:
                output_objs.append(obj)
            elif obj.nodeType() == 'blendWeighted':
                found_objs = self.get_output_objs_from_blend_node(obj)
                if found_objs:
                    output_objs += found_objs
        return output_objs



    def get_output_objs_from_blend_node(self, blend_node):
        output_objs = []
        output_connections = pm.listConnections(blend_node.output, s=0, d=1, scn=1)
        for obj in output_connections:
            if obj.nodeType() in self.ANIM_CURVE_NODE_TYPES:
                output_objs.append(obj)
        return output_objs'''



    def get_anim_curve_nodes_from_target_pose(self, target_pose_key):
        return self.hook_node.get_connected_nodes_from_target(target_pose_key)



    def new_anim_key_from_transforms(self, target_pose_key):
        driver_plug = self.hook_node.get_driver_plug(target_pose_key)
        blend_val = pm.getAttr(driver_plug)
        self.new_anim_key_at_blend_value(target_pose_key, blend_val)
        self.update_anim_keys_from_transforms(driver_plug)



    def new_anim_key_at_blend_value(self, target_pose_key, blend_val):
        target_pose = self.target_poses[target_pose_key]
        target_pose.add_keyframe(blend_val)



    def update_anim_keys_from_transforms(self, source_plug):
        for obj in self.output_objs:
            self.bake_obj_to_anim_keys(obj, source_plug)



    def bake_obj_to_anim_keys(self, obj, source_plug, cull_zeroes=False):
        transform_vals = {attr: acrv.get_true_transform_value(f'{obj}.{attr}') for attr in TRANSFORM_ATTRS}
        if self.all_transforms_are_zero(transform_vals):
            return False
        for key, val in transform_vals.items():
            if cull_zeroes and -0.00001 < val < 0.00001:
                continue
            self.bake_transform_attr_to_anim_key(obj, key, source_plug, val)



    def bake_transform_attr_to_anim_key(self, destination_obj, destination_attr, source_plug, transform_value):
        transform_attr = destination_attr
        ### destination_obj = destination_obj.getParent()
        destination_plug = f'{destination_obj}.{destination_attr}'
        needed_anim_curve = acrv.find_existing_anim_curve(source_plug, destination_plug)
        if needed_anim_curve:
            acrv.update_anim_curve_node(needed_anim_curve, destination_plug, source_plug, transform_value, needed_anim_curve)
        else:
            acrv.initialize_anim_curve(destination_plug, source_plug, transform_value, transform_attr)
        if not destination_obj == destination_obj:
            self.reset_plug(f'{destination_obj}.{destination_attr}')



    '''def process_connected_destination_plug(self, destination_input, destination_plug, source_plug, transform_value,
                                           transform_attr):
        destination_input_node_type = destination_input.nodeType()
        if destination_input_node_type in self.ANIM_CURVE_NODE_TYPES:
            self.process_connection_from_anim_curve(destination_plug, source_plug, destination_input, transform_value,
                                                    transform_attr)
        elif destination_input_node_type == 'blendWeighted':
            self.process_connection_from_blend_node(destination_input, source_plug, transform_value, transform_attr)



    def process_connection_from_blend_node(self, destination_input, source_plug, transform_value, transform_attr):
        blend_node = destination_input
        blend_node_input = pm.listConnections(blend_node.input, s=1, d=0, scn=1)
        if blend_node_input:
            self.process_connection_to_blend_node(blend_node, source_plug, transform_value, blend_node_input,
                                                  transform_attr)
        else:
            initialize_anim_curve(blend_node, get_next_free_multi_index(blend_node.input), source_plug,
                                       transform_value, transform_attr)



    def process_connection_to_blend_node(self, blend_node, source_plug, transform_value, blend_node_input,
                                         transform_attr):
        needed_anim_curve = None
        input_index = None
        for i in range(pm.getAttr(blend_node.input, size=1)):
            if self.needed_anim_curve_node_exists(blend_node.input[i], source_plug):
                needed_anim_curve = pm.listConnections(blend_node.input[i], s=1, d=0, scn=1)[0]
                input_index = i
        if needed_anim_curve:
            update_anim_curve_node(needed_anim_curve, blend_node.input[input_index], source_plug, transform_value,
                                        needed_anim_curve)
        else:
            existing_anim_curves = blend_node_input
            new_anim_curve_node = self.new_anim_curve(source_plug, transform_attr)
            combine_anim_curves(*existing_anim_curves, new_anim_curve_node)
            source_float = pm.getAttr(source_plug)
            destination_plug = pm.listConnections(new_anim_curve_node.output, s=0, d=1, plugs=1, scn=1)[0]
            set_key_on_anim_curve(destination_plug, 0, 0, new_anim_curve_node)
            set_key_on_anim_curve(destination_plug, source_float, transform_value, new_anim_curve_node)



    def process_connection_from_anim_curve(self, destination_plug, source_plug, destination_input, transform_value,
                                           transform_attr):
        if self.needed_anim_curve_node_exists(destination_plug, source_plug):
            anim_curve_node = pm.listConnections(destination_plug, s=1, d=0, scn=1)[0]
            update_anim_curve_node(destination_input, destination_plug, source_plug, transform_value,
                                        anim_curve_node)
        else:
            existing_anim_curve = destination_input
            new_anim_curve_node = self.new_anim_curve(source_plug, transform_attr)
            blend_node = combine_anim_curves(existing_anim_curve, new_anim_curve_node)
            blend_node.output.connect(destination_plug, f=1)
            source_float = pm.getAttr(source_plug)
            set_key_on_anim_curve(blend_node.input[1], 0, 0, new_anim_curve_node)
            set_key_on_anim_curve(blend_node.input[1], source_float, transform_value, new_anim_curve_node)'''



    def rename(self, new_name):
        actual_new_name = self.hook_node.rename(new_name)
        self.name = actual_new_name
        return actual_new_name



    def rename_target_pose(self, old_name, new_name):
        #
        self.target_poses[old_name].rename(new_name)
        self.target_poses[new_name] = self.target_poses[old_name]
        del(self.target_poses[old_name])
        self.target_pose_order[self.target_pose_order.index(old_name)] = new_name
        #
        self.hook_node.rename_target_pose(old_name, new_name)
        return new_name



    def update_target_pose_value(self, value, blend_target_key):
        #
        target_pose = self.target_poses[blend_target_key]
        target_pose.update_value(value)
        #
        target_pose_attr = self.hook_node.get_driver_plug(blend_target_key)
        pm.setAttr(target_pose_attr, target_pose.current_weight_value)



    def get_target_poses_from_node(self):
        return self.hook_node.get_target_poses()



    def get_target_pose(self, target_pose_key):
        if target_pose_key not in self.target_poses:
            return None
        return self.target_poses[target_pose_key]



    def duplicate_target_pose(self, target_pose_key):
        original_target_pose = self.target_poses[target_pose_key]
        new_target_pose_name = self.generate_duplicate_pose_name(target_pose_key)
        self.add_target_pose(new_target_pose_name)
        new_target_pose = self.target_poses[new_target_pose_name]
        self.copy_target_pose_keyframes(original_target_pose.name, new_target_pose.name)



    def copy_target_pose_keyframes(self, source_target_pose_key, destination_target_pose_key):
        dest_pose_plug = self.hook_node.get_driver_plug(destination_target_pose_key)
        source_pose_anim_curve_nodes = self.get_anim_curve_nodes_from_target_pose(source_target_pose_key)
        dest_pose_anim_curve_nodes = []
        for node in source_pose_anim_curve_nodes:

            orig_node_destinations = pm.listConnections(node.output, s=0, d=1, plugs=1, scn=1)
            destinations_to_remove = []
            for dest in orig_node_destinations:
                if dest.node().nodeType() == 'blendWeighted':
                    destinations_to_remove.append(dest)
            for dest in destinations_to_remove:
                orig_node_destinations.remove(dest)

            dup_node = pm.duplicate(node)[0]
            dest_pose_anim_curve_nodes.append(dup_node)
            pm.connectAttr(dest_pose_plug, dup_node.input)
            blend_node = acrv.combine_anim_curves(node, dup_node)
            [blend_node.output.connect(plug, f=1) for plug in orig_node_destinations]



    def generate_duplicate_pose_name(self, target_pose_key):
        duplicate_suffix = '_Copy'
        iter_limit = 10000
        new_target_pose_name = None
        existing_attr_aliases = self.target_poses
        for i in range(iter_limit):
            test_key = f'{target_pose_key}{duplicate_suffix*i}'
            if test_key not in existing_attr_aliases:
                new_target_pose_name = test_key
                break
        return new_target_pose_name



    def delete_target_pose(self, target_pose_key):
        #
        self.remove_target_pose_from_scene(target_pose_key)
        #
        del(self.target_poses[target_pose_key])
        self.target_pose_order.remove(target_pose_key)



    def remove_target_pose_from_scene(self, target_pose_key):
        self.delete_anim_curves_from_target_pose(target_pose_key)
        self.hook_node.remove_target_pose_attr_index(target_pose_key)



    def delete_anim_curves_from_target_pose(self, target_pose_key):
        target_pose = self.target_poses[target_pose_key]
        target_pose.delete_anim_curves(self.hook_node)



    def delete_hook_node(self):
        self.hook_node.delete_anim_curves()
        self.hook_node.delete()



    def flip_target_pose(self, target_pose_key):
        target_pose = self.target_poses[target_pose_key]
        target_pose.flip(self.hook_node)



    def mirror_target_pose(self, target_pose_key):
        target_pose = self.target_poses[target_pose_key]
        target_pose.mirror(self.hook_node)



    '''@staticmethod
    def get_float_range_from_anim_curve(anim_curve):
        
        keyframe_count = pm.keyframe(anim_curve, q=1, keyframeCount=1)
        float_range = pm.keyframe(anim_curve, q=1, index=(0, keyframe_count), floatChange=1)
        return min(float_range), max(float_range)'''



    @staticmethod
    def all_transforms_are_zero(transform_vals):
        for v in list(transform_vals.values()):
            if not -0.00001 < v < 0.00001:
                return False
        return True



    @staticmethod
    def reset_plug(plug):
        pm.setAttr(plug, 0)



    '''@staticmethod
    def needed_anim_curve_node_exists(destination_plug, source_plug):
        connected_nodes = pm.listConnections(destination_plug, s=1, d=0, scn=1)
        if not connected_nodes:
            return False
        anim_curve_node = connected_nodes[0]
        node_inputs = pm.listConnections(anim_curve_node.input, s=1, d=0, plugs=1, scn=1)
        if not node_inputs:
            return False
        if node_inputs[0] == source_plug:
            return True
        return False'''



# ----------------------------------------------------------------------------------------------------------------------
class HookNode:

    ANIM_CURVE_NODE_TYPES = ANIM_CURVE_NODE_TYPE
    WEIGHT_ATTR_NAME = 'Weight'
    OUTPUT_ATTR_NAME = 'OutputObjs'
    BLENDPOSE_DRIVER_ATTR_NAME = 'BlendposeDriver'
    TRANSFORM_ATTRS = TRANSFORM_ATTRS

    def __init__(
        self,
        name = None,
        node = None
    ):
        self.name = name
        self.node = node



    @classmethod
    def produce(cls, name):
        if pm.objExists(name):
            hook_node = cls.get_from_scene(name)
        else:
            hook_node = cls.create(name)
        return hook_node



    @classmethod
    def get_from_scene(cls, name):
        node = pm.PyNode(name)
        hook_node = HookNode(name=name, node=node)
        return hook_node



    @classmethod
    def create(cls, name):
        node_type = 'transform'
        node = pm.shadingNode(node_type, name=name, au=1)
        hook_node = HookNode(name=name, node=node)
        hook_node.add_attrs_to_node()
        hook_node.mark_node()
        return hook_node



    def add_attrs_to_node(self):
        attr_names = {'weight': self.WEIGHT_ATTR_NAME,
                      'output objs': 'OutputObjs'}
        pm.addAttr(self.node, longName=attr_names['weight'], attributeType='float', multi=1, keyable=1)
        pm.addAttr(self.node, longName=attr_names['output objs'], dataType='string', keyable=0)



    def mark_node(self):
        attr_name = 'IsBlendposeNode'
        pm.addAttr(self.node, longName=attr_name, attributeType=bool, keyable=0)
        pm.setAttr(f'{self.node}.{attr_name}', 1, lock=1)



    def add_target_pose(self, name, index):
        weight_attr_name = self.WEIGHT_ATTR_NAME
        pm.aliasAttr(name, f'{self.node}.{weight_attr_name}[{index}]')
        pm.setAttr(f'{self.node}.{weight_attr_name}[{index}]', 1)



    def get_target_poses(self):
        empty = {}
        pose_weight_attr = f'{self.node}.{self.WEIGHT_ATTR_NAME}'
        indices = pm.getAttr(pose_weight_attr, multiIndices=1)
        if not indices:
            return empty
        pose_attrs = {}
        for i in indices:
            attr = f'{pose_weight_attr}[{i}]'
            attr_alias = pm.aliasAttr(attr, q=1)
            if not attr_alias:
                continue
            pose_attrs[attr_alias] = TargetPose.create_target_pose_from_attr(attr)
        return pose_attrs



    def get_target_pose_attr(self, target_pose_key):
        if not pm.attributeQuery(target_pose_key, node=self.node, exists=1):
            return False
        return f'{self.node}.{target_pose_key}'



    def get_next_available_weight_index(self):
        indices = pm.getAttr(f'{self.node}.{self.WEIGHT_ATTR_NAME}', multiIndices=1)
        next_index = max(indices) + 1 if indices else 0
        return next_index



    def get_driver_plug(self, driver_attr_name):
        return f'{self.node}.{driver_attr_name}'



    def remove_target_pose_attr_index(self, target_pose_key):
        weight_attr = f'{self.node}.{self.WEIGHT_ATTR_NAME}'
        target_weight_attr = f'{self.node}.{target_pose_key}'
        pm.aliasAttr(target_weight_attr, remove=1)
        self.frontload_multi_attr(weight_attr)
        self.crop_multi_attr(weight_attr)



    def frontload_multi_attr(self, attr):
        attr_array_size = pm.getAttr(attr, size=1)
        shift_amount = 0
        for i in range(attr_array_size):
            attr_instance = f'{attr}[{i}]'
            attr_instance_alias = pm.aliasAttr(attr_instance, q=1)
            if not attr_instance_alias:
                shift_amount += 1
                continue
            if not shift_amount > 0:
                continue
            pm.aliasAttr(attr_instance, remove=1)
            new_index_instance = f'{attr}[{i - shift_amount}]'
            pm.aliasAttr(attr_instance_alias, new_index_instance)
            self.push_out_connections(new_index_instance, attr_instance)



    def connect_output_obj(self, obj):
        input_attr_name = self.BLENDPOSE_DRIVER_ATTR_NAME
        pm.addAttr(obj, longName=input_attr_name, dataType='string', keyable=0)
        pm.connectAttr(f'{self.node}.{self.OUTPUT_ATTR_NAME}', f'{obj}.{input_attr_name}')



    def disconnect_output_obj(self, obj):
        input_attr_name = self.BLENDPOSE_DRIVER_ATTR_NAME
        if not pm.attributeQuery(input_attr_name, node=obj, exists=1):
            return False
        for attr in TRANSFORM_ATTRS:
            output_obj_attr = f'{obj}.{attr}'
            upstream_nodes = pm.listHistory(output_obj_attr)
            if self.node in upstream_nodes:
                input = pm.listConnections(output_obj_attr, s=1, d=0, plugs=1, scn=1)[0]
                pm.disconnectAttr(input, output_obj_attr)
                pm.setAttr(output_obj_attr, 0)
        pm.disconnectAttr(f'{self.node}.{self.OUTPUT_ATTR_NAME}', f'{obj}.{input_attr_name}')



    def rename(self, new_name):
        return self.node.rename(new_name).nodeName()



    def get_output_objs_from_connections(self):
        output_objs = pm.listConnections(f'{self.node}.{self.OUTPUT_ATTR_NAME}', s=0, d=1, scn=1)
        return output_objs



    def get_connected_nodes_from_target(self, target_pose_key):
        anim_curve_nodes = []
        driver_plug = self.get_driver_plug(target_pose_key)
        connected_nodes = pm.listConnections(driver_plug, s=0, d=1, scn=1)
        for node in connected_nodes:
            if node.nodeType() in self.ANIM_CURVE_NODE_TYPES:
                anim_curve_nodes.append(node)
        return anim_curve_nodes



    def get_anim_curves(self):
        anim_curves = []
        connected_nodes = pm.listConnections(f'{self.node}.{self.WEIGHT_ATTR_NAME}', s=0, d=1, scn=1)
        for node in connected_nodes:
            if node.nodeType() in ANIM_CURVE_NODE_TYPE:
                anim_curves.append(node)
        return anim_curves



    def delete_anim_curves(self):
        anim_curves = self.get_anim_curves()
        for node in anim_curves:
            pm.delete(node)



    def delete(self):
        pm.delete(self.node)



    def get_node(self):
        return self.node



    def get_driven_output_objs_from_target_pose(self, target_pose_key):
        output_objs = pm.listConnections(f'{self.node}.{self.OUTPUT_ATTR_NAME}', s=0, d=1, scn=1)
        pose_weight_attr = f'{self.node}.{target_pose_key}'
        downstream_nodes = pm.listHistory(pose_weight_attr, future=1)
        driven_output_objs = []
        for node in downstream_nodes:
            if node in output_objs:
                driven_output_objs.append(node)
        return driven_output_objs



    def rename_target_pose(self, old_name, new_name):
        this_target_attr = None
        weight_attr = f'{self.node}.{self.WEIGHT_ATTR_NAME}'
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



    @staticmethod
    def crop_multi_attr(attr):
        orig_array_size = pm.getAttr(attr, size=1)
        for i in range(orig_array_size):
            final_index = (orig_array_size - 1) - i
            attr_instance = f'{attr}[{final_index}]'
            attr_instance_alias = pm.aliasAttr(attr_instance, q=1)
            if attr_instance_alias:
                break
            pm.removeMultiInstance(attr_instance, b=1)



    @staticmethod
    def push_out_connections(source_attr, dest_attr):
        new_index_out_connections = pm.listConnections(source_attr, s=0, d=1, plugs=1, scn=1)
        for connection in new_index_out_connections:
            pm.disconnectAttr(source_attr, connection)
        old_index_out_connections = pm.listConnections(dest_attr, s=0, d=1, plugs=1, scn=1)
        for connection in old_index_out_connections:
            pm.disconnectAttr(dest_attr, connection)
            pm.connectAttr(source_attr, connection, f=1)



# ----------------------------------------------------------------------------------------------------------------------
class TargetPose:

    ANIM_CURVE_NODE_TYPES = ANIM_CURVE_NODE_TYPE

    def __init__(
        self,
        name,
        weight_attr_index
    ):
        self.name = name
        self.key_frames = []
        self.current_weight_value = 1
        self.weight_attr_index = weight_attr_index
        self.float_range = [0, 1]
        self.slider_range = [0, 1]



    @classmethod
    def create_target_pose_from_attr(cls, attr):
        attr_alias = pm.aliasAttr(attr, q=1)
        index = int(attr.split('[')[1].split(']')[0])
        target_pose = TargetPose(name=attr_alias, weight_attr_index=index)

        target_pose.current_weight_value = pm.getAttr(attr)

        output_nodes = pm.listConnections(attr, s=0, d=1, scn=1)
        if not output_nodes:
            return target_pose
        anim_curve = None
        for node in output_nodes:
            if node.nodeType() in cls.ANIM_CURVE_NODE_TYPES:
                anim_curve = node
                break

        keyframe_count = pm.keyframe(anim_curve, q=1, keyframeCount=1)
        target_pose.key_frames = pm.keyframe(anim_curve, q=1, index=(0, keyframe_count), floatChange=1)
        target_pose.float_range = target_pose.get_float_range()
        target_pose.slider_range = target_pose.get_slider_range()

        return target_pose



    def get_float_range(self):
        default_pose_range = [0, 1]
        if not self.key_frames:
            return default_pose_range
        return min(self.key_frames), max(self.key_frames)



    def get_slider_range(self):
        slider_range = [0, 1]
        if self.float_range[0] < 0:
            slider_range[0] = self.float_range[0] * 2
        if self.float_range[1] > 1:
            slider_range[1] = self.float_range[1] * 2
        return slider_range



    def update_value(self, value):
        self.current_weight_value = value
        if value < self.slider_range[0]:
            self.float_range[0] = value
            self.slider_range[0] = value * 2
        if value > self.slider_range[1]:
            self.float_range[1] = value
            self.slider_range[1] = value * 2



    def rename(self, new_name):
        self.name = new_name



    def add_keyframe(self, val):
        self.key_frames.append(val)



    def flip(self, hook_node):
        driven_output_objs = self.get_driven_output_objs(hook_node)
        pose_weight_attr = hook_node.get_target_pose_attr(self.name)
        attr_destination_pairs = self.assemble_attr_pairs_list(pose_weight_attr, driven_output_objs)
        [acrv.switch_curve_connection(curve, old_attr, new_attr) for curve, new_attr, old_attr in attr_destination_pairs]



    def mirror(self, hook_node):
        driver_plug = hook_node.get_driver_plug(self.name)
        driven_output_objs = self.get_driven_output_objs(hook_node)
        pose_weight_attr = hook_node.get_target_pose_attr(self.name)
        attr_destination_pairs = self.assemble_attr_pairs_list(pose_weight_attr, driven_output_objs)
        for curve, new_plug, current_plug, in attr_destination_pairs:
            value = pm.getAttr(current_plug)
            transform_attr = new_plug.split('.')[-1]
            needed_anim_curve = acrv.find_existing_anim_curve(driver_plug, new_plug)
            if needed_anim_curve:
                acrv.update_anim_curve_node(needed_anim_curve, new_plug, driver_plug, value, needed_anim_curve)
            else:
                acrv.initialize_anim_curve(new_plug, driver_plug, value, transform_attr)



    def get_driven_output_objs(self, hook_node):
        driven_output_objs = hook_node.get_driven_output_objs_from_target_pose(self.name)
        return driven_output_objs



    def assemble_attr_pairs_list(self, pose_weight_attr, driven_objs):
        pairs = []
        for obj in driven_objs:
            opp_obj = self.get_opposite_obj_via_name(obj)
            if opp_obj not in driven_objs:
                continue
            pairs += self.get_attr_pairs_on_driven_obj(obj, pose_weight_attr, opp_obj)
        return pairs



    def get_attr_pairs_on_driven_obj(self, driven_obj, pose_weight_attr, opp_obj):
        pairs = []
        for attr in TRANSFORM_ATTRS:
            dest_attr = f'{driven_obj}.{attr}'
            input = pm.listConnections(dest_attr, s=1, d=0, scn=1)
            if not input:
                continue
            upstream_nodes = pm.listHistory(input)
            output = pm.listConnections(pose_weight_attr, s=0, d=1, scn=1)
            if not output:
                continue
            downstream_nodes = pm.listHistory(output, future=1)
            joining_nodes = list(set(upstream_nodes).intersection(downstream_nodes))
            for node in joining_nodes:
                if node.type() not in ANIM_CURVE_NODE_TYPE:
                    continue
                pair = [node, f'{opp_obj}.{attr}', dest_attr]
                pairs.append(pair)
        return pairs



    def delete_anim_curves(self, hook_node):
        for node in self.get_anim_curve_nodes(hook_node):
            for plug in pm.listConnections(node.output, s=0, d=1, plugs=1, scn=1):
                acrv.disconnect_anim_curve(node, plug)
            pm.delete(node)



    def get_anim_curve_nodes(self, hook_node):
        return hook_node.get_connected_nodes_from_target(self.name)



    @staticmethod
    def get_opposite_obj_via_name(obj):
        return gen.get_opposite_side_obj(obj)
