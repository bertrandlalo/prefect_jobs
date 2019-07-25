import datetime
import logging

from prefect import Flow

from iguazu import __version__
from iguazu.cache_validators import ParametrizedValidator
from iguazu.flows.datasets import generic_dataset_flow
from iguazu.recipes import inherit_params, register_flow
from iguazu.tasks.common import SlackTask
from iguazu.tasks.handlers import garbage_collect_handler, logging_handler
from iguazu.tasks.summarize import SummarizePopulation


logger = logging.getLogger(__name__)


@register_flow('summarize_galvanic')
@inherit_params(generic_dataset_flow)
def galvanic_summary_flow(*, workspace_name=None, query=None, alt_query=None,
                          **kwargs) -> Flow:
    """Collect all galvanic features in a single file"""
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
    # This is the main query that defines the dataset for merging the galvanic
    # features. There is a secondary query because some of the tables may not
    # be available on a new workspace.
    default_query = """\
        SELECT
            id,
            filename
        FROM base
        LEFT JOIN iguazu USING (id)
        LEFT JOIN omi using (id)
        WHERE
            base.state = 'READY' AND                    -- no temporary files
            base.filename LIKE '%_gsr.hdf5' AND         -- only HDF5 files
            base.filename NOT LIKE '%_gsr_gsr.hdf5' AND -- remove incorrect cases where we processed twice
            COALESCE(iguazu."MergeFilesFromGroups", '{{}}')::json->>'state' = 'SUCCESS' AND -- Only files whose mergefilefromgroups was successful
            COALESCE(iguazu."MergeFilesFromGroups", '{{}}')::json->>'version' = '{version}'     -- On this particular iguazu version
        ORDER BY base.id                                -- always in the same order
    """.format(version=__version__)  # Note the {{}} to avoid formatting the coalesce terms
    # There is no secondary query because this flow only makes sense *after*
    # the galvanic extract features flow has run
    default_alt_query = None
    kwargs['query'] = query or default_query
    kwargs['alt_query'] = alt_query or default_alt_query

    # Manage connections to other flows
    dataset_flow = generic_dataset_flow(**kwargs)
    features_files = dataset_flow.terminal_tasks().pop()

    # instantiate tasks
    merge_population = SummarizePopulation(
        # Iguazu task constructor arguments
        groups={'gsr_features_scr': None,
                'gsr_features_scl': None},
        filename='galvanic_summary',
        # Prefect task arguments
        state_handlers=[garbage_collect_handler, logging_handler],
        cache_for=datetime.timedelta(days=7),
        cache_validator=ParametrizedValidator(),
    )
    merge_population_corrected = SummarizePopulation(
        # Iguazu task constructor arguments
        groups={'gsr_features_scr_corrected': None,
                'gsr_features_scl_corrected': None},
        filename='galvanic_summary_corrected',
        # Prefect task arguments
        state_handlers=[garbage_collect_handler, logging_handler],
        cache_for=datetime.timedelta(days=7),
        cache_validator=ParametrizedValidator(),
    )
    notify = SlackTask(message='Galvanic feature summarization finished!')

    with Flow('galvanic_summary_flow') as flow:
        # Connect/extend this flow with the dataset flow
        flow.update(dataset_flow)
        population_summary = merge_population(features_files)
        population_summary_corrected = merge_population_corrected(features_files)

        # Send slack notification
        notify(upstream_tasks=[population_summary, population_summary_corrected])

        # TODO: what's the reference task of this flow?

    logger.debug('Created flow %s with tasks %s', flow, flow.tasks)
    return flow
