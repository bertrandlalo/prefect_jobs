# -*- coding: utf-8 -*-
from marshmallow import (
    fields, post_dump, post_load, Schema, validates, ValidationError
)

from iguazu.functions.typeform.models import (
    Configuration, Dimension, Domain, Question
)


class OrderedFieldsMixin:
    @post_dump
    def reorder_keys(self, data, **kwargs):
        declared_fields = getattr(self, 'declared_fields', {})
        for field in declared_fields:
            if field in data:
                data[field] = data.pop(field)
        return data


class QuestionSchema(Schema, OrderedFieldsMixin):
    field_ref = fields.String(required=True)
    reverse = fields.Boolean(required=False, missing=False, default=False)
    value_map = fields.Dict(required=False, missing=None, default=None)

    @post_load
    def make_question(self, data, **kwargs):
        return Question(**data)

    @post_dump
    def remove_defaults(self, data, **kwargs):
        if data['value_map'] is None:
            del data['value_map']
        if not data['reverse']:
            del data['reverse']
        return data


class DimensionSchema(Schema, OrderedFieldsMixin):
    name = fields.String(required=True)
    operation = fields.String(required=False, default='sum', missing='sum')
    reverse = fields.Boolean(required=False, missing=False, default=False)
    questions = fields.Nested(QuestionSchema, many=True)

    @validates('operation')
    def validate_operation(self, value):
        if value not in ('sum', 'mean'):
            raise ValidationError('operation must be one of "sum" or "mean"')

    @post_load
    def make_dimension(self, data, **kwargs):
        return Dimension(**data)

    @post_dump
    def remove_defaults(self, data, **kwargs):
        if not data['reverse']:
            del data['reverse']
        return data


class DomainSchema(Schema, OrderedFieldsMixin):
    name = fields.String(required=True)
    operation = fields.String(required=False, default='sum', missing='sum')
    dimensions = fields.Nested(DimensionSchema, many=True)

    @validates('operation')
    def validate_operation(self, value):
        if value not in ('sum', 'mean'):
            raise ValidationError('operation must be one of "sum" or "mean"')

    @post_load
    def make_domain(self, data, **kwargs):
        return Domain(**data)


class ConfigurationSchema(Schema, OrderedFieldsMixin):
    definitions = fields.Dict(required=False)
    domains = fields.Nested(DomainSchema, many=True)

    @post_load
    def make_configuration(self, data, **kwargs):
        return Configuration(**data)


__all__ = [
    'ConfigurationSchema', 'DimensionSchema', 'DomainSchema', 'QuestionSchema',
]


def generic_test(schema_cls, example):
    import json
    import sys
    import yaml

    schema = schema_cls()
    try:
        instance = schema.load(example)
    except ValidationError as err:
        print('Validation error:', err.messages)
        return

    print('Loaded instance:', instance)
    print('Dumped instance:', schema.dump(instance))
    print('Dumped instance (json):', json.dumps(schema.dump(instance), indent=2, ensure_ascii=False), sep='\n')
    print('Dumped instance (yaml):')
    yaml.safe_dump(schema.dump(instance), stream=sys.stdout, allow_unicode=True, default_flow_style=False,
                   sort_keys=False)


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


def test_config():
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


def unref(obj):
    """ Resolve JsonRef objects in `obj` """
    import jsonref
    if isinstance(obj, jsonref.JsonRef):
        obj = dict(obj)
    elif isinstance(obj, dict):
        for key in obj:
            obj[key] = unref(obj[key])
    elif isinstance(obj, list):
        for i in range(len(obj)):
            obj[i] = unref(obj[i])
    return obj


def test_real_config():
    import io
    import json
    import jsonref
    import yaml
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
    obj = yaml.safe_load(io.StringIO(config_text))
    obj = unref(jsonref.loads(json.dumps(obj)))
    generic_test(ConfigurationSchema, obj)


if __name__ == '__main__':
    test_question()
    test_dimension()
    test_domain()
    test_config()
    test_real_config()
