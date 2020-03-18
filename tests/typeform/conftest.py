import copy
import random
import string

import pytest


@pytest.fixture(scope='function')
def form_template():
    random_id = ''.join(random.choices(string.ascii_letters, k=6))
    return {
        '_links': {},            # not used
        'id': random_id,
        'hidden': ['id'],
        'logic': {},             # not used
        'title': f'random template for unit tests form {random_id}',
        'settings': {},          # not used
        'thankyou_screens': {},  # not used
        'welcome_screens': {},   # not used
        'theme': {},             # not used
        'variables': {},         # not used
        'workspace': {},         # not used
        'fields': [],            # to be filled by another fixture
    }


@pytest.fixture(scope='function')
def form_with_group(form_template):
    form = copy.deepcopy(form_template)
    nested_fields = [
        {
            'id': 'nested1',
            'ref': 'ref_nested1',
            'title': 'nested 1',
            'type': 'multiple_choice',
            'properties': {
                'choices': [
                    {'id': 'choice1', 'ref': 'ref_choice1', 'label': 'Jamais'},
                    {'id': 'choice2', 'ref': 'ref_choice2', 'label': '1 à 2 fois'},
                    {'id': 'choice3', 'ref': 'ref_choice3', 'label': '1 fois par semaine'},
                    {'id': 'choice4', 'ref': 'ref_choice4', 'label': '2-3 fois par semaine'},
                    {'id': 'choice5', 'ref': 'ref_choice5', 'label': 'Presque tous les jours'},
                    {'id': 'choice6', 'ref': 'ref_choice6', 'label': 'Tous les jours'},
                ]
            }
        },
        {
            'id': 'nested2',
            'ref': 'ref_nested2',
            'title': 'nested 2',
            'type': 'multiple_choice',
            'properties': {
                'choices': [
                    {'id': 'choice7', 'ref': 'ref_choice7', 'label': 'Jamais'},
                    {'id': 'choice8', 'ref': 'ref_choice8', 'label': '1 à 2 fois'},
                    {'id': 'choice9', 'ref': 'ref_choice9', 'label': '1 fois par semaine'},
                    {'id': 'choicea', 'ref': 'ref_choicea', 'label': '2-3 fois par semaine'},
                    {'id': 'choiceb', 'ref': 'ref_choiceb', 'label': 'Presque tous les jours'},
                    {'id': 'choicec', 'ref': 'ref_choicec', 'label': 'Tous les jours'},
                ]
            }
        }
    ]
    form['fields'] = [
        {
            'id': 'group1',
            'ref': 'ref_group1',
            'type': 'group',
            'properties': {
                'fields': nested_fields,
            },
        }
    ]
    return form


@pytest.fixture(scope='function')
def form_with_scale(form_template):
    form = copy.deepcopy(form_template)
    form['fields'] = [
        {
            'id': 'scale1',
            'ref': 'ref_scale1',
            'type': 'opinion_scale',
            'properties': {
                'start_at_one': True,
                'steps': 11,
            }
        },
        {
            'id': 'scale2',
            'ref': 'ref_scale2',
            'type': 'opinion_scale',
            'properties': {
                'start_at_one': False,
                'steps': 5,
            }
        },
        {
            'id': 'scale3',
            'ref': 'ref_scale3',
            'type': 'opinion_scale',
            'properties': {
                'start_at_one': True,
                'steps': 5,
            }
        }
    ]
    return form


@pytest.fixture(scope='function')
def form(form_template, form_with_group, form_with_scale):
    form = copy.deepcopy(form_template)
    form['fields'] = form_with_group['fields'] + form_with_scale['fields']
    return form


@pytest.fixture(scope='function')
def response():
    random_id = ''.join(random.choices(string.ascii_letters, k=6))
    return {
        'response_id': random_id,
        'answers': [
            {
                'field': {'id': 'nested1', 'ref': 'ref_nested1', 'type': 'multiple_choice'},
                'type': 'choice',
                'choice': {'label': '1 à 2 fois'},
            },
            {
                'field': {'id': 'neste2', 'ref': 'ref_nested2', 'type': 'multiple_choice'},
                'type': 'choice',
                'choice': {'label': 'Tous les jours'},
            },
            {
                'field': {'id': 'scale1', 'ref': 'ref_scale1', 'type': 'opinion_scale'},
                'type': 'number',
                'number': 2,
            },
            {
                'field': {'id': 'scale2', 'ref': 'ref_scale2', 'type': 'opinion_scale'},
                'type': 'number',
                'number': 0,
            },
            {
                'field': {'id': 'scale3', 'ref': 'ref_scale3', 'type': 'opinion_scale'},
                'type': 'number',
                'number': 5,
            }
        ]
    }


