# -*- coding: utf-8 -*-
import functools
import logging
import os
import pathlib
import tempfile
import traceback

import click
import pandas as pd
from prefect.engine.executors import LocalExecutor, SynchronousExecutor, DaskExecutor

from iguazu.core.files import parse_data_url
from iguazu.core.flows import execute_flow, REGISTRY
from iguazu.core.tasks import Task

logger = logging.getLogger(__name__)


class TaskNameListType(click.ParamType):
    name = 'text1[,text2...]'

    def convert(self, value, param, ctx):
        parts = value.split(',')
        definitions = []
        for p in parts:
            tup = click.types.StringParamType.convert(self, p, param, ctx)
            definitions.append(tup)
        return definitions


@click.group('flows')
def flows_group():
    """Flow commands"""
    pass


@flows_group.command(name='list')
def list_():
    """List all available flows"""
    records = []
    for name, klass in REGISTRY.items():
        doc = getattr(klass, '__doc__', None) or f'Not documented! Please add a docstring to {klass.__name__}'
        doc = doc.split('\n', 1)[0].strip()
        records.append({'NAME': name, 'DESCRIPTION': doc})
    df = pd.DataFrame.from_records(records).set_index('NAME').sort_index()

    click.secho('List of registered flows', fg='blue')
    with pd.option_context('display.width', 120, 'display.max_rows', None, 'display.max_colwidth', 120):
        click.echo(df.to_string())


@flows_group.command()
@click.argument('flow_name', type=click.Choice(REGISTRY.keys()),
                metavar='FLOW_NAME')
@click.option('-o', '--output', type=click.Path(dir_okay=False),
              required=False,
              help='Output PDF file where the rendered plan DAG will be saved.')
@click.option('--show/--no-show', is_flag=True, default=True, show_default=True,
              help='Opens the rendered graph.')
def info(flow_name, output, show):
    """Show information concerning the flow FLOW_NAME"""
    if flow_name not in REGISTRY:
        # Should not happen if used from click, but just in case
        click.secho(f'There is no registered flow with name "{flow_name}"', fg='yellow')
        raise click.ClickException(f'Unknown prepared flow')

    flow_class = REGISTRY[flow_name]
    click.secho(f'Creating flow from {flow_class.__name__}...', fg='blue')
    flow = flow_class()

    # Print task names
    click.secho(f'Flow {flow.name} defines the following tasks:', fg='green')
    tr = task_report(flow)
    click.secho(tr.to_string(index=False))

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

    def get_help(self, ctx):
        help_str = super().get_help(ctx)
        help_str = help_str.replace('\nCommands:\n', '\nAvailable flows:\n', 1)
        return help_str


@flows_group.group('run', cls=RunFlowGroup, subcommand_metavar='FLOW_NAME [ARGS] ...', no_args_is_help=True)
# @click.option('--default-data-backend', type=click.Choice(['local', 'quetzal']),
#               required=False, default='local',
#               help='Default data backend when creating new files without parents.')
@click.option('--temp-url', default=None, required=False,
              help='URL where temporary files will be saved. Use a complete url '
                   'with a scheme, such as file://temp_dir or quetzal://my_workspace/temp_dir')
@click.option('--output-url', default=None, required=False,
              help='URL where final files (not temporary) will be saved. Use a complete url '
                   'with a scheme, such as file://output_dir or quetzal://my_workspace/output_dir')
@click.option('--temp-dir', default=None, required=False,
              type=click.Path(file_okay=False, dir_okay=True, exists=False),
              help='Local directory where Iguazu and Prefect store information unrelated to '
                   'the data, such as caches.')
# @click.option('--default-workspace', required=False,
#               default=None, help='Default quetzal workspace when creating new files and '
#                                  'when using --data-target-backend quetzal')
# @click.option('--temp-dir', default=None, #type=click.Path(file_okay=False, dir_okay=True, exists=False),
#               required=False, help='Path where temporary files with processed data are saved. ')
# @click.option('--output-dir', default=None, #type=click.Path(file_okay=False, dir_okay=True, exists=False),
#               required=False, help='Path where final files with processed data are saved. ')
@click.option('--executor-type', type=click.Choice(['local', 'synchronous', 'dask']),
              default='local', help='Type of executor to run the flow. Default is local.')
@click.option('--executor-address', required=False,
              help='Address for a remote executor. Only used when --executor-type=dask.')
