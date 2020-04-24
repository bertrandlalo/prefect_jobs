import logging
import operator
from typing import Dict, List

import numpy as np

from iguazu.functions.typeform.api import get_form_fields, get_response_fields, parse_answer
from iguazu.functions.typeform import TypeformException


logger = logging.getLogger(__name__)


class _Tree:

    def __init__(self, children=None, reducer=None, is_leaf=False):
        self._children = children or []
        self._reducer = reducer or None
        self._is_leaf = is_leaf

    @property
    def reducer(self):
        if self._is_leaf is None:
            raise ValueError('Cannot reduce a leaf')
        operations = {
            'mean': np.mean,
            'sum': np.sum,
        }
        return operations[self._reducer]

    @property
    def is_leaf(self):
        return self._is_leaf

    def traverse(self, order='pre'):
        if self._is_leaf:
            return [self]
        children_traversal = sum([c.traverse() for c in self._children], [])
        if order == 'pre':
            return [self] + children_traversal
        elif order == 'post':
            return children_traversal + [self]
        else:
            raise ValueError('Traversal order must be "pre" or "post"')

    def get_range(self, form):
        mins = []
        maxs = []
        for c in self._children:
            qmin, qmax = c.get_range(form)
            mins.append(qmin)
            maxs.append(qmax)
        try:
            return self.reducer(mins), self.reducer(maxs)
        except TypeError:
            logger.error('Encountered a type error. Check how your form handles '
                         'the questions in %s. This often happens when one of '
                         'the questions is not handled correctly by a value map or '
                         'it is not possible to convert it to a numeric value.',
                         self)
            raise

    def get_value(self, form, response):
        vals = [c.get_value(form, response) for c in self._children]
        try:
            return self.reducer(vals)
        except TypeError:
            logger.error('Encountered a type error. Check how your form handles '
                         'the questions in %s. This often happens when one of '
                         'the questions is not handled correctly by a value map or '
                         'it is not possible to convert it to a numeric value.',
                         self)
            raise

    def get_value_dict(self, form, response):
        value = self.get_value(form, response)
        return {
            'type': type(self).__name__,
            'value': value,
        }


class Question(_Tree):
    def __init__(self, field_ref, reverse, value_map):
        super().__init__(children=None, reducer=None, is_leaf=True)
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

    def __str__(self):
        return f'Question<{self.field_ref}{" (reversed)" if self.reverse else ""}>'


class Dimension(_Tree):

    def __init__(self, name, operation, reverse, questions):
        self.name = name
        self.operation = operation
        self.reverse = reverse
        self.questions = questions
        super().__init__(self.questions, self.operation)

    def __str__(self):
        return f'Dimension<{self.name} ({len(self.questions)} questions){" (reversed)" if self.reverse else ""}>'


class Domain(_Tree):
    def __init__(self, name, operation, dimensions):
        self.name = name
        self.operation = operation
        self.dimensions = dimensions
        super().__init__(self.dimensions, self.operation)

    def __str__(self):
        return f'Domain<{self.name} ({len(self.dimensions)} questions){" (reversed)" if self.reverse else ""}>'


class Configuration(_Tree):
    def __init__(self, domains, definitions=None):
        self.domains = domains
        self.definitions = definitions
        super().__init__(children=self.domains, reducer=None, is_leaf=False)

    def collect_features(self, form, response) -> Dict:
        children_nodes = [
            node
            for node in self.traverse(order='pre')[1:]  # note that 1: drops self
            if not node.is_leaf
        ]
        names = map(operator.attrgetter('name'), children_nodes)
        values = map(lambda node: node.get_value_dict(form, response), children_nodes)
        features = dict(zip(names, values))
        return features

