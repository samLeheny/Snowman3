# Title: class_Blueprint.py
# Author: Sam Leheny
# Contact: samleheny@live.com

# Description:


###########################
##### Import Commands #####
import importlib
import os
import json
###########################
###########################


###########################
######## Variables ########

###########################
###########################





########################################################################################################################
class Blueprint:
    def __init__(
        self,
        dirpath = None,
        armature = None,
        attr_handoffs = None,
        module_connections = None,
        placer_connectors = None,
        space_blends = None

    ):
        self.dirpath = dirpath
        self.armature = armature
        self.attr_handoffs = attr_handoffs
        self.module_connections = module_connections
        self.placer_connectors = placer_connectors
        self.space_blends = space_blends