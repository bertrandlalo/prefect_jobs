__version__ = '0.2.0-dev5'

from . import utils  # Needed for a circular dependency resolution
from .core.tasks import Task


__all__ = ['__version__', 'Task']
