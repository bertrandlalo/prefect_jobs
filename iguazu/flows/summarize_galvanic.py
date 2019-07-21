import logging

from prefect import Flow
from prefect.tasks.notifications import SlackTask

from iguazu.flows.datasets import generic_dataset_flow
from iguazu.recipes import inherit_params, register_flow
from iguazu.tasks.summarize import SummarizePopulation

logger = logging.getLogger(__name__)


@register_flow('summarize_galvanic')
@inherit_params(generic_dataset_flow)
def galvanic_summary_flow(*, workspace_name=None, query=None, alt_query=None,
                          **kwargs) -> Flow:
    """Extract galvanic features"""
    logger.debug('Summarizing galvanic features flow')

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
            SELECT id, filename FROM base
            LEFT JOIN iguazu USING (id)
            WHERE 
            base.filename LIKE '%_gsr.hdf5' AND 
            iguazu.id IS NOT NULL
            LIMIT 3
    """
    default_alt_query = """\
            SELECT id, filename FROM base
            LEFT JOIN iguazu USING (id)
            WHERE 
            base.filename LIKE '%_gsr.hdf5' AND 
            iguazu.id IS NOT NULL
            LIMIT 3
    """
    # Todo : change default_alt_query?
    kwargs['query'] = query or default_query
    kwargs['alt_query'] = alt_query or default_alt_query

    # Manage connections to other flows
    dataset_flow = generic_dataset_flow(**kwargs)
    features_files = dataset_flow.terminal_tasks().pop()

    # instantiate tasks
    merge_population = SummarizePopulation(groups={'gsr_features_scr': None,
                                                   'gsr_features_scl': None})
    notify = SlackTask(message='Galvanic feature summarization finished!')

    with Flow('galvanic_summary_flow') as flow:
        # Connect/extend this flow with the dataset flow
        flow.update(dataset_flow)
        population_summary = merge_population(features_files)

        # Send slack notification
        notify(upstream_tasks=[population_summary])

        # TODO: what's the reference task of this flow?

    logger.debug('Created flow %s with tasks %s', flow, flow.tasks)
    return flow
