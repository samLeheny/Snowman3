# Title: placers.py
# Author: Sam Leheny
# Contact: samleheny@live.com

# Description:


###########################
##### Import Commands #####
import importlib
import Snowman3.riggers.utilities.classes.class_PlacerConnector as classPlacerConnector
importlib.reload(classPlacerConnector)
PlacerConnector = classPlacerConnector.PlacerConnector
###########################
###########################


###########################
######## Variables ########

###########################
###########################





def create_placer_connectors():

    placer_connectors = (


        PlacerConnector(
            source_module_key = 'L_clavicle',
            source_placer_key = 'clavicle',
            destination_module_key = 'spine',
            destination_placer_key = 'spine_5'
        ),

        PlacerConnector(
            source_module_key = 'R_clavicle',
            source_placer_key = 'clavicle',
            destination_module_key = 'spine',
            destination_placer_key = 'spine_5'
        ),

        PlacerConnector(
            source_module_key='L_leg',
            source_placer_key='thigh',
            destination_module_key='spine',
            destination_placer_key='spine_1'
        ),

        PlacerConnector(
            source_module_key='R_leg',
            source_placer_key='thigh',
            destination_module_key='spine',
            destination_placer_key='spine_1'
        ),

    )

    return placer_connectors
