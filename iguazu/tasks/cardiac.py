from typing import Mapping, Optional, Tuple

import pandas as pd
import prefect

from iguazu.core.exceptions import SoftPreconditionFailed
from iguazu.core.tasks import Task
from iguazu.helpers.files import FileProxy
from iguazu.functions.cardiac import (
    hrv_features, peak_to_rr, ppg_clean, ppg_peak_detection, rr_interpolation
)
from iguazu.functions.ppg_report import render_ppg_report

from dsu.pandas_helpers import estimate_rate


class CleanPPGSignal(Task):

    def __init__(self, *,
                 signals_hdf5_key: str = '/nexus/signal/nexus_signal_raw',
                 events_hdf5_key: str = '/unity/events/unity_events',
                 output_hdf5_key: str = '/iguazu/signal/ppg/clean',
                 warmup_duration: int = 30,
                 sampling_rate: int = 512,
                 filter_kwargs: Optional[Mapping] = None,
                 **kwargs):
        super().__init__(**kwargs)

        self.output_hdf5_key = output_hdf5_key
        self.warmup_duration = warmup_duration
        self.filter_kwargs = filter_kwargs or {}
        self.column = 'G'
        self.sampling_rate = sampling_rate

        self.auto_manage_input_dataframe('signals', signals_hdf5_key)
        self.auto_manage_input_dataframe('events', events_hdf5_key)

    def run(self, *,
            signals: pd.DataFrame,
            events: pd.DataFrame) -> FileProxy:

        if signals.empty:
            raise SoftPreconditionFailed('Input signals are empty')
        if events.empty:
            raise SoftPreconditionFailed('Input events are empty')

        output_file = self.default_outputs()

        df_output = ppg_clean(signals, events,
                              warmup_duration=self.warmup_duration,
                              column=self.column,
                              filter_kwargs=self.filter_kwargs,
                              sampling_rate=self.sampling_rate)

        with pd.HDFStore(output_file.file, 'w') as store:
            df_output.to_hdf(store, self.output_hdf5_key)

        return output_file

    def default_outputs(self, **kwargs):
        original_kws = prefect.context.run_kwargs
        signals = original_kws['signals']
        output = signals.make_child(suffix='_cardiac_clean')  # TODO: rename GSR _clean to _gsr_clean !
        # If it does not exist, create it? TODO: think about this... (the problem is that this is called several times!)
        # empty = pd.DataFrame()
        # with pd.HDFStore(output.file, 'w') as store:
        #     empty.to_hdf(store, self.output_hdf5_key)
        # OR
        # open(output.file, 'w').close()
        return output


class PPGDetectRR(Task):
    def __init__(self, *,
                 fs: int = 512,
                 signals_hdf5_key: str = '/iguazu/signal/ppg/clean',
                 output_hdf5_key: str = '/iguazu/signal/ppg', # a /RR or /RRi will be added
                 **kwargs):
        super().__init__(**kwargs)

        self.fs = fs
        self.column = 'G_filtered'
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
        rri = rr_interpolation(rr, self.fs)

        with pd.HDFStore(output_file.file, 'w') as store:
            rr.to_hdf(store, f'{self.output_hdf5_key}/RR')
            rri.to_hdf(store, f'{self.output_hdf5_key}/RRi')

        return output_file

    def default_outputs(self, **kwargs):
        original_kws = prefect.context.run_kwargs
        signals = original_kws['signals']
        output = signals.make_child(suffix='_ppg_peaks')
        # If it does not exist, create it? TODO: think about this... (the problem is that this is called several times!)
        # empty = pd.DataFrame()
        # with pd.HDFStore(output.file, 'w') as store:
        #     empty.to_hdf(store, self.output_hdf5_key)
        return output


class ExtractHRVFeatures(Task):

    def __init__(self, *,
                 rr_hdf5_key: str = '/iguazu/signal/ppg/RR',
                 rri_hdf5_key: str = '/iguazu/signal/ppg/RRi',
                 events_hdf5_key: str = '/iguazu/events',
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
