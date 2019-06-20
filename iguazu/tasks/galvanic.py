from typing import Dict, Optional
import os

from prefect import task
from prefect.engine import signals
import prefect
import pandas as pd

from iguazu.functions.galvanic import galvanic_cvx, galvanic_scrpeaks, galvanic_clean
from iguazu.functions.common import path_exists_in_hdf5, safe_read_hdf5
from iguazu.helpers.files import FileProxy


@task
def etl_galvanic_clean(io_filenames,  tranform_params, force=False,
                       input_paths = {"data": "/nexus/signal/nexus_signal_raw", "events": "/unity/events/unity_events"},
                       output_path = "/gsr/timeseries/preprocessed"):
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
        raise signals.SKIP(message="cleaning failed") #TODO: I'm not sure how to handle failures
    return str(output_filename)


class CleanSignal(prefect.Task):

    def __init__(self,
                 signal_group: Optional[str] = None,
                 events_group: Optional[str] = None,
                 output_group: Optional[str] = None,
                 signal_column: Optional[str] = None,
                 warmup_duration: int = 30,
                 glitch_kwargs: Optional[Dict] = None,
                 interpolation_kwargs: Optional[Dict] = None,
                 lowpass_kwargs: Optional[Dict] = None,
                 scaling_kwargs: Optional[Dict] = None,
                 corrupted_maxratio: Optional[float] = None,
                 force: bool = False,
                 **kwargs):
        super().__init__(**kwargs)
        self.signal_group = signal_group
        self.events_group = events_group
        self.output_group = output_group
        self.signals_column = signal_column
        self.warmup_duration = warmup_duration
        self.glitch_kwargs = glitch_kwargs or {}
        self.interpolation_kwargs = interpolation_kwargs or {}
        self.lowpass_kwargs = lowpass_kwargs or {}
        self.scaling_kwargs = scaling_kwargs or {}
        self.corrupted_maxratio = corrupted_maxratio or 100
        self.force = force

    def run(self,
            signal: FileProxy,
            events: FileProxy) -> FileProxy:

        output = signal.make_child(suffix='_clean')
        self.logger.info('Galvanic preprocessing for signal=%s, events=%s -> %s',
                         signal, events, output)

        # Notes on parameter management
        #
        # if I wanted to admit the rewrite of a parameter foo,
        # 1. Add foo to run parameter as an optional parameter with default None
        # 2.a Manage None with `foo = foo or self.foo`
        #
        # If I wanted to admit a global context value of parameter foo
        # 2.b `foo = foo or self.foo or context.get('foo', None)`
        #
        # Finally, if a default value is needed
        # 2.c `foo = foo or self.foo or context.get('foo', 'default_value')`
        #
        # In the following lines, we are not following these ideas yet. Maybe later.
        signal_group = self.signal_group or '/nexus/signal/nexus_signal_raw'
        events_group = self.events_group or '/unity/events/unity_events'
        signals_column = self.signals_column or 'F'
        output_group = self.output_group or '/gsr/timeseries/preprocessed'

        # Our current force detection code
        if not self.force and path_exists_in_hdf5(output.file, output_group):
            # TODO: consider a function that uses a FileProxy, in particular a
            #       QuetzalFile. In this case, we could read the metadata
            #       instead of downloading the file!
            self.logger.info('Output already exists, skipping')
            # raise signals.SKIP('Output already exists', result=output) #  Does not work!
            # TODO: consider a way to raise a skip with results. Currently, the
            #       only way I think this is possible is by making a new signal
            #       that derives from PrefectStateSignal and that uses a new
            #       custom state class as well.
            #       Another solution could be to use a custom state handler
            return output

        signal_file = signal.file.resolve()
        events_file = events.file.resolve()

        with pd.option_context('mode.chained_assignment', None), \
             pd.HDFStore(signal_file, 'r') as signal_store, \
             pd.HDFStore(events_file, 'r') as events_store:

            try:
                # TODO discuss: select column before sending it to a column
                df_signals = pd.read_hdf(signal_store, signal_group)
                df_events = pd.read_hdf(events_store, events_group)

                clean = galvanic_clean(df_signals, df_events, signals_column,
                                       self.warmup_duration,
                                       self.glitch_kwargs,
                                       self.interpolation_kwargs,
                                       self.lowpass_kwargs,
                                       self.scaling_kwargs,
                                       self.corrupted_maxratio)
                meta = {
                    'state': 'SUCCESS',
                    'version': '0.0',
                    'bad_ratio': clean.bad.mean(),
                }
            except Exception as ex:
                self.logger.warning('Galvanic clean graceful fail: %s', ex)
                clean = pd.DataFrame()
                meta = {
                    'state': 'FAILURE',
                    'version': '0.0',
                    'exception': str(ex),
                }

        # TODO: re-code the failure handling with respect to a task parameter
        # if fail_mode == 'grace': ==> generate empty dataframe, set metadata, return file (prefect raises success)
        # if fail_mode == 'skip':  ==> generate empty dataframe, set metadata, raise skip
        # if fail_mode == 'fail':  ==> raise exception as it arrives

        # Manage output, save to file
        output_file = output.file
        output_file.parent.mkdir(parents=True, exist_ok=True)
        with pd.HDFStore(output_file, 'w') as output_store:
            clean.to_hdf(output_store, output_group)
            output_store.get_node(output_group)._v_attrs['meta'] = {
                'galvanic': meta,
            }

        # Set meta on FileProxy so that Quetzal knows about this metadata
        output.metadata['galvanic'].update(meta)
        output.upload()

        return output


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
        raise signals.SKIP(message=str("cvx failed")) #TODO: I'm not sure how to handle failures
    return str(output_filename)


