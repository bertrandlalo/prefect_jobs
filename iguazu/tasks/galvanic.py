import re
from typing import Dict, Optional

import pandas as pd
import prefect

import iguazu
from iguazu.core.exceptions import SoftPreconditionFailed
from iguazu.core.files import FileAdapter
from iguazu.functions.galvanic import (
    downsample, galvanic_cvx, galvanic_scrpeaks, galvanic_clean, gsr_features
)
from iguazu.functions.specs import infer_standard_groups, store_output
from iguazu.functions.unity import VALID_SEQUENCE_KEYS


class CleanGSRSignal(iguazu.Task):
    """ Pre-process galvanic signals.

    This task performs the following steps:

        - truncate the signal between the beginning and end of the session
        - append a 'bad' column to estimate quality as a boolean
        - detect and remove glitches and 0.0 values due to OA saturation
        - inverse the voltage signal to estimate skin conductance
        - interpolate missing samples
        - low-pass filter the signal
        - scale the signal on the whole session between 0 and 1
    """

    def __init__(self, *,
                 signals_hdf5_key: Optional[str] = '/iguazu/signal/gsr/standard',
                 events_hdf5_key: Optional[str] = '/iguazu/events/standard',
                 output_hdf5_key: Optional[str] = 'iguazu/signal/gsr/clean',
                 warmup_duration: float = 30.,
                 interpolation_kwargs: Optional[Dict] = None,
                 filter_kwargs: Optional[Dict] = None,
                 scaling_kwargs: Optional[Dict] = None,
                 corrupted_maxratio: float = 0.6,
                 sampling_rate: float = 512,
                 **kwargs):
        """
        Parameters
        ----------
        signals_hdf5_key: group in the input hdf5 where the input signals are stored.
        Default to '/nexus/signal/nexus_signal_raw'.
        events_hdf5_key: group in the input  hdf5 where the input events are stored.
        Default to '/unity/events/unity_events'.
        output_hdf5_key: group in the output  hdf5 to store the output data. Default to
        'iguazu/signal/ppg/clean'
        warmup_duration: see the documentation of :py:func:`~iguazu.functions.galvanic.galvanic_clean`.
        interpolation_kwargs: see the documentation of :py:func:`~iguazu.functions.galvanic.galvanic_clean`.
        scaling_kwargs: see the documentation of :py:func:`~iguazu.functions.galvanic.galvanic_clean`.
        corrupted_maxratio: see the documentation of :py:func:`~iguazu.functions.galvanic.galvanic_clean`.
        sampling_rate: see the documentation of :py:func:`~iguazu.functions.galvanic.galvanic_clean`.
        kwargs: additive keywords arguments to call the `run` method.
        """
        super().__init__(**kwargs)

        self.output_hdf5_key = output_hdf5_key

        self.column = 'GSR'

        self.sampling_rate = sampling_rate
        self.warmup_duration = warmup_duration
        self.corrupted_maxratio = corrupted_maxratio
        self.interpolation_kwargs = interpolation_kwargs or dict(method='pchip')
        self.filter_kwargs = filter_kwargs or dict(
            order=100,
            frequencies=30,
            filter_type='lowpass',
        )
        self.scaling_kwargs = scaling_kwargs or dict(
            method='standard',
        )

        self.auto_manage_input_dataframe('signals', signals_hdf5_key)
        self.auto_manage_input_dataframe('annotations', signals_hdf5_key + '/annotations')
        self.auto_manage_input_dataframe('events', events_hdf5_key)

    def run(self, *,
            signals: pd.DataFrame,
            annotations: pd.DataFrame,
            events: pd.DataFrame) -> FileAdapter:
        if signals.empty:
            raise SoftPreconditionFailed('Input signals are empty')
        if events.empty:
            raise SoftPreconditionFailed('Input events are empty')

        output = self.default_outputs()

        self.logger.info('Galvanic preprocessing for signal=%s, events=%s -> %s',
                         signals, events, output)
        clean, clean_annotations = galvanic_clean(signals=signals, events=events, annotations=annotations,
                                                  column=self.column,
                                                  warmup_duration=self.warmup_duration,
                                                  corrupted_maxratio=self.corrupted_maxratio,
                                                  interpolation_kwargs=self.interpolation_kwargs,
                                                  filter_kwargs=self.filter_kwargs,
                                                  scaling_kwargs=self.scaling_kwargs)
        # todo: keep only last row?
        store_output(output.file, self.output_hdf5_key, dataframe=clean, annotations=clean_annotations)
        return output

    def default_outputs(self, **kwargs):
        original_kws = prefect.context.run_kwargs
        signals = original_kws['signals']
        output = self.create_file(
            parent=signals,
            suffix='_gsr_clean'
        )
        return output


