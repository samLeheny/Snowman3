import types
from collections import OrderedDict
import logging
import traceback



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

