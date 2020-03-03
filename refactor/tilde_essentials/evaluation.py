from typing import List, Tuple

from refactor.tilde_essentials.example import Example
from refactor.representation.TILDE_query import TILDEQuery
from refactor.tilde_essentials.split_criterion import SplitCriterion


class TestEvaluator:
    """
    Abstract TestEvaluator class: used for evaluating a test on an example
    """

    def evaluate_test(self, test: TILDEQuery, examples: List[Example], split_criterion: SplitCriterion):
        # TODO: Probably decide against how things are done now and favour theta-subsumption with result caching rather than bypassing that system.
        test_conj = test.to_conjunction()
         


    def _evaluate_special_test(self, query, examples):
        special_test_result = query.get_special_test().run(examples, self)
        raise NotImplementedError('I should actually implement this')

    def evaluate(self, example, test) -> bool:
        raise NotImplementedError('abstract method')
