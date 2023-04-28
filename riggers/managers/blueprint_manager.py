# Title: blueprint_manager.py
# Author: Sam Leheny
# Contact: samleheny@live.com

# Description:


###########################
##### Import Commands #####
import os
from dataclasses import dataclass, field
from typing import Sequence
import importlib
import pymel.core as pm
import json

import Snowman3.utilities.general_utils as gen
importlib.reload(gen)

import Snowman3.riggers.utilities.part_utils as part_utils
importlib.reload(part_utils)
PartManager = part_utils.PartManager
Part = part_utils.Part

import Snowman3.riggers.utilities.poseConstraint_utils as postConstraint_utils
importlib.reload(postConstraint_utils)
PostConstraintManager = postConstraint_utils.PostConstraintManager
PostConstraint = postConstraint_utils.PostConstraint
###########################
###########################

###########################
######## Variables ########
temp_files_dir = 'working'
versions_dir = 'versions'
core_data_filename = 'core_data'
default_version_padding = 4
###########################
###########################


########################################################################################################################
@dataclass
class Blueprint:
    asset_name: str
    dirpath: str = None
    parts: dict = field(default_factory=dict)
    post_constraints: dict = field(default_factory=list)
    custom_constraints: Sequence = field(default_factory=list)
    kill_ctrls: Sequence = field(default_factory=list)
    attribute_handoffs: dict = field(default_factory=list)


