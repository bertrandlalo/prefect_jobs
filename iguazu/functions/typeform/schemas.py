# -*- coding: utf-8 -*-
import json
import logging
import pkg_resources
from typing import Dict, List

import jsonref
import yaml
from marshmallow import (
    fields, post_dump, post_load, Schema, validates, ValidationError
)

from iguazu.functions.typeform.models import (
    Configuration, Dimension, Domain, Question
)

logger = logging.getLogger(__name__)


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

    @post_dump
    def remove_defaults(self, data, **kwargs):
        if not data['definitions']:
            del data['definitions']
        return data


def unref(obj):
    """ Resolve JsonRef objects in `obj` """
    if isinstance(obj, jsonref.JsonRef):
        obj = dict(obj)
    elif isinstance(obj, dict):
        for key in obj:
            obj[key] = unref(obj[key])
    elif isinstance(obj, list):
        for i in range(len(obj)):
            obj[i] = unref(obj[i])
    return obj


def collect_errors(error: ValidationError) -> str:
    parts = _collect_errors(error.messages, [])
    return '\n'.join(parts)


def _collect_errors(details: Dict, prefix: List[str]) -> List[str]:
    errors = []
    for key, value in details.items():
        new_prefix = prefix[:]
        if isinstance(key, int):
            new_prefix.append(f'[{key}]')
        elif prefix:
            new_prefix.extend(['.', str(key)])
        else:
            new_prefix.append(str(key))
        new_prefix_str = ''.join(new_prefix)

        if isinstance(value, dict):
            errors.extend(_collect_errors(value, new_prefix))
        elif isinstance(value, list):
            errors.extend([f'{new_prefix_str}: {v}' for v in value])
        else:
            errors.append(f'{new_prefix_str}: {value}')
    return errors


def load_config(file):
    if hasattr(file, 'read'):
        obj_with_refs = yaml.safe_load(file)
    else:
        with open(file, 'r') as f:
            obj_with_refs = yaml.safe_load(f)
    obj_without_refs = unref(jsonref.loads(json.dumps(obj_with_refs)))
    return obj_without_refs


def get_form_config(form_id: str) -> Configuration:
    resource_name = f'forms/{form_id}.yaml'
    logger.debug('Trying to find resource on %s named %s', __name__, resource_name)
    try:
        stream = pkg_resources.resource_stream(__name__, resource_name)
    except FileNotFoundError:
        logger.error('Could not find form configuration for %s', form_id, exc_info=True)
        raise
    config = load_config(stream)
    schema = ConfigurationSchema()

    try:
        instance = schema.load(config)
    except ValidationError as err:
        logger.error('Form configuration is invalid. Validation error details are:\n%s',
                     collect_errors(err))
        raise
    return instance


__all__ = [
    'ConfigurationSchema', 'DimensionSchema', 'DomainSchema', 'QuestionSchema',
    'load_config', 'get_form_config',
]
