import logging
import os
import time

import Snowman3.rigger.rig_api.proxy_objects as proxy_objs
import Snowman3.rigger.rig_factory.system_signals as signals
from Snowman3.rigger.rig_factory.objects.part_objects.part import Part
from Snowman3.rigger.rig_factory.objects.node_objects.joint import Joint
import Snowman3.rigger.rig_factory.build.utilities.controller_utilities as controller_utils
from Snowman3.rigger.rig_factory.objects.part_objects.base_part import BasePart
from Snowman3.rigger.rig_factory.objects.part_objects.part_group import PartGroup
from Snowman3.rigger.rig_factory.objects.part_objects.base_container import BaseContainer
from Snowman3.rigger.rig_factory.objects.part_objects.container import Container, ContainerGuide


DEBUG = os.getenv('PIPE_DEV_MODE') == 'TRUE'


# ----------------------------------------------------------------------------------------------------------------------
def change_hierarchy_parent(
        parts,
        hierarchy_parent,
        child_index=None
):
    if len(parts) < 1:
        raise Exception("You must provide at-least one part")
    parts = proxy_objs.resolve_objects(*parts)
    hierarchy_parent = proxy_objs.resolve_objects(hierarchy_parent)[0]

    if DEBUG:
        if hierarchy_parent is None:
            raise Exception("hierarchy_parent is None")
        if not isinstance(hierarchy_parent, (BaseContainer, Joint)):
            raise Exception(f"Invalid hierarchy_parent type : {type(hierarchy_parent)}")
    if child_index is None:
        child_index = len(hierarchy_parent.hierarchy_children)
    row = child_index
    for i, part in enumerate(parts):
        if DEBUG:
            if not isinstance(part, (BaseContainer, BasePart)):
                raise Exception(f"The part '{part.name}' does not seem to be a guide state part")
            if not part.hierarchy_parent:
                raise Exception(f"{part.name} does not seem to have a hierarchy_parent")
            if part not in part.hierarchy_parent.hierarchy_children:
                raise Exception(f"{part.name} not found in {hierarchy_parent.name}.hierarchy_children")


        if row > len(hierarchy_parent.hierarchy_children):
            raise Exception(
                "member_index '{}' is higher than the number of hierarchy_children: '{}'".format(
                    child_index, len(hierarchy_parent.hierarchy_children))
            )
        signals.part_hierarchy_signals['start_move'].emit(part, hierarchy_parent, row)
        old_children = part.hierarchy_parent.hierarchy_children
        old_index = old_children.index(part)
        part.part_owner.hierarchy_children.remove(part)
        old_children.remove(part)
        if hierarchy_parent == part.hierarchy_parent and row > old_index:  # drag and drop from same parent
            row -= 1
        hierarchy_parent.hierarchy_children.insert(row, part)
        part.hierarchy_parent = hierarchy_parent
        signals.part_hierarchy_signals['end_move'].emit()
        set_parent(part, hierarchy_parent)
        row += 1  # Fixing issue with parts sometimes reordering due to insert. Based off of selection order of parts


# ----------------------------------------------------------------------------------------------------------------------
def set_hierarchy_parent(
        part,
        hierarchy_parent,
        child_index=None
):
    part = proxy_objs.resolve_objects(part)[0]
    hierarchy_parent = proxy_objs.resolve_objects(hierarchy_parent)[0]

    if part.hierarchy_parent:
        return change_hierarchy_parent([part], hierarchy_parent)
    if DEBUG:
        if not isinstance(hierarchy_parent, (BaseContainer, Joint)):
            raise Exception('Invalid hierarchy_parent type:%s' % type(hierarchy_parent))
        if not isinstance(part, (BasePart, BaseContainer)):
            raise Exception('Invalid part type:%s' % type(part))
        if hierarchy_parent is None:
            raise Exception('Cannot set hierarchy_parent of %s to None' % part.name)
        if part.hierarchy_parent:
            raise Exception('%s already has a hierarchy_parent : %s' % (part.name, part.hierarchy_parent.name))

    if child_index is None:
        child_index = len(hierarchy_parent.hierarchy_children)
    signals.part_hierarchy_signals['start_set'].emit(hierarchy_parent, child_index)
    hierarchy_parent.hierarchy_children.insert(child_index, part)
    part.hierarchy_parent = hierarchy_parent
    signals.part_hierarchy_signals['end_set'].emit()
    set_parent(part, hierarchy_parent)


