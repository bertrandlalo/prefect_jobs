import copy
import datetime
import functools
import random
import string
from typing import Any, Dict, List, Optional, Union

from prefect import context, Task
from prefect.engine import signals
from prefect.engine.runner import ENDRUN
from quetzal.client import QuetzalAPIException, helpers

from iguazu.helpers.files import QuetzalFile
from iguazu.helpers.states import SkippedResult


ResultSetType = Union[QuetzalFile, Dict[str, Dict[str, Any]]]


class QuetzalBaseTask(Task):
    """ Base parent class for tasks that use Quetzal

    The objective of this class is to provide a Quetzal client property that
    is initialized with the API username, password, etc.

    Attributes
    ----------
    client: quetzal.client.Client
        Client object used to communicate using the Quetzal API.

    Parameters
    ----------
    url: str
        URL of the Quetzal server. If not set, it will use the
        :py:ref:`quetzal.client.config.Configuration` default fallback value,
        which is the `QUETZAL_URL` environment variable.
    username: str
        Identifier for a Quetzal user. If not set, it will use the
        :py:ref:`quetzal.client.config.Configuration` default fallback value,
        which is the `QUETZAL_USER` environment variable.
    password: str
        Password for a Quetzal user. If not set, it will use the
        :py:ref:`quetzal.client.config.Configuration` default fallback value,
        which is the `QUETZAL_PASSWORD` environment variable.
    insecure: bool
        When set, accept insecure connections, that is, connections over http
        instead of https or without a signed certificate. Set this to ``True``
        when using development servers.

    """

    def __init__(self,
                 url: Optional[str] = None,
                 username: Optional[str] = None,
                 password: Optional[str] = None,
                 insecure: bool = False,
                 **kwargs):
        super().__init__(**kwargs)
        self._client_args = dict(
            url=url, username=username, password=password, insecure=insecure,
        )
        self._client = None

    @property
    def client(self):
        if 'quetzal_client' in context:  #TODO: change order context < task
            return helpers.get_client(**context.quetzal_client)
        elif self._client is None:
            self._client = helpers.get_client(**self._client_args)
        return self._client

    def run(self) -> None:
        raise RuntimeError('QuetzalBaseTask is an abstract Task')

    def __getstate__(self):
        state = self.__dict__.copy()
        del state['_client']
        return state

    def __setstate__(self, state):
        self.__dict__.update(state)
        self._client = None


class Query(QuetzalBaseTask):
    """ Perform a query on Quetzal and return all its results

    This task uses the :py:ref:`quetzal.client.helpers.query` function to
    perform a SQL query on a Quetzal server and return all its results.

    Typically, this task will be used as one of the first tasks of a flow that
    uses Quetzal as a data source.

    """

    def __init__(self, as_proxy: bool = False, **kwargs):
        super().__init__(**kwargs)
        self._as_proxy = as_proxy

    def run(self,
            query: str,
            workspace_id: Optional[int] = None,
            id_column: Optional[str] = None) -> List[ResultSetType]:
        """ Perform the Quetzal SQL query

        Parameters
        ----------
        query: str
            Query in postgreSQL dialect.
        workspace_id: int
            Workspace where the query should be executed. If not set, it uses
            the global workspace.
        id_column: str
            Name of the column on the query that represents a Quetzal file id.

        Returns
        -------
        results
            A list of dictionaries, one for each result row.

        """
        for k,v in context.items():
            self.logger.info('Context: %s = %s', k ,v)
        # from remote_pdb import RemotePdb
        # RemotePdb('0.0.0.0', 4444).set_trace()
        self.logger.debug('Querying Quetzal at %s with SQL=%s',
                          self.client.configuration.host,
                          query)
        try:
            rows, total = helpers.query(self.client, workspace_id, query)
        except QuetzalAPIException as ex:
            self.logger.warning('Quetzal query task failed: %s', ex.title)
            raise
        self.logger.debug('Query gave %d results', total)

        if self._as_proxy:
            proxies = [QuetzalFile(file_id=row['id'], workspace_id=workspace_id) for row in rows]
            return proxies

        return rows


class ConvertToFileProxy(Task):

    def __init__(self, id_key: str = 'id', **kwargs):
        super().__init__(**kwargs)
        self.id_key = id_key

    def run(self,
            rows: Union[ResultSetType, List[ResultSetType]],
            workspace_id: Optional[int],  # Note: We do not provide a default, user must set None if they mean it
            id_key: Optional[str] = None,
            ) -> Union[QuetzalFile, List[QuetzalFile]]:
        is_list = isinstance(rows, list)
        if not is_list:
            rows = [rows]
        id_key = id_key or self.id_key
        file_proxies = []
        for row in rows:
            if id_key not in row:
                raise RuntimeError('Input row does not have expected id key')
            file = QuetzalFile(file_id=row[id_key], workspace_id=workspace_id)
            file_proxies.append(file)

        if not is_list:
            return file_proxies[0]
        return file_proxies


