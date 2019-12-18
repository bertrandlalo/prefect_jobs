""" Tasks related to standardization of data from the VR protocol """

import logging
from typing import List, Optional

import numpy as np
import pandas as pd
import prefect
from dsu.exceptions import DSUException
from dsu.dsp.resample import uniform_sampling
from dsu.pandas_helpers import estimate_rate

import iguazu
from iguazu.core.exceptions import (
    PostconditionFailed, SoftPreconditionFailed
)
from iguazu.functions.specs import (
    check_event_specification, check_signal_specification, EventSpecificationError
)
from iguazu.functions.unity import extract_standardized_events
from iguazu.helpers.files import FileProxy


logger = logging.getLogger(__name__)


VR_VALID_SEQUENCE_IDS = (
    "space-stress_game-tutorial_0",
    "space-stress_outro_0",
    "physio-sonification_respiration-feedback_0",
    "intro_calibration_0",
    "common_respiration-calibration_data-accumulation_0",
    "session_sequence_0",
    "physio-sonification_sequence_0",
    "space-stress_game_0",
    "space-stress_game_1",
    "physio-sonification_playground_0",
    "physio-sonification_cardiac-feedback_0",
    "cardiac-coherence_coherence-feedback_0",
    "physio-sonification_survey_0",
    "space-stress_sequence_0",
    "cardiac-coherence_score_0",
    "baseline_sequence_0",
    "baseline_sequence_1",
    "baseline_sequence_2",
    "baseline_sequence_3",
    "space-stress_game_enemy-wave_0",
    "space-stress_game_enemy-wave_1",
    "space-stress_game_enemy-wave_2",
    "space-stress_game_enemy-wave_3",
    "space-stress_game_enemy-wave_4",
    "space-stress_game_enemy-wave_5",
    "baseline_eyes-opened_0",
    "baseline_eyes-opened_1",
    "baseline_eyes-opened_2",
    "baseline_eyes-opened_3",
    "space-stress_breath-tutorial_0",
    "intro_disclaimer_0",
    "lobby_sequence_0",
    "lobby_sequence_1",
    "lobby_sequence_2",
    "physio-sonification_coherence-feedback_0",
    "space-stress_survey_0",
    "space-stress_survey_1",
    "intro_omi-logo_0",
    "cardiac-coherence_sequence_0",
    "intro_sequence_0",
    "cardiac-coherence_survey_0",
    "cardiac-coherence_survey_1",
    "space-stress_graph_0",
    "space-stress_graph_1",
    "space-stress_intro_0",
    "baseline_eyes-closed_0",
    "cardiac-coherence_data-accumulation_0",
)