# ----------------------------------------------------------------------------------------------------------------------
def set_parent(part, hierarchy_parent):
    if not hierarchy_parent:
        return dict(
            info='hierarchy parent is None. Skipping set parent'
        )
    if not isinstance(part, (Part, PartGroup)):
        return dict(
            info='hierarchy parent is not type: (Part, PartGroup). Skipping set parent'
        )

    parent = hierarchy_parent
    if isinstance(hierarchy_parent, (ContainerGuide, Container)):
        if not hierarchy_parent.control_group:
            raise Exception('Control group not found under Container: %s' % hierarchy_parent.name)
        parent = hierarchy_parent.control_group

    if part.parent == parent:
        return dict(
            info='The part %s is already parented to %s: Skipping set parent' % (part.name, parent.name)
        )
    if hierarchy_parent == part.part_owner:
        return dict(
            info='The part %s is already has the part owner to %s: Skipping set parent' % (part.name, parent.name)
        )

    part.set_parent(parent)

    return dict(
        info='The part "%s" was parented to: %s.' % (part.name, parent.name)
    )


# ----------------------------------------------------------------------------------------------------------------------
def remove_from_hierarchy(part):
    """
    Called just before a part gets deleted to safely remove it from the hierarchy
    """
    part = proxy_objs.resolve_objects(part)[0]
    root = part.get_root()
    hierarchy_parent = part.hierarchy_parent
    if DEBUG:
        if part == root:
            raise Exception('You cannot remove the root from hierarchy.')
        if hierarchy_parent is None:
            raise Exception('%s has no hierarchy_parent remove' % part.name)
        if not isinstance(hierarchy_parent, (BaseContainer, Joint)):
            raise Exception('Invalid hierarchy_parent type: %s' % type(hierarchy_parent))
        if part not in hierarchy_parent.hierarchy_children:
            raise Exception('%s not found in %s.hierarchy_children' % (part.name, hierarchy_parent.name))
    change_hierarchy_parent(
        [x for x in get_descendants(part) if isinstance(x, (BasePart, BaseContainer))],
        hierarchy_parent
    )
    # del x
    signals.part_hierarchy_signals['start_remove'].emit(part)
    hierarchy_parent.hierarchy_children.remove(part)
    part.hierarchy_parent = None
    signals.part_hierarchy_signals['end_remove'].emit()


# ----------------------------------------------------------------------------------------------------------------------
def get_hierarchy_data(root=None):
    controller = controller_utils.get_controller()
    if root is None:
        root = controller.root
    hierarchy_data = []
    local_parts = [x for x in root.get_parts() if x.layer == controller.current_layer]
    all_joints = controller.root.get_joints()
    for part_index, part in enumerate(local_parts):
        if DEBUG:
            if not part.hierarchy_parent:
                raise Exception('%s had no hierarchy parent' % part.name)
            if not isinstance(part.hierarchy_parent, (Joint, BasePart, BaseContainer)):
                raise Exception('%s has and invalid hierarchy_parent type: %s' % (
                        type(part.name),
                        part.hierarchy_parent
                    )
                )
        parent_joint_index = None
        legacy_joint_index = None
        parent_name = part.hierarchy_parent.name
        if isinstance(part.hierarchy_parent, Joint):
            if part.hierarchy_parent in all_joints:
                legacy_joint_index = all_joints.index(part.hierarchy_parent)
            parent_joint = part.hierarchy_parent
            parent_part = parent_joint.hierarchy_parent
            if DEBUG:
                if not isinstance(parent_part, (BasePart, BaseContainer)):
                    raise Exception('invalid parent part type: %s' % type(parent_part))
                if parent_joint not in parent_part.joints:
                    raise Exception(
                        '%s is not a member joint of: %s' % (
                            parent_joint.name,
                            parent_part.name
                        )
                    )
                if not parent_part.part_uuid:
                    logging.getLogger('rig_build').info(
                        'parent part "%s" doesnt have a part_uuid. (Assuming root or non-local)' % parent_part.name
                    )
            parent_part_uuid = parent_part.part_uuid
            parent_joint_index = parent_part.joints.index(parent_joint)
            parent_part_name = parent_part.name
        else:
            if not part.hierarchy_parent:
                raise Exception('%s.hierarchy_parent is None' % part.name)

            parent_part_uuid = part.hierarchy_parent.part_uuid
            parent_part_name = part.hierarchy_parent.name

        hierarchy_data.append(
            dict(
                part_name=part.name,
                part_uuid=part.part_uuid,
                parent_name=parent_name,
                parent_part_uuid=parent_part_uuid,
                parent_joint_index=parent_joint_index,
                parent_part_name=parent_part_name,
                legacy_joint_index=legacy_joint_index
            )
        )
    return hierarchy_data


