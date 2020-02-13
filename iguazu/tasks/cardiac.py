from typing import Mapping, Optional, Tuple
import logging

import pandas as pd
import prefect
from dsu.dsp.filters import filtfilt_signal, scale_signal
from dsu.pandas_helpers import estimate_rate

from iguazu.core.exceptions import PreconditionFailed, SoftPreconditionFailed
from iguazu.core.tasks import Task
from iguazu.helpers.files import FileProxy
from iguazu.functions.cardiac import (
    hrv_features, peak_to_nn, ppg_clean, ppg_peak_detection, nn_interpolation,
    extract_all_peaks, ssf, peak_detect
)
from iguazu.functions.ppg_report import render_ppg_report

# logger = logging.getLogger(__name__)


class CleanPPGSignal(Task):

    def __init__(self, *,
                 #signals_hdf5_key: str = '/nexus/signal/nexus_signal_raw',
                 signals_hdf5_key: str = '/iguazu/signal/ppg/standard',
                 # events_hdf5_key: str = '/unity/events/unity_events',
                 output_hdf5_key: str = '/iguazu/signal/ppg/clean',
                 # warmup_duration: int = 30,
                 # sampling_rate: int = 512,
                 # filter_kwargs: Optional[Mapping] = None,
                 **kwargs):
        super().__init__(**kwargs)

        self.output_hdf5_key = output_hdf5_key
        # self.warmup_duration = warmup_duration
        # self.filter_kwargs = filter_kwargs or {}
        # self.column = 'G'
        # self.sampling_rate = sampling_rate

        self.auto_manage_input_dataframe('signals', signals_hdf5_key)
        # self.auto_manage_input_dataframe('events', events_hdf5_key)

    def run(self, *,
            signals: pd.DataFrame,
            # events: pd.DataFrame
            ) -> FileProxy:

        if signals.empty:
            raise SoftPreconditionFailed('Input signals are empty')
        if 'PPG' not in signals.columns:
            raise SoftPreconditionFailed('Input signals do not have a PPG column')

        output_file = self.default_outputs()
        fs = int(estimate_rate(signals))
        bands = (0.5, 11)
        self.logger.info('Band-pass filtering signal between %.2f -- %.2f Hz '
                         'with a FIR filter of order %d', *bands, fs)

        filtered = filtfilt_signal(
            signals,
            order=fs,
            frequencies=bands,
            filter_type='bandpass',
            filter_design='fir',
        )
        scaled = scale_signal(filtered, method='robust')
        # scaled = filtered
        # scaled['SSF_PPG'] = ssf(scaled['PPG'])

        self.logger.info('Cleaned PPG signal, input shape %s, output shape %s',
                         signals.shape, scaled.shape)

        with pd.HDFStore(output_file.file, 'w') as store:
            scaled.to_hdf(store, self.output_hdf5_key)

        return output_file

    def default_outputs(self, **kwargs):
        original_kws = prefect.context.run_kwargs
        signals = original_kws['signals']
        output = signals.make_child(suffix='_ppg_clean')
        return output


class SSFPeakDetect(Task):

    def __init__(self,
                 signals_hdf5_key: str = '/iguazu/signal/ppg/clean',
                 ssf_output_hdf5_key: str = '/iguazu/signal/ppg/ssf',
                 nn_output_hdf5_key: str = '/iguazu/signal/ppg/NN',
                 nni_output_hdf5_key: str = '/iguazu/signal/ppg/NNi',
                 **kwargs):
        super().__init__(**kwargs)
        self.column = 'PPG'
        self.window_fraction = 0.125  # 0.125 of 512Hz is 64 samples, like the original paper

        self.ssf_output_hdf5_key = ssf_output_hdf5_key
        self.ssf_nn_output_hdf5_key = nn_output_hdf5_key
        self.ssf_nni_output_hdf5_key = nni_output_hdf5_key

        self.auto_manage_input_dataframe('signals', signals_hdf5_key)

    def run(self, *,  signals: pd.DataFrame) -> FileProxy:
        if signals.empty:
            raise SoftPreconditionFailed('Input signals are empty')
        if self.column not in signals.columns:
            raise SoftPreconditionFailed('Input signals do not have a PPG column')

        output_file = self.default_outputs()

        # Step 1: calculate SSF
        fs = estimate_rate(signals)
        window_samples = int(self.window_fraction * fs)
        ppg = signals[self.column]
        ppg_ssf = ssf(ppg, win=window_samples)
        df_ssf = pd.DataFrame({'PPG_SSF': ppg_ssf}, index=signals.index)
        self.logger.info('Calculated SSF signal, input shape %s, output shape %s',
                         signals.shape, ppg_ssf.shape)

        # Step 2: detect peak with adaptive threshold
        peaks, thresh = peak_detect(df_ssf.PPG_SSF, threshold_percentage=0.50)

        # Step 3: convert to PP intervals and post-process them
        df_interval = peak_to_nn(peaks).rename(columns={'interval': 'NN'})

        # Step 4: interpolate NN
        df_interpolated = nn_interpolation(df_interval, fs=fs, column='NN')

        with pd.HDFStore(output_file.file, 'w') as store:
            df_ssf.to_hdf(store, self.ssf_output_hdf5_key)
            df_interval.to_hdf(store, self.ssf_nn_output_hdf5_key)
            df_interpolated.to_hdf(store, self.ssf_nni_output_hdf5_key)

        return output_file

    def default_outputs(self, **kwargs):
        original_kws = prefect.context.run_kwargs
        signals = original_kws['signals']
        output = signals.make_child(suffix='_ssf')
        return output


