from Snowman3.rigger.rig_factory.objects.part_objects.base_container import BaseContainer
from Snowman3.rigger.rig_factory.objects.part_objects.part import PartGuide
import Snowman3.rigger.rig_factory as rig_factory

sides = dict(left='right', right='left')
side_prefixes = dict( R='L', L='R' )



def mirror_name(name):
    owner_tokens = name.split('_')
    if owner_tokens[0] in side_prefixes:
        owner_tokens[0] = side_prefixes[owner_tokens[0]]
        return '_'.join(owner_tokens)



def mirror_part(part):
    controller = part.controller
    mirror_blueprint = part.get_mirror_blueprint()
    owner = part.hierarchy_parent
    parent_joint = part.parent_joint
    if part.side in sides:
        owner_name = mirror_name(owner.name)
        if owner_name in controller.named_objects:
            owner = controller.named_objects[owner_name]
        if parent_joint:
            parent_joint_name = mirror_name(parent_joint.name)
            if parent_joint_name in controller.named_objects:
                parent_joint = controller.named_objects[parent_joint_name]

    mirror_blueprint['member_index'] = 0
    new_part = owner.create_part(
        part.__class__,
        **mirror_blueprint
    )

    if isinstance(part, PartGuide):
        for i, position in enumerate([[x[0]*-1.0, x[1], x[2]] for x in part.get_index_handle_positions()]):
            new_part.handles[i].plugs['translate'].set_value(position)

    if parent_joint:
        new_part.set_parent_joint(parent_joint)

    new_parts = [new_part]
    if isinstance(part, BaseContainer):
        part_list = list(part.get_parts(recursive=False))
        for part in part_list:
            new_parts.append(mirror_part(part))

    return new_parts
