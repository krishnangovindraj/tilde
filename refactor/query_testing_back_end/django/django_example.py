from typing import Iterable
from problog.logic import Term

from refactor.tilde_essentials.example import Example

from refactor.representation.example import ExampleWrapper
from refactor.query_testing_back_end.django.clause_handling import ClauseWrapper
from refactor.query_testing_back_end.django.django_wrapper.ClauseWrapper import ConversionException


# TODO: Efficiency hacks. Django might have ways of incrementally extending locked clauses.
class DjangoExample(Example):
    """
    Container class for an example, storing its data and label (types undefined)

    """
    def __init__(self, data: Iterable[Term], label, classification_term: Term = None, lock_external=True):
        self.external_rep = ClauseWrapper(clause_id=None)

        if classification_term is not None:
            self.external_representation.add_literal_as_head(classification_term)
            # self.external_rep.add_literal_to_body(~classification_term) # Does not work
        
        super().__init__(data, label, classification_term)
        if lock_external:
            self.external_representation.lock_adding_to_clause() # We need this. Things don't work without it. Bad news for the rules.
        
    def destruct(self):
        self.external_rep.destruct()

    def add_facts(self, facts):
        if self.external_rep.is_locked:
            raise ConversionException("Adding to a locked clause is not allowed. Please use the extend method")
        super().add_facts(facts)

        for fact in facts:  # type: Term
            self.external_rep.add_literal_to_body(fact)
            # TODO: Do we want this, given we have an equivalent representation right here? It's redundant but doesn't break anything
            # self.external_rep.add_problog_clause(fact)

    def clone(self):
        return DjangoExample(self.data, self.label, self.classification_term, False)

    def lock_example(self):
        self.external_rep.lock_adding_to_clause()

    def extension_context(self):
        return DjangoExample.DjangoExampleExtender(self)

    @property
    def external_representation(self):
        return self.external_rep

    class DjangoExampleExtender:
        def __init__(self, example: 'DjangoExample'):
            self._example = example

        def __enter__(self):
            new_clause = ClauseWrapper(clause_id=None)
            if self._example.classification_term is not None:
                new_clause.add_literal_as_head(self._example.classification_term)

            for fact in self._example.data:
                new_clause.add_literal_to_body(fact)

            old_clause = self._example.external_rep
            self._example.external_rep = new_clause
            old_clause.destruct()
            return self

        def __exit__(self, exc_type, exc_value, traceback):
            if exc_type is not None or exc_value is not None or traceback is not None:
                raise ConversionException('DjangoExampleExtender encountered an exception', exc_value)

            self._example.external_rep.lock_adding_to_clause()

        def extend(self, facts: Iterable[Term]):
            self._example.add_facts(facts)