# @click.option('--report', type=click.Path(dir_okay=False),  # report will now default to temp_dir/report-id.csv
#               required=False,
#               help='Output CSV report of the execution')
@click.option('--force', required=False, type=TaskNameListType(),
              help='Comma-separated list of tasks whose execution should be forced. '
                   'Use "--force all" to force all tasks')
@click.option('--cache/--no-cache', 'cache', is_flag=True, default=True, show_default=True,
              help='Use the prefect cache. ')
@click.option('--allow-flow-failure', is_flag=True, default=False,
              help='When this flag is set, a flow execution that is not successful will '
                   'not make the program exit with a non-zero exit code. By default, '
                   'flows that are not successful have an exit code of -1.')
@click.pass_context
def run_group(ctx, temp_url, output_url, temp_dir, executor_type, executor_address, force, cache, allow_flow_failure):
    """Run the flow registered as FLOW_NAME

    Use command `iguazu flows run --help` to get a list of all available flows.
    """
    ctx.obj = ctx.obj or {}
    opts = {
        'temp_url': temp_url,
        'output_url': output_url,
        'temp_dir': temp_dir,
        # 'data_source_backend': data_source_backend,
        # 'data_target_backend': data_target_backend,
        # 'data_target_backend_parameters': data_target_backend_parameters,
        # 'data_backend': data_backend,
        # 'data_backend_workspace_id': None,
        # 'temp_dir': temp_dir,
        # 'output_dir': output_dir,
        'executor_type': executor_type,
        'executor_address': executor_address,
        # 'csv_report': report,
        'force': force,
        'cache': cache,
        'allow_flow_failure': allow_flow_failure,
    }
    # if data_backend == 'quetzal':
    #     click.echo(f'Using Quetzal as data backend for default results, '
    #                f'determining workspace id of workspace "{default_workspace}..."')
    #     client = helpers.get_client()
    #     details, total = helpers.workspace.list_(client,
    #                                              name=default_workspace,
    #                                              deleted=False)
    #     if total == 0:
    #         ctx.fail(f'No workspace named "{default_workspace}" was found')
    #     elif total > 1:
    #         ctx.fail(f'Workspace "{default_workspace}" is not unique, there were '
    #                  f'{total} workspaces with the same name')
    #     opts['data_backend_workspace_id'] = details[0]['id']

    ctx.obj.update(opts)


def run_flow(flow_class, **kwargs):
    # Preparations before running the flow

    # Prepare executor
    ctx = click.get_current_context()
    ctx.obj = ctx.obj or {}
    executor_type = ctx.obj.get('executor_type', None)
    executor_address = ctx.obj.get('executor_address', None)
    executor = prepare_executor(executor_type, executor_address)

    # Manage non-trivial defaults
    temp_dir = ctx.obj.get('temp_dir', None)
    if not temp_dir:
        temp_dir = tempfile.mkdtemp()
        logger.info('--temp-dir was not set by command-line, using %s', temp_dir)
    temp_url = ctx.obj.get('temp_url', None)
    output_url = ctx.obj.get('output_url', None)
    if not temp_url or not output_url:
        tmpdir = pathlib.Path(tempfile.mkdtemp()).resolve()
        if not temp_url:
            temp_url = (tmpdir / 'temp').as_uri()
            logger.info('--temp-url was not set by command-line, using %s', temp_url)
        if not output_url:
            output_url = (tmpdir / 'output').as_uri()
            logger.info('--output-url was not set by command-line, using %s', output_url.path)
    temp_url = parse_data_url(temp_url)
    output_url = parse_data_url(output_url)

    # Prepare context arguments
    context_args = dict(
        temp_dir=temp_dir,
        temp_url=temp_url,
        output_url=output_url,
        # data_dir=ctx.obj.get('data_dir', None) or get_data_dir(), # TODO: consider this
        # temp_dir=ctx.obj.get('temp_dir', None) or tempfile.mkdtemp(),
        # output_dir=ctx.obj.get('output_dir', None) or tempfile.mkdtemp(),
        # quetzal_logs_workspace_name=ctx.obj.get('quetzal_logs',
        #                                         kwargs.get('workspace_name', None)),
        # data_backend=ctx.obj.get('data_backend', None),
        # data_backend_workspace_id=ctx.obj.get('data_backend_workspace_id', None),
    )

    # Handle --force
    forced_tasks = ctx.obj.get('force', [])
    if forced_tasks:
        if 'all' in forced_tasks:
            context_args['forced_tasks'] = 'all'
        else:
            context_args['forced_tasks'] = forced_tasks

    # Handle secrets
    context_args.setdefault('secrets', {})
    if 'SLACK_WEBHOOK_URL' in os.environ:
        context_args['secrets']['SLACK_WEBHOOK_URL'] = os.environ['SLACK_WEBHOOK_URL']

    quetzal_kws = dict(
        url=os.getenv('QUETZAL_URL', 'https://local.quetz.al/api/v1'),
        username=os.getenv('QUETZAL_USER', None),
        password=os.getenv('QUETZAL_PASSWORD', None),
        api_key=os.getenv('QUETZAL_API_KEY', None))
    quetzal_kws = {k: v for (k, v) in quetzal_kws.items() if v is not None}
    context_args['secrets']['QUETZAL_CLIENT_KWARGS'] = quetzal_kws

    ###
    # Flow execution
    ###
    flow, flow_state = execute_flow(flow_class, kwargs, executor, context_args, ctx.obj.get('cache', False))

    ###
    # Flow post-processing: reports et al.
    ###
    if isinstance(flow_state.result, Exception):
        click.secho(f'Flow state was an exception: {flow_state.result}', fg='red')
        ctx.fail(f'Flow run failed: {flow_state.result}.')

    # Create dataframe report and save to CSV
    df = state_report(flow_state, flow)
    report = ctx.obj.get('csv_report', None)
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
    errors = df.loc[~df.exception.isnull()].query('status != "TriggerFailed"')
    if not errors.empty:
        click.secho('Flow encountered the following exceptions:', fg='red')
        for idx, row in errors.iterrows():
            click.secho(row["task name"], fg='yellow')
            click.secho(row.exception)
        click.secho(f'Flow execution encountered {len(errors)} errors.', fg='red')
        if not context_args.get('allow_flow_failure', False):
            ctx.exit(-1)


