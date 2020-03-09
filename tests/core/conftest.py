import prefect
import pytest

from iguazu.core.files import LocalURL


@pytest.fixture(scope='function')
def temp_url(tmpdir):
    url = LocalURL(path=tmpdir)
    with prefect.context(temp_url=url):
        yield url
