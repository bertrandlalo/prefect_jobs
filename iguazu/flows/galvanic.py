import pathlib
from prefect.utilities.debug import raise_on_exception
from time import sleep, time
import os

import pandas as pd
from prefect.engine.executors import DaskExecutor, LocalExecutor, SynchronousExecutor
from prefect import task, Flow, Parameter, context
logger = context.get("logger")
from prefect.engine import signals
from prefect import unmapped

from iguazu.functions.galvanic import galvanic_clean, galvanic_scrpeaks, galvanic_cvx


basedir = "/Users/raph/OMIND_SERVER/DATA/DATA_testing/poc_jobs"

def safe_read_hdf5(filename, path):
    """
    Read a HDF5 file given its file name and path, in "read mode". If the Key does not exists, it returns None.
    Parameters
    ----------
    filename: name of the file to read.
    path: path to the data.

    Returns
    -------
    DataFrame or None
    """
    with pd.HDFStore(filename, "r") as store:
        try:
            return pd.read_hdf(store, path)
        except KeyError:
            return None

def path_exists_in_hdf5(filename, path):
    """
    Checks whether a given path exists in a HDF5 file.
    Parameters
    ----------
    filename: name of the file to read.
    path: path to the data.

    Returns
    -------
    boolean. True if the path exists, else False.
    """
    if os.path.isfile(filename):
        with pd.HDFStore(filename, "r") as store:
            keys = store.keys()
        if path in keys:
            return True
    return False

@task()
def list_files(basedir, pattern="**/*.hdf5"):
    """
    List the files located in basedir .
        TODO: Find a way to mimic Quetzal-client behavior?
    Parameters
    ----------
    basedir: local direction to list the files from.
    pattern: string with matching pattern to select the files.

    Returns
    -------
    files: a list of files matching the specified pattern.
    """
    path = pathlib.Path(basedir)
    #regex = re.compile(regex)
   #files = [file for file in path.glob('**/*') if regex.match(file.name)]
    files = [file for file in path.glob(pattern)]
    #files.sort()
    print("Select {N} files to process.".format(N=str(len(files))))
    return files

@task()
def io_filenames(filename, output_dir=None):
    """

    Parameters
    ----------
    filename
    output_dir

    Returns
    -------

    """
    input_filename = filename
    output_dir = output_dir or os.path.dirname(filename)
    if not os.path.isdir(output_dir):
        os.mkdir(output_dir)
    output_filename = os.path.join(output_dir, os.path.basename(input_filename))
    return {"in": input_filename, "out": output_filename}



galvanic_clean_params = Parameter("galvanic_clean_params",
                                  default={"warmup_duration": 30, "column_name": "F",
                                            "corrupted_maxratio": .3,
                                            "glitch_params": {"scaling": "robust",
                                             "nu": 1, "range": [-0.02, +0.02],  "rejection_win": 20},
                                            "interpolation_params": {"method": "cubic"},
                                            "lowpass_params": {"Wn": [35], "order": 5},
                                            "scaling_params":  {"method": "standard"}})
@task
def etl_galvanic_clean(io_filenames,  tranform_params, force=False,
                       input_paths = {"data": "/nexus/signal/nexus_signal_raw", "events": "/unity/events/unity_events"}, output_path = "/gsr/timeseries/preprocessed"):
    """
    This task is a basic ETL where the input and output are HDF5 files and where the transformation is made on a DataFrame.
    It consists in loading the data from an input file, applying some processing (transformations) and
    saving it into a file (same or other).

    Parameters
    ----------
    io_filenames: dictionary with key 'input' and 'output', containing the input and output file names
    tranform_params: dictionary with parameters to map when calling the transformation function
    force: whether or not to force the task if the output path already exists in the output DataFrame
    input_paths: list of paths that are expected to be found in the input DataFrame
    output_path: path where the result is stored in the output DataFrame

    Returns
    -------
    output filename with new path /gsr/timeseries/preprocessed
    """

    input_filename = io_filenames["in"]
    output_filename = io_filenames["out"]

    if not force and path_exists_in_hdf5(output_filename, output_path):
        return str(output_filename)

    data_params = {key: safe_read_hdf5(input_filename, input_paths[key]) for key in input_paths}

    print("Cleaning of gsr from file {stem}.".format(stem=os.path.basename(input_filename)))
    #Define parameter for 'clean_galvanic'

    try:
        data = galvanic_clean(**data_params, **tranform_params)
        meta = {"state": "success", "version": 0.0, "exception": None, "bad_ratio": data.bad.mean() }
    except Exception as e:
        data = pd.DataFrame()
        meta = {"state": "fail", "version": 0.0, "exception": str(e), "bad_ratio": None}

    # save in hdf
    with pd.HDFStore(output_filename, "a") as store:
        data.to_hdf(store, output_path)
        store.get_node(output_path)._v_attrs['meta'] = meta
    if data.empty:
        raise signals.FAIL(message="cleaning failed") #TODO: I'm not sure how to handle failures
    return str(output_filename)


galvanic_cvx_params = Parameter("galvanic_cvx_params", {"warmup_duration":  15,
                                    "column_name": "F_clean_inversed_lowpassed_zscored",
                                    "glitch_params":  {"scaling": False,
                                                     "nu": 0,
                                                     "range": [0, 4],
                                                     "rejection_win": 20},
                                                        "cvxeda_params": None})