class ApplyCVX(prefect.Task):
    def __init__(self,
                 signal_group: Optional[str] = None,
                 output_group: Optional[str] = None,
                 signal_column: Optional[str] = None,
                 warmup_duration: int = 15,
                 glitch_kwargs: Optional[Dict] = None,
                 cvxeda_kwargs: Optional[Dict] = None,
                 force: bool = False,
                 **kwargs):
        super().__init__(**kwargs)
        self.signal_group = signal_group
        self.output_group = output_group
        self.signals_column = signal_column
        self.warmup_duration = warmup_duration
        self.glitch_kwargs = glitch_kwargs or {}
        self.cvxeda_kwargs = cvxeda_kwargs or {}
        self.force = force

    def run(self, signal: FileProxy) -> FileProxy:
        output = signal.make_child(suffix='_cvx')
        self.logger.info('Galvanic CVXEDA for %s -> %s', signal, output)

        signal_group = self.signal_group or '/gsr/timeseries/preprocessed'
        signals_column = self.signals_column or 'F_clean_inversed_lowpassed_zscored'
        output_group = self.output_group or '/gsr/timeseries/deconvoluted'

        # Our current force detection code
        if not self.force and path_exists_in_hdf5(output.file, output_group):
            # TODO: consider a function that uses a FileProxy, in particular a
            #       QuetzalFile. In this case, we could read the metadata
            #       instead of downloading the file!
            self.logger.info('Output already exists, skipping')
            # raise signals.SKIP('Output already exists', result=output) #  Does not work!
            # TODO: consider a way to raise a skip with results. Currently, the
            #       only way I think this is possible is by making a new signal
            #       that derives from PrefectStateSignal and that uses a new
            #       custom state class as well.
            return output

        signal_file = signal.file

        with pd.option_context('mode.chained_assignment', None), \
             pd.HDFStore(signal_file, 'r') as signal_store:

            try:
                # TODO discuss: select column before sending it to a column
                df_signals = pd.read_hdf(signal_store, signal_group)
                cvx = galvanic_cvx(df_signals,
                                   signals_column,
                                   self.warmup_duration,
                                   self.glitch_kwargs,
                                   self.cvxeda_kwargs)
                meta = {
                    'state': 'SUCCESS',
                    'version': '0.0',
                    'bad_ratio': cvx.bad.mean(),
                }
            except Exception as ex:
                self.logger.warning('Galvanic CVX graceful fail: %s', ex)
                cvx = pd.DataFrame()
                meta = {
                    'state': 'FAILURE',
                    'version': '0.0',
                    'exception': str(ex),
                }

        # TODO: re-code the failure handling with respect to a task parameter
        # if fail_mode == 'grace': ==> generate empty dataframe, set metadata, return file (prefect raises success)
        # if fail_mode == 'skip':  ==> generate empty dataframe, set metadata, raise skip
        # if fail_mode == 'fail':  ==> raise exception as it arrives

        # Manage output, save to file
        output_file = output.file
        output_file.parent.mkdir(parents=True, exist_ok=True)
        with pd.HDFStore(output_file, 'w') as output_store:
            cvx.to_hdf(output_store, output_group)
            output_store.get_node(output_group)._v_attrs['meta'] = {
                'galvanic': meta,
            }

        # Set meta on FileProxy so that Quetzal knows about this metadata
        output.metadata['galvanic'].update(meta)
        output.upload()

        return output


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
        raise signals.SKIP(message="scrpeaks failed") #TODO: I'm not sure how to handle failures
    return str(output_filename)


