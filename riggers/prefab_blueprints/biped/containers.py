# Title: containers.py
# Author: Sam Leheny
# Contact: samleheny@live.com

# Description:


###########################
##### Import Commands #####
import importlib

import Snowman3.riggers.containers.rig_container_utils as rig_container_utils
importlib.reload(rig_container_utils)
ContainerCreator = rig_container_utils.ContainerCreator
ContainerData = rig_container_utils.ContainerData
###########################
###########################


###########################
######## Variables ########

###########################
###########################


containers = {}
container_inputs = [
    ContainerData('Root', 'root', 'M', (0, 0, 0)),
    ContainerData('Spine', 'biped_spine', 'M', (0, 101, 0.39)),
    ContainerData('Neck', 'biped_neck', 'M', (0, 150, 0.39)),
    ContainerData('Clavicle', 'biped_clavicle', 'L', (3, 146.88, 0.39)),
    ContainerData('Clavicle', 'biped_clavicle', 'R', (3, 146.88, 0.39)),
    ContainerData('Arm', 'biped_arm', 'L', (15, 146.88, 0.39)),
    ContainerData('Arm', 'biped_arm', 'R', (15, 146.88, 0.39)),
    ContainerData('Hand', 'biped_hand', 'L', (67.64, 146.88, 0.39)),
    ContainerData('Hand', 'biped_hand', 'R', (67.64, 146.88, 0.39)),
    ContainerData('Leg', 'leg_plantigrade', 'L', (8.5, 101, 0.39)),
    ContainerData('Leg', 'leg_plantigrade', 'R', (8.5, 101, 0.39)),
    ContainerData('Foot', 'foot_plantigrade', 'L', (8.5, 10, 0.39)),
    ContainerData('Foot', 'foot_plantigrade', 'R', (8.5, 10, 0.39)),
]

for container_data in container_inputs:
    container_creator = ContainerCreator(container_data)
    containers[f'{container_data.side}_{container_data.name}'] = container_creator.create_container()
