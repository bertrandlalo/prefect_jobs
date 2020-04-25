import datetime
import logging

from iguazu.cache_validators import ParametrizedValidator
from iguazu.core.flows import PreparedFlow
from iguazu.core.handlers import garbage_collect_handler, logging_handler
from iguazu.flows.datasets import GenericDatasetFlow
from iguazu.tasks.behavior import SpaceStressParticipantActions, SpaceStressSpawnsStimulations, SpaceStressScores
from iguazu.tasks.common import MergeFilesFromGroups, SlackTask
from iguazu.tasks.summarize import SummarizePopulation

logger = logging.getLogger(__name__)


class BehaviorFeaturesFlow(PreparedFlow):
    """Extract all behavior features from a file dataset"""

    REGISTRY_NAME = 'features_behavior'

    def _build(self,
               **kwargs):

        # Manage parameters
        kwargs = kwargs.copy()
        # Propagate workspace name because we captured it on kwargs
        kwargs['workspace_name'] = workspace_name
        # Force required families: Quetzal workspace must have the following
        # families: (nb: None means "latest" version)
        required_families = dict(
            iguazu=None,
            omi=None,
        )
        families = kwargs.get('families', {}) or {}  # Could be None by default args
        for name in required_families:
            families.setdefault(name, required_families[name])
        kwargs['families'] = families
        # In case there was no query, set a default one
        default_query = """\
            SELECT
            id,
            filename
            FROM base
            LEFT JOIN iguazu USING (id)
            LEFT JOIN omi using (id)
            WHERE
                base.state = 'READY' AND                 -- no temporary files
                base.filename LIKE '%.hdf5' AND          -- only HDF5 files
                iguazu.behavior::json->>'status' IS NULL AND  -- files not fully processed by iguazu on this flow
                iguazu.parents is NULL                   -- files not generated by iguazu
            ORDER BY base.id                             -- always in the same order
        """
        # This secondary, alternative query is defined for the case when a new
        # quetzal workspace is created, and the iguazu.gsr metadata does not even
        # exist. We need to to do this because the iguazu.gsr column does not exist
        # and postgres does not permit querying a non-existent column
        default_alt_query = """\
            SELECT
            id,
            filename
            FROM base
            LEFT JOIN iguazu USING (id)
            WHERE
                base.state = 'READY' AND             -- no temporary files
                base.filename LIKE '%.hdf5'          -- only HDF5 files
            ORDER BY base.id                         -- always in the same order
        """
        kwargs['query'] = query or default_query
        kwargs['alt_query'] = alt_query or default_alt_query

        # Manage connections to other flows
        dataset_flow = GenericDatasetFlow(**kwargs)
        self.update(dataset_flow)
        events = dataset_flow.terminal_tasks().pop()

        # Instantiate tasks
        extract_participant_actions = SpaceStressParticipantActions(
            # Prefect task arguments
            state_handlers=[garbage_collect_handler, logging_handler],
            cache_for=datetime.timedelta(days=7),
            cache_validator=ParametrizedValidator(force=force),
        )
        extract_spawns_stimulations = SpaceStressSpawnsStimulations(
            # Prefect task arguments
            state_handlers=[garbage_collect_handler, logging_handler],
            cache_for=datetime.timedelta(days=7),
            cache_validator=ParametrizedValidator(force=force),
        )
        extract_scores = SpaceStressScores(
            # Prefect task arguments
            state_handlers=[garbage_collect_handler, logging_handler],
            cache_for=datetime.timedelta(days=7),
            cache_validator=ParametrizedValidator(force=force),
        )
        merge_subject = MergeFilesFromGroups(
            # Iguazu task constructor arguments
            suffix="_behavior",
            status_metadata_key='behavior',
            # Prefect task arguments
            state_handlers=[garbage_collect_handler, logging_handler],
            cache_for=datetime.timedelta(days=7),
            cache_validator=ParametrizedValidator(force=force),
        )

        # Flow definition
        with self:
            # Behavior flow
            actions = extract_participant_actions.map(events=events)
            stimulations = extract_spawns_stimulations.map(events=events)
            scores = extract_scores.map(parent=events, stimulations=stimulations, actions=actions)

            subject_summary = merge_subject.map(parent=events,
                                                behavior_spacestress_actions=actions,
                                                behavior_spacestress_stimulations=stimulations,
                                                behavior_spacestress_scores=scores)


class BehaviorSummaryFlow(PreparedFlow):
    """Collect all behavior features in a single CSV file"""

    REGISTRY_NAME = 'summarize_behavior'

    def _build(self, *,
               workspace_name=None, query=None, alt_query=None,
               **kwargs):
        logger.debug('Summarizing behavior features flow')

        # Manage parameters
        kwargs = kwargs.copy()
        # Propagate workspace name because we captured it on kwargs
        kwargs['workspace_name'] = workspace_name
        # Force required families: Quetzal workspace must have the following
        # families: (nb: None means "latest" version)
        required_families = dict(
            iguazu=None,
            omi=None,
        )
        families = kwargs.get('families', {}) or {}  # Could be None by default args
        for name in required_families:
            families.setdefault(name, required_families[name])
        kwargs['families'] = families
        # In case there was no query, set a default one
        # In case there was no query, set a default one
        default_query = """\
            SELECT
                id,
                filename,
                iguazu.behavior::json->>'status' AS status,
                iguazu.state
            FROM base
            LEFT JOIN iguazu USING (id)
            LEFT JOIN omi using (id)
            WHERE
                base.state = 'READY' AND                    -- no temporary files
                base.filename LIKE '%_behavior.hdf5' AND         -- only HDF5 files
                base.filename NOT LIKE '%__behavior_behavior.hdf5' AND -- remove incorrect cases where we processed twice
                COALESCE(iguazu."MergeFilesFromGroups", '{}')::json->>'state' = 'SUCCESS' -- Only files whose mergefilefromgroups was successful
                -- AND iguazu.state = 'SUCCESS'
                --iguazu.gsr::json->>'status' = 'SUCCESS'     -- files not fully processed by iguazu on this flow
            ORDER BY base.id                                -- always in the same order
        """
        default_alt_query = None

        kwargs['query'] = query or default_query
        kwargs['alt_query'] = alt_query or default_alt_query

        # Manage connections to other flows
        dataset_flow = GenericDatasetFlow(**kwargs)
        self.update(dataset_flow)
        features_files = dataset_flow.terminal_tasks().pop()

        # instantiate tasks
        merge_population = SummarizePopulation(
            # Iguazu task constructor arguments
            groups={'behavior_spacestress_scores': None},
            filename='behavior_summary',
            # Prefect task arguments
            state_handlers=[garbage_collect_handler, logging_handler],
            cache_for=datetime.timedelta(days=7),
            cache_validator=ParametrizedValidator(),
        )

        notify = SlackTask(message='Behavior feature summarization finished!')

        with self:
            population_summary = merge_population(features_files)

            # Send slack notification
            notify(upstream_tasks=[population_summary])

            # TODO: what's the reference task of this flow?