# add all flows to the run_group
def _init_run_group():
    # for flow_name, wrapper in registry.items():
    #     cmd = click.command(flow_name)(run_flow_command(wrapper))
    #     run_group.add_command(cmd)
    for name, klass in REGISTRY.items():
        # partially bind run_flow to the class constructor, but also
        # do a wraps so that the docstring is propagated
        cmd = functools.wraps(klass)(functools.partial(run_flow, klass))
        for decorator in klass.click_options():
            cmd = decorator(cmd)
        run_cmd = click.command(name)(cmd)
        run_group.add_command(run_cmd)


def prepare_executor(executor_type, executor_address=None):
    """Instantiate a prefect executor"""
    if executor_type == 'dask':
        if executor_address is not None:
            executor = DaskExecutor(executor_address)
        else:
            executor = DaskExecutor(local_processes=True)
    elif executor_type == "synchronous":
        executor = SynchronousExecutor()
    elif executor_type == 'local':
        executor = LocalExecutor()
    else:
        # Should not happen if click parameters are done correctly, but
        # kept for completeness
        raise ValueError(f'Unknown executor type "{executor_type}".')

    return executor


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
            'order': (sorted_tasks.index(task) if task in sorted_tasks else sys.maxsize, task.name, -1),
        })
        if state.is_mapped():
            for i, mapped_state in enumerate(state.map_states):
                rows.append({
                    'task class': type(task).__name__,
                    'task name': f'{task.name}[{i}]',
                    'status': type(mapped_state).__name__,
                    'message': mapped_state.message,
                    'exception': extract_state_exception(mapped_state),
                    'order': (sorted_tasks.index(task) if task in sorted_tasks else sys.maxsize, task.name, i),
                })

    df = (
        pd.DataFrame.from_records(rows)
            # Show tasks by their topological order, then reset the index
            .sort_values(by='order')
            .reset_index(drop=True)
    )
    return df


def task_report(flow):
    rows = []
    for task in flow:
        rows.append({
            'Name': task.name,
            'Class': task.__class__.__name__,
            'Iguazu task?': 'Yes' if issubclass(task.__class__, Task) else 'No',
        })

    return pd.DataFrame.from_records(rows)


def extract_state_exception(state):
    """Get the formatted traceback string of a prefect state exception"""
    if not state.is_failed():
        return None
    tb = traceback.TracebackException.from_exception(state.result)
    return ''.join(tb.format())


_init_run_group()