# ----------------------------------------------------------------------------------------------------------------------
def set_hierarchy_parent_with_data(
        part_uuid,
        parent_part_uuid,
        parent_part_name,
        parent_joint_index,
        part_name,
        parent_name
):
    controller = controller_utils.get_controller()
    info_lines = []
    warning_lines = []
    if controller.namespace:
        part_name = '%s:%s' % (
            controller.namespace,
            part_name
        )
        info_lines.append(
            'Added namespace "%s" to part name: %s' % (
                controller.namespace,
                part_name
            )
        )
        if parent_name and parent_name != controller.root.name:
            parent_name = '%s:%s' % (
                controller.namespace,
                parent_name
            )
            info_lines.append(
                'Added namespace "%s" to expected parent name: %s' % (
                    controller.namespace,
                    parent_name
                )
            )
    if part_uuid not in controller.root.parts_by_uuid:
        return dict(
            status='warning',
            warning='The part_uuid was not found: part=%s uuid=%s' % (
                part_name,
                part_uuid
            )
        )
    part = controller.root.parts_by_uuid[part_uuid]
    if parent_part_uuid is None:
        if not parent_part_name:
            raise Exception(
                'Unable to resolve parent part: %s = None, parent_part_uuid = %s' % (
                    parent_part_uuid,
                    parent_part_name
                )
            )
        if parent_part_name not in controller.named_objects:
            raise Exception('Unable to find parent part by name: %s' % parent_part_name)
        parent_part = controller.named_objects[parent_part_name]
        info_lines.append('parent part resolved by name "%s" because parent uuid not found' % parent_part_name)
    else:
        if parent_part_name in controller.named_objects:  # parent parts from parent rigs
            parent_part = controller.named_objects[parent_part_name]
            info_lines.append(
                'parent part "%s" resolved by name.' % (
                    parent_part_name
                )
            )
        elif parent_part_uuid not in controller.root.parts_by_uuid:
            raise Exception(
                'The parent uuid was not found: part=%s parent=%s parent_part=%s parent_uuid=%s' % (
                    part_name,
                    parent_name,
                    parent_part_name,
                    parent_part_uuid
                )
            )
        else:
            parent_part = controller.root.parts_by_uuid[parent_part_uuid]
            info_lines.append(
                'parent part "%s" resolved by uuid: %s' % (
                    parent_part_name,
                    parent_part_uuid
                )
            )
    parent_joint = None
    if parent_joint_index is None:
        set_hierarchy_parent(
            part,
            parent_part
        )
        info_lines.append(
            'Set parent to %s using parent_part_uuid: %s' % (parent_part.name, parent_part_uuid)
        )
    elif parent_joint_index + 1 > len(parent_part.joints):
        parent_joint = parent_part.joints[-1]
        set_hierarchy_parent(
            part,
            parent_joint
        )
        warning_lines.append(
            'The joint index (%s) is higher than the number joints (%s) on parent part:%s\n%s' % (
                parent_joint_index,
                len(parent_part.joints),
                parent_part.name,
                'Parented to the last joint instead: %s' % parent_joint.name
            )
        )
    else:
        parent_joint = parent_part.joints[parent_joint_index]
        set_hierarchy_parent(
            part,
            parent_joint
        )
        info_lines.append(
            'Set parent to %s using parent_joint_index: %s' % (parent_joint.name, parent_joint_index)
        )
    if parent_joint:
        if parent_joint.name != parent_name:
            warning_lines.append(
                'The parent joints name seems to have changed from %s to %s' % (
                    parent_name,
                    parent_joint.name
                )
            )
    if part.name != part_name:
        warning_lines.append(
            'The parts name seems to have changed from %s to %s' % (
                part_name,
                part.name
            )
        )
    if parent_part.name != parent_part_name:
        warning_lines.append(
            'The parent parts name seems to have changed from %s to %s' % (
                parent_part_name,
                parent_part.name
            )
        )
    if warning_lines:
        return dict(
            status='warning',
            warning='\n'.join(warning_lines)
        )
    elif info_lines:
        return dict(
            info='\n'.join(info_lines)
        )


