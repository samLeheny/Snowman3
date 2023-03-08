# Title: class_Blueprint.py
# Author: Sam Leheny
# Contact: samleheny@live.com

# Description:


###########################
##### Import Commands #####

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
        asset_name,
        dirpath = None,
        loose_parts = None,
        modules = None

    ):
        self.asset_name = asset_name
        self.dirpath = dirpath
        self.loose_parts = loose_parts if loose_parts else {}
        self.modules = modules if modules else {}
