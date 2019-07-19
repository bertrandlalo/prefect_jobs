from typing import Dict, Optional

import pandas as pd
import prefect

from iguazu.functions.galvanic import galvanic_cvx, galvanic_scrpeaks, galvanic_clean, galvanic_baseline_correction
# from iguazu.helpers.decorators import SubprocessException
from iguazu.helpers.files import FileProxy
from iguazu.helpers.states import GRACEFULFAIL, SKIPRESULT
from iguazu.helpers.states import SKIPRESULT
from iguazu.helpers.tasks import get_base_meta, task_upload_result, task_fail, IguazuError


class CleanSignal(prefect.Task):
    """ Pre-process galvanic signals.

    This task performs the following steps:

        - troncate the signal between the begining and end of the session
        - append a 'bad' column to estimate quality as a boolean
        - detect and remove glitches and 0.0 values due to OA saturation
        - inverse the voltage signal to estimate skin conductance
        - interpolate missing samples
        - low-pass filter the signal
        - scale the signal on the whole session between 0 and 1
    """

    def __init__(self,
                 signal_group: Optional[str] = None,
                 events_group: Optional[str] = None,
                 output_group: Optional[str] = None,
                 signal_column: Optional[str] = None,
                 warmup_duration: int = 30,
                 quality_kwargs: Optional[Dict] = None,
                 interpolation_kwargs: Optional[Dict] = None,
                 filter_kwargs: Optional[Dict] = None,
                 scaling_kwargs: Optional[Dict] = None,
                 corrupted_maxratio: Optional[float] = None,
                 sampling_rate: Optional[float] = None,
                 force: bool = False,
                 **kwargs):
        """
        Parameters
        ----------
        signal_group: group in the input hdf5 where the input signals are stored.
        Default to '/nexus/signal/nexus_signal_raw'.
        events_group: group in the input  hdf5 where the input events are stored.
        Default to '/unity/events/unity_events'.
        output_group: group in the output  hdf5 to store the output data. Default to
        '/gsr/timeseries/preprocessed'
        signal_column: column in the input signal to select. Default to 'F'.
        warmup_duration: see the documentation of :py:func:`iguazu.functions.galvanic.galvanic_clean`.
        glitch_kwargs: see the documentation of :py:func:`galvanic_clean`.
        interpolation_kwargs: see the documentation of :py:func:`galvanic_clean`.
        lowpass_kwargs: see the documentation of :py:func:`galvanic_clean`.
        scaling_kwargs: see the documentation of :py:func:`galvanic_clean`.
        corrupted_maxratio: see the documentation of :py:ref:`galvanic_clean`.
        sampling_rate: see the documentation of :py:ref:`galvanic_clean`.
        force: if True, the task will run even if `output_group` from the output
         HDF5 file already contains some data.
        kwargs: additive keywords arguments to call the `run` method.
        """
        super().__init__(**kwargs)
        self.signal_group = signal_group
        self.events_group = events_group
        self.output_group = output_group
        self.signals_column = signal_column
        self.warmup_duration = warmup_duration
        self.quality_kwargs = quality_kwargs or {}
        self.interpolation_kwargs = interpolation_kwargs or {}
        self.filter_kwargs = filter_kwargs or {}
        self.scaling_kwargs = scaling_kwargs or {}
        self.sampling_rate = sampling_rate or 256
        self.corrupted_maxratio = corrupted_maxratio or 100
        self.force = force

    def run(self,
            signal: FileProxy,
            events: FileProxy) -> FileProxy:
        """
        This task is a basic ETL where the input and output are HDF5 file proxy
        and where the transformation is made on a DataFrame.
        It consists in loading the signals and events from the input files proxy,
        applying some processing (transformations) and
        saving the result into an output file proxy.

        The transformation that is performed is a cleaning of the galvanic signal.
        See the documentation of :func:`galvanic.galvanic_clean`.

        Parameters
        ----------
        signal: file proxy with input signals.
        events:  file proxy with input events.

        Returns
        -------
        output: file proxy with transformed signals.

        """

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
        if not self.force and output.metadata.get('iguazu', {}).get('state') is not None:
            self.logger.info('Output already exists, skipping')
            raise SKIPRESULT('Output already exists', result=output)

        # At that point, we are sure that the previous tasks succeeded and that
        # the output has not yet been generated ()

        signal_file = signal.file.resolve()
        events_file = events.file.resolve()

        try:
            # check if previous task succeeded
            if signal.metadata.get('iguazu', {}).get('state') == 'FAILURE':
                # Fail
                self.logger.info('Previous task failed, propagating failure')
                raise IguazuError('Previous task failed')

            with pd.option_context('mode.chained_assignment', None), \
                 pd.HDFStore(signal_file, 'r') as signal_store, \
                 pd.HDFStore(events_file, 'r') as events_store:

                # TODO discuss: select column before sending it to a column
                df_signals = pd.read_hdf(signal_store, signal_group)
                df_events = pd.read_hdf(events_store, events_group)

                df_output = galvanic_clean(df_signals, df_events, signals_column,
                                           self.warmup_duration,
                                           self.quality_kwargs,
                                           self.interpolation_kwargs,
                                           self.filter_kwargs,
                                           self.scaling_kwargs,
                                           self.corrupted_maxratio,
                                           self.sampling_rate)
                state = 'SUCCESS'
                meta = get_base_meta(self, state=state, bad_ratio=df_output.bad.mean())
                # Manage output, save to file
                task_upload_result(self, df_output, meta, state, output, output_group)
                self.logger.info('Clean galvanic signal finished successfully, '
                                 'final dataframe has shape %s', df_output.shape)
                return output
        except Exception as ex:
            # Manage output, save to file
            task_fail(self, ex, output, output_group)


