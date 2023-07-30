import Snowman3.rigger.rig_factory.common_modules as com
import Snowman3.utilities.controller_utils as controller_utils
import Snowman3.rigger.rig_factory.utilities.node_utilities.name_utilities as name_utils

def initialize_common_modules():
    com.controller_utils = controller_utils
    com.name_utils = name_utils
