import os
import time
import tempfile
import traceback

from prefect.engine.executors import DaskExecutor, LocalExecutor, SynchronousExecutor
from prefect.engine.state import Mapped, Failed
from prefect.tasks.control_flow import switch, merge
from prefect.utilities.debug import raise_on_exception
from prefect import Flow, Parameter, context
import click
import pandas as pd

from iguazu.tasks.common import ListFiles
from iguazu.tasks.galvanic import CleanSignal, ApplyCVX, DetectSCRPeaks
from iguazu.tasks.handlers import logging_handler
from iguazu.tasks.quetzal import CreateWorkspace, ScanWorkspace, Query
from iguazu.tasks.unity import ReportSequences
from iguazu.tasks.summarize import ExtractFeatures


@click.command()
@click.option('-b', '--base-dir', type=click.Path(file_okay=False, dir_okay=True, exists=True),
              required=False, help='Path from where the files with raw data are read. ')
@click.option('-o', '--output-dir', type=click.Path(file_okay=False, dir_okay=True, exists=False),
              required=False, help='Path where the files with processed data are saved. ')
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
def cli(base_dir, output_dir, data_source, executor_type, executor_address, visualize_flow, force, raise_exc):
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
        temp_dir=output_dir or tempfile.mkdtemp(),
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
    clean_signal = CleanSignal(
        warmup_duration=30,
        glitch_kwargs=dict(
            scaling='robust',
            nu=1,
            range=(-0.02, +0.02),
            rejection_win=35,
        ),
        interpolation_kwargs=dict(
            method='linear',
        ),
        lowpass_kwargs=dict(
            Wn=[35],
            order=5,
        ),
        scaling_kwargs=dict(
            method='standard',
        ),
        corrupted_maxratio=0.3,
        force=force,
        state_handlers=[logging_handler],
    )
    apply_cvx = ApplyCVX(
        warmup_duration=15,
        glitch_kwargs=dict(
            scaling=False,
            nu=0,
            range=(0, 4),
            rejection_win=20,
        ),
        cvxeda_kwargs=None,
        force=force,
        state_handlers=[logging_handler],
    )
    detect_scr_peaks = DetectSCRPeaks(
        warmup_duration=15,
        glitch_kwargs=dict(
            nu=0,
            range=(0, 7),
        ),
        peak_detection_kwargs=dict(
            width=0.5,
            prominence=0.1,
            prominence_window=15,
        ),
        force=force,
        state_handlers=[logging_handler],
    )
    extract_features_scr = ExtractFeatures(signals_group="/gsr/timeseries/scrpeaks",
                                           report_group="/unity/sequences_report",
                                           output_group="/gsr/features/scr",
                                           feature_definitions={
                                               "tau": {"class": "numpy.sum", "columns": ["SCR_peaks_detected"],
                                                       "divide_by_duration": True, "empty_policy": 0.0,
                                                       "drop_bad_samples": True},
                                               "median": {"class": "numpy.nanmedian",
                                                          "columns": ['SCR_peaks_increase-duration',
                                                                      'SCR_peaks_increase-amplitude'],
                                                          "divide_by_duration": False, "empty_policy": "bad",
                                                          "drop_bad_samples": True}})

    scl_columns = ['F_clean_inversed_lowpassed_zscored_SCL']
    extract_features_scl = ExtractFeatures(signals_group="/gsr/timeseries/deconvoluted",
                                           report_group="/unity/sequences_report",
                                           output_group="/gsr/features/scl",
                                           feature_definitions={
                                               "median": {"class": "numpy.nanmedian", "columns": scl_columns,
                                                          "divide_by_duration": False, "empty_policy": "bad",
                                                          "drop_bad_samples": True},
                                               "std": {"class": "numpy.nanstd", "columns": scl_columns,
                                                       "divide_by_duration": False, "empty_policy": "bad",
                                                       "drop_bad_samples": True},
                                               "ptp": {"class": "numpy.ptp", "columns": scl_columns,
                                                       "divide_by_duration": False, "empty_policy": "bad",
                                                       "drop_bad_samples": True},
                                               "linregress": {"custom": "linregress", "columns": scl_columns,
                                                              "divide_by_duration": False, "empty_policy": "bad",
                                                              "drop_bad_samples": True},
                                               "auc": {"custom": "auc", "columns": scl_columns,
                                                       "divide_by_duration": False, "empty_policy": "bad",
                                                       "drop_bad_samples": True},
                                           })

    report_sequences = ReportSequences(sequences=None)
    # Flow/runtime arguments
    flow_parameters = dict(
        basedir=base_dir,
        data_source=data_source,
        sql="""
            SELECT id, filename FROM base
            LEFT JOIN iguazu USING (id)
            WHERE 
            base.filename LIKE '%.hdf5' AND 
            iguazu.id IS NULL
            LIMIT 3
        """,
    )

    # Flow definition
    with Flow('galvanic-feature-extraction-flow') as flow:
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
        raw_signals = merge(local_files_dataset, remote_files_dataset)

        # Galvanic flow
        clean_signals = clean_signal.map(signal=raw_signals,
                                         events=raw_signals)
        cvx = apply_cvx.map(clean_signals)
        scr = detect_scr_peaks.map(cvx)
        sequences_reports = report_sequences.map(events=raw_signals)
        scr_features = extract_features_scr.map(signals=scr, report=sequences_reports)
        scl_features = extract_features_scl.map(signals=cvx, report=sequences_reports)

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
    cli()
