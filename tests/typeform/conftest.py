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
            'properties': nested_fields,
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
