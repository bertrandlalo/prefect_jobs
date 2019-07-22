import logging

from prefect import Flow

from iguazu.flows.datasets import generic_dataset_flow
from iguazu.recipes import inherit_params, register_flow
from iguazu.tasks.common import SlackTask
from iguazu.tasks.summarize import SummarizePopulation

logger = logging.getLogger(__name__)


@register_flow('summarize_behavior')
@inherit_params(generic_dataset_flow)
def behavior_summary_flow(*, workspace_name=None, query=None, alt_query=None,
                          **kwargs) -> Flow:
    """Summarize behavior features"""
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
            filename
            FROM base
            LEFT JOIN iguazu USING (id)
            LEFT JOIN omi using (id)
            WHERE
                base.state = 'READY' AND                 -- no temporary files
                base.filename LIKE '%.hdf5' AND          -- only HDF5 files
                iguazu.gsr::json->>'status'  = 'SUCCESS'   -- files not fully processed by iguazu on this flow
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
                base.state = 'READY'           -- no temporary files
            ORDER BY base.id                         -- always in the same order
        """
    kwargs['query'] = query or default_query
    kwargs['alt_query'] = alt_query or default_alt_query

    # Manage connections to other flows
    dataset_flow = generic_dataset_flow(**kwargs)
    features_files = dataset_flow.terminal_tasks().pop()

    # instantiate tasks
    merge_population = SummarizePopulation(groups={'behavior_spacestress_scores': None})

    notify = SlackTask(message='Behavior feature summarization finished!')

    with Flow('behavior_summary_flow') as flow:
        # Connect/extend this flow with the dataset flow
        flow.update(dataset_flow)
        population_summary = merge_population(features_files, filename='behavior_summary')

        # Send slack notification
        notify(upstream_tasks=[population_summary])

        # TODO: what's the reference task of this flow?

    logger.debug('Created flow %s with tasks %s', flow, flow.tasks)
    return flow