class ExtractStandardEvents(iguazu.Task):
    """Extract and standardize unity events from the VR protocol

    This task may be reusable on other OpenMind protocols, but has not been
    tested outside of the VR protocol data yet.

    Attributes
    ----------
    output_hdf5_key
        HDF5 group name where the standardized events will be saved in the
        output HDF5 file.

    Parameters
    ----------
    events_hdf5_key
        HDF5 group name where the events will be read from the input HDF5 file
    output_hdf5_key
        See :py:attr:`output_hdf5_key` attribute.

    """

    def __init__(self, *,
                 events_hdf5_key: str = '/unity/events/unity_events',
                 output_hdf5_key: str = '/iguazu/events/standard',
                 **kwargs):
        super().__init__(**kwargs)

        self.output_hdf5_key = output_hdf5_key
        self.auto_manage_input_dataframe('events', events_hdf5_key)

    def run(self, events: pd.DataFrame) -> FileProxy:
        """Extract and standardize unity events from the VR protocol

        Most of the logic of this task is expressed in the
        :py:func:`extract_standardized_events` function. This function simply
        wraps this logic to be usable as an Iguazu task.

        Parameters
        ----------
        events
            Dataframe with events in a VR-protocol compatible format.

        Returns
        -------
        A file with the events converted to standard format

        See Also
        --------
        :ref:`standard event specifications <event_specs>`.
        :py:func:`extract_standardized_events.

        """
        if events.empty:
            raise SoftPreconditionFailed('Input events are empty')

        output_file = self.default_outputs()
        dataframe = extract_standardized_events(events)

        self.logger.debug('Obtained %d events/sequences', dataframe.shape[0])
        if not dataframe.empty:
            self.logger.debug('Small extract of events/sequences:\n%s',
                              dataframe.to_string(max_rows=5))

        with pd.HDFStore(output_file.file, 'w') as store:
            dataframe.to_hdf(store, self.output_hdf5_key)

        return output_file

    def preconditions(self, *, events, **inputs):
        """ Check preconditions to extract standard events

        The precondition of this task that the `events` input is a file with
        a dataframe and this dataframe has some particular columns and types.
        However, this is not verified at the moment.
        """
        # TODO: perhaps we could add a verification that will detect if the
        #       input is really from the VR protocol, or at least check that
        #       the input is *compatible*

        return super().preconditions(events=events, **inputs)

    def default_outputs(self, **kwargs):
        """ Standard events default outputs

        The default outputs of this task is a file with an empty dataframe, but
        with the columns and types as required by the specification.

        See Also
        --------
        :py:func:`empty_events`.

        """
        original_kws = prefect.context.run_kwargs
        events = original_kws['events']
        output = events.make_child(suffix='_standard_events')
        return output

    def postconditions(self, results):
        """ Check standard event postconditions

        The postconditions of this task is that the result follows the event
        specification standard.
        """
        super().postconditions(results)

        if not isinstance(results, FileProxy):
            raise PostconditionFailed('Output was not a file')

        # Postcondition: file is empty
        if results.empty:
            return

        key = self.output_hdf5_key
        with pd.HDFStore(results.file, 'r') as store:
            dataframe = pd.read_hdf(store, key)
            check_event_specification(dataframe)

    # def default_metadata(self, exception, **inputs):
    #     metadata = super().default_metadata(exception, **inputs)
    #     events = inputs['events']
    #     metadata['iguazu'].setdefault('parents', [])
    #     metadata['iguazu']['parents'].append(events.id)
    #     return metadata


class FilterVRSequences(iguazu.Task):
    """ Select VR sequences from standard events"""

    def __init__(self, *,
                 selection: Optional[List[str]] = None,
                 input_hdf5_key: str = '/iguazu/events/standard',
                 output_hdf5_key: Optional[str] = '/iguazu/events/standard',
                 **kwargs):
        super().__init__(**kwargs)
        self.selection = tuple(selection or VR_VALID_SEQUENCE_IDS)
        self.output_hdf5_key = output_hdf5_key
        self.input_hdf5_key = input_hdf5_key
        self.auto_manage_input_dataframe('events', input_hdf5_key)

    def run(self, events: pd.DataFrame) -> FileProxy:
        output_file = self.default_outputs()
        idx_selected = events['id'].isin(self.selection)
        idx_sequences = ~events['end'].isnull()
        vr_sequences = events.loc[idx_selected & idx_sequences]

        self.logger.debug('Selected %d sequences out of %d standard events',
                          vr_sequences.shape[0], events.shape[0])
        if not vr_sequences.empty:
            self.logger.debug('Small extract of sequences:\n%s',
                              vr_sequences.to_string(max_rows=5))

        with pd.HDFStore(output_file.file, 'w') as store:
            vr_sequences.to_hdf(store, self.output_hdf5_key)

        return output_file

    def default_outputs(self, **kwargs):
        original_kws = prefect.context.run_kwargs
        events = original_kws['events']
        output = events.make_child(suffix='_standard_vr_sequences')
        # empty = empty_events()
        # key = self.output_hdf5_key
        # with pd.HDFStore(output.file, 'w') as store:
        #     empty.to_hdf(store, key)
        return output

    def preconditions(self, *, events, **inputs):
        super().preconditions(events=events, **inputs)
        try:
            with pd.HDFStore(events.file, 'r') as store:
                events = pd.read_hdf(store, key=self.input_hdf5_key)
            check_event_specification(events)
        except EventSpecificationError as ex:
            logger.info('VR selection will not run: the input does not '
                        'adhere to standard event specification')
            raise SoftPreconditionFailed('Input did not adhere to standard '
                                         'event specification') from ex

    def postconditions(self, results):
        super().postconditions(results)

        if not isinstance(results, FileProxy):
            raise PostconditionFailed('Output was not a file')

        # Postcondition: file is empty
        if results.empty:
            return

        key = self.output_hdf5_key
        with pd.HDFStore(results.file, 'r') as store:
            dataframe = pd.read_hdf(store, key)
            check_event_specification(dataframe)


