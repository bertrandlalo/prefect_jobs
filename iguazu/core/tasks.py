import contextlib
import datetime
import functools
import inspect
import logging
import os
from typing import (
    Any, Callable, Container, ContextManager, Iterable, Mapping, NoReturn,
    Optional,
)

import pandas as pd
import prefect
from prefect.engine.signals import ENDRUN
from prefect.utilities.exceptions import PrefectError

from iguazu import __version__
from iguazu.core.exceptions import PreviousResultsExist, SoftPreconditionFailed, GracefulFailWithResults
from iguazu.core.options import TaskOptions, ALL_OPTIONS
from iguazu.core.validators import GenericValidator
from iguazu.core.files import FileAdapter
from iguazu.helpers.states import GracefulFail, SkippedResult
from iguazu.tasks.handlers import garbage_collect_handler, logging_handler
from iguazu.utils import fullname

logger = logging.getLogger(__name__)


class ManagedTask(prefect.Task):
    # This class is not meant to be used directly, use iguazu.Task

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Swap the run and managed_run method so that users override the
        # run method like a regular prefect Task.
        #
        # An alternative implementation of this part could be done with a
        # metaclass, but after an initial attempt, using a metaclass results in
        # a more complex and longer code.
        # Python Zen #3: simple is better than complex
        run = getattr(self, 'run', None)
        managed_run = getattr(self, '_managed_run', None)
        setattr(self, 'run', managed_run)
        setattr(self, 'child_run', run)

    def child_run(self, **kwargs):
        # This function is only here to help type checking; it is dynamically
        # overwritten on the constructor
        return super().run()  # pragma: no cover

    def contexts(self) -> Iterable[ContextManager]:
        raise NotImplementedError

    def prepare_inputs(self, **inputs) -> Mapping:
        raise NotImplementedError

    def handle_outputs(self, outputs) -> Any:
        raise NotImplementedError

    def default_outputs(self, **inputs) -> Any:
        raise NotImplementedError

    def _managed_run(self, **inputs):
        # Create context manager that handles dynamic contexts: a derived class
        # can add as many contexts as needed, but we need to do __enter__ and
        # __exit__ for each context manager. Fortunately, contextlib.ExitStack
        # was designed exactly for this case
        with contextlib.ExitStack() as stack:

            # Add a prefect context so that any derived class can get the
            # run keyword arguments
            stack.enter_context(prefect.context(run_kwargs=inputs.copy()))
            for ctx in self.contexts():
                stack.enter_context(ctx)

            # Pre-process inputs. Failures are managed in the _safe... method
            prepared_inputs = self._safe_prepare_inputs(None, **inputs)
            prepared_inputs = prepared_inputs or {}  # handle empty kwargs so that it can be unpacked

            # Run task. Failures are managed in the _safe... method
            outputs = self._safe_run(None, **prepared_inputs)

            # Post-process outputs. Failures are managed in the _safe... method
            prepared_outputs = self._safe_handle_outputs(outputs)

            return prepared_outputs

    def _safe_prepare_inputs(self, safe_excs, **kws):
        return self._generic_safe(functools.partial(self.prepare_inputs, **kws),
                                  graceful_excs=safe_excs)

    def _safe_run(self, safe_excs, **inputs) -> Any:
        return self._generic_safe(functools.partial(self.child_run, **inputs),
                                  graceful_excs=safe_excs)

    def _safe_handle_outputs(self, results):
        # Prepare outputs cannot accept any graceful fails.
        # Otherwise, it would be recursively calling itself through:
        # handle_outputs [fails] -> graceful_fail -> handle_outputs (again!) ...
        return self._generic_safe(functools.partial(self.handle_outputs, results),
                                  graceful_excs=())

    def _generic_safe(self, func: Callable, graceful_excs: Optional[Container[Exception]] = None) -> Any:
        GRACEFUL_EXCEPTIONS = tuple(graceful_excs or ())
        if hasattr(func, 'func') and hasattr(func.func, '__name__'):
            name = func.func.__name__
        elif hasattr(func, '__name__'):
            name = func.__name__
        else:
            name = func

        if graceful_excs:
            self.logger.debug('Safe call to %s with graceful exceptions %s', name,
                              ', '.join([getattr(cls, '__name__', None) for cls in GRACEFUL_EXCEPTIONS]))
        else:
            self.logger.debug('Safe call to %s without graceful exceptions', name)

        try:
            exception = None
            result = func()

        except GRACEFUL_EXCEPTIONS as exc:
            self.logger.debug('Captured an expected exception (%s). '
                              'Iguazu will now graceful fail this task.',
                              type(exc).__name__, exc_info=True)
            exception = exc
            result = None

        except (ENDRUN, PrefectError) as exc:
            self.logger.info('Captured a Prefect exception (%s). '
                             'This bypasses any Iguazu-managed task code, '
                             'such as automatic upload of outputs. '
                             'The exception will be propagated.',
                             type(exc).__name__, exc_info=True)
            raise

        except Exception as exc:  # nopep8
            self.logger.warning('Captured an unexpected exception (%s). '
                                'Since this exception was not expected, '
                                'Iguazu will now hard fail this task. '
                                'Then, the exception will be propagated.',
                                type(exc).__name__, exc_info=True)
            self._hard_fail()
            raise

        if exception is not None:
            self._graceful_fail(exception)

            # _graceful_fail does not return so this never occurs, but just
            # in case we make a mistake in the future, let us hard fail
            self._hard_fail()
            raise RuntimeError('_graceful_fail should not return')

        return result

    def _graceful_fail(self, exc):
        kwargs = prefect.context.get('run_kwargs', {})
        outputs = self.default_outputs(**kwargs)
        prepared_outputs = self._safe_handle_outputs(outputs)
        raise ENDRUN(state=GracefulFail(message=f'{exc}. Graceful fail for {fullname(exc)}',
                                        result=prepared_outputs))

    def _hard_fail(self):
        try:
            kwargs = prefect.context.get('run_kwargs', {})
            outputs = self.default_outputs(**kwargs)
            for output in _iterate(outputs):
                if isinstance(output, FileAdapter):
                    output.delete()
        except:
            logger.warning('Encountered an exception during hard fail',
                           exc_info=True)


