import datetime
import random
import string
from typing import Any, Mapping, List, Optional

from prefect import Task
from prefect.engine import signals
from quetzal.client import QuetzalAPIException, helpers


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
                 url: str = None,
                 username: str = None,
                 password: str = None,
                 insecure: bool = False,
                 **kwargs):
        super().__init__(**kwargs)
        self._client = helpers.get_client(url, username, password, insecure)

    @property
    def client(self):
        return self._client

    def run(self) -> None:
        raise RuntimeError('QuetzalBaseTask is an abstract Task')


class QueryTask(QuetzalBaseTask):
    """ Perform a query on Quetzal and return all its results

    This task uses the :py:ref:`quetzal.client.helpers.query` function to
    perform a SQL query on a Quetzal server and return all its results.

    Typically, this task will be used as one of the first tasks of a flow that
    uses Quetzal as a data source.

    """

    def run(self, query: str, workspace_id: int = None) -> List[Mapping[str, Any]]:
        """ Perform the Quetzal SQL query

        Parameters
        ----------
        query: str
            Query in postgreSQL dialect.
        workspace_id: int
            Workspace where the query should be executed. If not set, it uses
            the global workspace.

        Returns
        -------
        results
            A list of dictionaries, one for each result row.

        """
        # TODO: manage username, password et al from context?
        self.logger.debug('Querying Quetzal with SQL=%s', query)
        try:
            results, total = helpers.query(self.client, workspace_id, query)
        except QuetzalAPIException as ex:
            self.logger.warning('Quetzal query task failed: %s', ex.title)
            raise
        self.logger.debug('Query gave %d results', total)
        return results


class CreateWorkspaceTask(QuetzalBaseTask):
    """ Create or retrieve a Quetzal workspace

    Attributes
    ----------
    exist_ok: bool
        When set, this task will retrieve a workspace with the provided name
        if it already exists. When not set and a workspace with the same already
        exists, the task will fail.

    """

    def __init__(self, exist_ok: bool = True, **kwargs):
        super().__init__(**kwargs)
        self.exist_ok = exist_ok  # TODO: decide: should this be here or a run parameter?

    def run(self,
            name: str = None,
            description: str = None,
            families: Mapping[str, Optional[int]] = None,
            temporary: bool = False) -> int:
        """

        Parameters
        ----------
        name: str
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

        families = families or {}
        name = name or 'iguazu-{date}-{rnd}'.format(
            date=datetime.datetime.now().strftime('%Y%m%d'),
            rnd=''.join(random.choices(string.ascii_lowercase, k=5))
        )
        description = description or 'Workspace created by iguazu'

        # Check if the requested workspace already exists
        workspaces, total = helpers.workspace.list_(self.client, name=name)
        if total == 0:
            # There was no workspace with such name, create it
            # This function will block until the workspace is initialized
            details = helpers.workspace.create(self.client, name, description,
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
