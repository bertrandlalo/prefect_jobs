import logging

from iguazu import __version__
from iguazu.core.exceptions import SoftPreconditionFailed
from iguazu.core.flows import PreparedFlow
from iguazu.flows.datasets import GenericDatasetFlow
from iguazu.functions.behavior import SequenceNotFound
from iguazu.tasks.behavior import SpaceStressFeatures
from iguazu.tasks.common import LoadDataframe, MergeDataframes, SlackTask
from iguazu.tasks.metadata import CreateFlowMetadata, UpdateFlowMetadata
from iguazu.tasks.standards import Report

logger = logging.getLogger(__name__)


class BehaviorFeaturesFlow(PreparedFlow):
    """Extract all behavior features from a file dataset"""

    REGISTRY_NAME = 'features_behavior'

    DEFAULT_QUERY = f"""\
    SELECT base->>'id'       AS id,        -- id is the bare minimum needed for the query task to work
           base->>'filename' AS filename,  -- this is just to help the human debugging this
           omind->>'user_hash' AS user_hash, -- this is just to help the openmind human debugging this
           iguazu->>'version' AS version   -- this is just to help the openmind human debugging this
    FROM   metadata
    WHERE  base->>'state' = 'READY'                -- No temporary files
    AND    base->>'filename' LIKE '%.hdf5'         -- Only HDF5 files
    AND    protocol->>'name' = 'bilan-vr'          -- Files from the VR bilan protocol
    AND    protocol->'extra' ->> 'legacy' = 'false'  -- Files that are not legacy
    AND    standard->'events' ? '/iguazu/events/standard'     -- containing standardized events
    AND    iguazu->>'status' = 'SUCCESS'           -- Files that were successfully standardized
    AND (
         iguazu->'flows'->'{REGISTRY_NAME}'->>'status' IS NULL
     OR  iguazu->'flows'->'{REGISTRY_NAME}'->>'version' IS NULL
     OR  iguazu->'flows'->'{REGISTRY_NAME}'->>'version' < '{__version__}'
)    ORDER BY id                                    -- always in the same order
    """

    def _build(self, **kwargs):
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
        raw_events = dataset_flow.terminal_tasks().pop()
        self.update(dataset_flow)
        create_flow_metadata = CreateFlowMetadata(flow_name=self.REGISTRY_NAME)

        behavior_features = SpaceStressFeatures(
            name='SpaceStressFeatures',
            events_hdf5_key='/iguazu/events/standard',
            output_hdf5_key='/iguazu/features/behavior',
            graceful_exceptions=(SequenceNotFound, SoftPreconditionFailed)
        )

        update_flow_metadata = UpdateFlowMetadata(flow_name=self.REGISTRY_NAME)

        report = Report()
        notify = SlackTask(preamble='Behavior feature extraction flow status finished.\n'
                                    'Task report:')

        # Build flow
        with self:
            create_noresult = create_flow_metadata.map(parent=raw_events)
            features_files = behavior_features.map(parent=raw_events, events=raw_events,
                                                   upstream_tasks=[create_noresult])
            update_noresult = update_flow_metadata.map(parent=raw_events, child=features_files)
            message = report(files=features_files, upstream_tasks=[update_noresult])
            notify(message=message)

        logger.debug('Built flow %s with tasks %s', self, self.tasks)

    @staticmethod
    def click_options():
        return GenericDatasetFlow.click_options()


class BehaviorSummaryFlow(PreparedFlow):
    """Collect all  cardiac features in a single CSV file"""

    REGISTRY_NAME = 'summarize_behavior'
    DEFAULT_QUERY = f"""
        SELECT
               base->>'id'       AS id,        -- id is the bare minimum needed for the query task to work
               base->>'filename' AS filename  -- this is just to help the human debugging this
        FROM   metadata
        WHERE  base->>'state' = 'READY'                -- No temporary files
        AND    base->>'filename' LIKE '%.hdf5'         -- Only HDF5 files TODO: remove _gsr_features hack
        AND    iguazu->>'status' = 'SUCCESS'           -- Files that were successfully standardized
        AND    iguazu->>'version' = '{__version__}'           -- Files from latest version 
        AND    standard->'features' ? '/iguazu/features/ppg/sequence' -- containing the PPG features
        ORDER BY id -- always in the same order                              -- always in the same order                              -- always in the same order
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
            key='/iguazu/features/behavior',
        )
        merge_features = MergeDataframes(
            filename='behavior_summary.csv',
            path='datasets',
        )

        notify = SlackTask(message='Behavioral features summarization finished!')

        with self:
            feature_dataframes = read_features.map(file=features_files)
            merged_dataframe = merge_features(parents=features_files, dataframes=feature_dataframes)
            # Send slack notification
            notify(upstream_tasks=[merged_dataframe])

    @staticmethod
    def click_options():
        return GenericDatasetFlow.click_options()
