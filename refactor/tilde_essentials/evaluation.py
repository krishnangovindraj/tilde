from typing import List, Tuple

from refactor.logic_manipulation_utils import TermManipulationUtils
from refactor.representation.example import ExampleWrapper
from refactor.representation.example_collection import ExampleCollection
from refactor.representation.TILDE_query import TILDEQuery
from refactor.tilde_essentials.example import Example
from refactor.tilde_essentials.query_wrapping import QueryWrapper
from refactor.tilde_essentials.split_criterion import SplitCriterion

class TildeTestResult:
    def __init__(self, test_query: TILDEQuery, test_results: Tuple[Example, bool]):
        self.test_query = test_query
        self.test_results = test_results

class TestEvaluator:
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

    def evaluate(self, example, test: QueryWrapper) -> bool:
        raise NotImplementedError('abstract method')

    def transform_example(self, example_wrapper: ExampleWrapper) -> Example:
        raise NotImplementedError('abstract method')

    def get_transformed_example_list(self, example_wrapper_list: List[ExampleWrapper]) -> List[Example]:
        return [self.transform_example(example_wrapper) for example_wrapper in example_wrapper_list]

    def wrap_query(self, tilde_query: TILDEQuery) -> QueryWrapper:
        raise NotImplementedError('abstract method')
