from typing import Iterable
from problog.logic import Term

from refactor.tilde_essentials.example import Example

from refactor.representation.example import ExampleWrapper
from refactor.query_testing_back_end.django.clause_handling import ClauseWrapper
class DjangoExample(Example):
    """
    Container class for an example, storing its data and label (types undefined)

    """
    def __init__(self, data: Iterable[Term], label, classification_term: Term = None):
        self.external_rep = ClauseWrapper(clause_id=None)

        if classification_term is not None:
            self.external_representation.add_literal_as_head(classification_term)
            # self.external_rep.add_literal_to_body(~classification_term) # Does not work
        
        super().__init__(data, label)
        self.external_rep.lock_adding_to_clause() # We need this. Things don't work without it. Bad news for the rules.
        
        
    def destruct(self):
        self.external_rep.destruct()

    def add_facts(self, facts):
        super().add_facts(facts)

        for fact in facts:  # type: Term
            self.external_rep.add_literal_to_body(fact)
            # TODO: Do we want this, given we have an equivalent representation right here? It's redundant but doesn't break anything
            # self.external_rep.add_problog_clause(fact)

    @property
    def external_representation(self):
        return self.external_rep
