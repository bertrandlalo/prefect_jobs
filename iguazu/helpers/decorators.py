import functools
import inspect

from iguazu.helpers.files import FileProxy


def auto_download(parameter_name):

    reserved = ["upstream_tasks", "mapped", "task_args", "flow", "fn"]
    if parameter_name in reserved:
        raise ValueError(f'Parameter name "{parameter_name}" is a reserved name')

    if parameter_name == 'self':
        raise ValueError('Cannot auto_download "self" parameter')

    def decorator(func):
        # Try to guess if func is a member function or a normal function and
        # also verify parameter_name is in the signature
        func = getattr(func, '__wrapped__', func)
        signature = inspect.getfullargspec(func)
        if parameter_name not in signature.args and parameter_name not in signature.kwonlyargs:
            raise ValueError(f'Parameter "{parameter_name}" not found in signature')

        is_member = ('self' in signature.args)

        if is_member:
            @functools.wraps(func)
            def inner(*args, **kwargs):
                if parameter_name in kwargs and isinstance(kwargs[parameter_name], FileProxy):
                    kwargs[parameter_name] = kwargs[parameter_name].file
                self = args[0]
                result = func(self, *args[1:], **kwargs)
                # TODO: manage upload?
                return result

        else:
            @functools.wraps(func)
            def inner(*args, **kwargs): # TODO: do we really need two functions?
                print('Before')
                if parameter_name in kwargs and isinstance(kwargs[parameter_name], FileProxy):
                    kwargs[parameter_name] = kwargs[parameter_name].file
                result = func(*args, **kwargs)
                # TODO: manage upload?
                return result

        return inner

    return decorator
