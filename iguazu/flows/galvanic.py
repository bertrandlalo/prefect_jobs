import os
import time

from prefect.utilities.debug import raise_on_exception
from prefect.engine.executors import DaskExecutor, LocalExecutor, SynchronousExecutor
from prefect import Flow, Parameter, context
import click

from iguazu.tasks.common import list_files, convert_to_file_proxy
from iguazu.tasks.galvanic import CleanSignal, ApplyCVX, DetectSCRPeaks
from iguazu.tasks.quetzal import Query, ConvertToFileProxy
from iguazu.tasks.vr_unity_events import ReportSequences


@click.command()
@click.option('-b', '--base-dir', type=click.Path(file_okay=False, dir_okay=True, exists=True),
              required=True, help='Path from where the files with raw data are read. ')
@click.option('-o', '--output-dir', type=click.Path(file_okay=False, dir_okay=True, exists=False),
              required=True, help='Path where the files with processed data are saved. ')
@click.option('--executor-type', type=click.Choice(['local', 'synchronous', 'dask']),
              default='local', help='Type of executor to run the flow. Default is local.')
@click.option('--visualize-flow', is_flag=True,
              help='Whether to visualize the flow graphs')
@click.option('--force', is_flag=True,
              help='Whether to force the processing if the path already exists in the output file. ')
def cli(base_dir, output_dir, executor_type, visualize_flow, force):

    """ Run the HDF5 pipeline on the specified FILENAMES.
    Do not specify any FILENAMES to run on *all* files found on DATAFOLDER.
    """
    if executor_type == 'dask':
        executor = DaskExecutor(local_processes=True)#, memory_limit=30 * 2 ** 30)
        # executor = DaskExecutor('localhost:8786')
    elif executor_type == "synchronous":
        executor = SynchronousExecutor()
    else: # default
        executor = LocalExecutor()

    # Context/global arguments
    context_args = dict(
        quetzal_client=dict(
            url=os.getenv('QUETZAL_URL', 'https://quetzal.omind.me/api/v1'),
            username=os.getenv('QUETZAL_USER', ''),
            password=os.getenv('QUETZAL_PASSWORD', ''),
            insecure=True,
        ),
        temp_dir=output_dir,
    )

    # Tasks and task arguments
    quetzal_query = Query(name='Query quetzal')
    convert_query = ConvertToFileProxy(id_key='id')
    clean_signal = CleanSignal(
        warmup_duration=30,
        glitch_kwargs=dict(
            scaling='robust',
            nu=1,
            range=(-0.02, +0.02),
            rejection_win=20,
        ),
        interpolation_kwargs=dict(
            method='cubic',
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
    )
    report_sequences = ReportSequences(sequences=None)
    # Flow/runtime arguments
    mode = 'local'  # TODO: move to click
    flow_parameters = dict()
    if mode == 'quetzal':
        flow_parameters['query'] = """
        SELECT * FROM base
        WHERE filename LIKE '%.hdf5'
        LIMIT 10
        """
    elif mode == 'local':
        flow_parameters['query'] = base_dir
    else:
        raise ValueError(f'Unknown mode "{mode}"')

    # Flow definition
    with Flow('test') as flow:

        query = Parameter('query')

        if mode == 'quetzal':
            rows = quetzal_query(query)
            input_files = convert_query(rows, workspace_id=None)
        else:
            rows = list_files(query)
            input_files = convert_to_file_proxy(rows, file_dir=base_dir)

        clean_signals = clean_signal.map(signal=input_files,
                                         events=input_files)
        cvx = apply_cvx.map(clean_signals)
        scr = detect_scr_peaks.map(cvx)
        sequences_reports = report_sequences.map(events=input_files)
    # Flow execution
    t0 = time.time()
    with raise_on_exception(), context(**context_args):
        flow_state = flow.run(parameters=flow_parameters,
                              executor=executor)
    local_execution_duration = time.time() - t0
    print(f'{executor_type} executor ran in {local_execution_duration} seconds')

    if visualize_flow:
        flow.visualize(flow_state=flow_state)


if __name__ == '__main__':    # __name__ is the process id, that decides for what the process is supposed to work on
    cli()
