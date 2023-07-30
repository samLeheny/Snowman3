import Snowman3.rigger.rig_factory.common_modules as com
import Snowman3.rigger.rig_factory.utilities.string_utilities as stu
from Snowman3.rigger.rig_factory.objects.rig_objects.constraint import *
from Snowman3.rigger.rig_factory.objects.node_objects.depend_node import DependNode
from Snowman3.rigger.rig_factory.objects.rig_objects.space_switcher import SpaceSwitcher


def create_space_switcher(*handles, **kwargs):
    controller = com.controller_utils.get_controller()
    container = controller.root
    if len(handles) < 2:
        raise Exception('Provide at-least 2 handles to create a space switchers. Found: %s' % handles)
    translate = kwargs.get('translate', True)
    rotate = kwargs.get('rotate', True)
    scale = kwargs.get('scale', False)
    dv = kwargs.get('dv', 0)
    handle = handles[-1]
    side = handle.side
    handle_matrix = handle.get_matrix()

    if handle.space_switcher:
        controller.schedule_objects_for_deletion(handle.space_switcher)
        controller.delete_scheduled_objects()  # THis is slowing down builds

    targets = handles[:-1]
    root_name = handle.root_name
    if ':' in handle.name:
        handle_namespace = ''.join(x.capitalize() or '_' for x in handle.name.split(':')[0].split('_'))
        if root_name:
            root_name = '%s%s' % (  # Fix duplicate names when constraining name-spaced accessories
                handle_namespace,
                root_name
            )
        else:
            root_name = handle_namespace

    this = handle.create_child(
        SpaceSwitcher,
        root_name=root_name,
        parent=container.utilities_group,
        translate=translate,
        rotate=rotate,
        scale=scale,
        dv=dv
    )

    if handle.plugs.exists('parentSpace'):
        controller.scene.deleteAttr(
            handle.plugs['parentSpace'].get_node().name,
            attribute=handle.plugs['parentSpace'].root_name
        )
        controller.schedule_objects_for_deletion(handle.plugs['parentSpace'])
        controller.delete_scheduled_objects()  # This is slowing down builds
    space_plug = handle.create_plug(
        kwargs.get('plug_name', 'parentSpace'),
        at='enum',
        k=True,
        en=':'.join([x.pretty_name for x in handles[:-1]]),
        dv=dv
    )
    owner = handle.owner
    if not owner:
        raise Exception(
            'Unable to find owner from "%s"' % handle
        )
    root = owner.get_root()
    if not root:
        raise Exception(
            'Unable to find root from handle "%s"' % handle
        )
    root.add_plugs(space_plug)
    target_groups = []
    rotate_order = handle.constraint_group.plugs['rotateOrder'].get_value()
    for i, target in enumerate(targets):
        target_group = this.create_child(
            Transform,
            segment_name='%s%sSpaceSwitch' % (
                this.segment_name,
                stu.underscore_to_pascalcase(target.name.split(':')[-1])
            ),
            matrix=handle_matrix,
            side=side,
        )
        target_groups.append(target_group)
        target_group.plugs['rotateOrder'].set_value(rotate_order)

        if translate and rotate:
            constraint = controller.create_object(
                ParentConstraint,
                target,
                target_group,
                mo=True
            )
            constraint.set_parent(this)

        elif rotate:
            controller.create_object(
                OrientConstraint,
                target,
                target_group,
                mo=True
            )
        elif translate:
            controller.create_object(
                PointConstraint,
                target,
                target_group,
                mo=True
            )
        if scale:
            controller.create_object(
                ScaleConstraint,
                target,
                target_group,
                mo=True
            )
    constraint_nodes = []
    if translate and rotate:
        constraint_nodes.append(
            controller.create_parent_constraint(
                target_groups,
                handle.constraint_group,
                mo=True,
                parent=this
            )
        )
    elif rotate:
        constraint_nodes.append(
            controller.create_orient_constraint(
                target_groups,
                handle.constraint_group,
                mo=True,
                parent=this
            )
        )
    elif translate:
        constraint_nodes.append(
            controller.create_point_constraint(
                target_groups,
                handle.constraint_group,
                mo=True
            )
        )
    if scale:
        constraint_nodes.append(
            controller.create_scale_constraint(
                target_groups,
                handle.constraint_group,
                mo=True,
                parent=this
            )
        )
    for i, target_group in enumerate(target_groups):
        condition = target_group.create_child(
            DependNode,
            node_type='condition',
        )
        space_plug.connect_to(condition.plugs['firstTerm'])  # if custom attr value
        condition.plugs['operation'].set_value(0)  # equal to
        condition.plugs['secondTerm'].set_value(i)  # i
        condition.plugs['colorIfTrueR'].set_value(1)  # turn on, if true
        condition.plugs['colorIfFalseR'].set_value(0)  # turn off, if false
        for constraint_node in constraint_nodes:
            plug = constraint_node.get_weight_plug(target_group)
            condition.plugs['outColorR'].connect_to(plug)
    this.targets = targets
    handle.space_switcher = this


