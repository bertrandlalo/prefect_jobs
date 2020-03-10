import logging

from iguazu.core.flows import PreparedFlow
from iguazu.flows.datasets import GenericDatasetFlow
from iguazu.functions.galvanic import GSRArtifactCorruption
from iguazu.tasks.common import LoadDataframe, MergeDataframes, PropagateMetadata, SlackTask
from iguazu.tasks.galvanic import CleanGSRSignal, ApplyCVX, DetectSCRPeaks, Downsample, ExtractGSRFeatures
from iguazu.tasks.metadata import CreateFlowMetadata, UpdateFlowMetadata

logger = logging.getLogger(__name__)



class GalvanicFeaturesFlow(PreparedFlow):
    """Extract all  cardiac features from a file dataset"""

    REGISTRY_NAME = 'features_galvanic'
    DEFAULT_QUERY = f"""
        SELECT base->>'id'       AS id,        -- id is the bare minimum needed for the query task to work
               base->>'filename' AS filename,  -- this is just to help the human debugging this
               omind->>'user_hash' AS user_hash, -- this is just to help the openmind human debugging this
               iguazu->>'version' AS version   -- this is just to help the openmind human debugging this
        FROM   metadata
        WHERE  base->>'state' = 'READY'                -- No temporary files
        AND    base->>'filename' LIKE '%.hdf5'         -- Only HDF5 files
        AND    protocol->>'name' = 'bilan-vr'          -- Files from the VR bilan protocol
        AND    standard->'signals' ? '/iguazu/signal/gsr/standard' -- containing the GSR signal
        AND    standard->'events' ? '/iguazu/events/standard'     -- containing standardized events
        AND    iguazu->>'status' = 'SUCCESS'           -- Files that were successfully standardized
--         AND    NOT(coalesce(iguazu->'flows' ? 'features_galvanic', FALSE ))     -- Only file where this flow has not ran
        ORDER BY id                                -- always in the same order
    """

    def _build(self, **kwargs):
        # Force required families: Quetzal workspace must have the following
        # families: (nb: None means "latest" version)
        required_families = dict(
            iguazu=None,
            omind=None,
            standard=None,
            protocol=None,
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

        # The cardiac features flow requires an upstream dataset flow in order
        # to provide the input files. Create one and deduce the tasks to
        # plug the cardiac flow to the output of the dataset flow
        dataset_flow = GenericDatasetFlow(**kwargs)
        raw_signals = dataset_flow.terminal_tasks().pop()
        events = raw_signals
        self.update(dataset_flow)

        create_flow_metadata = CreateFlowMetadata(flow_name=self.REGISTRY_NAME)

        # Instantiate tasks
        clean = CleanGSRSignal(
            signals_hdf5_key='/iguazu/signal/gsr/standard',
            events_hdf5_key='/iguazu/events/standard',
            output_hdf5_key='/iguazu/signal/gsr/clean',
            graceful_exceptions=(GSRArtifactCorruption,)
        )
        downsample = Downsample(
            signals_hdf5_key='/iguazu/signal/gsr/clean',
            output_hdf5_key='/iguazu/signal/gsr/downsampled',
        )
        cvx = ApplyCVX(
            signals_hdf5_key='/iguazu/signal/gsr/downsampled',
            output_hdf5_key='/iguazu/signal/gsr/cvx',
        )
        scrpeaks = DetectSCRPeaks(
            signals_hdf5_key='/iguazu/signal/gsr/cvx',
            output_hdf5_key='/iguazu/signal/gsr/scrpeaks',
        )

        extract_features = ExtractGSRFeatures(
            cvx_hdf5_key='/iguazu/signal/gsr/cvx',
            scrpeaks_hdf5_key='/iguazu/signal/gsr/scrpeaks',
            events_hdf5_key='/iguazu/events/standard',
            output_hdf5_key='/iguazu/features/gsr/sequence',
        )
        propagate_metadata = PropagateMetadata(propagate_families=['omind', 'protocol'])

        update_flow_metadata = UpdateFlowMetadata(flow_name=self.REGISTRY_NAME)

        notify = SlackTask(message='Cardiac feature extraction finished!')

        with self:
            create_noresult = create_flow_metadata.map(parent=raw_signals)
            # Signal processing branch
            clean_signals = clean.map(signals=raw_signals,
                                      annotations=raw_signals,
                                      events=events,
                                      upstream_tasks=[create_noresult])
            downsample_signals = downsample.map(signals=clean_signals,
                                                annotations=clean_signals,
                                                upstream_tasks=[create_noresult])
            cvx_signals = cvx.map(signals=downsample_signals,
                                  annotations=downsample_signals,
                                  upstream_tasks=[create_noresult])
            scr_peaks = scrpeaks.map(signals=cvx_signals,
                                     annotations=cvx_signals,
                                     upstream_tasks=[create_noresult])

            # Feature extraction
            features = extract_features.map(cvx=cvx_signals,
                                            scrpeaks=scr_peaks,
                                            events=events,
                                            parent=raw_signals)
            features_with_metadata = propagate_metadata.map(parent=raw_signals, child=features)
            update_noresult = update_flow_metadata.map(parent=raw_signals, child=features_with_metadata)
            # Send slack notification
            notify(upstream_tasks=[update_noresult])

        logger.debug('Built flow %s with tasks %s', self, self.tasks)

    @staticmethod
    def click_options():
        return GenericDatasetFlow.click_options()


class GalvanicSummaryFlow(PreparedFlow):
    """Collect all  cardiac features in a single CSV file"""

    REGISTRY_NAME = 'summarize_galvanic'
    DEFAULT_QUERY = f"""
        SELECT
               base->>'id'       AS id,        -- id is the bare minimum needed for the query task to work
               base->>'filename' AS filename  -- this is just to help the human debugging this
        FROM   metadata
        WHERE  base->>'state' = 'READY'                -- No temporary files
        AND    base->>'filename' LIKE '%.hdf5'         -- Only HDF5 files TODO: remove _gsr_features hack
        AND    iguazu->>'status' = 'SUCCESS'           -- Files that were successfully standardized
        AND    standard->'features' ? '/iguazu/features/gsr/sequence' -- containing the GSR signal
        ORDER BY id -- always in the same order
    """

    def _build(self,
               **kwargs):

        # Manage parameters
        kwargs = kwargs.copy()
        # Propagate workspace name because we captured it on kwargs
        # kwargs['workspace_name'] = workspace_name
        # Force required families: Quetzal workspace must have the following
        # families: (nb: None means "latest" version)
        required_families = dict(
            iguazu=None,
            omind=None,
            standard=None,
            protocol=None
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

        # Manage connections to other flows
        dataset_flow = GenericDatasetFlow(**kwargs)
        self.update(dataset_flow)
        features_files = dataset_flow.terminal_tasks().pop()

        # instantiate tasks. Use separate tasks for a classic ETL approach:
        # E: read features from HDF5 file
        # T and L: merge features into a single dataframe, then save as CSV
        read_features = LoadDataframe(
            key='/iguazu/features/gsr/sequence',
        )
        merge_features = MergeDataframes(
            filename='galvanic_summary.csv',
            path='datasets',
        )
        notify = SlackTask(message='Galvanic feature summarization finished!')

        with self:
            feature_dataframes = read_features.map(file=features_files)
            merged_dataframe = merge_features(parents=features_files, dataframes=feature_dataframes)
            # Send slack notification
            notify(upstream_tasks=[merged_dataframe])

    @staticmethod
    def click_options():
        return GenericDatasetFlow.click_options()
