# Title: class_PartConstructor.py
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


class PartConstructor:
    def __init__(
        self,
        part_name: str,
        side: str = None
    ):
        self.part_name = part_name
        self.side = side
    

    def proportionalize_vector_handle_positions(self, positions, placer_size):
        for i, pos in enumerate(positions):
            positions[i] = [pos[j] * (4 * placer_size) for j in range(3)]
        return positions


    def create_placers(self):
        pass


    def get_connection_pairs(self):
        pass


    def get_vector_handle_attachments(self):
        pass
