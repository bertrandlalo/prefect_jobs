import pytest

from iguazu.functions.typeform.schemas import get_form_config


@pytest.fixture(scope='function')
def sandbox_features(sandbox_form, sandbox_response):
    form_id = 's1JOxF'
    config = get_form_config(form_id)
    features = config.collect_features(sandbox_form, sandbox_response)
    return features


def test_sandbox_dimension_features(sandbox_features):
    features = sandbox_features

    assert features['art']['value'] == 4 + 4           # black==4 by value map and jojo rabbit rating
    assert features['bilingual']['value'] == 1         # boolean question: yes
    assert features['math']['value'] == 4              # math question: 1+1+1+1
    assert features['fayot']['value'] == 8             # rate this questionnaire
    assert features['agrees']['value'] == 1            # legal (agree to this questionnaire)
    # sum of several numerical questions, two of them reversed
    assert features['numerical']['value'] == 4 + 3 + 54
    # mean of several questions, two of them with value maps
    assert features['tastes']['value'] == (0 + 1 + 4) / 3


def test_sandbox_domain_features(sandbox_features):
    features = sandbox_features

    assert features['culture']['value'] == 8               # mean of a single dimension
    assert features['skills']['value'] == (1 + 4 + 8) / 3  # mean of three dimensions
    assert features['ethics']['value'] == 1                # sum of single dimension
    assert features['profile']['value'] == (5 / 3 + 61)    # sum of two dimensions
