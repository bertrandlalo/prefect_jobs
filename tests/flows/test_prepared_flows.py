import pytest

from iguazu.core.flows import REGISTRY


@pytest.mark.parametrize('flow_name', list(REGISTRY))
def test_create_flow(flow_name):
    klass = REGISTRY[flow_name]

    assert callable(klass), f'Registry had a non-callable entry for "{flow_name}"'

    # Call the constructor, it should work with the default args
    klass()
