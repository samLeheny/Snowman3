# Title: metadata_utils.py
# Author: Sam Leheny
# Contact: samleheny@live.com

# Description:


###########################
##### Import Commands #####
import Snowman3.utilities.general_utils as gen
import Snowman3.utilities.attribute_utils as attr_utils
###########################
###########################


###########################
######## Variables ########

###########################
###########################


class MetaDataAttr:
    def __init__(
        self,
        long_name = None,
        attribute_type = None,
        keyable = None,
        default_value_attr = None,
    ):
        self.long_name = long_name
        self.attribute_type = attribute_type
        self.keyable = keyable
        self.default_value_attr = default_value_attr


    def create(self, obj, scene_obj):
        default_value = self.get_default_value(obj)
        attr_utils.add_attr(scene_obj, long_name=self.long_name, attribute_type=self.attribute_type,
                            keyable=self.keyable, default_value=default_value)


    def get_default_value(self, obj):
        return getattr(obj, self.default_value_attr)