class ExtractNexusSignal(iguazu.Task):

    def __init__(self, *,
                 signals_hfd5_key: str = '/nexus/signal/nexus_signal_raw',
                 source_column: str,
                 target_column: str,
                 sampling_rate: int = 512,
                 output_hdf5_key: str,
                 **kwargs):
        super().__init__(**kwargs)

        self.output_hdf5_key = output_hdf5_key
        self.output_annotations_hdf5_key = '/'.join([output_hdf5_key, 'annotations'])
        self.source_column = source_column
        self.target_column = target_column
        self.sampling_rate = sampling_rate
        self.auto_manage_input_dataframe('signals', signals_hfd5_key)

    def run(self, signals: pd.DataFrame) -> FileProxy:
        logger.info('Extracting Nexus signal %s -> %s on file %s',
                    self.source_column, self.target_column,
                    prefect.context.run_kwargs['signals'])

        raw = (
            signals[[self.source_column]]
            .rename(columns={self.source_column: self.target_column})
        )

        # Estimate the sampling frequency: weird signals that have a heavy jitter
        # will fail here early and raise a ValueError. See issue #44
        try:
            fs = estimate_rate(raw)
        except DSUException as ex:
            logger.warning('Failed to estimate rate: %s, raising a precondition fail', ex)
            raise SoftPreconditionFailed(str(ex)) from ex

        logger.debug('Uniform resampling from %.3f Hz to %d Hz', fs, self.sampling_rate)
        # Uniform sampling, with linear interpolation.
        # sample-and-hold is not a good strategy, see issue 48:
        # https://github.com/OpenMindInnovation/iguazu/issues/48
        raw_uniform = uniform_sampling(raw, self.sampling_rate,)  # TODO: add linear interpolation
                                       #interpolation_kind='linear')

        # Create the annotations companion dataframe and mark any nan as a
        # "unknown" problem since it must come from the device / driver.
        # idx_sparse = raw_uniform.isna().any(axis='columns')
        #raw_annotations = raw_uniform.loc[idx_sparse].isna().replace({True: 'unknown', False: ''})
        # I have changed my mind: sparse complicates the code, and we are only saving so little space
        raw_annotations = raw_uniform.isna().replace({True: 'unknown', False: ''})

        n_samples = raw_uniform.shape[0]
        n_nans = (raw_annotations != '').sum()
        logger.debug('Finished standardization of Nexus signal %s -> %s. '
                     'Result has %d samples (%.1f seconds, %.1f minutes) '
                     '%d samples are NaN (%.1f %%).',
                     self.source_column, self.target_column,
                     n_samples,
                     n_samples / self.sampling_rate,
                     n_samples / self.sampling_rate / 60,
                     n_nans,
                     100 * n_nans / n_samples)
        if n_samples > 0:
            logger.debug('Extract of result:\n%s',
                         raw_uniform.to_string(max_rows=5))

        return self.save(raw_uniform, raw_annotations)

    # Refactored this method out of run so that it can be reused by a child
    # class such as ExtractGSRSignal
    def save(self, raw: pd.DataFrame, annotations: pd.DataFrame) -> FileProxy:
        output_file = self.default_outputs()
        with pd.HDFStore(str(output_file.file.resolve()), 'w') as store:
            raw.to_hdf(store, self.output_hdf5_key)
            annotations.to_hdf(store, self.output_annotations_hdf5_key)
            node = store.get_node(self.output_hdf5_key)
            node._v_attrs['standard'] = {
                'sampling_rate': self.sampling_rate,
            }

        return output_file

    def default_outputs(self, **kwargs):
        original_kws = prefect.context.run_kwargs
        signals = original_kws['signals']
        names = '_'.join([self.source_column, self.target_column])
        output = signals.make_child(suffix=f'_standard_{names}')
        return output

    def preconditions(self, *, signals, **kwargs):
        super().preconditions(signals=signals, **kwargs)

        # Precondition: input signals is not empty
        if signals.empty:
            raise SoftPreconditionFailed('Input signals are empty')

    def postconditions(self, results):
        super().postconditions(results)

        if not isinstance(results, FileProxy):
            raise PostconditionFailed('Output was not a file')

        # Postcondition: file is empty
        if results.empty:
            return

        # Postcondition: when file is not empty, it follows the signal spec
        key = self.output_hdf5_key
        with pd.HDFStore(str(results.file.resolve()), 'r') as store:
            dataframe = pd.read_hdf(store, key)
            check_signal_specification(dataframe)


