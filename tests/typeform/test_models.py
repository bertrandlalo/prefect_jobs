from iguazu.functions.typeform.models import Question


def test_question_range_with_value_map(form_with_group):
    value_map = {
        "Jamais": -100,
        "1 à 2 fois": 1,
        "1 fois par semaine": 2,
        "2-3 fois par semaine": 3,
        "Presque tous les jours": 4,
        "Tous les jours": +100,
    }
    question = Question(
        field_ref='ref_nested1',
        reverse=False,
        value_map=value_map,
    )
    qrange = question.get_range(form_with_group)
    assert qrange == (-100, +100)


def test_question_range(form_with_scale):
    qrange1 = Question(field_ref='ref_scale1', reverse=False, value_map=None).get_range(form_with_scale)
    qrange2 = Question(field_ref='ref_scale2', reverse=False, value_map=None).get_range(form_with_scale)
    qrange3 = Question(field_ref='ref_scale3', reverse=False, value_map=None).get_range(form_with_scale)

    assert qrange1 == (1, 11)
    assert qrange2 == (0, 4)
    assert qrange3 == (1, 5)


def test_question_range_reverse(form_with_scale):
    qrange1 = Question(field_ref='ref_scale1', reverse=True, value_map=None).get_range(form_with_scale)
    qrange2 = Question(field_ref='ref_scale2', reverse=True, value_map=None).get_range(form_with_scale)
    qrange3 = Question(field_ref='ref_scale3', reverse=True, value_map=None).get_range(form_with_scale)

    assert qrange1 == (1, 11)
    assert qrange2 == (0, 4)
    assert qrange3 == (1, 5)


def test_question_value_with_value_map(form_with_group, response):
    value_map = {
        "1 à 2 fois": 1,
        "Tous les jours": 5,
    }
    value1 = Question(
        field_ref='ref_nested1',
        reverse=False,
        value_map=value_map).get_value(form_with_group, response)
    value2 = Question(
        field_ref='ref_nested2',
        reverse=False,
        value_map=value_map).get_value(form_with_group, response)
    assert value1 == 1
    assert value2 == 5


def test_question_value_with_value_map_reversed(form_with_group, response):
    value_map = {
        "Jamais": 0,
        "1 à 2 fois": 1,
        "1 fois par semaine": 2,
        "2-3 fois par semaine": 3,
        "Presque tous les jours": 4,
        "Tous les jours": 5,
    }
    value1 = Question(
        field_ref='ref_nested1',
        reverse=True,
        value_map=value_map).get_value(form_with_group, response)
    value2 = Question(
        field_ref='ref_nested2',
        reverse=True,
        value_map=value_map).get_value(form_with_group, response)
    assert value1 == 4
    assert value2 == 0


def test_question_value(form_with_scale, response):
    value1 = Question(
        field_ref='ref_scale1',
        reverse=False,
        value_map=None).get_value(form_with_scale, response)
    value2 = Question(
        field_ref='ref_scale2',
        reverse=False,
        value_map=None).get_value(form_with_scale, response)
    value3 = Question(
        field_ref='ref_scale3',
        reverse=False,
        value_map=None).get_value(form_with_scale, response)
    assert value1 == 2
    assert value2 == 0
    assert value3 == 5


def test_question_value_reversed(form_with_scale, response):
    value1 = Question(
        field_ref='ref_scale1',
        reverse=True,
        value_map=None).get_value(form_with_scale, response)
    value2 = Question(
        field_ref='ref_scale2',
        reverse=True,
        value_map=None).get_value(form_with_scale, response)
    value3 = Question(
        field_ref='ref_scale3',
        reverse=True,
        value_map=None).get_value(form_with_scale, response)
    assert value1 == 10
    assert value2 == 4
    assert value3 == 1
