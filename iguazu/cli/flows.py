# -*- coding: utf-8 -*-
import inspect
import functools
import os
import pathlib
import tempfile
import traceback

import click
import pandas as pd
import prefect
from prefect.engine.executors import LocalExecutor, SynchronousExecutor

from iguazu.executors import DaskExecutor
from iguazu.recipes import registry


@click.group('flows')
def flows_group():
    """Flow commands"""
    pass


@flows_group.command()
@click.argument('flow_name', type=click.Choice(registry),
                metavar='FLOW_NAME')
@click.option('-o', '--output', type=click.Path(dir_okay=False),
              required=False,
              help='Output PDF file where the rendered plan DAG will be saved.')
@click.option('--show/--no-show', is_flag=True, default=True,
              help='Opens the rendered graph.')
def info(flow_name, output, show):
    """Show information of a flow"""
    if flow_name not in registry:  # TODO: can this be managed by click?
        raise click.ClickException(f'Unknown flow recipe {flow_name}')

    make_flow_func = registry[flow_name]

    click.secho(f'Creating flow from {make_flow_func.__name__}...', fg='blue')
    flow = make_flow_func()

    if output:
        # Handle output, prefect requires it to be without the .pdf extension
        path = pathlib.Path(output)
        if path.suffix != '.pdf':
            raise click.ClickException('Output filename must have a .pdf extension')
        filename = path.stem
    else:
        filename = None
        path = None

    try:
        if filename:
            flow.visualize(filename=filename)
        if show:
            flow.visualize()
    except ImportError as exc:
        raise click.ClickException(str(exc))

    # For some weird reason, graphviz makes a temporary file
    if filename and path.with_suffix('').exists():
        path.with_suffix('').unlink()


# @flows_group.command('list')
# def list_():
#     """List available flows"""
#     records = []
#     for name in registry:
#         func = registry[name]
#         doc = func.__doc__
#         # fg = None
#         if doc is None:
#             # fg = 'yellow'
#             doc = f'⚠️  Not documented, please document {func.__qualname__} ⚠️'
#         records.append((name, inspect.getmodule(func).__name__ + '.' + func.__qualname__, doc))
#
#     df = pd.DataFrame.from_records(records, columns=['flow_name', 'function', 'summary'])
#     with pd.option_context('display.max_colwidth', 80):
#         df_str = df.to_string(index=False)
#
#     click.secho('List of available flows:', fg='blue')
#     for i, line in enumerate(df_str.split('\n'), -1):
#         if i == -1:
#             click.secho(line.upper(), fg='blue')
#         else:
#             click.secho(line)


class RunFlowGroup(click.core.Group):
    """A regular click group, but with a custom error

    This class is completely ornamental, it replaces the CLI error message
    "No such command" with "No such flow", which makes more sense when running
    `iguazu flows run some-unknown-flow`.
    """

    def resolve_command(self, ctx, args):
        try:
            return super().resolve_command(ctx, args)
        except click.UsageError as exc:
            msg = exc.message.replace('No such command', 'No such flow', 1)
            raise click.UsageError(msg)


@flows_group.group('run', cls=RunFlowGroup, subcommand_metavar='FLOW_NAME [ARGS] ...', no_args_is_help=True)
@click.option('--temp-dir', type=click.Path(file_okay=False, dir_okay=True, exists=False),
              required=False, help='Path where temporary files with processed data are saved. ')
@click.option('--output-dir', type=click.Path(file_okay=False, dir_okay=True, exists=False),
              required=False, help='Path where final files with processed data are saved. ')
@click.option('--executor-type', type=click.Choice(['local', 'synchronous', 'dask']),
              default='local', help='Type of executor to run the flow. Default is local.')
@click.option('--executor-address', required=False,
              help='Address for a remote executor. Only used when --executor-type=dask.')
@click.option('--report', type=click.Path(dir_okay=False),
              required=False,
              help='Output CSV report of the execution')
