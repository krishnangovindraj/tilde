from typing import Iterable
from problog.logic import Term

from refactor.representation.example import ExampleWrapper
from refactor.tilde_essentials.example import Example

class SubtleExample(Example):
    
    def __init__(self, example: ExampleWrapper, label, is_training):
        self._external_rep = ''
        super().__init__(example, label)
    

    def add_facts(self, facts: Iterable[Term]):
        new_facts = [f for f in facts if f not in self.data]
        super().add_facts(facts)
        if len(self._external_rep) > 0 and len(facts) > 0:
            self.external_representation += ', '
        self._external_rep +=  ', '.join(map(SubtleExample.fact_to_str, new_facts))


    @property
    def external_representation(self):
        return self._external_rep

    @staticmethod
    def fact_to_str(fact: Term):
        return str(fact)