@pytest.fixture(scope='function')
def form_config_sums(tmp_path):
    contents = """\
definitions:
  maps:
    occurrence:
      "Jamais": 0
      "1 à 2 fois": 1
      "1 fois par semaine": 2
      "2-3 fois par semaine": 3
      "Presque tous les jours": 4
      "Tous les jours": 5

domains:
  - name: domain_one
    operation: sum
    dimensions:
    - name: dimension_one
      operation: sum
      questions:
        - field_ref: ref_nested1
          value_map:
            $ref: '#/definitions/maps/occurrence'
          reverse: false
        - field_ref: ref_nested2
          value_map:
            $ref: '#/definitions/maps/occurrence'
          reverse: false
    - name: dimension_two
      operation: sum
      questions:
        - field_ref: ref_scale1
        - field_ref: ref_scale2
        - field_ref: ref_scale3
"""
    from iguazu.functions.typeform.schemas import ConfigurationSchema, load_config
    file = tmp_path / 'form_config_sums.yaml'
    with file.open('w') as f:
        f.write(contents)
    config_obj = load_config(file)
    return ConfigurationSchema().load(config_obj)


@pytest.fixture(scope='function')
def form_config_sums_reversed(tmp_path):
    contents = """\
definitions:
  maps:
    occurrence:
      "Jamais": 0
      "1 à 2 fois": 1
      "1 fois par semaine": 2
      "2-3 fois par semaine": 3
      "Presque tous les jours": 4
      "Tous les jours": 5

domains:
  - name: domain_one
    operation: sum
    dimensions:
    - name: dimension_one
      operation: sum
      questions:
        - field_ref: ref_nested1
          value_map:
            $ref: '#/definitions/maps/occurrence'
          reverse: true
        - field_ref: ref_nested2
          value_map:
            $ref: '#/definitions/maps/occurrence'
          reverse: true
    - name: dimension_two
      operation: sum
      questions:
        - field_ref: ref_scale1
          reverse: true
        - field_ref: ref_scale2
          reverse: true
        - field_ref: ref_scale3
          reverse: true
"""
    from iguazu.functions.typeform.schemas import ConfigurationSchema, load_config
    file = tmp_path / 'form_config_sums_reversed.yaml'
    with file.open('w') as f:
        f.write(contents)
    config_obj = load_config(file)
    return ConfigurationSchema().load(config_obj)


@pytest.fixture(scope='function')
def form_config_means(tmp_path):
    contents = """\
    definitions:
      maps:
        occurrence:
          "Jamais": 0
          "1 à 2 fois": 1
          "1 fois par semaine": 2
          "2-3 fois par semaine": 3
          "Presque tous les jours": 4
          "Tous les jours": 5

    domains:
      - name: domain_one
        operation: mean
        dimensions:
        - name: dimension_one
          operation: mean
          questions:
            - field_ref: ref_nested1
              value_map:
                $ref: '#/definitions/maps/occurrence'
              reverse: false
            - field_ref: ref_nested2
              value_map:
                $ref: '#/definitions/maps/occurrence'
              reverse: false
        - name: dimension_two
          operation: mean
          questions:
            - field_ref: ref_scale1
            - field_ref: ref_scale2
            - field_ref: ref_scale3
    """
    from iguazu.functions.typeform.schemas import ConfigurationSchema, load_config
    file = tmp_path / 'form_config_means.yaml'
    with file.open('w') as f:
        f.write(contents)
    config_obj = load_config(file)
    return ConfigurationSchema().load(config_obj)


@pytest.fixture(scope='function')
def form_config_means_reversed(tmp_path):
    contents = """\
definitions:
  maps:
    occurrence:
      "Jamais": 0
      "1 à 2 fois": 1
      "1 fois par semaine": 2
      "2-3 fois par semaine": 3
      "Presque tous les jours": 4
      "Tous les jours": 5

domains:
  - name: domain_one
    operation: mean
    dimensions:
    - name: dimension_one
      operation: mean
      questions:
        - field_ref: ref_nested1
          value_map:
            $ref: '#/definitions/maps/occurrence'
          reverse: true
        - field_ref: ref_nested2
          value_map:
            $ref: '#/definitions/maps/occurrence'
          reverse: true
    - name: dimension_two
      operation: mean
      questions:
        - field_ref: ref_scale1
          reverse: true
        - field_ref: ref_scale2
          reverse: true
        - field_ref: ref_scale3
          reverse: true
"""
    from iguazu.functions.typeform.schemas import ConfigurationSchema, load_config
    file = tmp_path / 'form_config_means_reversed.yaml'
    with file.open('w') as f:
        f.write(contents)
    config_obj = load_config(file)
    return ConfigurationSchema().load(config_obj)


@pytest.fixture(params=['form_config_sums', 'form_config_sums_reversed'])
def form_config_all_sums(request):
    # "Meta" fixture as shown in
    # https://github.com/pytest-dev/pytest/issues/349#issuecomment-189370273
    # but updated to use the newer function getfixturevalue
    return request.getfixturevalue(request.param)


@pytest.fixture(params=['form_config_means', 'form_config_means_reversed'])
def form_config_all_means(request):
    # "Meta" fixture as shown in
    # https://github.com/pytest-dev/pytest/issues/349#issuecomment-189370273
    # but updated to use the newer function getfixturevalue
    return request.getfixturevalue(request.param)

