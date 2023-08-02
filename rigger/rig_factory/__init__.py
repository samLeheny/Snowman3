import os
import json
import Snowman3.rigger.rig_factory.utilities.node_utilities.name_utilities as name_utils

active_controller = None

settings_path = '{}/settings.json'.format(os.path.dirname(__file__.replace('\\', '/')))
with open(settings_path, mode='r') as f:
    settings_data = json.load(f)

index_dictionary = name_utils.index_dictionary  # index_dictionary[4] = 'd' but no order in dict
index_list = name_utils.index_list  # index_list[4] = 'd' and can get index from index_list.index('d')

roo_dict = dict(xyz=0, yzx=1, zxy=2, xzy=3, yxz=4, zyx=5)


class BipedRotateOrder:
    """
    Why does this need to be a class - Maybe a Dict instead? -Paxton
    """
    def __init__(self):
        self.main_ground = roo_dict['xzy']
        self.main_cog = roo_dict['xzy']
        self.spine_hip = roo_dict['xzy']
        self.spine_hip_gimbal = roo_dict['xyz']
        self.spine_mid_fk = roo_dict['xzy']
        self.spine_mid_ik = roo_dict['yzx']
        self.spine_chest = roo_dict['xzy']
        self.spine_chest_gimbal = roo_dict['xzy']
        self.neck = roo_dict['xzy']
        self.head = roo_dict['xzy']
        self.head_gimbal = roo_dict['zxy']
        self.arm_clavicle = roo_dict['yzx']
        self.arm_bendy = roo_dict['xyz']
        self.arm_upper_fk = roo_dict['zyx']
        self.arm_lower_fk = roo_dict['xyz']
        self.arm_wrist_fk = roo_dict['xzy']
        self.arm_wrist_fk_gimbal = roo_dict['zyx']
        self.arm_ik = roo_dict['xyz']
        self.fingers = roo_dict['xyz']
        self.leg_hip = roo_dict['xzy']
        self.leg_fk = roo_dict['xyz']
        self.leg_bendy = roo_dict['xyz']
        self.leg_ik = roo_dict['xyz']
