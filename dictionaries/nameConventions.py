# Title: nameConventions.py
# Author: Sam Leheny
# Contact: samleheny@live.com

# Description: A dictionary denoting various common standards when it comes to names and suffixes. All uses of these
# strings throughout Pigeon Suite will instead refer to the corresponding entries in this dictionary. That way, if ever
# a naming standard changes, it only needs to be updated in this file, and the changes will ripple throughout every
# other script in Pigeon Suite.


###########################
##### Import Commands #####
###########################
###########################




def create_dict():

    # Establish naming conventions class
    class NameConventionsDictionary:
        def __init__(self):

            # Prefixes
            self.animCtrl = "CTRL"
            self.setupCtrl = "SetupCTRL"
            self.prelimCtrl = "PrelimCTRL"
            #self.nonAnimCtrl = "SetupCTRL"
            self.bindJnt = "BIND"
            self.nonBindJnt = "JNT"
            self.curve = "CRV"
            self.set = "SET"
            self.locator = "LOC"
            self.spaceLoc = "SPACE"
            self.group = "GRP"
            self.ikHandle = "IKH"
            self.effector = "EFF"
            self.cluster = "CLUST"
            self.placer = "PLC"
            self.orienter = "ORI"
            self.follicle = "FOL"

            self.setupRigNamespace = "rigSetup"
            self.finalRigNamespace = "finalRig"

            # Side tags
            self.leftSideTag = "L"
            self.leftSideTag2 = "L2"
            self.leftSideTag3 = "L3"
            self.leftSideTag4 = "L4"

            self.rightSideTag = "R"
            self.rightSideTag2 = "R2"
            self.rightSideTag3 = "R3"
            self.rightSideTag4 = "R4"

            self.midSideTag = "M"
            self.midSideTag2 = "M2"
            self.midSideTag3 = "M3"
            self.midSideTag4 = "M4"

            self.majorSideTag = "major"
            self.majorSideTag2 = "major2"

    # Output dictionary class object
    return NameConventionsDictionary()