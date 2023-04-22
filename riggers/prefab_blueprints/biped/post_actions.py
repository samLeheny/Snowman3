# Title: post_actions.py
# Author: Sam Leheny
# Contact: samleheny@live.com

# Description:


###########################
##### Import Commands #####
import importlib

import Snowman3.riggers.utilities.poseConstraint_utils as postConstraint_utils
importlib.reload(postConstraint_utils)
PostConstraint = postConstraint_utils.PostConstraint
###########################
###########################


###########################
######## Variables ########

###########################
###########################


def run_post_actions(blueprint):
    blueprint = make_inter_part_attachments(blueprint)
    return blueprint


def make_inter_part_attachments(blueprint):
    constraints_list = []
    def sided_data(side):
        constraint_data_sets = [
            PostConstraint(f'{side}_Arm', 'Upperarm', f'{side}_Clavicle', 'ClavicleEnd', True),
            PostConstraint(f'{side}_Hand', 'Wrist', f'{side}_Arm', 'ForearmEnd', True),
            PostConstraint(f'{side}_Hand', 'Wrist', f'{side}_Arm', 'WristEnd', False),
            PostConstraint(f'{side}_Foot', 'Foot', f'{side}_Leg', 'ShinEnd', True),
            PostConstraint(f'{side}_Foot', 'Foot', f'{side}_Leg', 'AnkleEnd', False),
        ]
        return constraint_data_sets
    for side in ('L', 'R'):
        for data_set in sided_data(side):
            constraints_list.append(data_set)
    blueprint.post_constraints = constraints_list
    return blueprint

