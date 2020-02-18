import logging

from iguazu.core.flows import PreparedFlow
from iguazu.flows.datasets import GenericDatasetFlow
from iguazu.tasks.common import MergeHDF5, AddSourceMetadata, SlackTask
from iguazu.tasks.standards import Report
from iguazu.tasks.vr import (
    ExtractNexusGSRSignal, ExtractNexusSignal,
    ExtractStandardEvents,
)

logger = logging.getLogger(__name__)


class StandardizeVRFlow(PreparedFlow):
    """Extract and standardize all data from the VR protocol"""

    REGISTRY_NAME = 'standardize_vr'

    DEFAULT_QUERY = """\
SELECT base->>'id'       AS id,        -- id is the bare minimum needed for the query task to work
       base->>'filename' AS filename,  -- this is just to help the human debugging this
       omi->>'user_hash' AS user_hash  -- this is just to help the openmind human debugging this
FROM   metadata
WHERE  base->>'state' = 'READY'                -- No temporary files
AND    base->>'filename' LIKE '%.hdf5'         -- Only HDF5 files
AND    iguazu->>'created_by' IS NULL           -- No files created by iguazu
-- TODO: add a filter by protocol? Certainly needed for the VR protocol!
ORDER BY id                                    -- always in the same order
"""

    def _build(self, **kwargs):
        required_families = dict(
            iguazu=None,
            omi=None,
            standard=None,
        )
        families = kwargs.get('families', {}) or {}  # Could be None by default args
        for name in required_families:
            families.setdefault(name, required_families[name])
        kwargs['families'] = families

        # When the query is set by kwargs, leave the query and dialect as they
        # come. Otherwise, set to the default defined just above
        if not kwargs.get('query', None):
            kwargs['query'] = self.DEFAULT_QUERY
            kwargs['dialect'] = 'postgresql_json'

        # First part of this flow: obtain a dataset of files
        dataset_flow = GenericDatasetFlow(**kwargs)

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
        )
        update_meta = AddSourceMetadata(
            new_meta={
                'standard': {
                    'standardized': True,
                },
                # TODO: think about adding this
                # 'omi': {
                #     'protocol': 'vr',
                # },
            },
        )
        report = Report()
        notify = SlackTask(preamble='Standardization of VR flow status finished.\n'
                                    'Task report:')

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
            update_noresult = update_meta.map(file=merged)
            message = report(files=merged, upstream_tasks=[update_noresult])
            notify(message=message)

        logger.debug('Built flow %s with tasks %s', self, self.tasks)

    @staticmethod
    def click_options():
        return GenericDatasetFlow.click_options()
