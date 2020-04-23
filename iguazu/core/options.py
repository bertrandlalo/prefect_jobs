"""
Iguazu base task options

This module is intended to separate and isolate the options that a
:py:class:`iguazu.core.Task` supports.
"""

from dataclasses import dataclass, field, fields
from typing import Mapping, Optional, Tuple, Type

from iguazu.core.exceptions import SoftPreconditionFailed, GracefulFailWithResults


@dataclass(frozen=True)
class TaskOptions:
    graceful_exceptions: Tuple[Type] = (SoftPreconditionFailed, GracefulFailWithResults)
    """A tuple with all the exceptions that are accepted as a *graceful* way
    to fail in a task."""

    pandas_chained_assignment: Optional[str] = None
    """Set to ``None``, ``'warn'`` or ``'raise'`` to set up a pandas option
    manager with *mode.chained_assignment* set to this value. Any other value
    is ignored and does not set up any pandas option manager. 
    See :class:`pandas.option_context` and :data:`pandas.set_option`.
    """

    force: bool = False
    """Whether this task's execution should be forced, ignoring any previous
    results or cache."""

    metadata_journal_family: str = 'iguazu'
    """Name of the family where the iguazu metadata will be saved. 
    See :func:`iguazu.core.task.Task.default_metadata`. """

    managed_inputs: Mapping = field(default_factory=dict)
    """Mapping that has the parameters needed to convert each keyword parameter
    received in the Task run method to convert said parameter directly from
    a :class:`iguazu.helpers.files.FileAdapter` to a :class:`pandas.DataFrame`.
    """

    managed_inputs_exception_type: Optional[Type] = SoftPreconditionFailed
    """Exception type that will be raised if the automatic input management fails"""


ALL_OPTIONS = tuple(f.name for f in fields(TaskOptions))