@task
def etl_galvanic_cvx(io_filenames,  tranform_params, force=False, input_paths = {"data": "/gsr/timeseries/preprocessed"},  output_path = "/gsr/timeseries/deconvoluted"):
    """
    This task is a basic ETL where the input and output are HDF5 files and where the transformation is made on a DataFrame.
    It consists in loading the data from an input file, applying some processing (transformations) and
    saving it into a file (same or other).

    Parameters
    ----------
    io_filenames: dictionary with key 'input' and 'output', containing the input and output file names
    tranform_params: dictionary with parameters to map when calling the transformation function
    force: whether or not to force the task if the output path already exists in the output DataFrame
    input_paths: list of paths that are expected to be found in the input DataFrame
    output_path: path where the result is stored in the output DataFrame

    Returns
    -------
    output filename with new path /gsr/timeseries/deconvoluted
    """

    input_filename = io_filenames["in"]
    output_filename = io_filenames["out"]

    if not force and path_exists_in_hdf5(output_filename, output_path):
        return str(output_filename)

    data_params = {key: safe_read_hdf5(input_filename, input_paths[key]) for key in input_paths}

    print("Deconvolution from gsr in file {stem}.".format(stem=os.path.basename(input_filename)))

    try:
        data = galvanic_cvx(**data_params, **tranform_params)
        meta = {"state": "success", "version": 0.0, "exception": None, "bad_ratio": data.bad.mean() }
    except Exception as e:
        data = pd.DataFrame()
        meta = {"state": "fail", "version": 0.0, "exception": str(e), "bad_ratio": None}

    # save in hdf
    with pd.HDFStore(output_filename, "a") as store:
        data.to_hdf(store, output_path)
        store.get_node(output_path)._v_attrs['meta'] = meta
    if data.empty:
        raise signals.FAIL(message=str("cvx failed")) #TODO: I'm not sure how to handle failures
    return str(output_filename)


galvanic_scrpeaks_params = Parameter("galvanic_scrpeaks_params", {"warmup_duration": 15, "column_name": "F_clean_inversed_lowpassed_zscored_SCR",
                                                        "peaks_params": {"width": .5,
                                                                        "prominence": .1,
                                                                        "prominence_window": 15},
                                                        "glitch_params":  {"nu": 0,
                                                                         "range": [0, 7]}})

@task
def etl_galvanic_scrpeaks(io_filenames,  tranform_params, force=False,
                          input_paths = {"data": "/gsr/timeseries/deconvoluted"}, output_path = "/gsr/timeseries/scrpeaks"):
    """
    This task is a basic ETL where the input and output are HDF5 files and where the transformation is made on a DataFrame.
    It consists in loading the data from an input file, applying some processing (transformations) and
    saving it into a file (same or other).

    Parameters
    ----------
    io_filenames: dictionary with key 'input' and 'output', containing the input and output file names
    tranform_params: dictionary with parameters to map when calling the transformation function
    force: whether or not to force the task if the output path already exists in the output DataFrame
    input_paths: list of paths that are expected to be found in the input DataFrame
    output_path: path where the result is stored in the output DataFrame

    Returns
    -------
    output filename with new path /gsr/timeseries/scrpeaks
    """


    input_filename = io_filenames["in"]
    output_filename = io_filenames["out"]

    if not force and path_exists_in_hdf5(output_filename, output_path):
        return str(output_filename)

    data_params = {key: safe_read_hdf5(input_filename, input_paths[key]) for key in input_paths}

    print("Extraction of SCR Peaks characteristics from gsr in file {stem}.".format(stem=os.path.basename(input_filename)))

    try:
        data = galvanic_scrpeaks(**data_params, **tranform_params)
        meta = {"state": "success", "version": 0.0, "exception": None, "bad_ratio": data.bad.mean() }
    except Exception as e:
        data = pd.DataFrame()
        meta = {"state": "fail", "version": 0.0, "exception": str(e), "bad_ratio": None}

    # save in hdf
    with pd.HDFStore(output_filename, "a") as store:
        data.to_hdf(store, output_path)
        store.get_node(output_path)._v_attrs['meta'] = meta
    if data.empty:
        raise signals.FAIL(message="scrpeaks failed") #TODO: I'm not sure how to handle failures
    return str(output_filename)


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
    executor = LocalExecutor()
    #executor = DaskExecutor(local_processes=True, memory_limit=30*2**30)
    with raise_on_exception():
        flow_state = flow.run(executor=executor, parameters={"basedir": "/Users/raph/OMIND_SERVER/DATA/DATA_testing/poc_jobs",
                                                         "outputdir": "/Users/raph/OMIND_SERVER/DATA/DATA_testing/poc_jobs_preprocessed",
                                                            "force_clean": False, "force_cvx": True, "force_scrpeaks": True})
    #scraped_state = flow.run(executor=LocalExecutor(), parameters={"basedir":  "/Users/raph/OMIND_SERVER/DATA/DATA_testing/poc_jobs"})
    local_execution_duration = time() - t0
    print("Dask executor ran in {duration} seconds".format(duration=local_execution_duration))
    #    Local executor ran in 164.64 seconds

    flow.visualize(flow_state=flow_state)