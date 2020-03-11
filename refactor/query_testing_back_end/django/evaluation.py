from refactor.tilde_essentials.evaluation import TestEvaluator
from refactor.query_testing_back_end.django.django_example import DjangoExample
try:
    from src.ClauseWrapper import ClauseWrapper, HypothesisWrapper
    from src.subsumption_checking import check_subsumption
except ImportError as err:
    from refactor.query_testing_back_end.django.django_wrapper.ClauseWrapper import ClauseWrapper, HypothesisWrapper
    from refactor.query_testing_back_end.django.django_wrapper.subsumption_checking import check_subsumption

from refactor.representation.TILDE_query import TILDEQuery
from refactor.query_testing_back_end.django.clause_handling import build_hypothesis


class DjangoQueryEvaluator(TestEvaluator):
    def evaluate(self, example: DjangoExample, test: HypothesisWrapper) -> bool:
        example_clause_wrapper = example.external_rep  # type: ClauseWrapper

        does_subsume, run_time_ms = check_subsumption(test, example_clause_wrapper)
        return does_subsume

    def wrap_query(self, tilde_query: TILDEQuery):
        return build_hypothesis(tilde_query)