########################################################################################################################
class BlueprintManager:
    def __init__(
        self,
        asset_name: str = None,
        prefab_key: str = None,
        dirpath: str = None,
        blueprint = None
    ):
        self.asset_name = asset_name
        self.prefab_key = prefab_key
        self.dirpath = f'{dirpath}'
        self.tempdir = f'{self.dirpath}/{temp_files_dir}'
        self.versions_dir = f'{self.dirpath}/{versions_dir}'
        self.blueprint = blueprint



    def create_blueprint_from_prefab(self):
        print(f"Creating blueprint from prefab: '{self.prefab_key}'...")
        self.blueprint = self.create_new_blueprint()
        self.populate_prefab_blueprint()
        return self.blueprint


    def populate_prefab_blueprint(self):
        self.populate_blueprint_parts()
        self.populate_blueprint_custom_constraints()
        self.populate_blueprint_kill_ctrls()
        self.populate_blueprint_attr_handoffs()
        self.populate_blueprint_hierarchy()


    def populate_blueprint_attr_handoffs(self):
        dir_string = 'Snowman3.riggers.prefab_blueprints.{}.attr_handoffs'
        attr_handoffs = importlib.import_module(dir_string.format(self.prefab_key))
        importlib.reload(attr_handoffs)
        attr_handoffs_data = [vars(data) for data in attr_handoffs.inputs]
        self.blueprint.attribute_handoffs = attr_handoffs_data


    def populate_blueprint_hierarchy(self):
        dir_string = 'Snowman3.riggers.prefab_blueprints.{}.hierarchy'
        hierarchy = importlib.import_module(dir_string.format(self.prefab_key))
        importlib.reload(hierarchy)
        for part_key, parent_node_name in hierarchy.inputs:
            if part_key not in self.blueprint.parts:
                continue
            self.blueprint.parts[part_key].parent = parent_node_name


    def populate_blueprint_parts(self):
        dir_string = 'Snowman3.riggers.prefab_blueprints.{}.parts'
        prefab_parts = importlib.import_module(dir_string.format(self.prefab_key))
        importlib.reload(prefab_parts)
        self.blueprint.parts = prefab_parts.parts


    def populate_blueprint_custom_constraints(self):
        dir_string = 'Snowman3.riggers.prefab_blueprints.{}.custom_constraints'
        custom_constraints = importlib.import_module(dir_string.format(self.prefab_key))
        importlib.reload(custom_constraints)
        for constraint in custom_constraints.inputs:
            self.add_custom_constraint(constraint)
        #constraint_data = [vars(data) for data in custom_constraints.inputs]
        #self.blueprint.custom_constraints = constraint_data


    def add_custom_constraint(self, constraint):
        constraint_data = vars(constraint)
        self.blueprint.custom_constraints.append(constraint_data)


    def populate_blueprint_kill_ctrls(self):
        dir_string = 'Snowman3.riggers.prefab_blueprints.{}.kill_ctrls'
        kill_ctrls = importlib.import_module(dir_string.format(self.prefab_key))
        importlib.reload(kill_ctrls)
        ctrl_data = [vars(data) for data in kill_ctrls.inputs]
        self.blueprint.kill_ctrls = ctrl_data


    def create_new_blueprint(self):
        print(f"Creating new blueprint for asset '{self.asset_name}'...")
        self.blueprint = Blueprint(asset_name=self.asset_name, dirpath=self.tempdir)
        self.create_working_dir()
        self.create_versions_dir()
        return self.blueprint


    def load_blueprint_from_numbered_version(self, number):
        version_dir = self.get_numbered_version_dir(number)
        version_blueprint_filepath = f'{version_dir}/{core_data_filename}.json'
        self.blueprint_from_file(version_blueprint_filepath)


    def get_numbered_version_dir(self, number, version_padding=default_version_padding):
        padded_num_string = str(number).rjust(version_padding, '0')
        subdir_names = self.get_all_numbered_subdir_names()
        version_dir_string = f'{self.asset_name}-v{padded_num_string}'
        if version_dir_string not in subdir_names:
            return False
        dir = f'{self.versions_dir}/{version_dir_string}'
        return dir


    def load_blueprint_from_latest_version(self):
        latest_version_dir = self.get_latest_numbered_directory()
        latest_version_blueprint_filepath = f'{latest_version_dir}/{core_data_filename}.json'
        self.blueprint_from_file(latest_version_blueprint_filepath)


    def get_latest_numbered_directory(self):
        subdir_names = self.get_all_numbered_subdir_names()
        nums = [name.split('-v')[1] for name in subdir_names]
        latest_dir_string = f'{self.asset_name}-v{nums[-1]}'
        latest_dir_filepath = f'{self.versions_dir}/{latest_dir_string}'
        return latest_dir_filepath


    def save_blueprint_to_tempdisk(self):
        self.save_blueprint(self.tempdir)


    def create_working_dir(self):
        if not os.path.exists(self.tempdir):
            print("Asset 'working' directory created.")
            os.mkdir(self.tempdir)


    def create_versions_dir(self):
        if not os.path.exists(self.versions_dir):
            print("Asset 'versions' directory created.")
            os.mkdir(self.versions_dir)


    def save_work(self):
        print('Saving work...')
        self.update_blueprint_from_scene()
        self.save_blueprint_to_disk()
        self.save_blueprint_to_tempdisk()


    def get_blueprint_from_working_dir(self):
        self.blueprint = self.blueprint_from_file(f'{self.tempdir}/{core_data_filename}.json')
        return self.blueprint


    def update_blueprint_from_scene(self):
        for key, part in self.blueprint.parts.items():
            self.blueprint.parts[key] = self.update_part_from_scene(part)
        return self.blueprint


    def update_part_from_scene(self, part):
        scene_handle = pm.PyNode(part.scene_name)
        part.position = tuple(scene_handle.translate.get())
        part.rotation = tuple(scene_handle.rotate.get())
        part.scale = pm.getAttr(f'{scene_handle}.{"HandleSize"}')
        part = self.update_part_placers_from_scene(part)
        part = self.update_part_controls_from_scene(part)
        return part


    def update_part_placers_from_scene(self, part):
        for key, placer in part.placers.items():
            part.placers[key] = self.update_placer_from_scene(placer)
            part.placers[key] = self.update_vector_handles_from_scene(placer)
        return part


    def update_part_controls_from_scene(self, part):
        for key, ctrl in part.controls.items():
            part.controls[key] = self.update_control_shape_from_scene(ctrl)
        return part


    def update_placer_from_scene(self, placer):
        scene_placer = pm.PyNode(placer.scene_name)
        placer.position = tuple(scene_placer.translate.get())
        placer.rotation = tuple(scene_placer.rotate.get())
        return placer


    def update_vector_handles_from_scene(self, placer):
        def process_handle(vector):
            handle_name = f'{gen.side_tag(placer.side)}{placer.parent_part_name}_{placer.name}_{vector}'
            if not pm.objExists(handle_name):
                return False
            scene_vector_handle = pm.PyNode(handle_name)
            position = list(scene_vector_handle.translate.get())
            if vector == 'AIM':
                placer.vector_handle_positions[0] = position
            elif vector == 'UP':
                placer.vector_handle_positions[1] = position
        process_handle('AIM')
        process_handle('UP')
        return placer


    def update_control_shape_from_scene(self, ctrl):
        if not pm.objExists(ctrl.scene_name):
            return ctrl
        scene_ctrl = pm.PyNode(ctrl.scene_name)
        ctrl_shape_data = gen.get_shape_data_from_obj(scene_ctrl)
        ctrl.shape = ctrl_shape_data
        return ctrl


    def save_blueprint_to_disk(self):
        print("Saving work to disk...")
        asset_name = self.blueprint.asset_name
        new_save_dir = self.create_new_numbered_directory(asset_name)
        self.save_blueprint(dirpath=new_save_dir)


    def get_all_numbered_subdirs(self):
        version_dirs = [p[0] for p in os.walk(self.versions_dir)]
        version_subdirs = [version_dirs[i] for i in range(1, len(version_dirs))]
        return version_subdirs


    def get_all_numbered_subdir_names(self):
        version_subdirs = self.get_all_numbered_subdirs()
        subdir_names = [os.path.basename(os.path.normpath(p)) for p in version_subdirs]
        return subdir_names


    def create_new_numbered_directory(self, asset_name, version_padding=default_version_padding):
        version_subdirs = self.get_all_numbered_subdirs()
        subdir_names = self.get_all_numbered_subdir_names()
        if not version_subdirs:
            bulked_num = str(1).rjust(version_padding, '0')
            new_dir_string = f'{asset_name}-v{bulked_num}'
        else:
            nums = [name.split('-v')[1] for name in subdir_names]
            next_num = int(max(nums)) + 1
            bulked_num = str(next_num).rjust(version_padding, '0')
            new_dir_string = f'{asset_name}-v{bulked_num}'
        new_dir = f'{self.versions_dir}/{new_dir_string}'
        os.mkdir(new_dir)
        return new_dir


    def blueprint_from_file(self, filepath):
        blueprint_data = self.data_from_file(filepath)
        self.blueprint = self.blueprint_from_data(blueprint_data)
        return self.blueprint


    def data_from_file(self, filepath):
        with open(filepath, 'r') as fh:
            data = json.load(fh)
        return data


    def blueprint_from_data(self, data):
        self.blueprint = Blueprint(**data)
        self.blueprint.parts = self.parts_from_data(self.blueprint.parts)
        self.blueprint.post_constraints = self.post_constraints_from_data(self.blueprint.post_constraints)
        return self.blueprint


    def parts_from_data(self, parts_data):
        parts = {}
        for key, data in parts_data.items():
            new_part = Part(**data)
            manager = PartManager(new_part)
            manager.create_placers_from_data(new_part.placers)
            manager.create_controls_from_data(new_part.controls)
            parts[key] = manager.part
        return parts


    def post_constraints_from_data(self, post_constraints_data):
        post_constraints = []
        for data in post_constraints_data:
            post_constraints.append(PostConstraint(**data))
        return post_constraints


    def data_from_blueprint(self):
        data = vars(self.blueprint).copy()
        data['parts'] = self.parts_data_from_blueprint(self.blueprint.parts)
        data['post_constraints'] = self.post_constraints_data_from_blueprints(self.blueprint.post_constraints)
        return data


    def parts_data_from_blueprint(self, parts):
        data = {}
        for key, part in parts.items():
            manager = PartManager(part)
            data[key] = manager.data_from_part()
        return data


    def post_constraints_data_from_blueprints(self, post_constraints):
        data = []
        for post_constraint in post_constraints:
            manager = PostConstraintManager(post_constraint)
            data.append(manager.data_from_post_constraint())
        return data


    def data_from_part(self, part):
        part_manager = PartManager(part)
        return part_manager.data_from_part()


    def save_blueprint(self, dirpath=None):
        if not dirpath:
            dirpath = self.dirpath
        blueprint_data = self.data_from_blueprint()
        filepath = f'{dirpath}/{core_data_filename}.json'
        with open(filepath, 'w') as fh:
            json.dump(blueprint_data, fh, indent=5)


    def add_part(self, part):
        self.blueprint.parts[part.data_name] = part


    def remove_part(self, part):
        self.blueprint.parts.pop(part.data_name)


    def get_part(self, part_key):
        return self.blueprint.parts[part_key]


    def run_prefab_post_actions(self):
        dir_string = 'Snowman3.riggers.prefab_blueprints.{}.post_actions'
        prefab_post_actions = importlib.import_module(dir_string.format(self.prefab_key))
        importlib.reload(prefab_post_actions)
        self.blueprint = prefab_post_actions.run_post_actions(self.blueprint)
