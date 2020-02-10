"""
Utility functions used on iguazu that do not belong anywhere else.
"""

from typing import Any
import functools
import importlib
import pathlib
import pickle
import pkgutil


def fullname(obj: Any) -> str:
    """ Get the full module.class name of an object instance

    Parameters
    ----------
    obj
        An object

    Returns
    -------
    The name of the input object's class including its module.
    Built-in classes do not have a module.

    """
    module = obj.__class__.__module__
    # This assumes that str is in the __builtins__ module to verify if the
    # object is a builtin class instance. We cannot compare to a __builtins__
    # global variable: no such thing exists!
    # (got this from StackOverflow but cannot find the link)
    if module is None or module == str.__class__.__module__:
        return obj.__class__.__name__
    return module + '.' + obj.__class__.__name__


def all_subclasses(cls):
    """Get a set of all subclasses of `cls`"""
    direct_subclasses = set(cls.__subclasses__())
    recursive_subclasses = [
        all_subclasses(c) for c in direct_subclasses
    ]
    return functools.reduce(set.union, [direct_subclasses] + recursive_subclasses)


# https://stackoverflow.com/a/25562415/227103
def import_submodules(module, recursive=True):
    """ Import all submodules of a module, recursively, including subpackages

    Parameters
    ----------
    module: str or module
        The package to import
    recursive: bool

    Returns
    -------
    Dictionary of module names (str) to the imported modules

    """
    if isinstance(module, str):
        module = importlib.import_module(module)
    results = {}
    for loader, name, is_pkg in pkgutil.walk_packages(module.__path__):
        full_name = module.__name__ + '.' + name
        results[full_name] = importlib.import_module(full_name)
        if recursive and is_pkg:
            results.update(import_submodules(full_name, recursive=True))
    return results


def str2bool(value: str) -> bool:
    """Convert a string to bool

    This function considers any lower/upper case form of yes, true, t or 1
    as ``True``. Anything else is ``False``.
    """
    return str(value).lower() in ("yes", "true", "t", "1")


def dump_pickle(obj, filename='my_pickle.pickle'):
    path = pathlib.Path(filename)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "wb") as f:  # remember to open the file in binary mode
        pickle.dump(obj, f)  # serialize datetime.datetime object


def load_pickle(fname, default=None):
    try:
        with open(fname, 'rb') as file:
            obj = pickle.load(file)
        return obj
    except (OSError, IOError):
        return default
