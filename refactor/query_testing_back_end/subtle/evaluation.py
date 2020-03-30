from typing import Optional

from pyswip import Prolog

from refactor.representation.example import ExampleWrapper
from refactor.representation.TILDE_query import TILDEQuery
from refactor.tilde_essentials.evaluation import TestEvaluator
from refactor.tilde_essentials.example import Example
from refactor.tilde_essentials.query_wrapping import QueryWrapper
from refactor.query_testing_back_end.subtle.clause_handling import build_hypothesis
from refactor.query_testing_back_end.subtle.subtle_example import SubtleExample
from refactor.query_testing_back_end.subtle.query_wrapping import SubtleQueryWrapper

class SubtleQueryEvaluator(TestEvaluator):
    @staticmethod
    def build(subtle_path: str)-> 'SubtleQueryEvaluator':
            prolog = Prolog()
            prolog.consult(subtle_path)
            return SubtleQueryEvaluator(prolog)

    def __init__(self, prolog:Prolog):
        self.prolog=prolog

        self.subsumes_str = "subsumes([{subsumer}],[{subsumee}])"

    def _subsumes(self, test_str, example_str):
        query_results_list = list(self.prolog.query(
            self.subsumes_str.format(
                subsumer=test_str, subsumee=example_str)))
        if query_results_list:  # dictionary is False if empty
            return True
        else:
            return False

    def evaluate(self, example: Example, test: QueryWrapper) -> bool:
        example_string = example.external_representation  # type: str
        query_string = test.external_representation  # type: str

        does_subsume = self._subsumes(query_string, example_string)
        return does_subsume

    def transform_example(self, example_wrapper: ExampleWrapper) -> SubtleExample:
        classification_term = example_wrapper.classification_term if hasattr(example_wrapper, 'classification_term') else None
        example = SubtleExample(example_wrapper.logic_program, example_wrapper.label, classification_term)
        example.classification_term = example_wrapper.classification_term
        return example

    def wrap_query(self, tilde_query: TILDEQuery):
        return SubtleQueryWrapper(tilde_query, build_hypothesis(tilde_query))

def _main():
    subsumer_string = 'p(X),q(X)'
    subsubsumee_string = 'p(a),p(b),q(c),q(a)'

    query_str = "subsumes([{subsumer}],[{subsumee}])".format(
        subsumer=subsumer_string, subsumee=subsubsumee_string)

    print(query_str)
