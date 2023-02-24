# Title: modules.py
# Author: Sam Leheny
# Contact: samleheny@live.com

# Description:


###########################
##### Import Commands #####
import importlib
import Snowman3.riggers.utilities.classes.class_ArmatureModule as armatureModule
importlib.reload(armatureModule)
Module = armatureModule.ArmatureModule
###########################
###########################


###########################
######## Variables ########

###########################
###########################





def create_modules():

    modules = {

        'root':
            Module(
                rig_module_type = 'root',
                name = 'root',
                color = [0.6, 0.6, 0.6],
                position = (0, 0, 0)
            ),


        'spine':
            Module(
                rig_module_type = 'biped_spine',
                name = 'spine',
                position = (0, 101, 0.39)
            ),


        'neck':
            Module(
                rig_module_type = 'biped_neck',
                name = 'neck',
                position = (0, 150, 0.39),
                drive_target = {'neck': (('spine', 'spine_6'),)}
            ),


        'L_clavicle':
            Module(
                rig_module_type = 'biped_clavicle',
                name = 'clavicle',
                side = 'L',
                position = (3, 146.88, 0.39),
                draw_connections = {'clavicle': (('spine', 'spine_5'),)}
            ),


        'R_clavicle':
            Module(
                rig_module_type = 'biped_clavicle',
                name = 'clavicle',
                side = 'R',
                position = (3, 146.88, 0.39),
                draw_connections = {'clavicle': (('spine', 'spine_5'),)}
            ),


        'L_arm':
            Module(
                rig_module_type = 'biped_arm',
                name = 'arm',
                side = 'L',
                position = (15, 146.88, 0.39),
                drive_target = {'upperarm': (('L_clavicle', 'clavicle_end'),)}
            ),


        'R_arm':
            Module(
                rig_module_type = 'biped_arm',
                name = 'arm',
                side = 'R',
                position = (15, 146.88, 0.39),
                drive_target = {'upperarm': (('R_clavicle', 'clavicle_end'),)}
            ),


        'L_hand':
            Module(
                rig_module_type = 'biped_hand',
                name = 'hand',
                side = 'L',
                position = (67.64, 146.88, 0.39),
                drive_target = {'hand': (('L_arm', 'lowerarm_end'),
                                         ('L_arm', 'wrist_end'))}
            ),


        'R_hand':
            Module(
                rig_module_type = 'biped_hand',
                name = 'hand',
                side = 'R',
                position = (67.64, 146.88, 0.39),
                drive_target = {'hand': (('R_arm', 'lowerarm_end'),
                                         ('R_arm', 'wrist_end'))}
            ),


        'L_leg':
            Module(
                rig_module_type = 'leg_plantigrade',
                name = 'leg',
                side = 'L',
                position = (8.5, 101, 0.39),
                draw_connections = {'thigh': (('spine', 'spine_1'),)}
            ),


        'R_leg':
            Module(
                rig_module_type = 'leg_plantigrade',
                name = 'leg',
                side = 'R',
                position = (8.5, 101, 0.39),
                draw_connections = {'thigh': (('spine', 'spine_1'),)}
            ),


        'L_foot':
            Module(
                rig_module_type = 'foot_plantigrade',
                name = 'foot',
                side = 'L',
                position = (8.5, 10, 0.39),
                drive_target = {'foot': (('L_leg', 'calf_end'),
                                         ('L_leg', 'ankle_end'))}
            ),


        'R_foot':
            Module(
                rig_module_type = 'foot_plantigrade',
                name = 'foot',
                side = 'R',
                position = (8.5, 10, 0.39),
                drive_target = {'foot': (('R_leg', 'calf_end'), ('R_leg', 'ankle_end'))}
            )

    }

    return modules