# ----------------------------------------------------------------------------------------------------------------------
def get_named_hierarchy_data(root=None):
    controller = controller_utils.get_controller()
    if root is None:
        root = controller.root
    local_parts = [x for x in root.get_parts() if x.layer == controller.current_layer]
    named_hierarchy_data = []
    for part in local_parts:
        named_hierarchy_data.append(
            (
                part.name,
                part.hierarchy_parent.name if part.hierarchy_parent else None
            )
        )
    return named_hierarchy_data


# ----------------------------------------------------------------------------------------------------------------------
def set_named_hierarchy_data(named_hierarchy_data, sleep_time=0.0):
    controller = controller_utils.get_controller()
    for part_name, parent_name in named_hierarchy_data:
        time.sleep(sleep_time)  # So it doesn't crash the live QAbstractModels
        part = controller.named_objects.get(part_name, None)
        parent = controller.named_objects.get(parent_name, None)
        if not part:
            logging.getLogger('rig_build').warning('Unable to locate part: %s' % part_name)
        elif not parent:
            logging.getLogger('rig_build').warning('Unable to locate hierarchy parent: %s' % parent_name)
        else:
            print('Parenting %s to %s' % (part.name, parent.name))
            set_hierarchy_parent(part, parent)


# ----------------------------------------------------------------------------------------------------------------------
def get_all_hierarchy_parents(part=None):
    controller = controller_utils.get_controller()
    if part is None:
        if not controller.root:
            raise Exception('Rig not found.')
        part = controller.root
    all_hierarchy_parents = []
    is_container = isinstance(part, BaseContainer)
    if is_container:
        all_hierarchy_parents.append(part)
    all_hierarchy_parents.extend(part.joints)
    if is_container:
        child_parts = part.get_parts(recursive=False)
        for child_part in child_parts:
            all_hierarchy_parents.extend(get_all_hierarchy_parents(part=child_part))
    return all_hierarchy_parents


# ----------------------------------------------------------------------------------------------------------------------
def find_first_joint_ancestor(item):
    parent = get_owner(item)
    while parent:
        if isinstance(parent, Joint):
            return parent
        parent = get_owner(parent)


# ----------------------------------------------------------------------------------------------------------------------
def get_ancestors(item):
    ancestors = []
    owner = get_owner(item)
    while owner:
        ancestors.insert(0, owner)
        owner = get_owner(owner)
    return ancestors


# ----------------------------------------------------------------------------------------------------------------------
def get_descendants(item):
    descendants = [item]
    members = get_members(item)
    descendants.extend(members)
    for member in members:
        descendants.extend(get_descendants(member))
    return descendants


