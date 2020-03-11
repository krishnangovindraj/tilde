from refactor.tilde_essentials.example import Example

from refactor.representation.example import ExampleWrapper
from refactor.query_testing_back_end.django.clause_handling import ClauseWrapper
class DjangoExample(Example):
    """
    Container class for an example, storing its data and label (types undefined)

    """
    # TODO: Krishnan: This is a test update for homogenization. It is nowhere near complete.
    def __init__(self, example: ExampleWrapper, label, is_training):
        #raise NotImplementedError("No. This is a bit too complicated to take on first.")
        self.external_rep = ClauseWrapper(clause_id=None)

        if is_training:
            if hasattr(example, 'classification_term'):
                self.external_rep.add_literal_to_body(example.classification_term)
        
        super().__init__(example, label)
        self.external_rep.lock_adding_to_clause() # TODO: Do we need this?
        
        
    def destruct(self):
        self.external_rep.destruct()

    def add_facts(self, facts):
        super().add_facts(facts)

        for fact in facts:  # type: Term
            self.external_rep.add_literal_to_body(fact)
            # TODO: this: 
            # self.external_rep.add_problog_clause(fact)
    