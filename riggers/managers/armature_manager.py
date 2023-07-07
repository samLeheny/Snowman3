# Title: armature_manager.py
# Author: Sam Leheny
# Contact: samleheny@live.com

# Description:


###########################
##### Import Commands #####
import importlib
import pymel.core as pm

import Snowman3.utilities.general_utils as gen
importlib.reload(gen)

import Snowman3.riggers.managers.blueprint_manager as blueprint_manager_util
importlib.reload(blueprint_manager_util)
BlueprintManager = blueprint_manager_util.BlueprintManager

import Snowman3.riggers.utilities.part_utils as part_utils
importlib.reload(part_utils)
ScenePartManager = part_utils.ScenePartManager

import Snowman3.riggers.utilities.poseConstraint_utils as postConstraint_utils
importlib.reload(postConstraint_utils)
PostConstraintManager = postConstraint_utils.PostConstraintManager
###########################
###########################

###########################
######## Variables ########

###########################
###########################



########################################################################################################################
class ArmatureManager:
    def __init__(
        self
    ):
        self.scene_root = None
        self.armature_grp = None


    def build_armature_from_blueprint(self, blueprint):
        print("Building armature in scene from blueprint...")
        self.create_scene_armature_root(blueprint.asset_name)
        self.add_parts_from_blueprint(blueprint=blueprint)
        self.add_post_constraints(blueprint.post_constraints, blueprint.parts)


    def add_parts_from_blueprint(self, blueprint):
        for part in blueprint.parts.values():
            self.add_part(part)


    def add_post_constraints(self, post_constraints, parts):
        for data in post_constraints:
            source_scene_placer = self.get_scene_placer(data.source_placer, parts[data.source_part])
            target_scene_placer = self.get_scene_placer(data.target_placer, parts[data.target_part])
            if not all((source_scene_placer, target_scene_placer)):
                continue
            self.constrain_placer(source_scene_placer, target_scene_placer)
            if data.hide_target_placer:
                self.hide_placer(data.target_placer, parts[data.target_part])


    def add_part(self, part):
        parent = self.armature_grp
        scene_part_manager = ScenePartManager(part)
        scene_part = scene_part_manager.create_scene_part()
        scene_part.setParent(parent)
        pm.select(clear=1)
        return scene_part


    @staticmethod
    def remove_part(part):
        pm.delete(pm.PyNode(part.scene_name))


    def mirror_part(self, part):
        self.mirror_part_handle(part)
        self.mirror_part_placers(part)


    @staticmethod
    def mirror_part_handle(part, scale_attr='HandleSize'):
        scene_part_handle = pm.PyNode(part.scene_name)
        opposite_scene_part_handle = gen.get_opposite_side_obj(scene_part_handle)
        if not opposite_scene_part_handle:
            return False

        scene_part_handle_position = scene_part_handle.translate.get()
        scene_part_handle_position[0] = -scene_part_handle_position[0]
        opposite_scene_part_handle.translate.set(scene_part_handle_position)

        scene_part_handle_rotation = scene_part_handle.rotate.get()
        scene_part_handle_rotation[1] = -scene_part_handle_rotation[1]
        scene_part_handle_rotation[2] = -scene_part_handle_rotation[2]
        opposite_scene_part_handle.rotate.set(scene_part_handle_rotation)

        scene_part_handle_scale = pm.getAttr(f'{scene_part_handle}.{scale_attr}')
        pm.setAttr(f'{opposite_scene_part_handle}.{scale_attr}', scene_part_handle_scale)


    def mirror_part_placers(self, part):
        for key in part.placers.keys():
            self.mirror_placer_position(key, part)
            self.mirror_vector_handle_positions(key, part)
            self.mirror_orienter_rotation(key, part)


    def mirror_placer_position(self, placer_key, part):
        placer = part.placers[placer_key]
        if placer.is_pole_vector:
            self.mirror_pole_vector_placer(placer_key, part)
        else:
            scene_placer = self.get_scene_placer(placer_key, part)
            opposite_scene_placer = gen.get_opposite_side_obj(scene_placer)
            if not opposite_scene_placer:
                return False
            if opposite_scene_placer.translate.get(lock=1):
                return False
            scene_placer_local_position = list(scene_placer.translate.get())
            scene_placer_local_position[0] = -scene_placer_local_position[0]
            opposite_scene_placer.translate.set(tuple(scene_placer_local_position))


    def mirror_pole_vector_placer(self, placer_key, part):
        distance_attr_name = 'Distance'
        scene_placer = self.get_scene_placer(placer_key, part)
        opposite_scene_placer = gen.get_opposite_side_obj(scene_placer)
        scene_placer_pv_distance = pm.getAttr(f'{scene_placer}.{distance_attr_name}')
        pm.setAttr(f'{opposite_scene_placer}.{distance_attr_name}', scene_placer_pv_distance)


    def mirror_vector_handle_positions(self, placer_key, part):
        placer = self.get_placer(placer_key, part)
        def process_handle(vector):
            handle_name = f'{gen.side_tag(placer.side)}{placer.part_name}_{placer.name}_{vector}'
            if not pm.objExists(handle_name):
                return False
            scene_handle = pm.PyNode(handle_name)
            opposite_scene_handle = gen.get_opposite_side_obj(scene_handle)
            if not opposite_scene_handle:
                return False
            scene_handle_position = list(scene_handle.translate.get())
            scene_handle_position[0] = -scene_handle_position[0]
            opposite_scene_handle.translate.set(scene_handle_position)
        process_handle('AIM')
        process_handle('UP')


    def mirror_orienter_rotation(self, placer_key, part):
        scene_orienter = self.get_scene_orienter(placer_key, part)
        opposite_scene_orienter = gen.get_opposite_side_obj(scene_orienter)
        if not opposite_scene_orienter:
            return False
        scene_orienter_rotation = scene_orienter.rotate.get()
        opposite_scene_orienter.rotate.set(tuple(scene_orienter_rotation))


    @staticmethod
    def get_placer(placer_key, part):
        return part.placers[placer_key]


    def get_scene_placer(self, placer_key, part):
        placer = self.get_placer(placer_key, part)
        if not pm.objExists(placer.scene_name):
            return None
        return pm.PyNode(placer.scene_name)


    def get_scene_orienter(self, placer_key, part):
        placer = self.get_placer(placer_key, part)
        orienter_name = f"{gen.side_tag(placer.side)}{placer.part_name}_{placer.name}_ORI"
        if not pm.objExists(orienter_name):
            return None
        return pm.PyNode(orienter_name)


    @staticmethod
    def constrain_placer(source, target):
        transform_attrs = ('translate', 'rotate', 'scale', 'tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz')
        for attr in transform_attrs:
            pm.setAttr(f'{target}.{attr}', lock=0)
            gen.break_connections(f'{target}.{attr}')
        pm.parentConstraint(source, target, mo=1)
        pm.scaleConstraint(source, target, mo=1)


    def hide_placer(self, placer_key, part):
        scene_placer = self.get_scene_placer(placer_key, part)
        scene_placer.visibility.set(lock=0)
        scene_placer.visibility.set(0, lock=1)


    def create_scene_armature_root(self, scene_root_name):
        armature_grp_name = 'Armature'
        self.scene_root = pm.shadingNode('transform', name=scene_root_name, au=1)
        #gen.set_color(self.scene_root, 2)
        self.armature_grp = pm.group(name=armature_grp_name, em=1, p=self.scene_root)


    def hide_armature(self, lock_visibility=1):
        self.armature_grp.visibility.set(0, lock=lock_visibility)
