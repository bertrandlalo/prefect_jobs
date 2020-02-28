import logging

import click

from prefect import Parameter
from prefect.engine.cache_validators import never_use
from prefect.tasks.control_flow import switch
from prefect.tasks.control_flow.conditional import Merge
from quetzal.client.cli import FamilyVersionListType

from iguazu.core.flows import PreparedFlow
from iguazu.tasks.common import AlwaysSucceed, Log, ListFiles
from iguazu.core.handlers import logging_handler
from iguazu.tasks.quetzal import CreateWorkspace, Query, ScanWorkspace

logger = logging.getLogger(__name__)


class LocalDatasetFlow(PreparedFlow):
    """Create a file dataset from a local directory"""

    REGISTRY_NAME = 'dataset_local'

    def _build(self, *, base_dir: str = None, **kwargs):

        # Manage parameters
        # ... not needed for this flow ...

        # Instantiate tasks
        list_files = ListFiles(as_file_adapter=True)

        with self:
            directory = Parameter('base_dir', default=base_dir, required=False)
            trigger = AlwaysSucceed(name='trigger')
            dataset = list_files(directory, upstream_tasks=[trigger])

            self.set_reference_tasks([dataset])

        logger.debug('Built flow %s with tasks %s', self, self.tasks)

    @staticmethod
    def click_options():
        return (
            click.option('--base-dir', required=False,
                         type=click.Path(dir_okay=True, file_okay=False),
                         help='Local data directory'),
        )


class QuetzalDatasetFlow(PreparedFlow):
    """Create a file dataset from a Quetzal query"""

    REGISTRY_NAME = 'dataset_quetzal'

    # def __init__(self, **kwargs):
    #     kwargs.setdefault('name', 'quetzal_dataset_flow')
    #     super().__init__(**kwargs)

    def _build(self, *,
               families=None,
               query=None,
               dialect=None,
               workspace_name=None,
               limit=None,
               shuffle=False,
               **kwargs):
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
        dialect = dialect or 'postgresql'

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
            as_file_adapter=True,
            limit=limit,
            shuffle=shuffle,
            # Prefect task arguments
            state_handlers=[logging_handler],
            cache_validator=never_use,
        )

        # Define flow and its task connections
        with self:
            #with Flow('quetzal_dataset_flow') as flow:
            sql = Parameter('sql', default=sql, required=False)
            sql_dialect = Parameter('dialect', default=dialect, required=False)
            upstream = AlwaysSucceed(name='trigger')
            wid = create_or_retrieve(upstream_tasks=[upstream])
            wid_ready = scan(wid)  # wid_ready == wid, but we are using to set the task dependencies
            dataset = query(query=sql, dialect=sql_dialect, workspace_id=wid_ready)

            self.set_reference_tasks([dataset])

        logger.debug('Built flow %s with tasks %s', self, self.tasks)

    @staticmethod
    def click_options():
        return (
            click.option('--workspace-name', required=False, type=click.STRING,
                         help='Name of the Quetzal workspace to create or retrieve.'),
            click.option('--families', type=FamilyVersionListType(),
                         metavar='NAME:VERSION[,...]', required=False,
                         help='Comma-separated family NAMEs and VERSIONs to declare when '
                              'creating a new Quetzal workspace, or to ensure that they '
                              'are needed when an existing Quetzal workspace is retrieved. '
                              'For example: "--families base:latest,xdf:10" means that '
                              'the workspace should use the most recent version of the '
                              '"base" family, and the version 10 of the "xdf" family.'),
            click.option('--query', required=False, type=click.File(),
                         help='Filename to SQL query that defines the Quetzal dataset.'),
            click.option('--dialect', required=False,
                         help='Dialect use to express the query.'),
            click.option('--limit', metavar='N', required=False, type=click.INT,
                         help='Only take the first N results of the Quetzal query.'),
            click.option('--shuffle/--no-shuffle', is_flag=True, default=False,
                         help='Randomly shuffle the query results before selecting with '
                              '--limit and returning the results.'),
        )


class GenericDatasetFlow(PreparedFlow):
    """Create a file dataset from a local directory or Quetzal query"""

    REGISTRY_NAME = 'dataset_generic'

    # def __init__(self, **kwargs):
    #     kwargs.setdefault('name', 'generic_dataset_flow')
    #     super().__init__(**kwargs)

    def _build(self, *, data_source=None, **kwargs):
        local_flow = LocalDatasetFlow(**kwargs)
        qtzal_flow = QuetzalDatasetFlow(**kwargs)
        self.update(local_flow)
        self.update(qtzal_flow)

        merge = Merge()
        local_upstream_task = local_flow.get_tasks(name='trigger').pop()
        qtzal_upstream_task = qtzal_flow.get_tasks(name='trigger').pop()
        local_downstream_task = local_flow.reference_tasks().pop()
        qtzal_downstream_task = qtzal_flow.reference_tasks().pop()

        # Define flow and its task connections
        with self:
            data_source = Parameter('data_source', default=data_source, required=False)
            switch(condition=data_source,
                   cases={
                       'local': local_upstream_task,
                       'quetzal': qtzal_upstream_task,
                   })
            dataset = merge(local_branch=local_downstream_task,
                            quetzal_branch=qtzal_downstream_task)

            self.set_reference_tasks([dataset])

        logger.debug('Built flow %s with tasks %s', self, self.tasks)

    @staticmethod
    def click_options():
        return (
            click.option('--data-source', type=click.Choice(['local', 'quetzal']), default='local',
                         help='Source of data to choose for this flow.'),
        ) + LocalDatasetFlow.click_options() + QuetzalDatasetFlow.click_options()


class ShowDatasetFlow(PreparedFlow):
    """Show all files from a file dataset"""

    REGISTRY_NAME = 'dataset_show'

    def _build(self, **kwargs):
        dataset_flow = GenericDatasetFlow(**kwargs)
        dataset_downstream_task = dataset_flow.reference_tasks().pop()
        self.update(dataset_flow)

        echo = Log()

        with self:
            echo.map(input=dataset_downstream_task)

    @staticmethod
    def click_options():
        return GenericDatasetFlow.click_options()