# ----------------------------------------------------------------------------------------------------------------------
def get_members(item):
    if DEBUG:
        if not isinstance(item, (BasePart, BaseContainer, Joint)):
            raise Exception(
                'Invalid object type "%s" for model "%s"' % type(item).__name__
            )
    members = []
    if isinstance(item, BaseContainer):
        members = list(item.hierarchy_children)
        members.extend(item.joints)
    elif isinstance(item, BasePart):
        members = item.joints
    elif isinstance(item, Joint):
        members = item.hierarchy_children
    if DEBUG:
        for member in members:
            if not isinstance(member, (BaseContainer, BasePart, Joint)):
                raise Exception('Invalid member type: %s' % member)
            hierarchy_parent = get_owner(member)
            if hierarchy_parent != item:
                raise Exception(
                    'The hierarchy_parent of %s should be %s, but it is %s' % (
                        member,
                        item,
                        hierarchy_parent
                    )
                )
    return members


# ----------------------------------------------------------------------------------------------------------------------
def get_owner(item):
    if DEBUG:
        if not isinstance(item, (BasePart, BaseContainer, Joint)):
            raise Exception(
                'Invalid object type "%s"' % type(item).__name__
            )
    return item.hierarchy_parent


# ----------------------------------------------------------------------------------------------------------------------
def set_legacy_hierarchy_parent(
        expected_part_name,
        expected_parent_name,
        legacy_parent_name=None,
        legacy_joint_index=None
):
    if not expected_parent_name:
        return dict(
            status='warning',
            warning='expected_parent_name is None'
        )
    controller = controller_utils.get_controller()
    if controller.namespace:
        expected_part_name = '%s:%s' % (controller.namespace, expected_part_name)
        if expected_parent_name and expected_parent_name != controller.root.name:
            expected_parent_name = '%s:%s' % (controller.namespace, expected_parent_name)
    container = controller.root
    parts = container.get_parts()
    all_hierarchy_parents = get_all_hierarchy_parents()
    part_dict = dict((x.name, x) for x in parts)
    hierarchy_parents_dict = dict((x.name, x) for x in all_hierarchy_parents)
    used_legacy_joint_index = False
    if expected_parent_name not in hierarchy_parents_dict:
        if legacy_parent_name in hierarchy_parents_dict:
            expected_parent_name = legacy_parent_name
        elif legacy_joint_index is not None:
            all_joints = controller.root.get_joints()
            if len(all_joints) < (legacy_joint_index +1):
                raise Exception('Unable to resolve joint from legacy joint index')
            expected_parent_name = all_joints[legacy_joint_index].name
            used_legacy_joint_index = True
        else:
            return dict(
                status='warning',
                warning='Parent not found: %s' % expected_parent_name
            )
    if expected_part_name not in part_dict:
        return dict(
            status='warning',
            warning='Part not found: %s' % expected_part_name
        )
    hierarchy_parent = hierarchy_parents_dict[expected_parent_name]
    part = part_dict[expected_part_name]
    if isinstance(hierarchy_parent, Joint) and legacy_parent_name:
        legacy_parent = controller.named_objects.get(legacy_parent_name)
        if legacy_parent in get_descendants(hierarchy_parent):
            hierarchy_parent = legacy_parent

    set_hierarchy_parent(
        part,
        hierarchy_parent
    )
    logging.getLogger('rig_build').info('Set hierarchy_parent of %s to: %s' % (
        expected_part_name,
        expected_parent_name
    ))

    if used_legacy_joint_index:
        return dict(
            status='warning',
            warning='Unable to locate parent by name: "%s". Resolved parent: "%s" (using legacy joint index)' % (
                expected_parent_name,
                hierarchy_parent.name
            )
        )

    data_used = dict(
        expected_part_name=expected_part_name,
        expected_parent_name=expected_parent_name,
        legacy_parent_name=legacy_parent_name,
        legacy_joint_index=legacy_joint_index
    )

    return dict(
        warning='Set parent: %s\nUsing legacy data:\n%s' % (
            hierarchy_parent.name,
            '\n'.join(['%s=%s' % (x, data_used[x]) for x in data_used])
        ),
        status='warning'
    )
