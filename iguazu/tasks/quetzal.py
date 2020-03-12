import copy
import datetime
import functools
import random
import string
from typing import Any, Dict, List, Optional, Union

from prefect import context, Task
from prefect.engine import signals
from quetzal.client import helpers

from iguazu.core.files import QuetzalFile
from iguazu.core.files.quetzal import quetzal_client_from_secret

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
            # self._client = helpers.get_client(**self._client_args)
            self._client = quetzal_client_from_secret()
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

    This task uses the :py:ref:`quetzal.client.helpers` query function to
    perform a SQL query on a Quetzal server and return all its results.

    Typically, this task will be used as one of the first tasks of a flow that
    uses Quetzal as a data source.

    """
    # TODO: In the docstring above,
    #       put back reference to :py:ref:`quetzal.client.helpers.query` when
    #       the quetzal-client documentation includes this documentation.
    #       Check with:
    # python -m sphinx.ext.intersphinx \
    #           https://quetzal-client.readthedocs.io/en/latest/objects.inv

    def __init__(self,
                 as_file_adapter: bool = False,
                 shuffle: bool = False,
                 limit: Optional[int] = None,
                 **kwargs):
        super().__init__(**kwargs)
        self._as_file_adapter = as_file_adapter
        self.limit = limit
        self.shuffle = shuffle

    def run(self,
            query: str,
            dialect: str = 'postgresql',
            workspace_id: Optional[int] = None,
            id_column: Optional[str] = None) -> List[ResultSetType]:
        """ Perform the Quetzal SQL query

        Parameters
        ----------
        query: str
            Quetzal query.
        dialect: str
            Dialect used to express the `query`.
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
        if not query:
            raise signals.FAIL('Query is empty')

        self.logger.info('Querying Quetzal at %s with SQL (dialect %s)=\n%s',
                         self.client.configuration.host,
                         dialect, query)
        rows, total = helpers.query(self.client, workspace_id, query, dialect)

        # Handle results
        self.logger.info('Query gave %d results', total)

        # Shuffle the results
        if self.shuffle:
            random.shuffle(rows)

        # Only keep N results
        if self.limit is not None and total > self.limit:
            rows = rows[:self.limit]
            total = len(rows)
            self.logger.info('Query was limited to %d results', total)

        if self._as_file_adapter:
            for i, row in enumerate(rows):
                rows[i] = QuetzalFile.retrieve(file_id=row['id'], workspace_id=workspace_id)

        return rows


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
            A :py:class:`prefect.signals.FAIL` signal when the verification fails.

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
