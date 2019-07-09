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

from iguazu.tasks.common import ListFiles, MergeFilesFromGroups
from iguazu.tasks.galvanic import CleanSignal, ApplyCVX, DetectSCRPeaks, RemoveBaseline
from iguazu.tasks.handlers import logging_handler
from iguazu.tasks.quetzal import CreateWorkspace, ScanWorkspace, Query
from iguazu.tasks.summarize import ExtractFeatures
from iguazu.tasks.unity import ReportSequences


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
        workspace_name='gsr-devel-v4',
        temp_dir=temp_dir or tempfile.mkdtemp(),
        output_dir=output_dir or tempfile.mkdtemp(),
        raise_on_exception=raise_exc,
    )

    # Tasks and task arguments
    list_files = ListFiles(as_proxy=True)
    quetzal_create = CreateWorkspace(
        #workspace_name='gsr-devel-v3',
        exist_ok=True,
        families=dict(
            iguazu=None,
            galvanic=None,
            omi=None,
            vr_sequences=None,
            task=None,
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
            method='pchip',
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
        skip_on_upstream_skip=False,
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
        skip_on_upstream_skip=False,
    )
    report_sequences = ReportSequences(
        sequences=None,
        force=force,
        state_handlers=[logging_handler]
    )
    extract_features_scr = ExtractFeatures(
        signals_group="/gsr/timeseries/scrpeaks",
        report_group="/unity/sequences_report",
        output_group="/gsr/features/scr",
        feature_definitions=dict(
            rate={
                "class": "numpy.sum",
                "columns": ["SCR_peaks_detected"],
                "divide_by_duration": True,
                "empty_policy": 0.0,
                "drop_bad_samples": True,
            },
            median={
                "class": "numpy.nanmedian",
                "columns": ['SCR_peaks_increase-duration', 'SCR_peaks_increase-amplitude'],
                "divide_by_duration": False,
                "empty_policy": 0.0,
                "drop_bad_samples": True,
            }
        ),
        force=force,
        state_handlers=[logging_handler],
        skip_on_upstream_skip=False
    )
    scl_columns = ['F_clean_inversed_lowpassed_zscored_SCL']
    extract_features_scl = ExtractFeatures(
        signals_group="/gsr/timeseries/deconvoluted",
        report_group="/unity/sequences_report",
        output_group="/gsr/features/scl",
        feature_definitions={
            "median": {
                "class": "numpy.nanmedian",
                "columns": scl_columns,
                "divide_by_duration": False,
                "empty_policy": "bad",
                "drop_bad_samples": True,
            },
            "std": {
                "class": "numpy.nanstd",
                "columns": scl_columns,
                "divide_by_duration": False,
                "empty_policy": "bad",
                "drop_bad_samples": True,
            },
            "ptp": {
                "class": "numpy.ptp",
                "columns": scl_columns,
                "divide_by_duration": False,
                "empty_policy": "bad",
                "drop_bad_samples": True,
            },
            "linregress": {
                "custom": "linregress",
                "columns": scl_columns,
                "divide_by_duration": False,
                "empty_policy": "bad",
                "drop_bad_samples": True,
            },
            "auc": {
                "custom": "auc",
                "columns": scl_columns,
                "divide_by_duration": False,
                "empty_policy": "bad",
                "drop_bad_samples": True,
            },
        },
        force=force,
        state_handlers=[logging_handler],
        skip_on_upstream_skip=False,
    )
    baseline_sequences = ['lobby_sequence_0', 'lobby_sequence_1', 'physio-sonification_survey_0',
                          'cardiac-coherence_survey_0', 'cardiac-coherence_survey_1',
                          'cardiac-coherence_score_0']
    correct_scr = RemoveBaseline(
        features_group="/gsr/features/scr",
        output_group="/gsr/features/scr_corrected",
        sequences=baseline_sequences,
        columns=['SCR_peaks_detected_rate'],
        force=force,
        state_handlers=[logging_handler],
        skip_on_upstream_skip=False,
    )
    correct_scl = RemoveBaseline(
        features_group="/gsr/features/scl",
        output_group="/gsr/features/scl_corrected",
        sequences=baseline_sequences,
        columns=[
            'F_clean_inversed_lowpassed_zscored_SCL_median',
            'F_clean_inversed_lowpassed_zscored_SCL_ptp',
            'F_clean_inversed_lowpassed_zscored_SCL_linregress_slope',
            'F_clean_inversed_lowpassed_zscored_SCL_auc'
        ],
        force=force,
        state_handlers=[logging_handler],
        skip_on_upstream_skip=False,
    )
    merge_subject = MergeFilesFromGroups(
        suffix="_gsr",
        state_handlers=[logging_handler],
        skip_on_upstream_skip=False,
    )

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
            -- AND base.filename LIKE 'data_2018-02-16.09.32%'
            LIMIT 20
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
        scr_features_corrected = correct_scr.map(features=scr_features)
        scl_features_corrected = correct_scl.map(features=scl_features)

        subject_summary = merge_subject.map(parent=raw_signals,
                                            gsr_timeseries_deconvoluted=cvx,
                                            gsr_features_scr=scr_features_corrected,
                                            gsr_features_scl=scl_features_corrected,
                                            unity_sequences=sequences_reports)

    if visualize_flow:
        flow.visualize()

    # Flow execution
    t0 = time.time()
    with context(**context_args):
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