@click.pass_context
def run_group(ctx, temp_dir, output_dir, executor_type, executor_address, report):
    """Run flow FLOW_NAME

    Use command `iguazu flows list` to get a list of all available flows.
    """
    ctx.obj = ctx.obj or {}
    opts = {
        'temp_dir': temp_dir,
        'output_dir': output_dir,
        'executor_type': executor_type,
        'executor_address': executor_address,
        'csv_report': report,
    }
    ctx.obj.update(opts)


def run_flow_command(func):
    @functools.wraps(func)
    def decorator(**kwargs):
        from iguazu.recipes import execute_flow, state_report
        ###
        # Preparations before running the flow
        ###

        # Prepare executor
        ctx = click.get_current_context()
        ctx.obj = ctx.obj or {}
        executor_type = ctx.obj.get('executor_type', None)
        executor_address = ctx.obj.get('executor_address', None)
        if executor_type == 'dask':
            if executor_address:
                executor = DaskExecutor(executor_address)
            else:
                executor = DaskExecutor(local_processes=True)
        elif executor_type == 'synchronous':
            executor = SynchronousExecutor()
        elif executor_type == 'local':
            executor = LocalExecutor()
        else:
            # Should not happen if click parameters are done correctly, but
            # kept for completeness
            raise ValueError(f'Unknown executor type "{executor_type}".')

        # Prepare context arguments
        context_args = dict(
            temp_dir=ctx.obj.get('temp_dir', None) or tempfile.mkdtemp(),
            output_dir=ctx.obj.get('output_dir', None) or tempfile.mkdtemp(),
        )
        if {'QUETZAL_URL', 'QUETZAL_USER', 'QUETZAL_PASSWORD'} & set(os.environ):
            # At least one of these keys exist in the environment
            quetzal_kws = dict(
                url=os.getenv('QUETZAL_URL', 'https://local.quetz.al/api/v1'),
                username=os.getenv('QUETZAL_USER', 'admin'),
                password=os.getenv('QUETZAL_PASSWORD', 'password'),
                insecure=str2bool(os.getenv('QUETZAL_INSECURE', 0))
            )
            context_args['quetzal_client'] = quetzal_kws
        # force = ctx.obj.get('force', False)
        #
        # # Prepare flow parameters
        # flow_parameters = kwargs.copy()
        #
        # # Create flow
        # flow = func(**flow_parameters)
        # for p in list(flow_parameters):
        #     if p not in flow.parameters():
        #         flow_parameters.pop(p)

        ###
        # Flow execution
        ###
        flow, flow_state = execute_flow(func, kwargs, executor, context_args)
        # with prefect.context(**context_args):
        #     flow_state = flow.run(parameters=flow_parameters,
        #                           executor=executor)

        ###
        # Flow post-processing: reports et al.
        ###
        if isinstance(flow_state.result, Exception):
            click.secho(f'Flow state was an exception: {flow_state.result}', fg='red')
            ctx.fail(f'Flow run failed: {flow_state.result}.')
            #raise click.ClickException('Flow run failed')

        # Create dataframe report and save to CSV
        df = state_report(flow_state, flow)
        report = ctx.obj.get('report_csv', None)
        if report is None:
            tmpfile = tempfile.NamedTemporaryFile(prefix='iguazu_report_', suffix='.csv', delete=False)
            tmpfile.close()
            report = tmpfile.name
        if not df.empty:
            df = df[['status', 'task class', 'task name', 'message', 'exception']]
            df_upper = df.drop(columns='exception')
            df_upper.columns = [col.upper() for col in df_upper.columns]
            click.secho(df_upper.to_string())
            df.to_csv(report, index=False)
            click.secho(f'Saved CSV report on {report}', fg='blue')

        # Show a final error message if the flow failed
        errors = df.loc[~df.exception.isnull()]
        if not errors.empty:
            click.secho('Flow encountered the following exceptions:', fg='red')
            for idx, row in errors.iterrows():
                click.secho(row["task name"], fg='yellow')
                click.secho(row.exception)
            click.secho(f'Flow execution encountered {len(errors)} errors.', fg='red')
            ctx.exit(-1)

    return decorator