class ApplyCVX(prefect.Task):
    def __init__(self,
                 signal_group: Optional[str] = None,
                 output_group: Optional[str] = None,
                 signal_column: Optional[str] = None,
                 warmup_duration: int = 15,
                 threshold_scr: float = 4.,
                 cvxeda_kwargs: Optional[Dict] = None,
                 force: bool = False,
                 **kwargs):
        super().__init__(**kwargs)
        self.signal_group = signal_group
        self.output_group = output_group
        self.signals_column = signal_column
        self.warmup_duration = warmup_duration
        self.threshold_scr = threshold_scr
        self.cvxeda_kwargs = cvxeda_kwargs or {}
        self.force = force

    def run(self, signal: FileProxy) -> FileProxy:
        """
        This task is a basic ETL where the input and output are HDF5 file proxy
        and where the transformation is made on a DataFrame.
        It consists in loading the signals and events from the input files proxy,
        applying some processing (transformations) and
        saving the result into an output file proxy.

        The transformation that is performed is a deconvolution of the galvanic signal.
        See the documentation of :func:`galvanic.galvanic_cvx`.

        Parameters
        ----------
        signal: file proxy with input signals.

        Returns
        -------
        output: file proxy with transformed signals.

        """

        output = signal.make_child(suffix='_cvx')
        self.logger.info('Galvanic CVXEDA for %s -> %s', signal, output)

        signal_group = self.signal_group or '/gsr/timeseries/preprocessed'
        signals_column = self.signals_column or 'F_clean_inversed_lowpassed_zscored'
        output_group = self.output_group or '/gsr/timeseries/deconvoluted'

        # Our current force detection code
        if not self.force and output.metadata.get('iguazu', {}).get('state') is not None:
            self.logger.info('Output already exists, skipping')
            raise SKIPRESULT('Output already exists', result=output)

        # At that point, we are sure that the previous tasks succeeded and that
        # the output has not yet been generated ()

        signal_file = signal.file

        try:
            # check if previous task succeeded
            if signal.metadata['iguazu']['state'] != 'SUCCESS':
                # Fail
                self.logger.info('Previous task failed, propagating failure')
                raise IguazuError('Previous task failed')

            with pd.option_context('mode.chained_assignment', None), \
                 pd.HDFStore(signal_file, 'r') as signal_store:

                # TODO discuss: select column before sending it to a column
                df_signals = pd.read_hdf(signal_store, signal_group)
                assert isinstance(df_signals, pd.DataFrame)
                df_output = galvanic_cvx(df_signals,
                                         signals_column,
                                         self.warmup_duration,
                                         self.threshold_scr,
                                         self.cvxeda_kwargs)
                state = 'SUCCESS'
                meta = get_base_meta(self, state=state, bad_ratio=df_output.bad.mean())
                # Manage output, save to file
                task_upload_result(self, df_output, meta, state, output, output_group)
                return output
        except Exception as ex:
            # Manage output, save to file
            task_fail(self, ex, output, output_group)


