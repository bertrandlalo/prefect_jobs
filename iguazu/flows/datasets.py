import logging

import click

from prefect import Flow, Parameter, Task
from prefect.engine.cache_validators import never_use
from prefect.tasks.control_flow import switch
from prefect.tasks.control_flow.conditional import Merge

from iguazu.tasks.common import AlwaysFail, AlwaysSucceed, Log, ListFiles
from iguazu.tasks.handlers import logging_handler
from iguazu.tasks.quetzal import CreateWorkspace, Query, ScanWorkspace
from iguazu.recipes import inherit_params, register_flow
from quetzal.client.cli import FamilyVersionListType

logger = logging.getLogger(__name__)


@register_flow('local_dataset')
@click.option('--basedir', required=False,
              type=click.Path(dir_okay=True, file_okay=False),
              help='Local data directory')
def local_dataset_flow(*, basedir=None) -> Flow:
    """Create file dataset from a local directory"""
    logger.debug('Creating local dataset flow')

    # Manage parameters
    # ... not needed for this flow ...

    # Instantiate tasks
    list_files = ListFiles(as_proxy=True)

    # Define flow and its task connections
    with Flow('local_dataset_flow') as flow:
        basedir = Parameter('basedir', default=basedir, required=False)
        upstream = AlwaysSucceed(name='trigger')
        dataset = list_files(basedir, upstream_tasks=[upstream])

        flow.set_reference_tasks([dataset])

    logger.debug('Created flow %s with tasks %s', flow, flow.tasks)
    return flow


@register_flow('quetzal_dataset')
@click.option('--workspace-name', required=False, type=click.STRING,
              help='Name of the Quetzal workspace to create or retrieve.')
@click.option('--families', type=FamilyVersionListType(),
              metavar='NAME:VERSION[,...]', required=False,
              help='Comma-separated family NAMEs and VERSIONs to declare when '
                   'creating a new Quetzal workspace, or to ensure that they '
                   'are needed when an existing Quetzal workspace is retrieved. '
                   'For example: "--families base:latest,xdf:10" means that '
                   'the workspace should use the most recent version of the '
                   '"base" family, and the version 10 of the "xdf" family.')
@click.option('--query', required=False, type=click.File(),
              help='Filename to SQL query that defines the Quetzal dataset.')
@click.option('--alt-query', required=False, type=click.File(),
              help='Filename to an secondary SQL query that defines the Quetzal '
                   'dataset, but only when the primary query fails.')
@click.option('--limit', metavar='N', required=False, type=click.INT,
              help='Only take the first N results of the Quetzal query.')
def quetzal_dataset_flow(*,
                         workspace_name=None,
                         families=None,
                         query=None,
                         alt_query=None,
                         limit=None) -> Flow:
    """Create file dataset from a Quetzal query"""
    logger.debug('Creating Quetzal dataset flow')

    # Manage parameters
    families = families or dict(base=None)
    if query:
        if hasattr(query, 'read'):
            sql = query.read()
        elif isinstance(query, str):
            sql = query
        else:
            raise ValueError('Invalid query parameter type')
    else:
        sql = None
    if alt_query:
        if hasattr(alt_query, 'read'):
            alt_sql = alt_query.read()
        elif isinstance(alt_query, str):
            alt_sql = alt_query
        else:
            raise ValueError('Invalid alt_query parameter type')
    else:
        alt_sql = None

    # Instantiate tasks
    create_or_retrieve = CreateWorkspace(
        # Iguazu task constructor arguments
        exist_ok=True,
        families=families,
        workspace_name=workspace_name,
        # Prefect task arguments
        state_handlers=[logging_handler],
        cache_validator=never_use,
    )
    scan = ScanWorkspace(
        # Iguazu task constructor arguments
        # ... None ...
        # Prefect task arguments
        name='ScanWorkspace',  # Needs to set name otherwise it will be named _WorkspaceOperation
        state_handlers=[logging_handler],
        cache_validator=never_use,
    )
    query = Query(
        # Iguazu task constructor arguments
        as_proxy=True,
        limit=limit,
        # Prefect task arguments
        state_handlers=[logging_handler],
        cache_validator=never_use,
    )

    # Define flow and its task connections
    with Flow('quetzal_dataset_flow') as flow:
        sql = Parameter('sql', default=sql, required=False)
        alt_sql = Parameter('alt_sql', default=alt_sql, required=False)
        upstream = AlwaysSucceed(name='trigger')
        wid = create_or_retrieve(upstream_tasks=[upstream])
        wid_ready = scan(wid)  # wid_ready == wid, but we are using to set the task dependencies
        dataset = query(query=sql, alt_query=alt_sql, workspace_id=wid_ready)

        flow.set_reference_tasks([dataset])

    logger.debug('Created flow %s with tasks %s', flow, flow.tasks)
    return flow


@register_flow('generic_dataset')
@click.option('--data-source', type=click.Choice(['local', 'quetzal']), default='local',
              help='Source of data to choose for this flow.')
@inherit_params(local_dataset_flow)
@inherit_params(quetzal_dataset_flow)
def generic_dataset_flow(*,
                         data_source=None,
                         basedir=None,
                         workspace_name=None,
                         families=None,
                         query=None,
                         alt_query=None,
                         limit=None) -> Flow:
    """Create file dataset from a local dir or Quetzal query"""
    logger.debug('Creating generic (local or quetzal) dataset flow')

    local_flow = local_dataset_flow(basedir=basedir)
    qtzal_flow = quetzal_dataset_flow(workspace_name=workspace_name,
                                      families=families,
                                      query=query,
                                      alt_query=alt_query,
                                      limit=limit)
    merge = Merge()

    local_upstream_task = local_flow.get_tasks(name='trigger').pop()
    qtzal_upstream_task = qtzal_flow.get_tasks(name='trigger').pop()
    local_downstream_task = local_flow.reference_tasks().pop()
    qtzal_downstream_task = qtzal_flow.reference_tasks().pop()

    # Define flow and its task connections
    with Flow('merged_dataset_flow') as flow:
        # Add all the tasks of the upstream flows
        flow.update(local_flow)
        flow.update(qtzal_flow)

        # Then define this flow's tasks
        data_source = Parameter('data_source', default=data_source, required=False)
        switch(condition=data_source,
               cases={
                   'local': local_upstream_task,
                   'quetzal': qtzal_upstream_task,
               })
        dataset = merge(local_branch=local_downstream_task,
                        quetzal_branch=qtzal_downstream_task)

        flow.set_reference_tasks([dataset])

    logger.debug('Created flow %s with tasks %s', flow, flow.tasks)
    return flow


@register_flow('print_dataset')
@inherit_params(generic_dataset_flow)
def print_dataset_flow(**kwargs) -> Flow:
    """Flow that prints each file in its dataset"""

    logger.debug('Creating print dataset flow')

    dataset_flow = generic_dataset_flow(**kwargs)
    dataset_downstream_task = dataset_flow.reference_tasks().pop()

    echo = Log()

    with Flow('print_dataset_flow') as flow:
        # Add all the tasks of the upstream flows
        flow.update(dataset_flow)
        echo.map(input=dataset_downstream_task)

    return flow
