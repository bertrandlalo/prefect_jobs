import logging

from iguazu import __version__
from iguazu.core.flows import PreparedFlow
from iguazu.flows.datasets import GenericDatasetFlow
from iguazu.tasks.behavior import SpaceStressFeatures
from iguazu.tasks.common import SlackTask
from iguazu.tasks.standards import Report

logger = logging.getLogger(__name__)


class BehaviorFeaturesFlow(PreparedFlow):
    """Extract all behavior features from a file dataset"""

    REGISTRY_NAME = 'features_behavior'

    DEFAULT_QUERY = f"""\
           SELECT base->>'id'       AS id,        -- id is the bare minimum needed for the query task to work
                   base->>'filename' AS filename,  -- this is just to help the human debugging this
                   omi->>'user_hash' AS user_hash  -- this is just to help the openmind human debugging this
            FROM   metadata
            WHERE  base->>'state' = 'READY'                -- No temporary files
            AND    base->>'filename' LIKE '%standard.hdf5'         -- Only HDF5 files # todo: fix this ugly query
            AND    (standard->'standardized')::bool        -- Only standardized files
            AND    standard->'groups' ? '/iguazu/events/standard' -- with standardized events
            AND    iguazu->>'status' = 'SUCCESS'
           -- AND    iguazu->>'version' < '{__version__}'
            ORDER BY id                                       -- always in the same order
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

        events_files = dataset_flow.terminal_tasks().pop()
        self.update(dataset_flow)

        behavior_features = SpaceStressFeatures(
            name='SpaceStressFeatures',
            events_hdf5_key='/iguazu/events/standard',
            output_hdf5_key='/iguazu/features/behavior',
        )

        report = Report()
        notify = SlackTask(preamble='Behavior feature extraction flow status finished.\n'
                                    'Task report:')

        # Build flow
        with self:
            features_files = behavior_features.map(parent=events_files, events=events_files)
            message = report(files=features_files)
            notify(message=message)

        logger.debug('Built flow %s with tasks %s', self, self.tasks)

    @staticmethod
    def click_options():
        return GenericDatasetFlow.click_options()
