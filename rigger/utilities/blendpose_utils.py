# Title: blendpose_utils.py
# Author: Sam Leheny
# Contact: samleheny@live.com


###########################
##### Import Commands #####
import importlib
import copy
import pymel.core as pm
import Snowman3.utilities.general_utils as gen
importlib.reload(gen)
import Snowman3.rigger.utilities.animCurve_utils as acrv
importlib.reload(acrv)
AnimCurve = acrv.AnimCurve
###########################
###########################


###########################
######## Variables ########
ANIM_CURVE_NODE_TYPE = ('animCurveUA', 'animCurveUL', 'animCurveUT', 'animCurveUU',
                        'animCurveTA', 'animCurveTL', 'animCurveTT', 'animCurveTU')
TRANSFORM_ATTRS = ('tx', 'ty', 'tz', 'rx', 'ry', 'rz')
HOOK_NODE_TYPE = 'transform'
HOOK_NODE_ID_ATTR = 'IsBlendposeNode'
HOOK_NODE_SUFFIX = 'BPHook'
###########################
###########################



# ----------------------------------------------------------------------------------------------------------------------
class BlendposeManager:

    HOOK_NODE_TYPE = HOOK_NODE_TYPE
    HOOK_NODE_ID_ATTR = HOOK_NODE_ID_ATTR

    def __init__(
        self,
        blendposes = None,
        blendpose_order = None,
    ):
        self.blendposes = blendposes or {}
        self.blendpose_order = blendpose_order or self.get_blendpose_order()



    @classmethod
    def populate_manager_from_scene(cls):
        manager = BlendposeManager()
        all_hook_nodes = manager.get_hook_nodes_in_scene()
        [ manager.add_existing_blendpose(hook_node_name=node.nodeName()) for node in all_hook_nodes ]
        return manager



    @classmethod
    def populate_manager_from_data(cls, blendposes):
        blendposes = {k: Blendpose.create_from_data(**v) for k, v in blendposes.items()}
        manager = BlendposeManager(blendposes)
        return manager



    def get_blendpose_order(self):
        if not self.blendposes:
            return []
        else:
            return [k for k in self.blendposes]



    def create_blendpose(self, name=None):
        if not name:
            name = self.generate_new_blendpose_name()
        new_blendpose = Blendpose(name)
        if name not in self.blendpose_order:
            self.blendpose_order.append(name)
        self.blendposes[name] = new_blendpose



    def add_blendpose_from_data(self, **kwargs):
        blendpose = Blendpose.create_from_data(**kwargs)
        self.blendpose_order.append(blendpose.name)
        self.blendposes[blendpose.name] = blendpose



    def add_existing_blendpose(self, name=None, hook_node_name=None):
        if hook_node_name and not name:
            name = hook_node_name.split('_BPHook')[0]
        if name not in self.blendpose_order:
            self.blendpose_order.append(name)
        self.blendposes[name] = Blendpose.create_blendpose_from_scene(name=name)



    def connect_output_objs_to_blendpose(self, blendpose_key):
        self.blendposes[blendpose_key].connect_all_output_objs()



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
        print(f'Output objects updated for blendpose: {blendpose_key}')



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



    def get_hook_node(self, blendpose_key):
        blendpose = self.blendposes[blendpose_key]
        return blendpose.hook_node.get_node()



    def select_hook_node(self, blendpose_key):
        hook_node = self.get_hook_node(blendpose_key)
        pm.select(hook_node, replace=1)



    def get_all_target_objs(self, blendpose_key):
        return self.blendposes[blendpose_key].get_all_target_objs()



    def all_blendposes_data_dict(self):
        return {k: v.data_dict() for k, v in self.blendposes.items()}



    def build_blendposes_from_data(self, data):
        data = copy.deepcopy(data)
        for key in data:
            self.add_blendpose_from_data(**data[key])
            self.connect_output_objs_to_blendpose(key)
            blendpose = self.blendposes[key]
            for i, target_pose in enumerate(blendpose.target_poses.values()):
                blendpose.create_target_pose_on_hook_node(target_pose)
                [anim_curve.node_from_data() for anim_curve in target_pose.anim_curves]



    def get_hook_nodes_in_scene(self):
        nodes = pm.ls(type=self.HOOK_NODE_TYPE)
        hook_nodes = [node for node in nodes if pm.attributeQuery(self.HOOK_NODE_ID_ATTR, node=node, exists=1)]
        return hook_nodes



    @staticmethod
    def generate_new_blendpose_name():
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



