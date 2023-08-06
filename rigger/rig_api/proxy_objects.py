import Snowman3.rigger.rig_factory.build.utilities.controller_utilities as cut
import logging
import traceback
import weakref


def resolve_objects(*objects):
    """
    Convert strings and proxy objects into real objects
    """
    controller = cut.get_controller()
    resolved_nodes = []
    for obj in objects:
        resolved_node = obj
        if isinstance(obj, weakref.ProxyType):
            try:
                resolved_node = obj.__repr__.__self__
            except ReferenceError as e:
                logging.getLogger('rig_build').error(traceback.format_exc())
                raise Exception("unable to resolve weakref.Proxy object. (It has probably been deleted)")
        if isinstance(obj, str):
            if obj in controller.named_objects:
                resolved_node = controller.named_objects[resolved_node]
            else:
                raise Exception(f"Part not found: '{resolved_node}'")
        resolved_nodes.append(resolved_node)
    return resolved_nodes
