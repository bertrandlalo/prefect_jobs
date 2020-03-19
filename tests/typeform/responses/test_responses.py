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


@pytest.fixture(scope='function')
def vr_features(vr_form, vr_response):
    form_id = 'HoS3mL'
    config = get_form_config(form_id)
    features = config.collect_features(vr_form, vr_response)
    return features


def test_vr_questionnaire_dimension_features(vr_features):
    features = vr_features

    assert features['inhibitory_anxiety']['value'] == 1 + 2 + 3 + 3 + 2
    assert features['prospective_anxiety']['value'] == 2 + 2 + 1 + 1 + 1 + 2 + 3
    assert features['avoidance_coping']['value'] == 5 + 5 + 3
    assert features['emotional_support_seeking']['value'] == 5 + 5 + 4 + 3 + 3
    assert features['instrumental_support_seeking']['value'] == 5 + 5 + 4 + 5 + 3 + 6 + 4 + 6
    assert features['preventive_coping']['value'] == 4 + 4 + 2 + 2 + 3 + 2 + 3 + 2 + 4 + 5
    # Next feature has 3 reversed questions:            *                           *               *
    assert features['proactive_coping']['value'] == 5 + 2 + 5 + 6 + 6 + 5 + 3 + 6 + 3 + 5 + 5 + 5 + 2 + 4
    assert features['reflective_coping']['value'] == 6 + 6 + 6 + 5 + 4 + 4 + 4 + 4 + 4 + 3 + 3
    assert features['strategic_coping']['value'] == 5 + 3 + 6 + 6
    # Next feature has 3 reversed questions:      *       *   *
    assert features['engagement']['value'] == 5 + 6 + 6 + 5 + 6
    # Next feature has 1 reversed question:        *
    assert features['flexibility']['value'] == 6 + 6 + 6 + 6
    # Next feature has 2 reversed questions:         *                   *
    assert features['novelty_producing']['value'] == 4 + 3 + 4 + 7 + 4 + 4
    # Next feature has 2 reversed questions:           *   *
    assert features['novelty_seeking']['value'] == 5 + 3 + 3 + 6 + 6 + 6
    # Next 3 features use value maps
    assert features['emotional_well-being']['value'] == 4 + 4 + 3
    assert features['psychological_well-being']['value'] == 2 + 3 + 3 + 3 + 4 + 1
    assert features['social_well-being']['value'] == 1 + 4 + 3 + 2 + 3
    assert features['autonomy']['value'] == 5 + 5 + 6 + 6
    assert features['competence']['value'] == 5 + 4 + 5 + 4
    assert features['relatedness']['value'] == 4 + 4 + 5 + 3
    assert features['life_of_engagement']['value'] == 3 + 5 + 4 + 5 + 3 + 4
    assert features['life_of_meaning']['value'] == 4 + 3 + 5 + 5 + 4 + 5
    assert features['life_of_pleasure']['value'] == 4 + 5 + 1 + 2 + 2 + 3
    assert features['disengagement']['value'] == 2 + 2 + 3 + 4
    assert features['humanity']['value'] == 4 + 5 + 3 + 2
    assert features['indifference']['value'] == 3 + 2 + 2 + 4
    assert features['kindness']['value'] == 4 + 3 + 3 + 4
    assert features['others_mindfullness']['value'] == 4 + 3 + 5 + 4
    assert features['separation']['value'] == 1 + 2 + 4 + 3
    assert features['negative_activation']['value'] == 3 + 3 + 3 + 3 + 2
    assert features['negative_duration']['value'] == 5 + 4 + 3 + 4 + 4
    assert features['negative_intensity']['value'] == 2 + 3 + 2 + 2 + 2
    assert features['positive_activation']['value'] == 4 + 3 + 5 + 4 + 4
    assert features['positive_duration']['value'] == 3 + 3 + 4 + 4 + 5
    assert features['positive_intensity']['value'] == 5 + 4 + 4 + 5 + 4
    assert features['common_humanity']['value'] == 3 + 2
    assert features['isolation']['value'] == 4 + 2
    assert features['over_identified']['value'] == 2 + 3
    assert features['self_judgment']['value'] == 2 + 4
    assert features['self_kindness']['value'] == 3 + 2
    assert features['self_mindfullness']['value'] == 3 + 4
    assert features['self_efficacity']['value'] == 5 + 3 + 4 + 5 + 4 + 4 + 6 + 6 + 6 + 5


def test_vr_questionnaire_domain_features():
    pass
