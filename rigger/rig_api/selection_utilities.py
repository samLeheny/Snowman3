from Snowman3.rigger.rig_factory.objects.part_objects.base_part import BasePart
from Snowman3.rigger.rig_factory.objects.part_objects.base_container import BaseContainer
from Snowman3.rigger.rig_factory.objects.rig_objects.curve_handle import CurveHandle



def get_selected_parts(controller, types=None, recursive=False):
    if types is None:
        types = (BasePart, BaseContainer)
    selected_names = controller.scene.get_selected_transform_names()
    selected_transforms = [controller.named_objects[x] for x in selected_names if x in controller.named_objects]
    selected_parts = [x for x in selected_transforms if isinstance(x, types)]
    all_parts = []
    for part in selected_parts:
        all_parts.append(part)
        if recursive and isinstance(part, BaseContainer):
            all_parts.extend(part.get_parts())
    return list(set(all_parts))



def get_selected_part_handles(controller, types=None, include_selected_handles=False):
    handles = []
    for part in get_selected_parts(controller, types=types):
        handles.extend(part.get_handles())
    if include_selected_handles:
        handles.extend(get_selected_handles(controller))
    return list(set(handles))



def get_selected_handles(controller, types=None):
    if types is None:
        types = (CurveHandle, )
    selected_transform_names = controller.scene.get_selected_transform_names()
    selected_transforms = [
        controller.named_objects[x] for x in selected_transform_names if x in controller.named_objects]
    selected_handles = [x for x in selected_transforms if isinstance(x, types)]
    return selected_handles
