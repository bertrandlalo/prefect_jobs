import pathlib
import tempfile
import traceback

import click
import pandas as pd
from prefect import context

from iguazu.recipes import factory_methods as factory


@click.group('flows')
def flows_group():
    """Flow commands and helpers"""
    pass


@flows_group.command()
@click.argument('flow_name', type=click.Choice(factory),
                metavar='FLOW_NAME')
@click.option('-o', '--output', type=click.Path(dir_okay=False),
              required=False,
              help='Output PDF file where the rendered plan DAG will be saved.')
@click.option('--show/--no-show', is_flag=True, default=True,
              help='Opens the rendered graph.')
def plan(flow_name, output, show):
    """Show a flow DAG plan"""
    if flow_name not in factory:  # TODO: can this be managed by click?
        raise click.ClickException(f'Unknown flow recipe {flow_name}')

    make_flow_func = factory[flow_name]

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


@flows_group.command('list')
def list_():
    """List available flows"""
    click.secho('List of available flows:', fg='blue')
    for name in factory:
        func = factory[name]
        doc = func.__doc__
        fg = None
        if doc is None:
            fg = 'yellow'
            doc = f'Not documented, please document {func.__qualname__} !!!'
        click.secho(f'\t{name} :\t', nl=False)
        click.secho(doc, fg=fg)


@flows_group.command()
@click.argument('flow_name', type=click.Choice(factory),
                metavar='FLOW_NAME')
@click.option('-o', '--output', type=click.Path(dir_okay=False),
              required=False,
              help='Output PDF file where the rendered execution DAG will be saved.')
@click.option('--show/--no-show', is_flag=True, default=True,
              help='Opens the rendered graph.')
@click.option('--report', type=click.Path(dir_okay=False),
              required=False,
              help='Output CSV report of the execution')
@click.pass_context
def run(ctx, flow_name, output, show, report):
    """Run a flow"""
    func = factory[flow_name]
    flow = func()

    context_args = {
        #'raise_on_exception': True,
    }

    with context(**context_args):
        flow_state = flow.run()

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
            'exception': extract_exception(state),
        })
        if state.is_mapped():
            for i, mapped_state in enumerate(state.map_states):
                rows.append({
                    'task class': type(task).__name__,
                    'task name': f'{task.name}[{i}]',
                    'status': type(mapped_state).__name__,
                    'message': mapped_state.message,
                    'exception': extract_exception(mapped_state),
                })

    df = pd.DataFrame.from_records(rows)
    if not df.empty:
        df = df[['status', 'task class', 'task name', 'message', 'exception']]
        df_upper = df.copy()
        df_upper.columns = [col.upper() for col in df_upper.columns]
        print(df_upper.to_string())
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


def extract_exception(state):
    if not state.is_failed():
        return None
    tb = traceback.TracebackException.from_exception(state.result)
    return ''.join(tb.format())
