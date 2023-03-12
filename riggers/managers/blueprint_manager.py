# Title: blueprint_manager.py
# Author: Sam Leheny
# Contact: samleheny@live.com

# Description:


###########################
##### Import Commands #####
import os
import importlib

import Snowman3.utilities.general_utils as gen
importlib.reload(gen)

import Snowman3.riggers.utilities.blueprint_utils as blueprint_utils
importlib.reload(blueprint_utils)
Blueprint = blueprint_utils.Blueprint

import Snowman3.riggers.utilities.placer_utils as placer_utils
importlib.reload(placer_utils)
Placer = placer_utils.Placer
###########################
###########################

###########################
######## Variables ########
temp_files_dir = 'working'
versions_dir = 'versions'
version_padding = 4
###########################
###########################



class BlueprintManager:
    def __init__(
        self,
        asset_name: str = None,
        prefab_key: str = None,
        dirpath: str = None
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
        blueprint_utils.save_blueprint(dirpath=self.tempdir, blueprint=blueprint)



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
        blueprint = blueprint_utils.blueprint_from_file(self.tempdir)
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
        blueprint_utils.save_blueprint(dirpath=new_save_dir, blueprint=blueprint)



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



    ####################################################################################################################
    def test(self, num):

        '''import Snowman3.riggers.modules.root.data.placers as placers
        module_placers = placers.placers

        for placer in module_placers:
            placer_utils.create_scene_placer(placer=placer)'''

        import Snowman3.riggers.utilities.part_utils as part_utils
        importlib.reload(part_utils)
        Part = part_utils.Part

        import Snowman3.riggers.utilities.module_utils as module_utils
        importlib.reload(module_utils)
        Module = module_utils.Module

        m1 = Module(name='spine', side=None)
        m2 = Module(name='pelvis', side=None)

        if num == 1:
            blueprint = blueprint_utils.blueprint_from_file(self.tempdir)
            for module in (m1, m2):
                blueprint_utils.create_scene_module(module)
                L_test_part = Part(name='arm', side='L', handle_size=None, position=[3, 0, 0])
                R_test_part = Part(name='arm', side='R', handle_size=None, position=[-3, 0, 0])
                blueprint_utils.create_part(L_test_part, module)
                blueprint_utils.create_part(R_test_part, module)

        '''if num == 2:
            L_test_part = Part(name='arm', side='L', handle_size=None, position=[3, 0, 0],
                               scene_name='L_spine_arm_PART')
            blueprint_utils.remove_part_from_module(L_test_part, m1)'''

        if num == 2:
            blueprint = blueprint_utils.blueprint_from_file(self.tempdir)
            for module in (m1, m2):
                module_key = f'{gen.side_tag(module.side)}{module.name}'
                blueprint_utils.mirror_module(blueprint, module_key)

        if num == 3:
            blueprint = blueprint_utils.blueprint_from_file(self.tempdir)
            blueprint_utils.update_blueprint_from_scene(blueprint)

        if num == 4:
            blueprint = blueprint_utils.blueprint_from_file(self.tempdir)
            m = module_utils.module_from_data(blueprint.modules['spine'])
            p = part_utils.part_from_data(m.parts['L_arm'])
            L_x_placer = Placer(name='shoulder', side='L', position=(4, 5, 6), size=1.1)
            blueprint_utils.create_placer(L_x_placer, p, m)
