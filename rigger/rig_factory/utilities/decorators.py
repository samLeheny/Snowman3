import types
from collections import OrderedDict
import logging
import traceback
import maya.api.OpenMaya as om
import maya.cmds as mc



def flatten_values(*args):
    nodes = []
    for arg in args:
        if isinstance(arg, (dict, OrderedDict)):
            nodes.extend(flatten_values(*arg.itervalues()))
        elif isinstance(arg, (list, tuple, set)):
            nodes.extend(flatten_values(*arg))
        else:
            nodes.append(arg)
    return nodes



def flatten_items(*args):
    nodes = []
    for arg in args:
        if isinstance(arg, (list, tuple, set, types.GeneratorType)):
            nodes.extend(flatten_items(*arg))
        else:
            nodes.append(arg)
    return nodes



def flatten_args(func):
    def flatten(*args, **kwargs):
        return func(*flatten_items(*args), **kwargs)
    return flatten



def check_simple_args(func, strict=True, trace_as_message=False):
    def check_simple(self, *args, **kwargs):
        for value in flatten_values(args, kwargs):
            if not isinstance(value, (int, float, basestring, bool)):
                message = f"Complex object passed to method, please replace with simple object! -" \
                          f"{str(value)} ({type(value)})"
                if strict:
                    if trace_as_message:
                        raise TypeError(code_warning(message, as_string=True, as_error=True))
                    raise TypeError(message)
                code_warning(message)
                break  # Limit to single warning per command
        return func(self, *args, **kwargs)
    return check_simple



def code_warning(message, lines=1, as_string=False, as_error=False):
    """
    Warn about a certain point in the code, showing stack trace
    without bringing up this or the line that calls this command
    """
    logger = logging.getLogger('rig_build')
    warn_level = 'Error' if as_error else 'Warning'
    warnMessage = '\n' + '\n'.join(traceback.format_stack(None, lines+2)[:-2]) + warn_level + ": " + message
    if as_string:
        return warnMessage
    logger.warning(warnMessage)


def get_m_object(node):
    if isinstance(node, om.MObject):
        return node
    elif isinstance(node, om.MDagPath):
        return node.node()
    elif isinstance(node, basestring):
        node_count = len(mc.ls(node))
        if node_count > 1:
            raise Exception('Duplicate node names: %s' % node)
        if node_count < 0:
            raise Exception('Node does not exist: %s' % node)
        selection_list = om.MSelectionList()
        selection_list.add(node)
        m_object = om.MObject()
        selection_list.getDependNode(0, m_object)
        return m_object



def m_object_arg(func):
    def convert_to_m_object(*args, **kwargs):
        args = list(args)
        args[0] = get_m_object(args[0])
        return func(*args, **kwargs)
    return convert_to_m_object
