__version__ = '0.4.0'

from . import utils  # Needed for a circular dependency resolution
from .core.files import FileAdapter
from .core.tasks import Task


__all__ = ['__version__', 'FileAdapter', 'Task']
