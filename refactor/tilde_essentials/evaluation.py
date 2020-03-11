from typing import List, Tuple

from refactor.logic_manipulation_utils import TermManipulationUtils
from refactor.representation.TILDE_query import TILDEQuery
from refactor.special_tests.special_test import TildeTestResult
from refactor.tilde_essentials.example import Example
from refactor.tilde_essentials.query_wrapping import QueryWrapper
from refactor.tilde_essentials.split_criterion import SplitCriterion

class TestEvaluator:
    
    # TODO: Probably decide against how things are done now and favour theta-subsumption with result caching rather than bypassing that system.
        
    """
    Abstract TestEvaluator class: used for evaluating a test on an example
    """
    def evaluate_test(self, tilde_query: TILDEQuery, examples: List[Example], split_criterion: SplitCriterion) -> TildeTestResult:
        # HACK: Terrible hack because of a lack of consistency in the wrapping 
        original_test_conj = tilde_query.to_conjunction()
        current_query = tilde_query

        seen_unstable = False    
        
        for l in TermManipulationUtils.conjunction_to_list(original_test_conj):
            if hasattr(l, 'special_test') and l.special_test is not None:
                if seen_unstable and not l.special_test.is_stable():
                    raise Exception("Two unstable tests aren't supported. The complexity would end up being the product. Pls no. Fix your language.")
                else:
                    seen_unstable = seen_unstable or not l.special_test.is_stable()

                test_result = l.special_test.run(current_query, examples, self, split_criterion)
                current_query = test_result.test_query

        # TODO: Fix HACK! Both hax
        if not hasattr(current_query.literal, 'refine_state'):
            raise Exception("The special test failed to set the refine_state")
        
        current_query.literal.refine_state = tilde_query.literal.refine_state
        tilde_query.literal = current_query.literal
        
        results = []
        test = self.wrap_query(tilde_query)
        for ex in examples:
            results.append( (ex, self.evaluate(ex, test)) )
        test.destruct()

        return TildeTestResult(tilde_query, results)

    def _evaluate_special_test(self, query, examples):
        special_test_result = query.get_special_test().run(examples, self)
        raise NotImplementedError('I should actually implement this')

    def evaluate(self, example, test: QueryWrapper) -> bool:
        raise NotImplementedError('abstract method')

    def wrap_query(self, tilde_query: TILDEQuery) -> QueryWrapper:
        raise NotImplementedError('abstract method')