def set_space_switcher_data(data):
    controller = com.controller_utils.get_controller()
    namespace = controller.namespace
    new_switcher_data = dict()
    for handle_name in data:
        full_name = handle_name
        if namespace and ':' not in full_name:
            full_name = '%s:%s' % (namespace, handle_name)
        switcher_type, plug_data, target_data = data[handle_name]
        new_target_data = []
        for target_name, pretty_name in target_data:
            full_target_name = target_name
            if namespace and ':' not in full_target_name:
                full_target_name = '%s:%s' % (
                    namespace,
                    target_name
                )
            new_target_data.append([full_target_name, pretty_name])
        new_switcher_data[full_name] = [switcher_type, plug_data, target_data]
    missing_targets = []
    missing_handles = []
    for handle_name in data:
        handle = controller.named_objects.get(handle_name, None)
        if handle:
            targets = []
            switcher_type, plug_data, target_data = data[handle_name]
            for target_name, pretty_name in target_data:
                target = controller.named_objects.get(target_name, None)
                if target:
                    target.pretty_name = pretty_name
                    targets.append(target)
                else:
                    missing_targets.append(target_name)
            targets.append(handle)
            create_space_switcher(*targets, **plug_data)
        else:
            missing_handles.append(handle_name)
    if missing_targets:
        shortened_targets = [missing_targets[x] for x in range(len(missing_targets)) if x < 6]
        controller.raise_warning('Unable to find space switcher target(s)\n%s' % '\n'.join(shortened_targets))
    if missing_handles:
        shortened_handles = [missing_handles[x] for x in range(len(missing_handles)) if x < 6]
        controller.raise_warning('Unable to find space switcher handles(s)\n%s' % '\n'.join(shortened_handles))


def create_space_switcher_from_data(handle_name, handle_data):
    controller = com.controller_utils.get_controller()
    namespace = controller.namespace
    full_handle_name = handle_name
    if namespace and ':' not in full_handle_name:
        full_handle_name = f'{namespace}:{handle_name}'
    switcher_type, plug_data, target_data = handle_data
    new_target_data = []
    for target_name, pretty_name in target_data:
        full_target_name = target_name
        if namespace and ':' not in full_target_name:
            full_target_name = f'{namespace}:{target_name}'
        new_target_data.append([full_target_name, pretty_name])

    handle = controller.named_objects.get(full_handle_name, None)
    if not handle:
        return dict(
            status='warning',
            warning=f'Handle not found: {full_handle_name}'
        )
    targets = []
    missing_targets = []
    switcher_type, plug_data, target_data = handle_data
    for target_name, pretty_name in target_data:
        target = controller.named_objects.get(target_name, None)
        if target:
            target.pretty_name = pretty_name
            targets.append(target)
        else:
            missing_targets.append(target_name)
    targets.append(handle)
    create_space_switcher(*targets, **plug_data)
    if missing_targets:
        return dict(
            status='warning',
            warning='Some targets were not found: %s' % ', '.join(missing_targets)
        )
    return dict(
        info='Added spaces: %s' % ', '.join([x.name for x in targets])
    )