class Downsample(iguazu.Task):

    def __init__(self, *,
                 signals_hdf5_key: Optional[str] = '/iguazu/signal/gsr/clean',
                 output_hdf5_key: Optional[str] = '/iguazu/signal/gsr/downsampled',
                 sampling_rate: float = 256,
                 **kwargs):
        super().__init__(**kwargs)

        self.output_hdf5_key = output_hdf5_key
        self.sampling_rate = sampling_rate

        self.auto_manage_input_dataframe('signals', signals_hdf5_key)
        self.auto_manage_input_dataframe('annotations', signals_hdf5_key + '/annotations')

    def run(self, *,
            signals: pd.DataFrame,
            annotations: pd.DataFrame) -> FileAdapter:
        if signals.empty:
            raise SoftPreconditionFailed('Input signals are empty')

        downsampled = downsample(signals, self.sampling_rate)
        downsampled_annotations = annotations.loc[downsampled.index, :]

        output = self.default_outputs()

        store_output(output.file, self.output_hdf5_key, dataframe=downsampled, annotations=downsampled_annotations)
        return output

    def default_outputs(self, **kwargs):
        original_kws = prefect.context.run_kwargs
        signals = original_kws['signals']
        output = self.create_file(
            parent=signals,
            suffix='_gsr_downsampled'
        )
        return output


class ApplyCVX(iguazu.Task):
    def __init__(self, *,
                 signals_hdf5_key: Optional[str] = '/iguazu/signal/gsr/downsampled',
                 output_hdf5_key: Optional[str] = '/iguazu/signal/gsr/deconvoluted',
                 column: str = 'GSR_filtered_clean_zscored',
                 warmup_duration: float = 15.,
                 threshold_scr: float = 4.,
                 epoch_size: int = 300,
                 epoch_overlap: int = 60,
                 cvxeda_kwargs: Optional[Dict] = None,
                 **kwargs):
        super().__init__(**kwargs)

        self.output_hdf5_key = output_hdf5_key
        self.column = column
        self.warmup_duration = warmup_duration
        self.threshold_scr = threshold_scr
        self.epoch_size = epoch_size
        self.epoch_overlap = epoch_overlap
        self.cvxeda_kwargs = cvxeda_kwargs or {}

        self.auto_manage_input_dataframe('signals', signals_hdf5_key)
        self.auto_manage_input_dataframe('annotations', signals_hdf5_key + '/annotations')

    def run(self, *,
            signals: pd.DataFrame,
            annotations: pd.DataFrame) -> FileAdapter:
        if signals.empty:
            raise SoftPreconditionFailed('Input signals are empty')

        output = self.default_outputs()

        cvx, cvx_annotations = galvanic_cvx(signals=signals,
                                            annotations=annotations,
                                            column=self.column,
                                            warmup_duration=self.warmup_duration,
                                            threshold_scr=self.threshold_scr,
                                            epoch_size=self.epoch_size,
                                            epoch_overlap=self.epoch_overlap,
                                            )

        store_output(output.file, self.output_hdf5_key, dataframe=cvx, annotations=cvx_annotations)
        return output

    def default_outputs(self, **kwargs):
        original_kws = prefect.context.run_kwargs
        signals = original_kws['signals']
        output = self.create_file(
            parent=signals,
            suffix='_cvx'
        )
        return output


