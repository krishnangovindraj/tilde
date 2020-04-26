from typing import Iterable
from typing import Iterable
from problog.logic import Term

from refactor.representation.example import ExampleWrapper
from refactor.tilde_essentials.example import Example

class SubtleExample(Example):
    
    def __init__(self, data: Iterable[Term], label, classification_term: Term = None):
        # TODO: Is this right?
        self._external_rep = SubtleExample.fact_to_str(~classification_term) if classification_term is not None else ''
        super().__init__(data, label, classification_term)

    def _add_facts_to_external_representation(self, facts: Iterable[Term]):
        if len(self.external_representation) > 0:
            self._external_rep += ', '
        self._external_rep +=  ', '.join(map(SubtleExample.fact_to_str, facts))

    def clone(self):
        return SubtleExample(self.data, self.label, self.classification_term)

    @property
    def external_representation(self):
        return self._external_rep

    @staticmethod
    def fact_to_str(fact: Term):
        return str(fact)