# ----------------------------------------------------------------------------------------------------------------------
class Blendpose:

    ANIM_CURVE_NODE_TYPES = ANIM_CURVE_NODE_TYPE
    WEIGHT_ATTR_NAME = 'Weight'
    OUTPUT_ATTR_NAME = 'OutputObjs'
    TRANSFORM_ATTRS = TRANSFORM_ATTRS

    def __init__(
        self,
        name,
        target_poses = None,
        output_objs = None,
        target_pose_order = None,
    ):
        self.name = name
        self.target_poses = target_poses or {}
        self.output_objs = output_objs or []
        self.target_pose_order = target_pose_order or []
        self.hook_node = HookNode.produce(name)
        self.isExpanded = True



    @classmethod
    def create_blendpose_from_scene(cls, name=None):
        blendpose = Blendpose(name=name)
        blendpose.target_poses = blendpose.get_target_poses_from_node()
        [ blendpose.target_pose_order.append(key) for key in blendpose.target_poses ]
        blendpose.output_objs = blendpose.get_output_objs_from_connections()
        return blendpose



    @classmethod
    def create_from_data(cls, **kwargs):
        inst_inputs = Blendpose._get_inst_inputs(**kwargs)

        if 'output_objs' in inst_inputs:
            inst_inputs['output_objs'] = cls.get_output_objs(inst_inputs['output_objs'])

        if 'target_poses' in inst_inputs:
            inst_inputs['target_poses'] = { k: TargetPose.create_from_data(**v)
                                            for k, v in inst_inputs['target_poses'].items() }

        return Blendpose(**inst_inputs)



    @classmethod
    def _get_inst_inputs(cls, **kwargs):
        class_params = cls.__init__.__code__.co_varnames
        inst_inputs = {name: kwargs[name] for name in kwargs if name in class_params}
        return inst_inputs



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
        index = self.get_next_available_weight_index()
        self.target_poses[name] = TargetPose(name=name, weight_attr_index=index)
        self.isExpanded = True
        self.target_pose_order.append(name)
        #
        self.create_target_pose_on_hook_node(self.target_poses[name])



    def get_next_available_weight_index(self):
        return self.hook_node.get_next_available_weight_index()



    def create_target_pose_on_hook_node(self, target_pose):
        self.hook_node.add_target_pose(target_pose)



    def add_output_objs(self, *objs):
        self.output_objs = self.output_objs + list(objs)
        [self.hook_node.connect_output_obj(obj) for obj in objs]



    def connect_all_output_objs(self):
        [self.hook_node.connect_output_obj(obj) for obj in self.output_objs]



    def remove_output_objs(self, *objs):
        for obj in objs:
            if obj not in self.output_objs:
                continue
            self.output_objs.remove(obj)
            self.hook_node.disconnect_output_obj(obj)



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
            acrv.update_anim_curve_node(needed_anim_curve, destination_plug, source_plug, transform_value)
        else:
            acrv.initialize_anim_curve(destination_plug, source_plug, transform_value, transform_attr)
        if not destination_obj == destination_obj:
            self.reset_plug(f'{destination_obj}.{destination_attr}')



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



    def get_all_target_objs(self):
        return self.output_objs



    def data_dict(self):
        attrs = vars(self).copy()
        exclusion = ('isExpanded', 'target_poses', 'hook_node', 'output_objs')
        for k in exclusion:
            del attrs[k]
        attrs['target_poses'] = { k: self.target_poses[k].data_dict(self.hook_node) for k in self.target_poses }
        attrs['hook_node'] = self.hook_node.name
        attrs['output_objs'] = [ obj.nodeName() for obj in self.output_objs ]
        return attrs



    @staticmethod
    def all_transforms_are_zero(transform_vals):
        for v in list(transform_vals.values()):
            if not -0.00001 < v < 0.00001:
                return False
        return True



    @staticmethod
    def reset_plug(plug):
        pm.setAttr(plug, 0)



    @staticmethod
    def get_output_objs(objs):
        for i, obj in enumerate(objs):
            if not type(obj) == str:
                continue
            if pm.objExists(obj):
                objs[i] = pm.PyNode(obj)
        return objs



