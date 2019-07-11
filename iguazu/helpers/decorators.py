import logging
import functools
import inspect
import multiprocessing
import pickle
import sys
import time
import traceback

from iguazu.helpers.files import FileProxy


logger = logging.getLogger(__name__)


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


class SubprocessException(Exception):
    pass


# modified from https://gist.github.com/stuaxo/889db016e51264581b50
# which in turn was modified from https://gist.github.com/schlamar/2311116#file-processify-py-L17
# also see https://stackoverflow.com/q/2046603/227103


def processify(func):
    """ Decorator to run a function as a process.

    Be sure that every argument and the return value
    is *pickable*.
    The created process is joined, so the code does not
    run in parallel.
    """

    def process_func(q, *args, **kwargs):
        try:
            result = func(*args, **kwargs)
            # Try to pickle it: if it is not pickleable, this will raise an error
            print('Will it pickle?')
            pickle.dumps(result)
            print('Yes, it pickles')
        except:
            ex_type, ex_value, tb = sys.exc_info()
            print('Captured exception', ex_type, str(ex_value))
            error = ex_type, ex_value, ''.join(traceback.format_tb(tb))
            result = None
        else:
            error = None

        print('Putting result in queue')
        q.put((result, error))
        print('End process_func')

    @functools.wraps(func)
    def wrap_func(*args, **kwargs):
        # register original function with different name
        # in sys.modules so it is pickable
        process_func.__name__ = func.__name__ + 'processify_func'
        setattr(sys.modules[__name__], process_func.__name__, process_func)

        q = multiprocessing.Queue()
        p = multiprocessing.Process(target=process_func, args=[q] + list(args), kwargs=kwargs)
        p.start()
        print('Waiting for process', p.pid, p.name)
        counter = 0
        #p.join()
        while q.empty() and p.exitcode is None:
            counter += 1
            if counter % 60 == 0:
                print('Still waiting silently...')
                p.join(1)
            time.sleep(1)
        print('Stopped waiting because:')
        print('Queue is empty?', q.empty())
        print('Exitcode is not None?', p.exitcode)
        # while p.exitcode is None:
        #     #logger.debug('Waiting for process %d: %s', p.pid, p.name)
        #     counter += 1
        #     if counter % 60 == 0:
        #         print('Still waiting silently...')
        #         p.join(1)
        #     time.sleep(1)

        # if p.exitcode == 0:
        #     result, error = q.get()
        # else:
        #     result = None
        #     error = (SubprocessException, SubprocessException(f'Process failed with code {p.exitcode}'), 'No traceback')

        error = None
        result = None
        if not q.empty():
            print('Obtaining results from queue...')
            result, error = q.get()
        print('Joining process...')
        p.join()
        print('Process ended with code', p.exitcode)

        print('Returning result...')
        if error:
            print('Returning exception error')
            ex_type, ex_value, tb_str = error
            message = f'{ex_value} (in subprocess)\n{tb_str}'
            raise ex_type(message)
        elif p.exitcode != 0:
            print('Exit code was not 0, returning error')
            raise SubprocessException(f'Subprocess failed with code {p.exitcode}')

        print('Returning complete result')
        return result

    return wrap_func