class Task(ManagedTask):

    def __init__(self, **kwargs):
        # Manage prefect kwargs
        prefect_params = inspect.getfullargspec(prefect.Task.__init__).args[1:]
        prefect_kwargs = {k: kwargs.pop(k) for k in list(kwargs) if k in prefect_params}

        # Manage Iguazu kwargs that map to a TaskOptions field
        unknown_params = [k for k in kwargs if k not in ALL_OPTIONS]
        if unknown_params:
            raise TypeError(f'Unexpected keyword arguments on '
                            f'{self.__class__.__name__}.__init__: parameters '
                            f'{unknown_params} are neither a '
                            f'iguazu.TaskOptions field, nor a '
                            f'prefect.Task keyword argument')
        self._meta = TaskOptions(**kwargs)

        # Manage iguazu TaskOptions that update prefect kwargs:
        #
        # The following keys on this dictionary are the prefect.Task.__init__
        # keyword arguments whose default values we want to change. This avoids
        # repeating the same init kwargs on all iguazu tasks in a flow
        prefect_defaults = dict(
            state_handlers=(garbage_collect_handler, logging_handler),
            cache_for=datetime.timedelta(days=7),
            cache_validator=GenericValidator(use_inputs=True, use_parameters=True, force=self.meta.force),
        )
        for k, v in prefect_defaults.items():
            prefect_kwargs.setdefault(k, v)

        # Initialize prefect task
        super().__init__(**prefect_kwargs)
        self.logger.debug('Created %s with %s', self, self.meta)

    def contexts(self) -> Iterable[ContextManager]:
        ctxs = []
        pandas_mode = self.meta.pandas_chained_assignment
        if pandas_mode in (None, 'warn', 'raise'):
            self.logger.debug('Setting pandas context mode.chained_assignment to %s', pandas_mode)
            ctxs.append(pd.option_context('mode.chained_assignment', pandas_mode))

        return tuple(ctxs)

    def preconditions(self, **inputs) -> NoReturn:
        """ Check preconditions on the task inputs

        This function does several automatic verification on the inputs such as
        force verification, check that previous results do not exist, etc.

        You can add your own preconditions by overriding this method, but
        do not forget to call the parent method with
        ``super().preconditions(...)``.

        When overriding this method, you should raise a
        :py:class:`PreconditionFailed` when there is an unmet condition of the
        inputs but the default outputs of the task can be used in downstream
        tasks. This is useful for cases where one wants the flow to continue
        even if there is a small problem on this particular task.

        If there is a non-recoverable error, or when the default outputs should
        not be used downstream, raise another exception that does not derive
        from :py:class:`PreconditionFailed`.

        Note that the inputs are received without any automatic transformation
        like the file adapter to dataframe transformation.

        Parameters
        ----------
        inputs
            Like ``**kwargs``, these are all the keyword arguments sent to
            the run method of the task

        Raises
        ------
        PreconditionFailed
            When the input does not meet a required condition but the task can
            continue with its default outputs.
        """
        # Precondition 1:
        # Previous output does not exist or task is forced
        default_output = self.default_outputs(**inputs)
        family = self.meta.metadata_journal_family
        if isinstance(default_output, FileAdapter):
            default_output_meta = default_output.metadata.get(family, {})
            if not self.forced and default_output_meta.get('status', None) is not None:
                raise PreviousResultsExist('Previous results already exist')

        # Precondition 2:
        # Inputs are *not* marked as a failed result from a previous task
        for input_name, input_value in inputs.items():
            if not isinstance(input_value, FileAdapter):
                continue
            input_meta = input_value.metadata.get(family, {})
            if input_meta.get('status', None) == 'FAILURE':

                raise SoftPreconditionFailed('Previous task failed, generating a file '
                                             'with a failed status')

        # Precondition 3:
        # Keys of each input HDF5 exists in the file
        # This is done automatically by the prepare_inputs

    def postconditions(self, results) -> NoReturn:
        pass

    def prepare_inputs(self, **inputs) -> Mapping:

        # Verify preconditions
        self.preconditions(**inputs)

        exc_class = self.meta.managed_inputs_exception_type

        for k, (args, kwargs) in self.meta.managed_inputs.items():
            # Ignore any kwargs that is not managed through self.meta.managed_inputs
            if k not in inputs:
                continue

            # Ignore any None value
            input_value = inputs[k]
            if input_value is None:
                continue

            # Read the file
            if isinstance(input_value, FileAdapter):
                file = input_value.file
            elif isinstance(input_value, (str, bytes, os.PathLike)):
                file = input_value
            else:
                raise ValueError(f'Input {k} (type {k.__class__.__name__}) '
                                 f'cannot be auto converted to dataframe, '
                                 f'it must be a FileAdapter, str, bytes or os.PathLike')

            if not file.exists() and exc_class is not None:
                raise exc_class(f'Input file {file} does not exist')

            if file.stat().st_size == 0:
                self.logger.info(f'Input %s is empty, generating empty dataframe', k)
                inputs[k] = pd.DataFrame()
                continue

            if args:
                key = args[0]
                args = args[1:]
            else:
                key = None

            self.logger.debug('managed_inputs: extracting key=%s for input %s on file %s',
                              key, k, file)
            with pd.HDFStore(file, 'r') as store:
                if key not in store:

                    if exc_class is not None:
                        raise exc_class(f'Key {key} not present on HDF5 file for input {k}')
                    else:
                        self.logger.debug('Input %s not present on HDF5 file %s'
                                          'for input %s, but no input exception '
                                          'type was configured. Continuing...',
                                          key, file, k)
                else:
                    # Read the dataframe, but be careful when the key is a group and not a node
                    try:
                        obj = pd.read_hdf(store, key, *args, **kwargs)
                    except TypeError:
                        self.logger.warning('Could read HDF5 key %s on file %s for input %s, '
                                            'yet the key does exists on the HDF5. '
                                            'Did you set a group name instead of a node name?',
                                            key, file, k, exc_info=True)
                        obj = None
                    # Type verification
                    if not isinstance(obj, pd.DataFrame):
                        if exc_class is not None:
                            raise exc_class(f'Input {key} for input {k} '
                                            f'was not a pandas dataframe')
                        else:
                            self.logger.debug('Input %s was not a dataframe on '
                                              'HDF5 file %s for input %s, but no '
                                              'input exception type was configured. '
                                              'Continuing...')
                    else:
                        self.logger.debug('Input %s read into a dataframe of shape %s',
                                          k, obj.shape)
                    inputs[k] = obj

        return inputs

    def handle_outputs(self, outputs) -> Any:
        # Set the metadata to the outputs that are file adapters.
        meta = self.default_metadata(None, **prefect.context.run_kwargs)
        for output in _iterate(outputs):
            if isinstance(output, FileAdapter):
                # If the underlying task did not generate anything,
                # create an empty file
                file = output.file
                if not file.exists():
                    self.logger.debug('Task did not generate a FileAdapter output '
                                      'with contents, creating an empty file')
                    open(str(file.resolve()), 'w').close()
                # TODO: update or replace?
                output.metadata.update(meta)

        # Verify postconditions
        self.postconditions(outputs)

        # Upload outputs that are file adapters
        for output in _iterate(outputs):
            if isinstance(output, FileAdapter):
                output.upload()

        # Note: I tried to design and implement a mechanism here similar to
        #       prepare_inputs: It would use the .meta configuration to
        #       automatically convert any output dataframe into a hdf5 file.
        #       I could not manage to find an elegant way of creating a
        #       FileAdapter: this is usually done inside the user task run method,
        #       so I do not know how to do it here unless we add another new
        #       abstract method to create it.

        return outputs

    def default_outputs(self, **inputs) -> Any:
        return None

    def default_metadata(self, exception, **inputs) -> Mapping:
        if exception is None:
            status = 'SUCCESS'
            problem = None
        elif isinstance(exception, PreviousResultsExist):
            # When a previous results exceptions is thrown, then do not set any
            # new metadata
            return dict()

        else:
            # Does it make sense to set this to "GRACEFUL_FAIL"?
            # In my opinion, FAILED tasks should not be saved. Moreover,
            # non-graceful exceptions are actually raised and not captured.
            # So we could agree that if a task shows FAILED, it means that it
            # has gracefully failed
            status = 'FAILED'
            # TODO: auto-convert iguazu exception to problem JSON RFC-7807
            problem = {
                'type': fullname(exception),
                'title': str(exception),
            }

        parents = []
        for value in inputs.values():
            if isinstance(value, FileAdapter):
                parents.append(value.id)

        # TODO: it would be useful to add the inputs to the journal.
        #       However, we need to "safe-convert" because if the __str__ of
        #       one of the inputs is too large, it would probably be a problem
        #       to the file or quetzal database that saves this.
        #       Maybe this would do the trick:
        #       'kwargs': prefect.context.get('input_kwargs', None),

        family_name = self.meta.metadata_journal_family
        metadata = {
            family_name: {
                'created_by': 'iguazu',
                'version':  __version__,
                'task': f'{self.__class__.__module__}.{self.__class__.__name__}',
                'task_version': self.version,
                'status': status,
                'problem': problem,
                'parents': parents,
            }
        }
        return metadata

    def auto_manage_input_dataframe(self, name, *args, **kwargs):
        if not hasattr(self, '_meta'):
            raise AttributeError(f'No meta member in {self.__class__.__name__}, '
                                 f'did you call the super constructor before '
                                 f'auto_manage_input_dataframe?')
        opt_dict = self.meta.__dict__
        opt_dict['managed_inputs'][name] = (args, kwargs)
        self._meta = TaskOptions(**opt_dict)

    @property
    def version(self):
        """ Version of this task

        Any derived task that wishes to manually manage and track their version
        should overwrite this method/property
        """
        from iguazu import __version__
        return __version__

    @property
    def meta(self):
        return self._meta

    @property
    def forced(self):
        if self.meta.force:
            return True
        elif 'forced_tasks' in prefect.context:
            forced_tasks = prefect.context.forced_tasks
            return self.name in forced_tasks or 'all' in forced_tasks
        return False

    def _safe_prepare_inputs(self, safe_excs, **kws):
        safe_excs = safe_excs or ()
        safe_excs = tuple(set(safe_excs) | set(self.meta.graceful_exceptions))
        return super()._safe_prepare_inputs(safe_excs, **kws)

    def _safe_run(self, safe_excs, **inputs) -> Any:
        safe_excs = safe_excs or ()
        safe_excs = tuple(set(safe_excs) | set(self.meta.graceful_exceptions))
        return super()._safe_run(safe_excs, **inputs)

    def _graceful_fail(self, exc):
        kwargs = prefect.context.get('run_kwargs', {})
        meta = self.default_metadata(exc, **kwargs)
        # When its a partial fail (with outputs), create an ENDRUN signal
        # with the results directly
        # if isinstance(exc, PrefectStateSignal):
        #     # TODO: I am not sure this works! In particular exc.results seems weird!
        #     prepared_outputs = exc.results
        #     endrun = ENDRUN(state=GracefulFail(message=f'{exc}. Graceful fail for {fullname(exc)}',
        #                     result=prepared_outputs))
        # else:
        # When its not a partial fail with output,
        # Call ManagedTask._graceful_fail to get an ENDRUN prefect signal
        # but then hijack it to set a custom state
        try:
            endrun = ENDRUN(state=GracefulFail())
            super()._graceful_fail(exc)
        except ENDRUN as signal:
            endrun = signal

        # Set the metadata to the outputs that are file adapters
        # Note: we need to do this again (graceful_fail already calls
        # prepare_outputs which uploads and updates metadata), because
        # the metadata of a graceful fail is different (it's the default one)
        prepared_outputs = endrun.state.result
        for output in _iterate(prepared_outputs):
            if isinstance(output, FileAdapter):
                # TODO: update or replace?
                output.metadata.update(meta)
                output.upload()

        # Hijack/change the ManagedTask._graceful_fail for a different
        # state depending on the exception
        if isinstance(exc, PreviousResultsExist):
            new_state = SkippedResult(message='Previous results already exist.',
                                      result=prepared_outputs)
            endrun.state = new_state
        elif isinstance(exc, GracefulFailWithResults):
            new_state = GracefulFail(message='Gracefully failed with some partial results',
                                     result=prepared_outputs)
            endrun.state = new_state

        raise endrun


def _iterate(obj_or_tup):
    if obj_or_tup is None:
        return
    elif isinstance(obj_or_tup, tuple):
        yield from obj_or_tup
    yield obj_or_tup