class ExtractNexusGSRSignal(ExtractNexusSignal):
    # Add documentation link to
    # https://docs.google.com/presentation/d/1sjV9Jcng-UlZiIye-lrykPBOsTi2701pj1QUXSpoHL4/edit#slide=id.g4db82b9433_1_5

    def __init__(self, *,
                 linear_offset: float = 0,
                 linear_slope: float = 1,
                 **kwargs):
        super().__init__(**kwargs)
        self.b = linear_offset
        self.m = linear_slope

    def run(self, signals: pd.DataFrame) -> FileProxy:
        # Call the regular extraction, then annotate known Nexus GSR problems.
        parent_output_file = super().run(signals=signals)

        logger.info('Running GSR-specific processing of Nexus signals')

        # We need to re-read the dataframe
        with pd.HDFStore(str(parent_output_file.file.resolve()), 'r') as store:
            raw = pd.read_hdf(store, self.output_hdf5_key)
            annotations = pd.read_hdf(store, self.output_annotations_hdf5_key)

        # Quell typing checks because read_hdf returns object or dataframe
        assert isinstance(raw, pd.DataFrame)
        assert isinstance(annotations, pd.DataFrame)

        # Nexus max-saturation:
        # Because Nexus is weird, saturation should be >= 2000 but they set it to 0
        saturation_max = (raw[self.target_column] == 0) | (raw[self.target_column] >= 2000)
        # Nexus min-saturation:
        # We are choosing zero, which has been observed with real resistances
        # to be 10 to 100 Ω, that is, between 1e6 and 1e5 µS, so this is
        # outside the amplifier range (which is documented to be
        # between 0.1 and 1000 µS)
        saturation_min = (raw[self.target_column] < 0)

        # Convert from mV (amplifier values) to kΩ, then invert for µS
        raw = 1000 / (raw * self.m + self.b)  # type: pd.DataFrame

        # Mark saturations with nan and annotate them. Note that we need to
        # do this AFTER converting to µS
        raw.loc[saturation_min | saturation_max, self.target_column] = np.nan
        annotations.loc[saturation_min, self.target_column] = 'saturated low'
        annotations.loc[saturation_max, self.target_column] = 'saturated high'

        n_samples = raw.shape[0]
        n_saturated_min = saturation_min.sum()
        n_saturated_max = saturation_max.sum()
        logger.debug('Finished GSR-specific standardization of Nexus signal. '
                     'Result has %d samples (%.1f seconds, %.1f minutes) '
                     '%d samples are NaN (%.1f %%) due to '
                     '%d samples being low-saturated (%.1f %%) and '
                     '%d samples being high-saturated (%.1f %%)',
                     n_samples,
                     n_samples / self.sampling_rate,
                     n_samples / self.sampling_rate / 60,
                     n_saturated_min + n_saturated_max,
                     100 * (n_saturated_min + n_saturated_max) / n_samples,
                     n_saturated_min,
                     100 * n_saturated_min / n_samples,
                     n_saturated_max,
                     100 * n_saturated_max / n_samples)

        return self.save(raw, annotations)
