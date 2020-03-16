from typing import Iterable
from problog.logic import Term

from refactor.representation.example import ExampleWrapper
from refactor.tilde_essentials.example import Example

class SubtleExample(Example):
    
    def __init__(self, example: ExampleWrapper, label, is_training):
        self._external_rep = SubtleExample.fact_to_str(~example.classification_term) # TODO: Is this right?
        super().__init__(example, label)

    def add_facts(self, facts: Iterable[Term]):
        new_facts = [f for f in facts if f not in self.data]
        if len(new_facts) > 0:
            super().add_facts(new_facts)
            self._external_rep += ', '
            self._external_rep +=  ', '.join(map(SubtleExample.fact_to_str, new_facts))

    @property
    def external_representation(self):
        return self._external_rep

    @staticmethod
    def fact_to_str(fact: Term):
        return str(fact)