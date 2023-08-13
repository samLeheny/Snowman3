import os
import inspect
import weakref
import logging
import Snowman3.rigger.rig_factory.objects as obs
from Snowman3.rigger.rig_factory.objects.part_objects.part_array import PartArrayGuide
from Snowman3.rigger.rig_factory.objects.part_objects.part import PartGuide
import Snowman3.rigger.rig_factory.build.utilities.controller_utilities as ctrl_utils
import Snowman3.rigger.rig_factory.system_signals as system_signals
from Snowman3.rigger.rig_factory.objects.part_objects.base_container import BaseContainer
from Snowman3.rigger.rig_factory.objects.part_objects.container import Container, ContainerGuide
import Snowman3.rigger.rig_api.proxy_objects as prx
from Snowman3.rigger.rig_factory.objects.part_objects.base_part import BasePart
from Snowman3.rigger.rig_factory.objects.node_objects.joint import Joint


DEBUG = os.getenv('PIPE_DEV_MODE') == 'TRUE'


# ----------------------------------------------------------------------------------------------------------------------
def create_root(klass, **kwargs):
    """
    Creates the main Container group at the root of the rig
    """
    controller = ctrl_utils.get_controller()
    if controller.root:
        raise Exception(f"There is already a root created: {controller.root.name}")
    if klass not in obs.__dict__:
        raise Exception(f"Invalid object type: {klass}")
    object_type = obs.__dict__[klass]
    if not issubclass(object_type, (ContainerGuide, Container)):
        raise Exception(
            "Invalid type: {object_type.__name__}. New containers must be type: (ContainerGuide, Container)")

    kwargs = object_type.pre_process_kwargs(**kwargs)
    system_signals.root_signals['start_change'].emit()
    controller.root = controller.create_object( klass, **kwargs )
    system_signals.root_signals['end_change'].emit(controller.root)

    return weakref.proxy(controller.root)



# ----------------------------------------------------------------------------------------------------------------------
def create_part(part_owner, klass, **kwargs):
    """
    Creates a part underneath a ContainerGuide or PartGroupGuide
    """
    create_members = kwargs.pop('create_members', True)
    if inspect.isclass(klass):
        klass = klass.__name__
    if part_owner is None:
        raise Exception('Part owner is None')
    if klass not in obs.__dict__:
        raise Exception(f'Invalid object type: {klass}')
    if 'parent' in kwargs:
        raise Exception(
            'you should not pass a "parent" keyword argument to create_part. The parent will be set automatically.')
    controller = part_owner.controller
    object_type = obs.__dict__[klass]
    """
    if DEBUG:
        owner_type = part_owner.__class__
        guide_owner_types = (PartGroupGuide, ContainerGuide)
        guide_member_types = (PartGuide, PartGroupGuide)
        if not issubclass(object_type, guide_member_types):
            raise Exception(
                'Invalid type: "%s". Valid types: (PartGuide , PartGroupGuide)' % object_type.__name__
            )
        if not isinstance(part_owner, guide_owner_types):
            raise Exception(
                'Invalid part part_owner: "%s". Valid types: (PartGroupGuide , ContainerGuide)' % owner_type.__name__
            )
    """
    kwargs = object_type.pre_process_kwargs(**kwargs)
    new_part = controller.create_object(
        klass,
        part_owner = part_owner,
        hierarchy_parent = part_owner,
        parent = part_owner,
        **kwargs
    )
    if create_members and isinstance(new_part, PartArrayGuide):
        new_part.create_members()
    for joint in new_part.joints:
        joint.hierarchy_parent = new_part
    """
    if DEBUG:
        for handle in new_part.handles:
            if handle.owner != new_part:
                raise Exception(
                    'The owner of handle %s is %s (it should be %s)' % (
                        handle.name,
                        handle.owner.name,
                        new_part.name
                    )
                )
    """
    new_part.post_create(**kwargs)
    if isinstance(new_part, PartGuide):
        new_part.after_first_create()

    if kwargs.get('proxy', True):
        return weakref.proxy(new_part)
    return new_part


# ----------------------------------------------------------------------------------------------------------------------
def delete_parts(*parts):
    parts = prx.resolve_objects(*parts)
    part_roots = pow.get_root_parts(parts)
    del parts
    controller = ctrl_utils.get_controller()
    for part in part_roots:
        part_owner = part.part_owner
        hierarchy_parent = part.hierarchy_parent
        if DEBUG:
            if not isinstance(part, (BasePart, BaseContainer)):
                raise Exception('Invalid part type: %s' % type(part))
            if not isinstance(hierarchy_parent, (Joint, BaseContainer)):
                raise Exception('Invalid hierarchy_parent type: %s' % type(hierarchy_parent))
            if not isinstance(part_owner, (BasePart, BaseContainer)):
                raise Exception('Invalid part_owner type: %s' % type(part_owner))
        if part.layer is not None:
            controller.root.deleted_parent_entity_part_names.append(part.name)
        controller.schedule_objects_for_deletion(part)
        # if DEBUG:
        #     if part in part_owner.part_members:
        #         raise Exception('The part "%s" was not removed from its owners members' % part.name)
        #     if part in hierarchy_parent.hierarchy_children:
        #         raise Exception('The part "%s" was not removed from its parents hierarchy_children' % part.name)
        del part
    del part_roots
    controller.delete_scheduled_objects()


# ----------------------------------------------------------------------------------------------------------------------
def toggle_parts_orientation_mode():
    logger = logging.getLogger('rig_build')
    controller = ctrl_utils.get_controller()
    if controller.root:
        parts = controller.root.get_parts()
        guide_state = isinstance(controller.root, ContainerGuide)
        if guide_state:
            for part in parts:
                if hasattr(part, 'allowed_modes'):
                    part.set_guide_mode('translation')
                    logger.warning('%s part toggled to translation mode.' % part)


# ----------------------------------------------------------------------------------------------------------------------
def delete_container():
    controller = ctrl_utils.get_controller()
    if not controller.scene.objExists('Container'):
        raise Exception('"Container" group does not exist')
    controller.scene.delete('Container')
    controller.scene.delete_unused_nodes()


# ----------------------------------------------------------------------------------------------------------------------
def delete_vert(build, remove_vertices=False):
    if remove_vertices:
        part_blueprints = build.rig_blueprint['part_members']
        for part_bp in part_blueprints:
            handle_vertices = part_bp.get('handle_vertices', None)
            if handle_vertices:
                part_bp['handle_vertices'] = {}


# ----------------------------------------------------------------------------------------------------------------------
def reset_controller():
    controller = ctrl_utils.get_controller()
    controller.reset()
    system_signals.controller_signals['reset'].emit()
    system_signals.controller_signals['reset'].emit()
