from typing import Any, Mapping, List

from prefect import Task
from quetzal.client import QuetzalAPIException, helpers


class QueryTask(Task):
    """ Perform a query on Quetzal and return all its results

    This task uses the :py:ref:`quetzal.client.helpers.query` function to
    perform a SQL query on a Quetzal server and return all its results.

    Typically, this task will be used as one of the first tasks of a flow that
    uses Quetzal as a data source.

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
        self.client = helpers.get_client(url, username, password, insecure)

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