class DetectSCRPeaks(prefect.Task):

    def __init__(self,
                 signal_group: Optional[str] = None,
                 output_group: Optional[str] = None,
                 signal_column: Optional[str] = None,
                 warmup_duration: float = 15,
                 peaks_kwargs: Optional[Dict] = None,
                 max_increase_duration: float = 7,
                 force: bool = False,
                 **kwargs):
        super().__init__(**kwargs)
        self.signal_group = signal_group
        self.output_group = output_group
        self.signals_column = signal_column
        self.warmup_duration = warmup_duration
        self.max_increase_duration = max_increase_duration
        self.peaks_kwargs = peaks_kwargs or {}
        self.force = force

    def run(self, signal: FileProxy) -> FileProxy:
        """
        This task is a basic ETL where the input and output are HDF5 file proxy
        and where the transformation is made on a DataFrame.
        It consists in loading the signals and events from the input files proxy,
        applying some processing (transformations) and
        saving the result into an output file proxy.

        The transformation that is performed is a detection of SCR peaks and the
        estimation of their characteristics.
        See the documentation of :func:`galvanic.galvanic_scrpeaks`.

        Parameters
        ----------
        signal: file proxy with input signals.
        events:  file proxy with input events.

        Returns
        -------
        output: file proxy with transformed signals.

        """

        output = signal.make_child(suffix='_scr')
        self.logger.info('Galvanic SCR peak detection for %s -> %s', signal, output)

        signal_group = self.signal_group or '/gsr/timeseries/deconvoluted'
        signals_column = self.signals_column or 'F_clean_inversed_lowpassed_zscored_SCR'
        output_group = self.output_group or '/gsr/timeseries/scrpeaks'

        # Our current force detection code
        if not self.force and output.metadata.get('iguazu', {}).get('state') is not None:
            self.logger.info('Output already exists, skipping')
            raise SKIPRESULT('Output already exists', result=output)

        # At that point, we are sure that the previous tasks succeeded and that
        # the output has not yet been generated ()

        signal_file = signal.file

        try:
            # check if previous task succeeded
            if signal.metadata['iguazu']['state'] != 'SUCCESS':
                # Fail
                self.logger.info('Previous task failed, propagating failure')
                raise IguazuError('Previous task failed')

            with pd.option_context('mode.chained_assignment', None), \
                 pd.HDFStore(signal_file, 'r') as signal_store:

                # TODO discuss: select column before sending it to a column
                df_signals = pd.read_hdf(signal_store, signal_group)
                assert isinstance(df_signals, pd.DataFrame)
                if df_signals.empty:
                    raise Exception(
                        "Received empty dataframe. ")  # Todo: Handle FAIL in previous tasks to avoid having to check the emptyness here.
                df_output = galvanic_scrpeaks(df_signals,
                                              signals_column,
                                              self.warmup_duration,
                                              self.peaks_kwargs,
                                              self.max_increase_duration)
                state = 'SUCCESS'
                meta = get_base_meta(self, state=state, bad_ratio=df_output.bad.mean())
                # Manage output, save to file
                task_upload_result(self, df_output, meta, state, output, output_group)
                return output
        except Exception as ex:
            # Manage output, save to file
            task_fail(self, ex, output, output_group)


class RemoveBaseline(prefect.Task):
    """ Remove pseudo-baseline for each feature.
    """

    def __init__(self,
                 features_group: str,
                 output_group: str,
                 sequences: Optional[list] = None,
                 columns: Optional[list] = None,
                 force: bool = False,
                 **kwargs):
        """

        Parameters
        ----------
        signals_group
        report_group
        output_group
        feature_definitions
        sequences
        columns
        force
        kwargs
        """
        super().__init__(**kwargs)
        self.features_group = features_group
        self.output_group = output_group
        self.sequences = sequences or ['lobby_sequence_0',
                                       'lobby_sequence_1',
                                       'physio-sonification_survey_0',
                                       'cardiac-coherence_survey_0',
                                       'cardiac-coherence_survey_1',
                                       'cardiac-coherence_score_0']
        self.columns = columns
        self.force = force

    def run(self,
            features: FileProxy) -> FileProxy:

        output = features.make_child(suffix='_corrected')
        self.logger.info('Correcting baseline for features %s -> %s',
                         features, output)

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
        features_group = self.features_group  # No default value is given here
        output_group = self.output_group  # No default value is given here

        # Our current force detection code
        if not self.force and output.metadata.get('iguazu', {}).get('state') is not None:
            self.logger.info('Output already exists, skipping')
            raise SKIPRESULT('Output already exists', result=output)

        features_file = features.file.resolve()

        with pd.option_context('mode.chained_assignment', None), \
             pd.HDFStore(features_file, 'r') as features_store:
            try:
                # check if previous task succeeded
                if features.metadata['iguazu']['state'] != 'SUCCESS':
                    # Fail
                    self.logger.info('Previous task failed, propagating failure')
                    raise IguazuError('Previous task failed')

                # TODO discuss: select column before sending it to a column
                df_features = pd.read_hdf(features_store, features_group)
                assert isinstance(df_features, pd.DataFrame)
                if df_features.empty:
                    # TODO: Handle FAIL in previous tasks to avoid having to check the emptiness here.
                    raise Exception("Received empty dataframe. ")
                df_output, valid_sequences_ratio = galvanic_baseline_correction(df_features,
                                                                                sequences=self.sequences,
                                                                                columns=self.columns)
                state = 'SUCCESS'
                meta = get_base_meta(self, state=state, valid_sequences_ratio=valid_sequences_ratio)
                # Manage output, save to file
                task_upload_result(self, df_output, meta, state, output, output_group)
                return output

            except Exception as ex:
                # Manage output, save to file
                task_fail(self, ex, output, output_group)