class CreateWorkspace(QuetzalBaseTask):
    """ Create or retrieve a Quetzal workspace

    Attributes
    ----------
    exist_ok: bool
        When set, this task will retrieve a workspace with the provided name
        if it already exists. When not set and a workspace with the same already
        exists, the task will fail.

    """

    def __init__(self, *,
                 workspace_name: Optional[str] = None,
                 description: Optional[str] = None,
                 families: Optional[Dict[str, Optional[int]]] = None,
                 exist_ok: bool = True,
                 **kwargs):
        super().__init__(**kwargs)
        self.workspace_name = workspace_name
        self.description = description or 'Workspace created by iguazu'
        self.families = copy.deepcopy(families or {})
        self.exist_ok = exist_ok  # TODO: decide: should this be here or a run parameter?

    def run(self,
            workspace_name: Optional[str] = None,
            description: Optional[str] = None,
            families: Optional[Dict[str, Optional[int]]] = None,
            temporary: bool = False) -> int:
        """ Create a Quetzal workspace, or retrieve it if it already exists

        Parameters
        ----------
        workspace_name: str
            Name for the new workspace. If not set, a random name will be generated.
        description: str
            Description for the new workspace. If not set, a fallback description
            will be used.
        families: dict
            Dictionary of family to version number with the required metadata
            families and versions. A ``None`` value means `"latest"`.
        temporary: bool
            Whether the workspace should be marked temporary or not on Quetzal.

        Returns
        -------
        id: int
            Workspace identifier on the Quetzal API.

        """

        random_name = 'iguazu-{date}-{rnd}'.format(
            date=datetime.datetime.now().strftime('%Y%m%d'),
            rnd=''.join(random.choices(string.ascii_lowercase, k=5))
        )

        families = families or self.families
        workspace_name = (
            # Workspace name parameter resolution priority:
            # 1. the task run parameter
            workspace_name or
            # 2. the task parameter (set on constructor)
            self.workspace_name or
            # 3. the context value (set on a prefect context)
            context.get('workspace_name', None) or
            # 4. a random fallback name
            random_name
        )
        description = description or self.description

        # Check if the requested workspace already exists
        workspaces, total = helpers.workspace.list_(self.client, name=workspace_name)
        if total == 0:
            # There was no workspace with such name, create it
            # This function will block until the workspace is initialized
            details = helpers.workspace.create(self.client, workspace_name, description,
                                               families, temporary, wait=True)
            # After initialization of a workspace, it can be INVALID, which
            # means that something went wrong
            if details.status != 'READY':
                raise signals.FAIL('Workspace failed to initialize')
            return details.id

        elif total == 1:
            if not self.exist_ok:
                raise signals.FAIL('Workspace already exists')
            # There is exactly one workspace with that name, verify its
            # metadata families and versions. If the requirements are met,
            # return the id
            details = workspaces[0]
            self._verify_workspace_requirements(details, families)

            return details['id']

        else:
            # There are many results. For the moment, fail. Maybe in the future
            # we could guess the right workspace
            raise signals.FAIL('Several workspaces found with the same name')

    def _verify_workspace_requirements(self, workspace, families):
        """ Check that an existing workspace family mets the required families

        Parameters
        ----------
        workspace: dict
            Dictionary representation of workspace details.
        families: dict
            Dictionary of family to version number with the required metadata
            families and versions. A ``None`` value means `"latest"`.

        Returns
        -------
        None

        Raises
        ------
        prefect.signals.PrefectStateSignal
            A :py:ref:`prefect.signals.FAIL` signal when the verification fails.

        """
        for name, version in families.items():
            if name not in workspace['families']:
                raise signals.FAIL('Workspace exists but does not have '
                                   'the required families')
            # version == None means that we want the latest.
            # No check is done but we could implement something more strict later
            if version is not None and version > families[name]:
                raise signals.FAIL('Workspace does not meet family version '
                                   'requirement')


class _WorkspaceOperation(QuetzalBaseTask):

    _known_operations = dict(
        commit=helpers.workspace.commit,
        scan=helpers.workspace.scan,
        delete=helpers.workspace.delete,
    )

    def __init__(self, operation: str, **kwargs):
        if operation not in _WorkspaceOperation._known_operations:
            raise ValueError(f'Invalid workspace operation "{operation}"')
        super().__init__(**kwargs)
        self._operation = operation

    def run(self, workspace_id: str) -> int:
        function = _WorkspaceOperation._known_operations[self._operation]
        details = function(self.client, wid=workspace_id, wait=True)
        return details.id


CommitWorkspace = functools.partial(_WorkspaceOperation, 'commit')
CommitWorkspace.__doc__ = """Commit the metadata and new files on a Quetzal workspace"""

ScanWorkspace = functools.partial(_WorkspaceOperation, 'scan')
ScanWorkspace.__doc__ = """Update the metadata view of a Quetzal workspace"""

DeleteWorkspace = functools.partial(_WorkspaceOperation, 'delete')
DeleteWorkspace.__doc__ = """Delete a workspace"""
