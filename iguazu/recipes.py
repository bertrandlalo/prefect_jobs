# Note: this module cannot go in iguazu.flows due to circular dependency,
#       we could eventually use a lazy dictionary or something like that

import inspect
import logging
import traceback
import sys

import click
import pandas as pd
import prefect


logger = logging.getLogger(__name__)


registry = dict()


def register_flow(flow_name):

    # TODO: verification there is no whitespace on flow_name (it would not work with the cli)

    def decorator(func):

        if flow_name in registry:
            fn = registry[flow_name].__wrapped__
            qn = '.'.join([inspect.getmodule(fn).__name__, fn.__qualname__])
            raise ValueError(f'Cannot register flow {flow_name}: it was already '
                             f'registered by {qn}')

        # @functools.wraps(func)
        # def wrapper(*args, **kwargs):
        #     return func(*args, **kwargs)

        logger.debug('Registering flow %s -> %s.%s',
                     flow_name,
                     inspect.getmodule(func).__name__,
                     func.__qualname__)
        registry[flow_name] = func #wrapper

        from iguazu.cli.flows import run_group, run_flow_command
        cmd = click.command(flow_name)(run_flow_command(func))
        run_group.add_command(cmd)

        return func

    return decorator


def inherit_params(base):
    #
    # if not hasattr(base, '__click_params__'):
    #     raise ValueError('Cannot inherit click parameters or options from a '
    #                      'function that does not use click parameter or options')

    def decorator(func):
        for param in getattr(base, '__click_params__', []):
            click.decorators._param_memo(func, param)
        return func

    return decorator


# Import flows in order to trigger all @register_flow decorators
def _import_flows():
    logger.debug('Recursively importing flows to fill the registry')

    import iguazu.flows.datasets
    logger.debug('Loaded flows in %s', iguazu.flows.datasets)
    import iguazu.flows.galvanic
    logger.debug('Loaded flows in %s', iguazu.flows.galvanic)


_import_flows()

#
# factory_methods = {
#     # Dataset handling flows
#     'datasets:local': iguazu.flows.datasets.local_dataset_flow,
#     'datasets:merged': iguazu.flows.datasets.merged_dataset_flow,
#     'datasets:quetzal': iguazu.flows.datasets.quetzal_dataset_flow,
#     'datasets:debug': iguazu.flows.datasets.print_dataset_flow,
#     # Galvanic flows
#     'galvanic:template': iguazu.flows.galvanic.galvanic_features_template,
#     'galvanic:pipeline': iguazu.flows.galvanic.galvanic_features_flow,
#     # Feature collection
# }


def execute_flow(func, func_kwargs, executor, context_args, flow_kwargs=None):
    flow_parameters = func_kwargs.copy()
    flow_kwargs = flow_kwargs or {}

    # Create flow
    flow = func(**flow_parameters)
    for p in list(flow_parameters):
        if p not in flow.parameters():
            flow_parameters.pop(p)

    with prefect.context(**context_args):
        flow_state = flow.run(parameters=flow_parameters,
                              executor=executor,
                              **flow_kwargs)
    return flow, flow_state


def state_report(flow_state, flow=None):
    rows = []
    sorted_tasks = flow.sorted_tasks() if flow else []
    for task in flow_state.result:
        state = flow_state.result[task]
        rows.append({
            'task class': type(task).__name__,
            'task name': task.name,
            'status': type(state).__name__,
            'message': state.message,
            'exception': extract_state_exception(state),
            'order': (sorted_tasks.index(task) if task in sorted_tasks else sys.maxsize, -1),
        })
        if state.is_mapped():
            for i, mapped_state in enumerate(state.map_states):
                rows.append({
                    'task class': type(task).__name__,
                    'task name': f'{task.name}[{i}]',
                    'status': type(mapped_state).__name__,
                    'message': mapped_state.message,
                    'exception': extract_state_exception(mapped_state),
                    'order': (sorted_tasks.index(task) if task in sorted_tasks else sys.maxsize, i),
                })

    df = (
        pd.DataFrame.from_records(rows)
            # Show tasks by their topological order, then reset the index
            .sort_values(by='order')
            .reset_index(drop=True)
    )
    return df


def extract_state_exception(state):
    """Get the formatted traceback string of a prefect state exception"""
    if not state.is_failed():
        return None
    tb = traceback.TracebackException.from_exception(state.result)
    return ''.join(tb.format())
