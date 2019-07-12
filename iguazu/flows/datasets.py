import logging

from prefect import Flow, Parameter, Task
from prefect.engine.cache_validators import never_use
from prefect.tasks.control_flow import switch, merge

from iguazu.tasks.common import Log, ListFiles
from iguazu.tasks.handlers import logging_handler
from iguazu.tasks.quetzal import CreateWorkspace, Query, ScanWorkspace

logger = logging.getLogger(__name__)


def local_dataset_flow(*,
                       basedir=None,
                       as_proxy=True) -> Flow:
    """Flow to create a file dataset from a local directory"""
    logger.debug('Creating local dataset flow')

    # Manage parameters
    # ... not needed for this flow ...

    # Instantiate tasks
    list_files = ListFiles(as_proxy=as_proxy)

    # Define flow and its task connections
    with Flow('local_dataset_flow') as flow:
        basedir = Parameter('basedir', default=basedir, required=False)
        _ = list_files(basedir)

    logger.debug('Created flow: %s with tasks %s', flow, flow.tasks)
    return flow


def quetzal_dataset_flow(*,
                         workspace_name=None,
                         families=None,
                         sql=None,
                         as_proxy=True) -> Flow:
    """Flow to create a file dataset from a Quetzal query"""
    logger.debug('Creating Quetzal dataset flow')

    # Manage parameters
    families = families or dict(base=None)

    # Instantiate tasks
    as_proxy = as_proxy or True
    create_or_retrieve = CreateWorkspace(
        exist_ok=True,
        families=families,
        workspace_name=workspace_name,
        state_handlers=[logging_handler],
        cache_validator=never_use,
    )
    scan = ScanWorkspace(
        name='ScanWorkspace',  # Needs to set name otherwise it will be named _WorkspaceOperation
        state_handlers=[logging_handler],
        cache_validator=never_use,
    )
    query = Query(
        as_proxy=as_proxy,
        state_handlers=[logging_handler],
        cache_validator=never_use,
    )

    # Define flow and its task connections
    with Flow('quetzal_dataset_flow') as flow:
        sql = Parameter('sql', default=sql, required=False)
        wid = create_or_retrieve()
        wid_ready = scan(wid)  # wid_ready == wid, but we are using to set the task dependencies
        _ = query(query=sql, workspace_id=wid_ready)

    logger.debug('Created flow: %s with tasks %s', flow, flow.tasks)
    return flow


def merged_dataset_flow(*,
                        data_source='local',
                        basedir='.',
                        workspace_name=None,
                        families=None,
                        sql=None) -> Flow:
    """Flow to create a file dataset from a local directory or Quetzal query"""

    logger.debug('Creating merged local or quetzal dataset flow')

    local_ds_flow = local_dataset_flow(basedir=basedir)
    quetzal_ds_flow = quetzal_dataset_flow(workspace_name=workspace_name,
                                           families=families,
                                           sql=sql)

    local_ds_root = local_ds_flow.get_tasks(task_type=ListFiles)[0]
    local_ds_terminal = local_ds_root
    quetzal_ds_root = quetzal_ds_flow.get_tasks(task_type=CreateWorkspace)[0]
    quetzal_ds_terminal = quetzal_ds_flow.get_tasks(task_type=Query)[0]

    # Define flow and its task connections
    with Flow('merged_dataset_flow') as flow:
        # Add all the tasks of the upstream flows
        flow.update(local_ds_flow)
        flow.update(quetzal_ds_flow)

        # Then define this flow's tasks
        data_source = Parameter('data_source', default=data_source, required=False)
        switch(condition=data_source,
               cases={
                   'local': local_ds_root,
                   'quetzal': quetzal_ds_root,
               })
        _ = merge(local_ds_terminal, quetzal_ds_terminal)

    logger.debug('Created flow: %s with tasks %s', flow, flow.tasks)
    return flow


def print_dataset_flow(**kwargs) -> Flow:
    """Flow that prints each file in its dataset"""

    logger.debug('Creating print dataset flow')

    dataset_flow = merged_dataset_flow(**kwargs)
    dataset_terminal = dataset_flow.terminal_tasks().pop()

    echo = Log()

    with Flow('print_dataset_flow') as flow:
        # Add all the tasks of the upstream flows
        flow.update(dataset_flow)
        echo.map(dataset_terminal)

    return flow

