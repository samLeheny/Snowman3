import copy
import functools
import Snowman3.rigger.rig_factory.objects as obs
from Snowman3.rigger.rig_factory.build.tasks.task_objects import BuildTask
import Snowman3.rigger.rig_factory.build.utilities.controller_utilities as cut


# ----------------------------------------------------------------------------------------------------------------------
def get_parts_positions_tasks(entity_builds, root_task):
    create_parts_task = BuildTask(
        name='Positions',
        parent=root_task
    )
    for build in entity_builds:
        entity_task = BuildTask(
            build=build,
            parent=create_parts_task,
            name=build.entity
        )
        create_position_tasks(
            entity_task,
            build,
            copy.deepcopy(build.rig_blueprint['part_members'])
        )


# ----------------------------------------------------------------------------------------------------------------------
def create_position_tasks(
        parent_task,
        build,
        part_blueprints
):
    for part_blueprint in part_blueprints:
        handle_positions = part_blueprint.get('handle_positions', None)
        index_handle_positions = part_blueprint.get('index_handle_positions', None)
        part_name = obs.__dict__[part_blueprint['klass']].get_predicted_name(**part_blueprint)
        sub_part_blueprints = part_blueprint.pop('part_members', [])
        BuildTask(
            build=build,
            parent=parent_task,
            name=part_blueprint.get('name', part_blueprint['klass']),
            create_children_function=functools.partial(
                create_handle_position_tasks,
                part_name,
                handle_positions,
                index_handle_positions
            )
        )
        create_position_tasks(
            parent_task,
            build,
            sub_part_blueprints
        )


# ----------------------------------------------------------------------------------------------------------------------
def create_handle_position_tasks(
        part_name,
        handle_positions,
        index_handle_positions
):

    new_tasks = []
    controller = cut.get_controller()
    if controller.namespace:
        part_name = '%s:%s' % (controller.namespace, part_name)
    part = controller.named_objects[part_name]
    handles = part.get_handles()
    if not handles:
        return dict(
            info='The part "%s" seems to not have any handles.' % part.name
        )
    for i in range(len(handles)):
        handle = handles[i]
        handle_name = handle.name.split(':')[-1]
        if handle_positions and handle_name in handle_positions:
            position_task = BuildTask(
                name='%s (by name)' % handle.name,
                function=functools.partial(
                    set_handle_position,
                    handle.name,
                    handle_positions[handle_name],

                )
            )
        elif index_handle_positions and len(index_handle_positions) == len(handles):
            position_task = BuildTask(
                name='%s (by index)' % handle.name,
                function=functools.partial(
                    set_handle_world_position,
                    handle.name,
                    index_handle_positions[i]

                )
            )
            position_task.info = 'handle name "%s" not found in data:\n\n%s' % (
                handle.name,
                '\n'.join(handle_positions.keys())
            )
        else:
            position_task = BuildTask(
                name='%s (position not found)' % handle.name,
                function=functools.partial(
                    set_handle_position,
                    handle.name,
                    None

                )
            )
        new_tasks.append(position_task)
    return new_tasks


# ----------------------------------------------------------------------------------------------------------------------
def set_handle_world_position(handle_name, handle_position):
    if handle_position is None:
        return dict(
            warning='Unable to resolve handle position.',
            status='warning'
        )
    controller = cut.get_controller()
    handle = controller.named_objects[handle_name]
    controller.xform(handle.name, ws=True, t=handle_position)
    return dict(
        info='Set handle position for "%s" to %s' % (handle.name, handle_position)
    )


# ----------------------------------------------------------------------------------------------------------------------
def set_handle_position(handle_name, handle_position):
    if handle_position is None:
        return dict(
            warning='Unable to resolve handle position.',
            status='warning'
        )
    controller = cut.get_controller()
    handle = controller.named_objects[handle_name]
    handle.plugs['translate'].set_value(handle_position)
    return dict(
        info='Set handle position for "%s" to %s' % (handle.name, handle_position)
    )


# ----------------------------------------------------------------------------------------------------------------------
def get_parts_vertices_tasks(entity_builds, root_task):
    create_parts_task = BuildTask(
        name='Vertices',
        parent=root_task
    )
    for build in entity_builds:
        entity_task = BuildTask(
            build=build,
            parent=create_parts_task,
            name=build.entity
        )
        create_vertices_tasks(
            entity_task,
            build,
            copy.deepcopy(build.rig_blueprint['part_members'])
        )


# ----------------------------------------------------------------------------------------------------------------------
def create_vertices_tasks(
        parent_task,
        build,
        part_blueprints
):
    for part_blueprint in part_blueprints:
        handle_vertices = part_blueprint.get('handle_vertices', None)
        part_name = obs.__dict__[part_blueprint['klass']].get_predicted_name(**part_blueprint)
        sub_part_blueprints = part_blueprint.pop('part_members', [])
        if handle_vertices:
            BuildTask(
                build=build,
                parent=parent_task,
                name=part_blueprint.get('name', part_blueprint['klass']),
                function=functools.partial(
                    set_vertex_data,
                    part_name,
                    handle_vertices
                )
            )

        create_vertices_tasks(
            parent_task,
            build,
            sub_part_blueprints
        )


# ----------------------------------------------------------------------------------------------------------------------
def set_vertex_data(part_name, handle_vertices):
    if not handle_vertices:
        return dict(
            info='Index handle positions not found'
        )
    controller = cut.get_controller()
    if controller.namespace:
        part_name = '%s:%s' % (controller.namespace, part_name)

    part = controller.named_objects[part_name]
    part.set_vertex_data(handle_vertices)
    missing_handles = [x.name for x in part.handles if x.name not in handle_vertices]
    if missing_handles:
        return dict(
            status='warning',
            warning='Vertices for the following handles not found:\n\n%s' % '\n'.join(missing_handles)
        )
