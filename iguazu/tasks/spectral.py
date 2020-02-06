import copy
from typing import Dict, Optional, Tuple

import pandas as pd
import prefect

from iguazu.helpers.files import FileProxy
from iguazu.helpers.states import SKIPRESULT
from iguazu.helpers.tasks import get_base_meta, task_upload_result, task_fail
from iguazu.core.exceptions import IguazuError
from iguazu.functions.spectral import bandpower


class BandPowers(prefect.Task):

    def __init__(self,
                 epoch_size: int,
                 epoch_overlap: int,
                 bands: Dict[str, Tuple[float, float]],
                 relative: bool = False,
                 signal_group: Optional[str] = None,
                 signal_column: Optional[str] = None,
                 output_group: Optional[str] = None,
                 force: Optional[bool] = None,
                 **kwargs):
        super().__init__(**kwargs)
        self.epoch_size = epoch_size
        self.epoch_overlap = epoch_overlap
        self.bands = copy.deepcopy(bands)
        self.relative = relative
        self.signal_group = signal_group
        self.signal_column = signal_column
        self.output_group = output_group
        self.force = force

    def run(self, signal: FileProxy) -> FileProxy:

        output = signal.make_child(suffix='_bp' + ('_rel' if self.relative else '_abs'))
        self.logger.info('Band power extraction for signal=%s -> %s', signal, output)

        # Our current force detection code
        if not self.force and output.metadata.get('iguazu', {}).get('state') is not None:
            self.logger.info('Output already exists, skipping')
            raise SKIPRESULT('Output already exists', result=output)

        # At that point, we are sure that the previous tasks succeeded and that
        # the output has not yet been generated ()

        signal_file = str(signal.file)
        signal_group = self.signal_group or '/gsr/timeseries/preprocessed'
        output_group = self.output_group or '/gsr/timeseries/bandpowers'

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
                df_output = bandpower(df_signals[[self.signal_column]], self.bands,
                                      epoch_size=self.epoch_size, epoch_overlap=self.epoch_overlap,
                                      relative=self.relative)
                state = 'SUCCESS'
                meta = get_base_meta(self, state=state)
                # Manage output, save to file
                task_upload_result(self, df_output, meta, state, output, output_group)
                return output
        except Exception as ex:
            # Manage output, save to file
            self.logger.warning('BandPowers failed with an exception', exc_info=True)
            task_fail(self, ex, output, output_group)

        return output
