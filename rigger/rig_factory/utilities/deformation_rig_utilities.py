import logging
import Snowman3.rigger.rig_factory.environment as env
from Snowman3.rigger.rig_factory.objects.node_objects.joint import Joint


def create_deform_joint(control_joint, parent):
    logging.getLogger('rig_build').info('Creating deform joint from : %s, ' % control_joint)
    deform_joint = control_joint.create_child(
        Joint,
        parent=parent,
        functionality_name='Bind'
    )
    deform_joint.plugs['radius'].set_value(control_joint.size)
    deform_joint.zero_rotation()
    deform_joint.plugs.set_values(
        overrideEnabled=True,
        overrideRGBColors=True,
        overrideColorRGB=env.colors['bindJoints'],
        radius=control_joint.plugs['radius'].get_value(),
        type=control_joint.plugs['type'].get_value(),
        side={'center': 0, 'left': 1, 'right': 2, None: 3}[control_joint.side],
        drawStyle=control_joint.plugs['drawStyle'].get_value(2),
    )
    control_joint.plugs['rotateOrder'].connect_to(deform_joint.plugs['rotateOrder'])
    control_joint.plugs['inverseScale'].connect_to(deform_joint.plugs['inverseScale'])
    control_joint.plugs['jointOrient'].connect_to(deform_joint.plugs['jointOrient'])
    control_joint.plugs['translate'].connect_to(deform_joint.plugs['translate'])
    control_joint.plugs['rotate'].connect_to(deform_joint.plugs['rotate'])
    control_joint.plugs['scale'].connect_to(deform_joint.plugs['scale'])
    control_joint.plugs['drawStyle'].set_value(2)
    control_joint.relationships['deform_joint'] = deform_joint
    return deform_joint


def get_first_joint_ancestor(child):
    parent = child.parent
    while parent:
        if isinstance(parent, Joint):
            return parent
        parent = parent.parent


def parent_deform_joint(part, control_joint):
    deform_joint = control_joint.relationships.get('deform_joint')
    if not deform_joint:
        raise Exception('unable to resolve deform joint for control_joint: %s' % control_joint)
    if isinstance(control_joint.parent, Joint):
        deform_joint_parent = control_joint.parent.relationships.get('deform_joint')
        if not deform_joint_parent:
            raise Exception('unable to resolve deform joint for control_joint parent: %s' % control_joint)
        deform_joint.set_parent(deform_joint_parent)
    else:
        if not part.hierarchy_parent:
            raise Exception('Part "%s" had no owner. unable to resolve deform joint' % part)
        if isinstance(part.hierarchy_parent, Joint):
            owner_deform_joint = part.hierarchy_parent.relationships.get('deform_joint')
            if not owner_deform_joint:
                raise Exception('Owner joint "%s" dod not have a deform joint' % part.hierarchy_parent)
            deform_joint.set_parent(owner_deform_joint)

        """assume the is root level joint in part and parent to owner."""

