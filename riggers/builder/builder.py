# Title: builder.py
# Author: Sam Leheny
# Contact: samleheny@live.com

# Description:


###########################
##### Import Commands #####
import os
import importlib

import Snowman3.riggers.utilities.classes.class_Blueprint as class_Blueprint
importlib.reload(class_Blueprint)
Blueprint = class_Blueprint.Blueprint

import Snowman3.riggers.IO.blueprint_IO as class_BlueprintIO
importlib.reload(class_BlueprintIO)
BlueprintIO = class_BlueprintIO.BlueprintIO
###########################
###########################

###########################
######## Variables ########
temp_files_dir = 'working'
versions_dir = 'versions'
version_padding = 4
###########################
###########################


class RigBuilder:
    def __init__(
        self,
        asset_name = None,
        prefab_key = None,
        dirpath = None
    ):
        self.asset_name = asset_name
        self.prefab_key = prefab_key
        self.dirpath = f'{dirpath}'
        self.tempdir = f'{self.dirpath}/{temp_files_dir}'
        self.versions_dir = f'{self.dirpath}/{versions_dir}'


    ####################################################################################################################
    def create_new_blueprint(self):
        print('Creating new blueprint...')
        blueprint = Blueprint(asset_name=self.asset_name, dirpath=self.dirpath)
        self.create_working_dir()
        self.create_versions_dir()
        self.save_blueprint_to_tempdisk(blueprint)


    ####################################################################################################################
    def save_blueprint_to_tempdisk(self, blueprint):
        blueprint_io = BlueprintIO(blueprint=blueprint)
        blueprint_io.save(self.tempdir)


    ####################################################################################################################
    def create_working_dir(self):
        if not os.path.exists(self.tempdir):
            os.mkdir(self.tempdir)


    ####################################################################################################################
    def create_versions_dir(self):
        if not os.path.exists(self.versions_dir):
            os.mkdir(self.versions_dir)


    ####################################################################################################################
    def save_work(self):
        print('Saving work...')
        working_blueprint = self.get_blueprint_from_working_dir()
        updated_working_blueprint = self.update_blueprint_from_scene(working_blueprint)
        self.save_blueprint_to_disk(updated_working_blueprint)
        self.save_blueprint_to_tempdisk(updated_working_blueprint)


    ####################################################################################################################
    def get_blueprint_from_working_dir(self):
        print("Fetching current working blueprint...")
        blueprint_io = BlueprintIO()
        blueprint = blueprint_io.load(self.tempdir)
        return blueprint


    ####################################################################################################################
    def update_blueprint_from_scene(self, blueprint):
        print("Updating working blueprint with scene data...")
        return blueprint


    ####################################################################################################################
    def save_blueprint_to_disk(self, blueprint):
        print("Saving work to disk...")
        asset_name = blueprint.asset_name
        new_save_dir = self.create_new_numbered_directory(asset_name)
        blueprint_io = BlueprintIO(blueprint=blueprint)
        blueprint_io.save(new_save_dir)


    ####################################################################################################################
    def create_new_numbered_directory(self, asset_name, version_padding=version_padding):
        version_dirs = [p[0] for p in os.walk(self.versions_dir)]
        version_subdirs = [version_dirs[i] for i in range(1, len(version_dirs))]
        subdir_names = [os.path.basename(os.path.normpath(p)) for p in version_subdirs]
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

