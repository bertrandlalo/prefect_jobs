import pytest

from iguazu.functions.typeform.models import Configuration
from iguazu.functions.typeform.schemas import get_form_config


@pytest.mark.parametrize('form_id', ['HoS3mL', 's1JOxF'])
def test_configs(form_id):
    config = get_form_config(form_id)  # should not fail with validation error
    assert isinstance(config, Configuration)
