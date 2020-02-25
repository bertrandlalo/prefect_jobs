""" General signal processing tasks """

import pandas as pd

import prefect
from dsu.pandas_helpers import estimate_rate

from iguazu import Task
from iguazu.core.exceptions import SoftPreconditionFailed
from iguazu.core.files import FileProxy
from iguazu.functions.cardiac import extract_all_peaks  # todo: move out of cardiac


class ExtractPeaks(Task):

    def __init__(self, *,
                 signals_hdf5_key: str,
                 output_hdf5_key: str,
                 column: str,
                 **kwargs):
        super().__init__(**kwargs)
        self.column = column
        self.output_hdf5_key = output_hdf5_key
        self.auto_manage_input_dataframe('signal', signals_hdf5_key)

    def run(self, *, signal: pd.DataFrame) -> FileProxy:
        output_file = self.default_outputs()

        if self.column not in signal:
            raise SoftPreconditionFailed(f'Input dataframe does not have column "{self.column}"')
        x = signal[self.column]
        fs = int(estimate_rate(x))

        properties, _ = extract_all_peaks(x, window_size=fs)

        with pd.HDFStore(output_file.file, 'w') as store:
            properties.to_hdf(store, self.output_hdf5_key)

        return output_file

    def default_outputs(self, **kwargs):
        original_kws = prefect.context.run_kwargs
        signals = original_kws['signal']
        output = signals.make_child(suffix='_peaks')
        return output
