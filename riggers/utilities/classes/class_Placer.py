# Title: class_Placer.py
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



class Placer:
    def __init__(
        self,
        name: str,
        side = None,
        position = None,
        size = None,
        vector_handle_positions = None,
        orientation = None
    ):
        self.name = name
        self.side = side
        self.position = position if position else (0, 0, 0)
        self.size = size if size else 1.0
        self.vector_handle_positions = vector_handle_positions
        self.orientation = orientation
        self.has_vector_handles = True if vector_handle_positions else False