class DetectSCRPeaks(prefect.Task):

    def __init__(self,
                 signal_group: Optional[str] = None,
                 output_group: Optional[str] = None,
                 signal_column: Optional[str] = None,
                 warmup_duration: int = 15,
                 glitch_kwargs: Optional[Dict] = None,
                 peak_detection_kwargs: Optional[Dict] = None,
                 force: bool = False,
                 **kwargs):
        super().__init__(**kwargs)
        self.signal_group = signal_group
        self.output_group = output_group
        self.signals_column = signal_column
        self.warmup_duration = warmup_duration
        self.glitch_kwargs = glitch_kwargs or {}
        self.peak_detection_kwargs = peak_detection_kwargs or {}
        self.force = force

    def run(self, signal: FileProxy) -> FileProxy:
        output = signal.make_child(suffix='_scr')
        self.logger.info('Galvanic SCR peak detection for %s -> %s', signal, output)

        signal_group = self.signal_group or '/gsr/timeseries/deconvoluted'
        signals_column = self.signals_column or 'F_clean_inversed_lowpassed_zscored_SCR'
        output_group = self.output_group or '/gsr/timeseries/scrpeaks'

        # Our current force detection code
        if not self.force and path_exists_in_hdf5(output.file, output_group):
            # TODO: consider a function that uses a FileProxy, in particular a
            #       QuetzalFile. In this case, we could read the metadata
            #       instead of downloading the file!
            self.logger.info('Output already exists, skipping')
            # raise signals.SKIP('Output already exists', result=output) #  Does not work!
            # TODO: consider a way to raise a skip with results. Currently, the
            #       only way I think this is possible is by making a new signal
            #       that derives from PrefectStateSignal and that uses a new
            #       custom state class as well.
            return output

        signal_file = signal.file

        with pd.HDFStore(signal_file, 'r') as signal_store:

            try:
                # TODO discuss: select column before sending it to a column
                df_signals = pd.read_hdf(signal_store, signal_group)
                scr = galvanic_scrpeaks(df_signals,
                                        signals_column,
                                        self.warmup_duration,
                                        self.peak_detection_kwargs,
                                        self.glitch_kwargs)
                meta = {
                    'state': 'SUCCESS',
                    'version': '0.0',
                    'bad_ratio': scr.bad.mean(),
                }
            except Exception as ex:
                self.logger.warning('Galvanic SCR peak detection graceful fail: %s', ex)
                scr = pd.DataFrame()
                meta = {
                    'state': 'FAILURE',
                    'version': '0.0',
                    'exception': str(ex),
                }

        # TODO: re-code the failure handling with respect to a task parameter
        # if fail_mode == 'grace': ==> generate empty dataframe, set metadata, return file (prefect raises success)
        # if fail_mode == 'skip':  ==> generate empty dataframe, set metadata, raise skip
        # if fail_mode == 'fail':  ==> raise exception as it arrives

        # Manage output, save to file
        output_file = output.file
        output_file.parent.mkdir(parents=True, exist_ok=True)
        with pd.HDFStore(output_file, 'w') as output_store:
            scr.to_hdf(output_store, output_group)
            output_store.get_node(output_group)._v_attrs['meta'] = {
                'galvanic': meta,
            }

        # Set meta on FileProxy so that Quetzal knows about this metadata
        output.metadata['galvanic'].update(meta)
        output.upload()

        return output