# ----------------------------------------------------------------------------------------------------------------------
class HookNode:

    ANIM_CURVE_NODE_TYPES = ANIM_CURVE_NODE_TYPE
    HOOK_NODE_TYPE = HOOK_NODE_TYPE
    HOOK_NODE_ID_ATTR = HOOK_NODE_ID_ATTR
    WEIGHT_ATTR_NAME = 'Weight'
    OUTPUT_ATTR_NAME = 'OutputObjs'
    BLENDPOSE_DRIVER_ATTR_NAME = 'BlendposeDriver'
    TRANSFORM_ATTRS = TRANSFORM_ATTRS
    HOOK_NODE_SUFFIX = HOOK_NODE_SUFFIX

    def __init__(
        self,
        name = None,
        node = None
    ):
        self.name = name
        self.node = node
        self.blendpose_name = name



    @classmethod
    def produce(cls, name):
        node_name = name
        if pm.objExists(node_name):
            hook_node = cls.get_from_scene(node_name)
        else:
            hook_node = cls.create(node_name)
        return hook_node



    @classmethod
    def get_from_scene(cls, name):
        node = pm.PyNode(name)
        hook_node = HookNode(name=name, node=node)
        return hook_node



    @classmethod
    def create(cls, name):
        node_type = cls.HOOK_NODE_TYPE
        node = pm.shadingNode(node_type, name=name, au=1)
        hook_node = HookNode(name=name, node=node)
        hook_node.mark_node()
        hook_node.add_attrs_to_node()
        return hook_node



    def add_attrs_to_node(self):
        pm.addAttr(self.node, longName=self.WEIGHT_ATTR_NAME, attributeType='float', multi=1, keyable=1)
        pm.addAttr(self.node, longName=self.OUTPUT_ATTR_NAME, dataType='string', keyable=0)



    def mark_node(self):
        pm.addAttr(self.node, longName=self.HOOK_NODE_ID_ATTR, attributeType=bool, keyable=0)
        pm.setAttr(f'{self.node}.{self.HOOK_NODE_ID_ATTR}', 1, lock=1)



    def add_target_pose(self, target_pose):
        weight_attr_name = self.WEIGHT_ATTR_NAME
        weight_plug = f'{self.node}.{weight_attr_name}[{target_pose.weight_attr_index}]'
        pm.aliasAttr(target_pose.name, weight_plug)
        pm.setAttr(f'{self.node}.{weight_attr_name}[{target_pose.weight_attr_index}]', 1)
        if target_pose.driver:
            self.connect_target_pose_weight_attr(weight_plug, target_pose.driver)



    def connect_target_pose_weight_attr(self, weight_plug, driver_data):
        driver_node, driver_attr = driver_data
        if not pm.objExists(driver_node):
            return False
        if not pm.attributeQuery(driver_attr, node=weight_plug, exists=1):
            return False
        driver_plug = f'{driver_node}.{driver_attr}'
        pm.connectAttr(driver_plug, weight_plug)



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
        if not pm.attributeQuery(input_attr_name, node=obj, exists=1):
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



    def get_output_objs_from(self):
        return pm.listConnections(f'{self.node}.{self.OUTPUT_ATTR_NAME}', s=0, d=1, scn=1)



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
        weight_attr_index,
        key_frames = None,
        anim_curves = None,
        current_weight_value = None,
        float_range = None,
        slider_range = None,
        driver = None,
    ):
        self.name = name
        self.weight_attr_index = weight_attr_index
        self.key_frames = key_frames or []
        self.anim_curves = anim_curves
        self.current_weight_value = current_weight_value or 1
        self.float_range = float_range or [0, 1]
        self.slider_range = slider_range or [0, 1]
        self.driver = driver



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



    @classmethod
    def create_from_data(cls, **kwargs):
        inst_inputs = TargetPose._get_inst_inputs(**kwargs)

        if inst_inputs['anim_curves']:
            inst_inputs['anim_curves'] = [ AnimCurve.create_from_data(**data) for data in inst_inputs['anim_curves'] ]

        return TargetPose(**inst_inputs)



    @classmethod
    def _get_inst_inputs(cls, **kwargs):
        class_params = cls.__init__.__code__.co_varnames
        inst_inputs = {name: kwargs[name] for name in kwargs if name in class_params}
        return inst_inputs



    def get_float_range(self):
        default_pose_range = [0.0, 1.0]
        if not self.key_frames:
            return default_pose_range
        return [min(self.key_frames), max(self.key_frames)]



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
        [acrv.redirect_curve_connection(crv, old_attr, new_attr) for crv, new_attr, old_attr in attr_destination_pairs]



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
                acrv.update_anim_curve_node(needed_anim_curve, new_plug, driver_plug, value)
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
            self.sever_attr_outputs(node.output)
            pm.delete(node)



    def get_anim_curve_nodes(self, hook_node):
        return hook_node.get_connected_nodes_from_target(self.name)



    def export_anim_curves(self, hook_node):
        anim_curve_nodes = self.get_anim_curve_nodes(hook_node)
        anim_curves = [ AnimCurve.create_from_node(node) for node in anim_curve_nodes ]
        anim_curves_data = [curve.data_dict() for curve in anim_curves]
        return anim_curves_data



    def get_driver_plug(self, hook_node):
        target_pose_weight_plug = f'{hook_node.name}.Weight[{self.weight_attr_index}]'
        possible_driver_plugs = pm.listConnections(target_pose_weight_plug, s=1, d=0, scn=1, plugs=1)
        if not possible_driver_plugs:
            return None
        driving_node = pm.listConnections(target_pose_weight_plug, s=1, d=0, scn=1)[0]
        return [driving_node.nodeName(), str(possible_driver_plugs[0]).split('.', 1)[1]]



    def data_dict(self, hook_node):
        attrs = vars(self).copy()

        attrs['anim_curves'] = self.export_anim_curves(hook_node)
        attrs['driver'] = self.get_driver_plug(hook_node)

        return attrs



    @staticmethod
    def get_opposite_obj_via_name(obj):
        return gen.get_opposite_side_obj(obj)



    @staticmethod
    def sever_attr_outputs(attr):
        node = acrv.get_node_from_attr(attr)
        for plug in pm.listConnections(attr, s=0, d=1, plugs=1, scn=1):
            acrv.disconnect_anim_curve(node, plug)


    # ------------------------------------------------------------------------------------------------------------------
    blendposes = {
        'Face': {
            'name': 'Face',
            'target_pose_order': [
                'JawVert',
                'JawHor'
            ],
            'target_poses': {
                'JawVert': {
                    'name': 'JawVert',
                    'weight_attr_index': 0,
                    'key_frames': [
                        0.0,
                        1.0
                    ],
                    'current_weight_value': 1.0,
                    'float_range': (
                        0.0,
                        1.0
                    ),
                    'slider_range': [
                        0,
                        1
                    ]
                },
                'JawHor': {
                    'name': 'JawHor',
                    'weight_attr_index': 1,
                    'key_frames': [],
                    'current_weight_value': 1.0,
                    'float_range': [
                        0,
                        1
                    ],
                    'slider_range': [
                        0,
                        1
                    ]
                }
            },
            'hook_node': 'Face',
            'output_objs': [
                'bind_jaw'
            ]
        }
    }