# add all flows to the run_group
def _init_run_group():
    for flow_name, wrapper in registry.items():
        #cmd = click.command(flow_name)(wrapper)#(run_flow()(wrapper))
        cmd = click.command(flow_name)(run_flow_command(wrapper))
        run_group.add_command(cmd)


# @run_group.command('a')
# def a():
#     pass


@flows_group.command()
@click.argument('flow_name', type=click.Choice(registry),
                metavar='FLOW_NAME')
# @click.argument('flow-parameters', type=CLIFlowParameterType(),
#                 metavar='PARAMS', nargs=-1)
@click.option('--executor-type', type=click.Choice(['local', 'synchronous', 'dask']),
              default='local', help='Type of executor to run the flow. Default is local.')
@click.option('--executor-address', required=False,
              help='Address for a remote executor. Only used when --executor-type=dask.')
# @click.option('-o', '--output', type=click.Path(dir_okay=False),
#               required=False,
#               help='Output PDF file where the rendered execution DAG will be saved.')
# @click.option('--show/--no-show', is_flag=True, default=True,
#               help='Opens the rendered graph.')
@click.option('--report', type=click.Path(dir_okay=False),
              required=False,
              help='Output CSV report of the execution')
@click.pass_context
def run_old(ctx, flow_name, flow_parameters, executor_type, executor_address, #output, show,
            report):
    """Run a flow"""

    flow_parameters = dict(flow_parameters)

    # Prepare executor
    executor = prepare_executor(executor_type, executor_address)

    func = registry[flow_name]
    flow = func(**flow_parameters)

    context_args = {
        #'raise_on_exception': True,
    }
    flow_parameters = {}

    with prefect.context(**context_args):
        flow_state = flow.run(
            parameters=flow_parameters,
            executor=executor,
        )

    #
    # Post-execution handling
    #
    report = report or tempfile.NamedTemporaryFile(prefix='iguazu_report_',
                                                   suffix='.csv', delete=False).name

    if isinstance(flow_state.result, Exception):
        click.secho(f'Flow state was an exception: {flow_state.result}', fg='red')
        raise click.ClickException('Flow run failed')

    rows = []
    for task in flow_state.result:
        state = flow_state.result[task]
        rows.append({
            'task class': type(task).__name__,
            'task name': task.name,
            'status': type(state).__name__,
            'message': state.message,
            'exception': extract_state_exception(state),
        })
        if state.is_mapped():
            for i, mapped_state in enumerate(state.map_states):
                rows.append({
                    'task class': type(task).__name__,
                    'task name': f'{task.name}[{i}]',
                    'status': type(mapped_state).__name__,
                    'message': mapped_state.message,
                    'exception': extract_state_exception(mapped_state),
                })

    df = pd.DataFrame.from_records(rows)
    if not df.empty:
        df = df[['status', 'task class', 'task name', 'message', 'exception']]
        df_upper = df.drop(columns='exception')
        df_upper.columns = [col.upper() for col in df_upper.columns]
        click.secho(df_upper.to_string())
        if report:
            df.to_csv(report, index=False)
            click.secho(f'Saved CSV report on {report}', fg='blue')

    errors = df.loc[~df.exception.isnull()]
    if not errors.empty:
        click.secho('Flow encountered the following exceptions:', fg='red')
        for idx, row in errors.iterrows():
            click.secho(row["task name"], fg='yellow')
            click.secho(row.exception)
        ctx.exit(-1)


def extract_state_exception(state):
    """Get the formatted traceback string of a prefect state exception"""
    if not state.is_failed():
        return None
    tb = traceback.TracebackException.from_exception(state.result)
    return ''.join(tb.format())


def prepare_executor(executor_type, executor_address=None):
    if executor_type == 'dask':
        if executor_address is not None:
            executor = DaskExecutor(executor_address)
        else:
            executor = DaskExecutor(local_processes=True)
    elif executor_type == "synchronous":
        executor = SynchronousExecutor()
    else:  # default
        executor = LocalExecutor()

    return executor


def str2bool(value):
    return str(value).lower() in ("yes", "true", "t", "1")
