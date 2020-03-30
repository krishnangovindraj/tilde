from problog.logic import Term
from typing import List

from refactor.tilde_essentials.query_wrapping import QueryWrapper
from refactor.tilde_essentials.evaluation import TestEvaluator
from refactor.representation.example import ExampleWrapper
from refactor.representation.language import TypeModeLanguage
from refactor.query_testing_back_end.django.django_example import DjangoExample
from refactor.query_testing_back_end.django.query_wrapping import DjangoQueryWrapper
try:
    from src.ClauseWrapper import ClauseWrapper, HypothesisWrapper
    from src.subsumption_checking import check_subsumption
except ImportError as err:
    from refactor.query_testing_back_end.django.django_wrapper.ClauseWrapper import ClauseWrapper, HypothesisWrapper
    from refactor.query_testing_back_end.django.django_wrapper.subsumption_checking import check_subsumption

from refactor.representation.TILDE_query import TILDEQuery
from refactor.query_testing_back_end.django.clause_handling import build_hypothesis


class DjangoQueryEvaluator(TestEvaluator):
    def __init__(self, language: TypeModeLanguage):
        super().__init__()
        # This is to prevent django from blowing up bit-sets  NewTypePredicate-ReleaseTypePredicate cycles.
        # tl;dr : We create a clause with all possible predicates AND DO NOT DELETE IT till the end of the program.
        # This ensures a reference count of one and prevents django from growing the bitset each time.
        prediction_goal = language.get_prediction_goal()
        self.reference_pin_clause = ClauseWrapper(clause_id=None)
        self.reference_pin_clause.add_literal_as_head(Term(prediction_goal.functor, ["__refpin_arg__"] * prediction_goal.arity) ) # Ok, how do i do that?
        for rmode in language.get_refinement_modes():
            self.reference_pin_clause.add_literal_to_body(Term(rmode[0], *(["__refpin_arg__"] * rmode[1])))
        self.reference_pin_clause.lock_adding_to_clause()

    def evaluate(self, example: DjangoExample, test: DjangoQueryWrapper) -> bool:
        hypothesis_wrapper = test.external_representation
        example_clause_wrapper = example.external_representation  # type: ClauseWrapper
        does_subsume, run_time_ms = check_subsumption(hypothesis_wrapper, example_clause_wrapper)
        return does_subsume

    def transform_example(self, example_wrapper: ExampleWrapper) -> DjangoExample:
        classification_term = example_wrapper.classification_term if hasattr(example_wrapper, 'classification_term') else None
        example = DjangoExample(example_wrapper.logic_program, example_wrapper.label, classification_term)
        example.classification_term = example_wrapper.classification_term
        return example

    def wrap_query(self, tilde_query: TILDEQuery) -> QueryWrapper:
        return DjangoQueryWrapper(tilde_query, build_hypothesis(tilde_query))
