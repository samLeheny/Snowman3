import Snowman3.rigger.rig_factory.objects as obs
import Snowman3.rigger.rig_api.proxy_objects as prx
from Snowman3.rigger.rig_factory.objects.part_objects.base_container import BaseContainer
import Snowman3.rigger.rig_factory.common_modules as com

side_mirror_map = {'left': 'right', 'right': 'left'}


def get_edited_blueprints(parts, parts_data):
    copy_blueprints = dict()
    part_names = []
    for part in prx.resolve_objects(*parts):
        parts_list = [part]
        copy_blueprints[part.name] = dict(
            blueprint=get_duplicate_blueprints(
                parts_list,
                parts_data
            ),
            owner_name=part.part_owner.name
        )
        part_names.append(part.name)
        del parts_list, part
    del parts
    return copy_blueprints


def mirror_parts(parts):
    return duplicate_parts(
        parts,
        get_parts_mirror_data(parts),
        mirror=True
    )


def get_parts_mirror_data(parts):
    parts_data = dict()
    for root_part in parts:
        for part in com.part_owners.get_descendants(
                root_part,
                include_self=True
        ):
            if part.side == 'left':
                side = 'right'
            elif part.side == 'right':
                side = 'left'
            else:
                side = part.side
            parts_data[part.name] = dict(
                root_name=part.root_name,
                side=side
            )
    return parts_data


def duplicate_parts(parts, parts_data, mirror=False):
    parts = prx.resolve_objects(*parts)
    new_root_parts = []

    for part in parts:
        new_part = build_duplicate_parts(
            get_duplicate_blueprints(
                [part],
                parts_data,
                mirror=mirror
            ),
            part.part_owner
        )[0]
        new_root_parts.append(new_part)

    for r in range(len(new_root_parts)):
        if isinstance(parts[r], BaseContainer):
            old_parts = parts[r].get_parts(include_self=True)
            new_parts = new_root_parts[r].get_parts(include_self=True)
            if len(old_parts) != len(new_parts):
                raise Exception('Duplicated part count did not match.')
        else:
            old_parts = [parts[r]]
            new_parts = [new_root_parts[r]]
        for p in range(len(new_parts)):
            copy_data_between_parts(
                old_parts[p],
                new_parts[p],
                parts_data
            )
    return new_root_parts


def copy_data_between_parts(
        old_part,
        new_part,
        parts_data
):
    """
    Copies data between two sets of parts during mirror/duplicate operations
    """
    controller = com.controller_utils.get_controller()
    old_parent = old_part.hierarchy_parent
    if old_parent is None:
        raise Exception('hierarchy_parent of %s is None' % old_part.name)
    if len(new_part.handles) != len(old_part.handles):
        raise Exception(
            'Handle count mismatch between new part "%s" (%s) and old part "%s" (%s)' % (
                new_part.name,
                len(new_part.handles),
                old_part.name,
                len(old_part.handles)
            )
        )
    for h in range(len(old_part.handles)):
        position = old_part.handles[h].plugs['translate'].get_value()
        if old_part.side in side_mirror_map and side_mirror_map[old_part.side] == new_part.side:
            position[0] = position[0] * -1
        new_part.handles[h].plugs['translate'].set_value(position)
    if old_parent == controller.root:
        new_parent = controller.root
    else:
        parent_root_name = old_parent.root_name
        parent_side = old_parent.side
        if old_parent.name in parts_data:
            part_data = parts_data[old_parent.name]
            parent_root_name = part_data['root_name']
            parent_side = part_data['side']
        predicted_parent_name = old_parent.extract_name(
            side=parent_side,
            root_name=parent_root_name
        )
        if predicted_parent_name in controller.named_objects:
            new_parent = controller.named_objects[predicted_parent_name]
        else:
            new_parent = old_parent
    new_part.set_hierarchy_parent(new_parent)


def build_duplicate_parts(part_blueprints, part_owner):
    part_owner = prx.resolve_objects(part_owner)[0]
    new_parts = []
    for part_blueprint in part_blueprints:
        klass = part_blueprint.pop('klass')
        for part in part_owner.get_parts(recursive=False):
            if not isinstance(part, (obs.BasePart, obs.BaseContainer)):
                raise Exception('Invalid part: %s' % type(part))
        part_blueprint['create_members'] = False
        member_blueprints = part_blueprint.pop('part_members', [])
        part_blueprint['proxy'] = False
        new_part = part_owner.create_part(
            klass,
            **part_blueprint
        )
        new_parts.append(new_part)
        build_duplicate_parts(
            member_blueprints,
            new_part
        )
    return new_parts


def get_duplicate_blueprints(
        parts,
        parts_data,
        mirror=False
):
    blueprints = []
    for part in parts:
        if mirror:
            blueprint = part.get_mirror_blueprint()
        else:
            blueprint = part.get_blueprint()
        old_name = part.name
        if old_name in parts_data:
            part_data = parts_data[old_name]
            blueprint['root_name'] = part_data['root_name']
            blueprint['side'] = part_data['side']
        blueprint.pop('name', None)
        if isinstance(part, BaseContainer):
            blueprint['part_members'] = get_duplicate_blueprints(
                part.part_members,
                parts_data=parts_data,
                mirror=mirror
            )
        blueprints.append(blueprint)
    return blueprints


def simple_mirror(parts):
    """
    A simple mirroring function from Paxton to use as an example/reference. To use, pass in the parts that the user
    wants to mirror and call this function.

    :param parts: list of parts to be mirrored(Selecting a PartGroup will mirror all parts under the group)
    :type parts: list

    :return: returns list of newly mirrored parts
    :rtype: list
    """
    controller = com.controller_utils.get_controller()
    sides = dict(
        left='right',
        right='left',
        center='center'
    )

    mirrored_parts = duplicate_parts(
        parts,
        dict((x.name, dict(side=sides[x.side], root_name=x.root_name)) for x in controller.root.get_parts())
    )

    return mirrored_parts
