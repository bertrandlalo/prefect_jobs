import os

from prefect import task
from prefect.engine import signals
import pandas as pd

from iguazu.functions.galvanic import galvanic_cvx, galvanic_scrpeaks, galvanic_clean
from iguazu.functions.common import path_exists_in_hdf5, safe_read_hdf5

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