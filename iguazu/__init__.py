__version__ = '0.4.0'  # DO NOT CHANGE HERE. Use bump2version
# Please read the docs/source/versioning.rst document on how to update the version number


from . import utils  # Needed for a circular dependency resolution
from .core.files import FileAdapter
from .core.tasks import Task


__all__ = ['__version__', 'FileAdapter', 'Task']
