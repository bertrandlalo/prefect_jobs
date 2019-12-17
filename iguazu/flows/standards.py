import logging

from iguazu.core.flows import PreparedFlow
from iguazu.flows.datasets import LocalDatasetFlow
from iguazu.tasks.common import MergeHDF5, AddSourceMetadata
from iguazu.tasks.standards import Report
from iguazu.tasks.vr import (
    ExtractNexusGSRSignal, ExtractNexusSignal,
    ExtractStandardEvents,
)

logger = logging.getLogger(__name__)


class StandardizeVRFlow(PreparedFlow):
    """Extract and standardize all data from the VR protocol"""

    REGISTRY_NAME = 'standardize_vr'

    def _build(self, **kwargs):
        # First part of this flow: obtain a dataset of files
        dataset_flow = LocalDatasetFlow(**kwargs)

        raw_files = dataset_flow.terminal_tasks().pop()
        self.update(dataset_flow)

        standardize_events = ExtractStandardEvents(
            name='UnityToStandardEvents',
            events_hdf5_key='/unity/events/unity_events',
            output_hdf5_key='/iguazu/events/standard',
        )
        # filter_vr = FilterVRSequences()
        standardize_ppg_signals = ExtractNexusSignal(
            name='NexusToStandardPPG',
            signals_hfd5_key='/nexus/signal/nexus_signal_raw',
            output_hdf5_key='/iguazu/signal/ppg/standard',
            source_column='G',
            target_column='PPG',
        )
        standardize_gsr_signals = ExtractNexusGSRSignal(
            name='NexusToStandardGSR',
            signals_hfd5_key='/nexus/signal/nexus_signal_raw',
            output_hdf5_key='/iguazu/signal/gsr/standard',
            source_column='F',
            target_column='GSR',
        )
        standardize_pzt_signals = ExtractNexusSignal(
            name='NexusToStandardPZT',
            signals_hfd5_key='/nexus/signal/nexus_signal_raw',
            output_hdf5_key='/iguazu/signal/pzt/standard',
            source_column='H',
            target_column='PZT',
        )
        merge = MergeHDF5(
            suffix='_standard',
            temporary=False,
            verify_status=True,
            hdf5_family='standard',
            meta_keys=['standard'],
            # extra_metadata={
            #     'iguazu': {
            #         'standardized': True,
            #     }
            # }

        )
        update_meta = AddSourceMetadata(
            new_meta={
                'standard': {
                    'standardized': True,
                }
            },
            #source_family='standard',
        )
        report = Report()

        # Build flow
        with self:
            standard_events = standardize_events.map(events=raw_files)
            # vr_sequences = filter_vr.map(events=standard_events)
            standard_ppg = standardize_ppg_signals.map(signals=raw_files)
            standard_gsr = standardize_gsr_signals.map(signals=raw_files)
            standard_pzt = standardize_pzt_signals.map(signals=raw_files)
            merged = merge.map(
                parent=raw_files,
                events=standard_events,
                PPG=standard_ppg,
                GSR=standard_gsr,
                PZT=standard_pzt,
            )
            update_noresult = update_meta.map(target=merged, source=raw_files)
            report(files=merged, upstream_tasks=[update_noresult])

        logger.debug('Built flow %s with tasks %s', self, self.tasks)

    @staticmethod
    def click_options():
        return LocalDatasetFlow.click_options()
