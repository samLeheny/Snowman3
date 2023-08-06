from Snowman3.rigger.rig_factory.objects.node_objects.transform import Transform
from Snowman3.rigger.rig_factory.objects.base_objects.properties import ObjectProperty, DataProperty, ObjectListProperty



class Joint(Transform):

    hierarchy_children = ObjectListProperty( name='hierarchy_children', default_value=[] )
    hierarchy_parent = ObjectProperty( name='hierarchy_parent' )
    disconnected_joints = DataProperty( name='disconnected_joints', default_value=False )
    suffix = 'Jnt'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.node_type = 'joint'

    def zero_rotation(self):
        self.controller.zero_joint_rotation(self)
