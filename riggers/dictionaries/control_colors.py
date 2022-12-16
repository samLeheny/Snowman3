# Title: control_colors.py
# Author: Sam Leheny
# Contact: samleheny@live.com

# Description:


###########################
##### Import Commands #####
import Snowman.dictionaries.nameConventions as nameConventions
reload(nameConventions)
nom = nameConventions.create_dict()
###########################
###########################





########################################################################################################################
def create_dict():

    sided_ctrl_color = {

        nom.leftSideTag: [0.075, 0.445, 1],
        nom.leftSideTag2: [0, 0.220, 1],
        nom.leftSideTag3: [0.32, 0.3, 1],
        nom.leftSideTag4: [0, 0, 1],

        nom.rightSideTag : [1, 0.075, 0.075],
        nom.rightSideTag2 : [0.663, 0.028, 0.032],
        nom.rightSideTag3 : [0.950, 0.385, 0.142],
        nom.rightSideTag4 : [1, 0, 0],

        nom.midSideTag : [0.25, 1, 0],
        nom.midSideTag2 : [0, 1, 0.033],
        nom.midSideTag3 : [0, 0.33, 0],
        nom.midSideTag4 : [0, 0.278, 0.097],

        nom.majorSideTag : [0.445, 1, 0.175],
        nom.majorSideTag2 : [0.67, 0.28, 0],

        "root" : 2,
        "root_offset" : 3,

        'squetch' : [0.3, 1, 0],
        'settings' : 1,
        'tweak' : 24,
        "setup_root" : 16,

    }

    return sided_ctrl_color
