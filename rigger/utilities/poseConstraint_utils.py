# Title: postConstraint_utils.py
# Author: Sam Leheny
# Contact: samleheny@live.com

# Description:


###########################
##### Import Commands #####
from dataclasses import dataclass
###########################
###########################


###########################
######## Variables ########

###########################
###########################



########################################################################################################################
@dataclass
class PostConstraint:
    source_part: str
    source_placer: str
    target_part: str
    target_placer: str
    hide_target_placer: bool



########################################################################################################################
class PostConstraintManager:
    def __init__(
        self,
        post_constraint
    ):
        self.post_constraint = post_constraint


    @classmethod
    def data_from_post_constraint(cls, post_constraint):
        return vars(post_constraint).copy()
