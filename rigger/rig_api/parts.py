import inspect
import weakref
import Snowman3.rigger.rig_factory.objects as obs
from Snowman3.rigger.rig_factory.objects.part_objects.part_array import PartArrayGuide
from Snowman3.rigger.rig_factory.objects.part_objects.part import PartGuide
import Snowman3.rigger.rig_factory.build.utilities.controller_utilities as cut
import Snowman3.rigger.rig_factory.system_signals as sig
from Snowman3.rigger.rig_factory.objects.part_objects.container import Container, ContainerGuide



def create_root(klass, **kwargs):
    """
    Creates the main Container group at the root of the rig
    """
    controller = cut.get_controller()
    if controller.root:
        raise Exception(f"There is already a root created: {controller.root.name}")
    if klass not in obs.__dict__:
        raise Exception(f"Invalid object type: {klass}")
    object_type = obs.__dict__[klass]
    if not issubclass(object_type, (ContainerGuide, Container)):
        raise Exception(
            "Invalid type: {object_type.__name__}. New containers must be type: (ContainerGuide, Container)")

    kwargs = object_type.pre_process_kwargs(**kwargs)
    sig.root_signals['start_change'].emit()
    controller.root = controller.create_object( klass, **kwargs )
    sig.root_signals['end_change'].emit(controller.root)

    return weakref.proxy(controller.root)



def create_part(part_owner, klass, **kwargs):
    """
    Creates a part underneath a ContainerGuide or PartGroupGuide
    """
    create_members = kwargs.pop('create_members', True)
    if inspect.isclass(klass):
        klass = klass.__name__
    if part_owner is None:
        raise Exception("Part owner is None")
    if klass not in obs.__dict__:
        raise Exception(f"Invalid object type: {klass}")
    if 'parent' in kwargs:
        raise Exception(
            "you should not pass a 'parent' keyword argument to create_part. The parent will be set automatically.")
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
