from prefect.utilities.debug import raise_on_exception
from time import time
from prefect.engine.executors import DaskExecutor, LocalExecutor, SynchronousExecutor
from prefect import Flow, Parameter, context
logger = context.get("logger")
from prefect import unmapped



galvanic_clean_params = Parameter("galvanic_clean_params",
                                  default={"warmup_duration": 30, "column_name": "F",
                                            "corrupted_maxratio": .3,
                                            "glitch_params": {"scaling": "robust",
                                             "nu": 1, "range": [-0.02, +0.02],  "rejection_win": 20},
                                            "interpolation_params": {"method": "cubic"},
                                            "lowpass_params": {"Wn": [35], "order": 5},
                                            "scaling_params":  {"method": "standard"}})

galvanic_cvx_params = Parameter("galvanic_cvx_params", {"warmup_duration":  15,
                                    "column_name": "F_clean_inversed_lowpassed_zscored",
                                    "glitch_params":  {"scaling": False,
                                                     "nu": 0,
                                                     "range": [0, 4],
                                                     "rejection_win": 20},
                                                        "cvxeda_params": None})

galvanic_scrpeaks_params = Parameter("galvanic_scrpeaks_params", {"warmup_duration": 15, "column_name": "F_clean_inversed_lowpassed_zscored_SCR",
                                                        "peaks_params": {"width": .5,
                                                                        "prominence": .1,
                                                                        "prominence_window": 15},
                                                        "glitch_params":  {"nu": 0, "range": [0, 7]}})


import click
@click.command()
@click.option('-b', '--basedir', type=click.Path(file_okay=False, dir_okay=True, exists=True),
              required=True, help='Path from where the files with raw data are read. ')
@click.option('-o', '--outputdir', type=click.Path(file_okay=False, dir_okay=True, exists=False),
              required=True, help='Path where the files with processed data are saved. ')
@click.option('--executor_type', type=click.Choice(['local', 'synchronous', 'dask']),
              help='Type of executor to run the flow. ')
@click.option('--visualize_flow', is_flag=True,
              help='Whether to visualize the flow graphs')
@click.option('--force', is_flag=True,
              help='Whether to force the processing if the path already exists in the output file. ')

def cli(basedir, outputdir, executor_type, visualize_flow, force):

    """ Run the HDF5 pipeline on the specified FILENAMES.
    Do not specify any FILENAMES to run on *all* files found on DATAFOLDER.
    """
    from iguazu.tasks.galvanic import etl_galvanic_clean, etl_galvanic_cvx, etl_galvanic_scrpeaks
    from iguazu.tasks.common import list_files, io_filenames
    with Flow("process gsr") as flow:
        basedir_param = Parameter("basedir")
        outputdir_param = Parameter("outputdir")

        force_clean = Parameter("force_clean")
        force_cvx = Parameter("force_cvx")
        force_scrpeaks = Parameter("force_scrpeaks")

        list_files = list_files(basedir_param)
        io_filenames1 = io_filenames.map(list_files, unmapped(outputdir_param))
        etl_galvanic_clean = etl_galvanic_clean.map(io_filenames=io_filenames1,
                                                    tranform_params=unmapped(galvanic_clean_params),
                                                    force=unmapped(force_clean))
        io_filenames2 = io_filenames.map(etl_galvanic_clean)
        etl_galvanic_cvx = etl_galvanic_cvx.map(io_filenames=io_filenames2,
                                                tranform_params=unmapped(galvanic_cvx_params),
                                                force=unmapped(force_cvx))
        io_filenames3 = io_filenames.map(etl_galvanic_cvx)
        etl_galvanic_scrpeaks = etl_galvanic_scrpeaks.map(io_filenames=io_filenames3,
                                                          tranform_params=unmapped(galvanic_scrpeaks_params),
                                                          force=unmapped(force_scrpeaks))
    if visualize_flow:
        flow.visualize()
    t0 = time()
    if executor_type == 'dask':
        executor = DaskExecutor(local_processes=True, memory_limit=30 * 2 ** 30)
    elif executor_type=="synchronous":
        executor = SynchronousExecutor()
    else: # default
        executor = LocalExecutor()

    with raise_on_exception():
        flow_state = flow.run(executor=executor,
                              parameters={"basedir": basedir,
                                          "outputdir": outputdir,
                                          "force_clean": force, "force_cvx": force, "force_scrpeaks": force})
    local_execution_duration = time() - t0
    print("{executor_type} executor ran in {duration} seconds".format(executor_type=executor_type,
                                                                      duration=local_execution_duration))

    if visualize_flow:
        flow.visualize(flow_state=flow_state)


if __name__ == '__main__':    # __name__ is the process id, that decides for what the process is supposed to work on
    cli()