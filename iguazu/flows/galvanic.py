from prefect.utilities.debug import raise_on_exception
from time import time
from prefect.engine.executors import DaskExecutor, LocalExecutor, SynchronousExecutor
from prefect import Flow, Parameter, context
logger = context.get("logger")
from prefect import unmapped
from iguazu.tasks.common import list_files, io_filenames
from iguazu.tasks.galvanic import etl_galvanic_clean, etl_galvanic_cvx, etl_galvanic_scrpeaks


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



if __name__ == '__main__':    # __name__ is the process id, that decides for what the process is supposed to work on
    with Flow("process gsr") as flow:
        basedir = Parameter("basedir")
        outputdir = Parameter("outputdir")

        force_clean = Parameter("force_clean")
        force_cvx = Parameter("force_cvx")
        force_scrpeaks = Parameter("force_scrpeaks")

        # for a list of all episodes
        list_files = list_files(basedir)
        io_filenames1 = io_filenames.map(list_files, unmapped(outputdir))
        etl_galvanic_clean = etl_galvanic_clean.map(io_filenames=io_filenames1, tranform_params=unmapped(galvanic_clean_params), force=unmapped(force_clean))
        io_filenames2 = io_filenames.map(etl_galvanic_clean)
        etl_galvanic_cvx = etl_galvanic_cvx.map(io_filenames=io_filenames2, tranform_params=unmapped(galvanic_cvx_params), force=unmapped(force_cvx))
        io_filenames3 = io_filenames.map(etl_galvanic_cvx)
        etl_galvanic_scrpeaks = etl_galvanic_scrpeaks.map(io_filenames=io_filenames3, tranform_params=unmapped(galvanic_scrpeaks_params),
                                            force=unmapped(force_scrpeaks))

    flow.visualize()
    t0 = time()
    executor = LocalExecutor()  # You can comment this line and uncomment the following to use a Dask executor.
    #executor = DaskExecutor(local_processes=True, memory_limit=30*2**30)
    with raise_on_exception():
        flow_state = flow.run(executor=executor, parameters={"basedir": "/Users/raph/OMIND_SERVER/DATA/DATA_testing/poc_jobs",
                                                         "outputdir": "/Users/raph/OMIND_SERVER/DATA/DATA_testing/poc_jobs_preprocessed",
                                                            "force_clean": False, "force_cvx": True, "force_scrpeaks": True})
    local_execution_duration = time() - t0
    print("Dask executor ran in {duration} seconds".format(duration=local_execution_duration))
    #    Local executor ran in 164.64 seconds

    flow.visualize(flow_state=flow_state)