import os
import Snowman3.rigger.rig_api.proxy_objects as prx
import Snowman3.rigger.rig_factory.system_signals as sig
from Snowman3.rigger.rig_factory.objects.part_objects.base_part import BasePart
from Snowman3.rigger.rig_factory.objects.part_objects.part import PartGuide, Part
from Snowman3.rigger.rig_factory.objects.rig_objects.curve_handle import CurveHandle
from Snowman3.rigger.rig_factory.objects.rig_objects.guide_handle import GuideHandle
from Snowman3.rigger.rig_factory.objects.part_objects.base_container import BaseContainer
from Snowman3.rigger.rig_factory.objects.part_objects.container import ContainerGuide, Container
from Snowman3.rigger.rig_factory.objects.part_objects.part_group import PartGroupGuide, PartGroup
DEBUG = os.getenv('PIPE_DEV_MODE') == 'TRUE'


def set_part_owner(
        part,
        part_owner,
        member_index=None
):
    part = prx.resolve_objects(part)[0]
    part_owner = prx.resolve_objects(part_owner)[0]

    if part.part_owner:
        return change_part_owners(
            [part],
            part_owner,
            member_index=member_index
        )
    if DEBUG:
        if not isinstance(part_owner, BaseContainer):
            raise Exception('Invalid part_owner type:%s' % type(part_owner))
        if not isinstance(part, (BasePart, BaseContainer)):
            raise Exception('Invalid part type:%s' % type(part))
        if part_owner is None:
            raise Exception('Cannot set part_owner of %s to None' % part.name)
        if part.part_owner:
            raise Exception('%s already has a part_owner : %s' % (part.name, part.part_owner))
    if member_index is None:
        member_index = get_next_member_index(part, part_owner)
    sig.part_owner_signals['start_set'].emit(part_owner, member_index)
    part_owner.part_members.insert(member_index, part)
    part.part_owner = part_owner
    sig.part_owner_signals['end_set'].emit(part)


def change_part_owners(
        parts,
        part_owner,
        member_index=None
):
    if len(parts) < 1:
        raise Exception('You must provide at-least one part')
    parts = prx.resolve_objects(*parts)
    part_owner = prx.resolve_objects(part_owner)[0]

    if member_index is None:
        member_index = len(part_owner.part_members)

    if DEBUG:
        if part_owner is None:
            raise Exception('part_owner is None')
        if not isinstance(part_owner, (ContainerGuide, PartGroupGuide)):
            raise Exception('Invalid part_owner %s type:%s' % (part_owner.name, type(part_owner)))
        if member_index > part_owner.part_members:
            raise Exception(
                'member_index "%s" is higher than the number of members: %s' % (
                    member_index,
                    len(part_owner.part_members)
                )
            )
    row = member_index
    for part in parts:
        if DEBUG:
            if not part.part_owner:
                raise Exception('%s does not seem to have a part_owner' % part.name)
            if part not in part.part_owner.part_members:
                raise Exception('%s not found in %s.part_members' % (part.name, part_owner.name))
        sig.part_owner_signals['start_move'].emit(
            part,
            part_owner,
            row
        )
        old_members = part.part_owner.part_members
        old_index = old_members.index(part)
        part.part_owner.part_members.remove(part)
        if part_owner == part.part_owner and row >= old_index:  # drag and drop from same parent
            row -= 1
        part_owner.part_members.insert(row, part)
        part.part_owner = part_owner
        sig.part_owner_signals['end_move'].emit()
        row += 1  # Fixing issue with parts sometimes reordering due to insert. Based off of selection order of parts


def remove_from_part_members(part):
    part = prx.resolve_objects(part)[0]
    part_owner = part.part_owner
    if DEBUG:
        if part_owner is None:
            raise Exception('%s has no part_owner remove' % part.name)
        if not isinstance(part_owner, BaseContainer):
            raise Exception('Invalid part_owner type: %s' % part_owner)
        if part not in part_owner.part_members:
            raise Exception('%s not found in %s.part_members' % (part.name, part_owner.name))
    sig.part_owner_signals['start_remove'].emit(part)
    part_owner.part_members.remove(part)
    part.part_owner = None
    sig.part_owner_signals['end_remove'].emit()
    del part
    del part_owner


def get_next_member_index(part, part_owner):
    """
    Get the index to insert part_member under part_owner
    If part is local (layer=None), insert after last local part
    If part is parent/accessory, insert at end
    Note: This ensures parent/child parts are always in the correct order
    """
    child_parts = part_owner.get_parts(recursive=False)
    if part.layer is None:
        for i, child_part in enumerate(child_parts):
            if child_part.layer is not None:
                return i
    return len(child_parts)


def get_ancestors(item, include_self=True):
    ancestors = []
    if include_self:
        ancestors.append(item)
    owner = get_owner(item)
    while owner:
        ancestors.insert(0, owner)
        owner = get_owner(owner)
    return ancestors


def get_descendants(item, include_self=True):
    descendants = []
    if include_self:
        descendants.append(item)
    members = get_members(item)
    descendants.extend(members)
    for member in members:
        descendants.extend(get_descendants(member))
    return descendants


def get_members(item):
    members = []
    if isinstance(item, BaseContainer):
        members.extend(item.part_members)
        members.extend(get_handles(item))
    elif isinstance(item, (Part, PartGuide)):
        members.extend(get_handles(item))
    elif isinstance(item, (CurveHandle, GuideHandle)):
        pass
    else:
        raise Exception('The model does not support owner type "%s"' % type(item))
    if DEBUG:
        for member in members:
            if not isinstance(member, (BaseContainer, BasePart, CurveHandle, GuideHandle)):
                raise Exception('Invalid member type: %s' % member)
            owner = get_owner(member)
            if owner != item:
                raise Exception(
                    'The owner of %s should be %s, but it is %s --MEM----> %s, %s' % (
                        member,
                        item,
                        owner,
                        id(item),
                        id(owner)
                    )
                )
    return members


def get_handles(part):
    handles = []
    for handle in part.handles:
        handles.append(handle)
        # if isinstance(handle, GroupedHandle) and handle.gimbal_handle:
        #     handles.append(handle.gimbal_handle)
    return handles


def get_owner(item):
    if isinstance(
            item,
            (Container, ContainerGuide)
    ):
        return None
    if isinstance(
            item,
            (
                Part,
                PartGuide,
                PartGroup,
                PartGroupGuide
            )
    ):
        owner = item.part_owner

    elif isinstance(
            item,
            (
                    CurveHandle,
                    GuideHandle,
            )
    ):
        owner = item.owner
    else:
        raise Exception('The model does not support object type "%s"' % type(item))
    if DEBUG:
        if owner is None:
            raise Exception('Invalid owner type %s.part_owner = None' % item.name)
        if not isinstance(owner, (BaseContainer, BasePart)):
            raise Exception('Invalid owner type %s.part_owner =%s' % (item.name, type(owner)))
    return owner


def part_is_descendant(parts, part):
    ancestors = get_ancestors(part)
    for x in parts:
        if x != part and x in ancestors:
            return True


def get_root_parts(parts):
    return [x for x in parts if not part_is_descendant(parts, x)]
