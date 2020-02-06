import inspect
import logging
import pathlib

import prefect

from iguazu.utils import (
    all_subclasses, import_submodules, load_pickle, dump_pickle
)


logger = logging.getLogger(__name__)


class PreparedFlow(prefect.Flow):

    REGISTRY_NAME = None

    def __init__(self, *args, **kwargs):
        # Separate kwargs of prefect.Flow
        prefect_params = inspect.getfullargspec(prefect.Flow.__init__).args
        prefect_kwargs = {k: kwargs.pop(k) for k in list(kwargs) if k in prefect_params}
        if not args and 'name' not in prefect_kwargs:
            args = (getattr(self.__class__, 'REGISTRY_NAME', None), )

        super().__init__(*args, **prefect_kwargs)
        # Call the user-defined build function with the remaining kwargs
        self._build(**kwargs)

    def _build(self, **kwargs):
        raise NotImplementedError('You need to implement the _build function')

    @staticmethod
    def click_options():
        return tuple()


def _get_flow_registry():
    # Force the import of all flows, so that the all_subclasses call later
    # does capture all declared classes
    import_submodules('iguazu.flows')

    registered_classes = {}
    for klass in all_subclasses(PreparedFlow):
        # Only consider classes with a defined class variable REGISTRY_NAME
        name = getattr(klass, 'REGISTRY_NAME', None)
        if name is None:
            continue
        elif name in registered_classes:
            raise RuntimeError(f'There are several flows registered under the'
                               f'same name "{name}"')
        registered_classes[getattr(klass, 'REGISTRY_NAME')] = klass

    return registered_classes


def execute_flow(func, func_kwargs, executor, context_args):
    flow_parameters = func_kwargs.copy()

    # Create flow
    flow = func(**flow_parameters)  # type: prefect.core.Flow
    known_parameters = {k.name: k.default for k in flow.parameters()}
    for p in list(flow_parameters):
        if p not in known_parameters or flow_parameters[p] is None:
            flow_parameters.pop(p)

    # Read cached states from a local file
    cache_filename = (
            pathlib.Path(context_args['temp_dir']) /
            'cache' /
            'task_states.pickle'
    )
    context_args.setdefault('caches', {})
    try:
        logger.info('Trying to restore previous cache from %s', cache_filename)
        previous_cache = load_pickle(cache_filename, None) or {}
        logger.info('Restored cached had %d elements', len(previous_cache))
        context_args['caches'] = previous_cache
        # flow_kwargs['task_states'] = adapt_task_states(load_pickle(state_filename, default={}),
        #                                                flow.sorted_tasks())
    except:
        logger.warning('Could not read cache at %s', cache_filename, exc_info=True)

    with prefect.context(**context_args) as context:
        # flow.schedule = prefect.schedules.OneTimeSchedule(start_date=pendulum.now() - datetime.timedelta(days=2))
        flow_state = flow.run(parameters=flow_parameters,
                              executor=executor,
                              run_on_schedule=True)
        cache = context.caches

    # # Save cached states to a local file
    # if isinstance(flow_state.result, Exception):
    #     logger.info('No cached saved because the flow result is an exception:\n%s',
    #                 ''.join(traceback.TracebackException.from_exception(flow_state.result).format()))
    # else:
    #     try:
    #         update_task_states(flow_state.result, state_filename)
    #     except:
    #         logger.warning('Could not save cache to %s', state_filename, exc_info=True)
    try:
        logger.info('Saving cache with %d elements to %s', len(cache), cache_filename)
        dump_pickle(cache, cache_filename)
    except:
        logger.warning('Could not save cache to %s', cache_filename, exc_info=True)

    return flow, flow_state


REGISTRY = _get_flow_registry()
