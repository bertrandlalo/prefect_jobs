from typing import Optional

import pandas as pd
import prefect

import iguazu
from iguazu.core.exceptions import SoftPreconditionFailed, GracefulFailWithResults
from iguazu.core.files import FileAdapter
from iguazu.functions.respiration import respiration_clean, respiration_sequence_features, NoRespirationPeaks
from iguazu.functions.specs import infer_standard_groups
from iguazu.utils import deep_update


class CleanPZTSignal(iguazu.Task):
    """ Pre-process respiratory signals.
    """

    def __init__(self,
                 signals_hdf5_key: Optional[str] = '/iguazu/signal/pzt/standard',
                 events_hdf5_key: Optional[str] = '/iguazu/events/standard',
                 output_hdf5_key: Optional[str] = 'iguazu/signal/pzt/clean',
                 **kwargs):

        super().__init__(**kwargs)

        self.output_hdf5_key = output_hdf5_key

        self.auto_manage_input_dataframe('signals', signals_hdf5_key)
        self.auto_manage_input_dataframe('events', events_hdf5_key)

    def run(self,
            signals: FileAdapter,
            events: FileAdapter) -> FileAdapter:

        if events.empty:
            raise SoftPreconditionFailed('Input events are empty')

        output_file = self.default_outputs()

        self.logger.info('Respiration preprocessing for signal=%s, events=%s -> %s',
                         signals, events, output_file)

        # truncate signals between first and last events
        begins, ends = events.index[0], events.index[-1]
        signals = signals[begins:ends]

        if len(signals) < 2:
            raise SoftPreconditionFailed('Input signals are empty')

        # clean signals
        clean = respiration_clean(signals)

        # todo: find some file examples where signal is bad

        with pd.HDFStore(output_file.file, 'w') as store:
            clean.to_hdf(store, self.output_hdf5_key)
        return output_file

    def default_outputs(self, **kwargs):
        original_kws = prefect.context.run_kwargs
        signals = original_kws['signals']
        output = self.create_file(
            parent=signals,
            suffix=f'_pzt_clean',
            temporary=True,
        )
        return output


class ExtractPZTFeatures(iguazu.Task):
    """ Pre-process respiratory signals.
    """

    def __init__(self,
                 signals_hdf5_key: Optional[str] = '/iguazu/signal/pzt/clean',
                 events_hdf5_key: Optional[str] = '/iguazu/events/standard',
                 output_hdf5_key: Optional[str] = 'iguazu/features/pzt/sequence',
                 **kwargs):

        super().__init__(**kwargs)

        self.output_hdf5_key = output_hdf5_key

        self.auto_manage_input_dataframe('signals', signals_hdf5_key)
        self.auto_manage_input_dataframe('events', events_hdf5_key)

    def run(self,
            signals: pd.DataFrame,
            events: pd.DataFrame,
            parent: FileAdapter) -> FileAdapter:
        if signals.empty:
            raise SoftPreconditionFailed('Input signals are empty')
        if events.empty:
            raise SoftPreconditionFailed('Input events are empty')

        output_file = self.default_outputs()

        self.logger.info('Respiration preprocessing for signal=%s, events=%s -> %s',
                         signals, events, output_file)

        # extract sequential features
        try:
            features = respiration_sequence_features(signals, events)
        except NoRespirationPeaks:
            # generate empty dataframe with features
            raise GracefulFailWithResults('Could not find peaks/trough in PZT signal, '
                                          'which is reflects a bad signal . ')

        if not features.empty:
            features.loc[:, 'file_id'] = parent.id

        with pd.HDFStore(output_file.file, 'w') as store:
            features.to_hdf(store, self.output_hdf5_key)
        deep_update(output_file.metadata, {'standard': infer_standard_groups(output_file.file_str)})
        return output_file

    def default_outputs(self, **kwargs):
        original_kws = prefect.context.run_kwargs
        parent = original_kws['parent']
        output = self.create_file(
            parent=parent,
            suffix=f'_pzt_features',
            temporary=False,
        )
        return output