class DetectSCRPeaks(iguazu.Task):
    def __init__(self,
                 *,
                 signals_hdf5_key: Optional[str] = '/iguazu/signal/gsr/deconvoluted',
                 output_hdf5_key: Optional[str] = '/iguazu/signal/gsr/scrpeaks',
                 column: str = 'GSR_SCR',
                 max_increase_duration: float = 7.,
                 peaks_kwargs: Optional[dict] = None,
                 **kwargs):
        super().__init__(**kwargs)

        self.output_hdf5_key = output_hdf5_key
        self.column = column
        self.peaks_kwargs = peaks_kwargs or dict(width=0.5,
                                                 prominence=.1,
                                                 prominence_window=15,
                                                 rel_height=.5)
        self.max_increase_duration = max_increase_duration
        self.auto_manage_input_dataframe('signals', signals_hdf5_key)
        self.auto_manage_input_dataframe('annotations', signals_hdf5_key + '/annotations')

    def run(self, *,
            signals: pd.DataFrame,
            annotations: pd.DataFrame) -> FileAdapter:
        if signals.empty:
            raise SoftPreconditionFailed('Input signals are empty')
        output = self.default_outputs()
        peaks, peaks_annotations = galvanic_scrpeaks(signals,
                                                     annotations,
                                                     column=self.column,
                                                     peaks_kwargs=self.peaks_kwargs,
                                                     max_increase_duration=self.max_increase_duration)
        store_output(output.file, self.output_hdf5_key, dataframe=peaks, annotations=peaks_annotations)
        return output

    def default_outputs(self, **kwargs):
        original_kws = prefect.context.run_kwargs
        signals = original_kws['signals']
        output = self.create_file(
            parent=signals,
            suffix='_scrpeaks'
        )
        return output


class ExtractGSRFeatures(iguazu.Task):

    def __init__(self, *,
                 cvx_hdf5_key: str = '/iguazu/signal/gsr/cvx',
                 scrpeaks_hdf5_key: str = '/iguazu/signal/gsr/scrpeaks',
                 events_hdf5_key: str = '/iguazu/events/standard',
                 output_hdf5_key: str = '/iguazu/features/gsr',
                 **kwargs):
        super().__init__(**kwargs)

        self.output_hdf5_key = output_hdf5_key
        self.auto_manage_input_dataframe('cvx', cvx_hdf5_key)
        self.auto_manage_input_dataframe('scrpeaks', scrpeaks_hdf5_key)
        self.auto_manage_input_dataframe('events', events_hdf5_key)

    def run(self, *,
            cvx: pd.DataFrame,
            scrpeaks: pd.DataFrame,
            events: Optional[pd.DataFrame] = None,
            parent: FileAdapter) -> FileAdapter:  # TODO: events should be named sequences?

        if cvx.empty:
            raise SoftPreconditionFailed('Input cvx signals are empty')
        if scrpeaks.empty:
            raise SoftPreconditionFailed('Input scrpeaks signals are empty')
        if events.empty:
            raise SoftPreconditionFailed('Input events are empty')

        output = self.default_outputs()
        blacklist = re.compile('.*(intro|outro|lobby).*')  # regexp to remove lobbies that are too short for GSR
        known_sequences = [sequence for sequence in VALID_SEQUENCE_KEYS if not blacklist.match(sequence)]
        # intro is warm up
        features = gsr_features(cvx, scrpeaks, events, known_sequences=known_sequences)
        if not features.empty:
            features.loc[:, 'file_id'] = parent.id

        store_output(output.file, self.output_hdf5_key, dataframe=features, annotations=None)
        output.metadata['standard'] = infer_standard_groups(output.file_str)
        return output

    def default_outputs(self, **kwargs):
        original_kws = prefect.context.run_kwargs
        parent = original_kws['parent']
        output = self.create_file(
            parent=parent,
            suffix='_gsr_features',
            temporary=False,
        )
        return output
