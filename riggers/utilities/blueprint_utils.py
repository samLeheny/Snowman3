# Title: blueprint_utils.py
# Author: Sam Leheny
# Contact: samleheny@live.com

# Description:


###########################
##### Import Commands #####

###########################
###########################

###########################
######## Variables ########
core_data_filename = 'core_data'
###########################
###########################



########################################################################################################################
class Blueprint:
    def __init__(
        self,
        asset_name,
        dirpath = None,
        modules = None,

    ):
        self.asset_name = asset_name
        self.dirpath = dirpath
        self.modules = modules if modules else {}