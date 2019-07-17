import os
import tempfile
import time
import traceback

import click
import pandas as pd
from prefect import Flow, Parameter, context
from prefect.engine.executors import DaskExecutor, LocalExecutor, SynchronousExecutor
from prefect.engine.state import Mapped, Failed
from prefect.tasks.control_flow import switch, merge
from prefect.utilities.debug import raise_on_exception

from iguazu.tasks.common import ListFiles
from iguazu.tasks.quetzal import CreateWorkspace, ScanWorkspace, Query
from iguazu.tasks.summarize import SummarizePopulation


@click.command()
@click.option('-b', '--base-dir', type=click.Path(file_okay=False, dir_okay=True, exists=True),
              required=False, help='Path from where the files with raw data are read. ')
@click.option('-t', '--temp-dir', type=click.Path(file_okay=False, dir_okay=True, exists=False),
              required=False, help='Path where temporary files with processed data are saved. ')
@click.option('-o', '--output-dir', type=click.Path(file_okay=False, dir_okay=True, exists=False),
              required=False, help='Path where final files with processed data are saved. ')
@click.option('--data-source', type=click.Choice(['local', 'quetzal']),
              default='local', help='Data source that provides input files for this flow.')
@click.option('--executor-type', type=click.Choice(['local', 'synchronous', 'dask']),
              default='local', help='Type of executor to run the flow. Default is local.')
@click.option('--executor-address', required=False,
              help='Address for a remote executor. Only used when --executor-type=dask.')
@click.option('--visualize-flow', is_flag=True,
              help='Whether to visualize the flow graphs')
@click.option('--force', is_flag=True,
              help='Whether to force the processing if the path already exists in the output file. ')
@click.option('--raise/--no-raise', 'raise_exc', is_flag=True, default=False,
              help='Raise the exceptions encountered during execution when scheduler is local')
def cli(base_dir, temp_dir, output_dir, data_source, executor_type, executor_address, visualize_flow, force, raise_exc):
    """ Run the HDF5 pipeline on the specified FILENAMES.
    Do not specify any FILENAMES to run on *all* files found on DATAFOLDER.
    """
    if executor_type == 'dask':
        if executor_address:
            executor = DaskExecutor(executor_address)
        else:
            executor = DaskExecutor(local_processes=True)
    elif executor_type == "synchronous":
        executor = SynchronousExecutor()
    else:  # default
        executor = LocalExecutor()

    # Context/global arguments
    context_args = dict(
        quetzal_client=dict(
            url=os.getenv('QUETZAL_URL', 'https://local.quetz.al/api/v1'),
            username=os.getenv('QUETZAL_USER', 'admin'),
            password=os.getenv('QUETZAL_PASSWORD', 'secret'),
            insecure=True,
        ),
        temp_dir=temp_dir or tempfile.mkdtemp(),
        output_dir=output_dir or tempfile.mkdtemp(),
        raise_on_exception=raise_exc,
    )

    # Tasks and task arguments
    list_files = ListFiles(as_proxy=True)
    quetzal_create = CreateWorkspace(
        workspace_name='iguazu-dev-8',
        exist_ok=True,
        families=dict(
            iguazu=None,
            galvanic=None,
            omi=None,
            vr_sequences=None,
        ),
    )
    quetzal_scan = ScanWorkspace(
        name='Update workspace SQL views',
    )
    quetzal_query = Query(
        name='Query quetzal',
        as_proxy=True,
    )

    merge_population = SummarizePopulation(groups={'gsr_features_scr': None,
                                                   'gsr_features_scl': None})

    # Flow/runtime arguments
    flow_parameters = dict(
        basedir=base_dir,
        data_source=data_source,
        sql="""
            SELECT id, filename FROM base
            LEFT JOIN iguazu USING (id)
            WHERE 
            base.filename LIKE '%_gsr.hdf5' AND 
            iguazu.id IS NOT NULL
            LIMIT 3
        """,
    )

    # Flow definition
    with Flow('galvanic-population-summarize-flow') as flow:
        sql = Parameter('sql')
        basedir = Parameter('basedir')
        data_source = Parameter('data_source')

        # For file data source: extract files
        local_files_dataset = list_files(basedir)

        # For quetzal data source: query files
        wid = quetzal_create()
        wid_bis = quetzal_scan(wid)
        remote_files_dataset = quetzal_query(query=sql, workspace_id=wid_bis)

        # conditional on the local or quetzal data source
        switch(condition=data_source,
               cases={'local': local_files_dataset, 'quetzal': wid})
        features_files = merge(local_files_dataset, remote_files_dataset)

        # Summary flow
        population_summary = merge_population(features_files)

    if visualize_flow:
        flow.visualize()

    # Flow execution
    t0 = time.time()
    with raise_on_exception(), context(**context_args):
        flow_state = flow.run(parameters=flow_parameters,
                              executor=executor)
    local_execution_duration = time.time() - t0
    print(f'{executor_type} executor ran in {local_execution_duration} seconds')

    if visualize_flow:
        flow.visualize(flow_state=flow_state)

    # TODO: refactor this report somewhere else!
    task_rows = []
    exceptions = []
    if isinstance(flow_state.result, Exception):
        exceptions.append(flow_state.result)

    else:
        for t in flow_state.result:
            state = flow_state.result[t]
            if isinstance(state, Mapped):
                for i, s in enumerate(state.map_states):
                    task_rows.append({
                        'task class': type(t).__name__,
                        'task name': f'{t.name}[{i}]',
                        'status': type(s).__name__.upper(),
                        'message': s.message,
                        'exception': s.result if isinstance(s, Failed) else '',
                    })
                    if isinstance(s, Failed):
                        exceptions.append(s.result)
            else:
                task_rows.append({
                    'task class': type(t).__name__,
                    'task name': t.name,
                    'status': type(state).__name__.upper(),
                    'message': state.message,
                    'exception': t.result if isinstance(t, Failed) else '',
                })
                if isinstance(t, Failed):
                    exceptions.append(t.result)

        df = pd.DataFrame.from_records(task_rows)
        if not df.empty:
            df = df[['status', 'task class', 'task name', 'message', 'exception']]
            df.columns = [col.upper() for col in df.columns]
            print(df.to_string(index=False))

    if exceptions:
        print('\n\n\nEncountered the following exceptions:')
        for i, exc in enumerate(exceptions, 1):
            print(f'Exception {i} / {len(exceptions)}:')
            traceback.print_tb(exc.__traceback__)
            print('\n')


if __name__ == '__main__':  # __name__ is the process id, that decides for what the process is supposed to work on
    #cli()
    print('Removed this cli!')