class PPGDetectRR(Task):
    def __init__(self, *,
                 #fs: int = 512,
                 signals_hdf5_key: str = '/iguazu/signal/ppg/clean',
                 output_hdf5_key: str = '/iguazu/signal/ppg',  # a /RR or /RRi will be added
                 **kwargs):
        super().__init__(**kwargs)

        #self.fs = fs
        #self.column = 'G_filtered'
        self.column = 'PPG'
        self.output_hdf5_key = output_hdf5_key
        self.auto_manage_input_dataframe('signals', signals_hdf5_key)

    def run(self, *,
            signals: pd.DataFrame) -> FileProxy:
        output_file = self.default_outputs()

        if self.column not in signals:
            raise SoftPreconditionFailed(f'Input dataframe does not have column "{self.column}"')
        ppg = signals[self.column]
        ppg_fs = estimate_rate(ppg)
        peaks = ppg_peak_detection(ppg)
        rr = peak_to_rr(ppg, peaks, ppg_fs)
        rri = rr_interpolation(rr, ppg_fs)

        with pd.HDFStore(output_file.file, 'w') as store:
            rr.to_hdf(store, f'{self.output_hdf5_key}/RR')
            rri.to_hdf(store, f'{self.output_hdf5_key}/RRi')

        return output_file

    def default_outputs(self, **kwargs):
        original_kws = prefect.context.run_kwargs
        signals = original_kws['signals']
        output = signals.make_child(suffix='_ppg_peaks')
        return output


class ExtractHRVFeatures(Task): # TODO: add standard preconditions

    def __init__(self, *,
                 rr_hdf5_key: str = '/iguazu/signal/ppg/RR',
                 rri_hdf5_key: str = '/iguazu/signal/ppg/RRi',
                 events_hdf5_key: str = '/iguazu/events/standard',
                 output_hdf5_key: str = '/iguazu/features/ppg',  # TODO: what to put here?
                 **kwargs):
        super().__init__(**kwargs)

        self.output_hdf5_key = output_hdf5_key
        self.auto_manage_input_dataframe('rr', rr_hdf5_key)
        self.auto_manage_input_dataframe('rri', rri_hdf5_key)
        self.auto_manage_input_dataframe('events', events_hdf5_key)

    def run(self, *,
            rr: pd.DataFrame,
            rri: pd.DataFrame,
            events: Optional[pd.DataFrame] = None) -> FileProxy:  #TODO: events should be named sequences?
        output_file = self.default_outputs()

        # if not events.empty:
        #     import ipdb; ipdb.set_trace(context=21)
        #     pass

        df_peaks = hrv_features(rr, rri, events)

        with pd.HDFStore(output_file.file, 'w') as store:
            df_peaks.to_hdf(store, self.output_hdf5_key)

        return output_file

    def default_outputs(self, **kwargs):
        original_kws = prefect.context.run_kwargs
        signals = original_kws['rr']
        output = signals.make_child(suffix='_hrv_features')
        # If it does not exist, create it? TODO: think about this... (the problem is that this is called several times!)
        # empty = pd.DataFrame()
        # with pd.HDFStore(output.file, 'w') as store:
        #     empty.to_hdf(store, self.output_hdf5_key)
        return output


class PPGReport(Task):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # self.auto_manage_input_dataframe('raw', '/nexus/signal/nexus_signal_raw')
        # self.auto_manage_input_dataframe('clean', '/iguazu/signal/ppg/clean')
        # self.auto_manage_input_dataframe('rr', '/iguazu/signal/ppg/RR')
        # self.auto_manage_input_dataframe('rri', '/iguazu/signal/ppg/RRi')

    def run(self, *,
            original: FileProxy,
            raw: FileProxy,
            clean: FileProxy,
            rr: FileProxy,
            rri: FileProxy) -> FileProxy:

        metadata = original.metadata

        raw, raw_meta = self.get_dataframe(raw, '/nexus/signal/nexus_signal_raw')
        clean, clean_meta = self.get_dataframe(clean, '/iguazu/signal/ppg/clean')
        rr, rr_meta = self.get_dataframe(rr, '/iguazu/signal/ppg/RR')
        rri, rri_meta = self.get_dataframe(rri, '/iguazu/signal/ppg/RRi')

        try:
            fs = int(estimate_rate(clean))
        except:
            self.logger.warning('Could not estimate sampling rate, assuming 1Hz')
            fs = 1

        raw_signal = clean_signal = pd.DataFrame()
        if 'G' in raw:
            raw_signal = raw[['G']]
        if 'G_filtered' in clean:
            clean_signal = clean[['G_filtered']]

        html = render_ppg_report(raw_signal, clean_signal, rr, rri,
                                 raw_meta, clean_meta, rr_meta, rri_meta,
                                 fs=fs)

        output = self.default_outputs()
        with open(output.file, 'w', encoding='utf-8') as f:
            f.write(html)

        return output

    def default_outputs(self, **kwargs):
        original_kws = prefect.context.run_kwargs
        clean = original_kws['raw']
        output = clean.make_child(path='html_reports/ppg', extension='.html')
        return output

    def get_dataframe(self, file: FileProxy, key: str) -> Tuple[pd.DataFrame, Mapping]:
        metadata = file.metadata
        journal = metadata.get(self.meta.metadata_journal_family, {})
        status = journal.get('status', None)
        if status != 'SUCCESS':
            dataframe = pd.DataFrame()
        else:
            try:
                with pd.HDFStore(str(file.file.resolve()), 'r') as store:
                    obj = pd.read_hdf(store, key)
                    assert isinstance(obj, pd.DataFrame)
                    dataframe = obj
            except:
                self.logger.warning('Failed to read HDF5 key %s of %s',
                                    key, file, exc_info=True)
                dataframe = None

        return dataframe, journal
