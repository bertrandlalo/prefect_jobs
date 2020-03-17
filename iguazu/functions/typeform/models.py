import logging

from iguazu.functions.typeform.api import get_form_fields, get_response_fields, parse_answer
from iguazu.functions.typeform import TypeformException


logger = logging.getLogger(__name__)


class Question:
    def __init__(self, field_ref, reverse, value_map):
        self.field_ref = field_ref
        self.reverse = reverse
        self.value_map = value_map

    def get_value(self, form, response):
        response_id = response['response_id']
        # fields_map = get_form_fields(form)
        answer_map = get_response_fields(response)

        # Obtain response
        if self.field_ref not in answer_map:
            logger.warning('Response %s is missing expected field %s',
                           response_id, self.field_ref)
            raise TypeformException('Response does not have an expected field.')
        answer = answer_map[self.field_ref]
        value = parse_answer(answer)

        # Convert response to value according to value map
        if self.value_map:
            if value not in self.value_map:
                logger.warning('Response %s could not use value map for question %s '
                               'due to missing value %s',
                               response_id, self.field_ref, value)
                raise TypeformException(f'Missing value "{value}" in value map')
            value = self.value_map[value]

        # Manage reverse
        if self.reverse:
            min_value, max_value = self.get_range(form)
            value = min_value + max_value - value

        return value

    def get_range(self, form):
        if self.value_map:
            return min(self.value_map.values()), max(self.value_map.values())

        form_id = form['id']
        fields_map = get_form_fields(form)
        if self.field_ref not in fields_map:
            raise TypeformException(f'Missing field {self.field_ref} on form {form_id}')
        field = fields_map[self.field_ref]
        field_type = field['type']
        if field_type not in ('opinion_scale',):
            raise TypeformException(f'Dont know how to manage a field type {field_type}')
        properties = field['properties']
        min_value = int(properties['start_at_one'])
        max_value = properties['steps'] - int(not properties['start_at_one'])
        return min_value, max_value




class Dimension:
    def __init__(self, name, operation, reverse, questions):
        self.name = name
        self.operation = operation
        self.reverse = reverse
        self.questions = questions


class Domain:
    def __init__(self, name, operation, dimensions):
        self.name = name
        self.operation = operation
        self.dimensions = dimensions


class Configuration:
    def __init__(self, domains, definitions):
        self.domains = domains
        self.definitions = definitions
