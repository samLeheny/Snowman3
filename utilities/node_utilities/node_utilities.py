from Snowman3.utilities.objects.node_objects.joint import Joint

def zero_joint_rotation(joint):
    rotation_plug = joint.plugs['rotate']
    joint_orient_plug =  joint.plugs['jointOrient']
    rotation = rotation_plug.get_value([0.0, 0.0, 0.0])
    joint_orientation = joint_orient_plug.get_value([0.0, 0.0, 0.0])
    rotation_plug.set_value([0.0, 0.0, 0.0])
    joint_orient_plug.set_value(rotation[i] + joint_orientation[i] for i in range(len(rotation)))
