from Snowman3.rigger.rig_factory.objects.node_objects.joint import Joint

def zero_joint_rotation(joint):
    rotation_plug = joint.plugs['rotate']
    joint_orient_plug = joint.plugs['jointOrient']
    rotation = rotation_plug.get_value([0.0, 0.0, 0.0])
    joint_orient = joint_orient_plug.get_value([0.0, 0.0, 0.0])
    rotation_plug.set_value([0.0, 0.0, 0.0])
    joint_orient_plug.set_value([rotation[x] + joint_orient[x] for x in range(len(rotation))])
