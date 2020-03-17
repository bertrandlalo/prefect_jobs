# These tests were created, in most cases, as code to test the
# serialization/deserialization of typeform/iguazu schemas
# You can check the output with
# pytest -o log_cli=true -o log_cli_level=DEBUG -sv tests/typeform/test_schemas.py

import io
import json
import logging

import yaml

from iguazu.functions.typeform.schemas import (
    ConfigurationSchema, DimensionSchema, DomainSchema, QuestionSchema,
    load_config
)

logger = logging.getLogger(__name__)


def generic_test(schema_cls, example):
    schema = schema_cls()
    instance = schema.load(example)

    logger.debug('Loaded instance: %s', instance)
    logger.debug('Dumped instance:\n%s', schema.dump(instance))
    logger.debug('Dumped instance (json):\n%s', json.dumps(schema.dump(instance), indent=2, ensure_ascii=False))
    stream = io.StringIO()
    yaml.safe_dump(schema.dump(instance), stream=stream,
                   allow_unicode=True, default_flow_style=False, sort_keys=False)
    stream.flush()
    stream.seek(0)
    logger.debug('Dumped instance (yaml):\n%s', stream.read())


def test_question():
    question_example = {
        'field_ref': "xyz123",
        'value_map': {
            'never': 0,
            'sometimes': 1,
            'always': 2,
            "1 à 2 fois": 3,
        },
    }
    generic_test(QuestionSchema, question_example)


def test_dimension():
    dimension_example = {
        'name': 'some_dimension_name',
        'questions': [
            {'field_ref': "xyz123"},
            {'field_ref': "abc000", "reverse": True},
        ],
    }
    generic_test(DimensionSchema, dimension_example)


def test_domain():
    domain_example = {
        'name': 'some_domain_name',
        'dimensions': [
            {
                'name': 'some_dimension_name',
                'questions': [
                    {'field_ref': "xyz123"},
                    {'field_ref': "abc000", "reverse": True},
                ],
                'operation': 'mean',
            },
            {
                'name': 'another_dimension_name',
                'questions': [
                    {'field_ref': "foo", 'reverse': True},
                    {'field_ref': "bar", "reverse": False},
                ],
                'reverse': True
            }
        ]
    }
    generic_test(DomainSchema, domain_example)


def test_dict_config():
    example_config = {
        'definitions': {'foo': 'bar'},
        'domains': [
            {
                'name': 'some_domain_name',
                'dimensions': [
                    {
                        'name': 'some_dimension_name',
                        'questions': [
                            {'field_ref': "xyz123"},
                            {'field_ref': "abc000", "reverse": True},
                        ],
                        'operation': 'mean',
                    },
                    {
                        'name': 'another_dimension_name',
                        'questions': [
                            {'field_ref': "foo", 'reverse': True},
                            {'field_ref': "bar", "reverse": False},
                        ],
                        'reverse': True
                    }
                ]
            },
            {
                'name': 'some_other_domain_name',
                'dimensions': [
                    {
                        'name': 'first_dimension',
                        'questions': [
                            {'field_ref': "ref1"},
                            {'field_ref': "ref2"},
                        ],
                        'operation': 'mean',
                    },
                    {
                        'name': 'second_dimensions',
                        'operation': 'sum',
                        'questions': [
                            {'field_ref': "ref3", 'reverse': True},
                            {'field_ref': "ref4", "reverse": False},
                        ],
                        'reverse': True
                    }
                ]
            }
        ]
    }
    generic_test(ConfigurationSchema, example_config)


def test_file_config(tmp_path):
    config_text = """\
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
  - name: mental_health
    operation: mean
    dimensions:
    - name: emotional_well-being
      operation: sum
      questions:
        - field_ref: 47373e16dfeb7d01
          value_map:
            $ref: '#/definitions/maps/occurrence'
          reverse: false
        - field_ref: e53f0bc7317e6995
          value_map:
            $ref: '#/definitions/maps/occurrence'
          reverse: false
        - field_ref: 7758bec371913adb
          value_map:
            $ref: '#/definitions/maps/occurrence'
          reverse: false
    - name: social_well-being
      operation: sum
      questions:
        - field_ref: 3e01e3861f317b64
        - field_ref: ddc572070aeec689
        - field_ref: f109c3f45764ab61
        - field_ref: 3c22d6b5c5394e79
        - field_ref: 057b82c2e4dde124
    """
    file = tmp_path / 'config.yaml'
    with file.open('w') as f:
        f.write(config_text)
    obj = load_config(file)
    generic_test(ConfigurationSchema, obj)
