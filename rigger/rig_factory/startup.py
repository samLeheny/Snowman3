import Snowman3.rigger.rig_factory.common_modules as com
import Snowman3.rigger.rig_factory.build.utilities.controller_utilities as controller_utils
import Snowman3.rigger.rig_factory.utilities.node_utilities.name_utilities as name_utils
import Snowman3.rigger.rig_api.part_owners as part_owners
import Snowman3.rigger.rig_api.parts as part_utils
import Snowman3.rigger.rig_api.part_hierarchy as part_hierarchy

def initialize_common_modules():
    com.controller_utils = controller_utils
    com.name_utils = name_utils
    com.part_tools = part_utils
    com.part_owners = part_owners
    com.part_hierarchy = part_hierarchy
