import logging

from iguazu import __version__
from iguazu.core.flows import PreparedFlow
from iguazu.flows.datasets import GenericDatasetFlow
from iguazu.tasks.common import LoadDataframe, MergeDataframes, SlackTask
from iguazu.tasks.metadata import CreateFlowMetadata, UpdateFlowMetadata
from iguazu.tasks.respiration import CleanPZTSignal, ExtractPZTFeatures
from iguazu.tasks.standards import Report

logger = logging.getLogger(__name__)


class RespirationFeaturesFlow(PreparedFlow):
    """Extract all  respiration features from a file dataset"""

    REGISTRY_NAME = 'features_respiration'
    DEFAULT_QUERY = f"""
            SELECT base->>'id'       AS id,        -- id is the bare minimum needed for the query task to work
                   base->>'filename' AS filename,  -- this is just to help the human debugging this
                   omind->>'user_hash' AS user_hash, -- this is just to help the openmind human debugging this
                   iguazu->>'version' AS version   -- this is just to help the openmind human debugging this
            FROM   metadata
            WHERE  base->>'state' = 'READY'                -- No temporary files
            AND    base->>'filename' LIKE '%.hdf5'         -- Only HDF5 files
            AND    protocol->>'name' = 'bilan-vr'          -- Files from the VR bilan protocol
            AND    standard->'signals' ? '/iguazu/signal/pzt/standard' -- containing the PZT signal
            AND    standard->'events' ? '/iguazu/events/standard'     -- containing standardized events
            AND    iguazu->>'status' = 'SUCCESS'           -- Files that were successfully standardized
            AND    COALESCE (iguazu->'flows'->'features_respiration' ->> 'version', '') <  '{__version__}'
            ORDER BY id                                -- always in the same order
        """

    def _build(self, *, plot=False, **kwargs):
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
        clean = CleanPZTSignal(
            signals_hdf5_key='/iguazu/signal/pzt/standard',
            events_hdf5_key='/iguazu/events/standard',
            output_hdf5_key='/iguazu/signal/pzt/clean',
        )

        extract_features = ExtractPZTFeatures(
            signals_hdf5_key='/iguazu/signal/pzt/clean',
            events_hdf5_key='/iguazu/events/standard',
            output_hdf5_key='/iguazu/features/pzt/sequence',
        )
        update_flow_metadata = UpdateFlowMetadata(flow_name=self.REGISTRY_NAME)
        report = Report()
        notify = SlackTask(message='Respiration feature extraction finished\n'
                                   'Task report:')
        with self:
            create_noresult = create_flow_metadata.map(parent=raw_signals)
            # Signal processing branch
            clean_signals = clean.map(signals=raw_signals, events=events, upstream_tasks=[create_noresult])
            # Feature extraction
            features = extract_features.map(signals=clean_signals,
                                            events=events,
                                            parent=raw_signals)

            # Send slack notification
            update_noresult = update_flow_metadata.map(parent=raw_signals, child=features)
            message = report(files=features, upstream_tasks=[update_noresult])
            notify(message=message)

        logger.debug('Built flow %s with tasks %s', self, self.tasks)

    @staticmethod
    def click_options():
        return GenericDatasetFlow.click_options()


class RespirationSummaryFlow(PreparedFlow):
    """Collect all  respiration features in a single CSV file"""

    REGISTRY_NAME = 'summarize_respiration'
    DEFAULT_QUERY = f"""
        SELECT
               base->>'id'       AS id,        -- id is the bare minimum needed for the query task to work
               base->>'filename' AS filename  -- this is just to help the human debugging this
        FROM   metadata
        WHERE  base->>'state' = 'READY'                -- No temporary files
        AND    base->>'filename' LIKE '%.hdf5'         -- Only HDF5 files TODO: remove _gsr_features hack
        AND    iguazu->>'status' = 'SUCCESS'           -- Files that were successfully standardized
        AND    standard->'features' ? '/iguazu/features/pzt/sequence' -- containing the GSR signal
        ORDER BY id -- always in the same order
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

        # Manage connections to other flows
        dataset_flow = GenericDatasetFlow(**kwargs)
        self.update(dataset_flow)
        features_files = dataset_flow.terminal_tasks().pop()

        # instantiate tasks. Use separate tasks for a classic ETL approach:
        # E: read features from HDF5 file
        # T and L: merge features into a single dataframe, then save as CSV
        read_features = LoadDataframe(
            key='/iguazu/features/pzt/sequence',
        )
        merge_features = MergeDataframes(
            filename='respiration_summary.csv',
            path='datasets',
        )
        notify = SlackTask(message='Respiration feature summarization finished!')

        with self:
            feature_dataframes = read_features.map(file=features_files)
            merged_dataframe = merge_features(parents=features_files, dataframes=feature_dataframes)
            # Send slack notification
            notify(upstream_tasks=[merged_dataframe])

    @staticmethod
    def click_options():
        return GenericDatasetFlow.click_options()
