class Question:
    def __init__(self, field_ref, reverse, value_map):
        self.field_ref = field_ref
        self.reverse = reverse
        self.value_map = value_map


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
