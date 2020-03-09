import prefect
import pytest

from iguazu.core.files import LocalURL


@pytest.fixture(scope='function')
def temp_url(tmpdir):
    """Create a temporary LocalURL file and set a prefect context

    This avoids doing doing ``with prefect.context(temp_url=...):``
    """
    url = LocalURL(path=tmpdir)
    with prefect.context(temp_url=url):
        yield url
