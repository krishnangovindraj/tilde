from .generate_and_sample import GenerateAndSampleSplitter

from typing import Optional, List, Iterable
from refactor.tilde_essentials.example import Example
from refactor.representation.TILDE_query import TILDEQuery 

from refactor.tilde_essentials.split_criterion import SplitCriterion
from refactor.tilde_essentials.evaluation import TestEvaluator
from refactor.tilde_essentials.test_generation import TestGeneratorBuilder
from refactor.tilde_essentials.tree_node import TreeNode
from refactor.tilde_essentials.splitter import SplitInfo, Splitter

from random import sample as random_sample

class SampleNSelectBestGSSplitter(GenerateAndSampleSplitter):

    def __init__(self, split_criterion_str, test_evaluator: TestEvaluator,
                 test_generator_builder: TestGeneratorBuilder, n_tests_to_sample: int, verbose=False):
        
        self.n_tests_to_sample = n_tests_to_sample
        super().__init__(split_criterion_str, test_evaluator, test_generator_builder)
        
        self.verbose=verbose    
    
    def _sample_tests(self, all_tests: List[TILDEQuery], examples: List[Example]) -> List[TILDEQuery]:
        return random_sample(all_tests, min(len(all_tests), self.n_tests_to_sample))

    def _select_test(self, candidate_tests: Iterable[TILDEQuery], examples: List[Example], split_criterion: SplitCriterion)-> SplitInfo:
        current_best_split_info = None
        for candidate_test in candidate_tests:
            examples_satisfying_test, examples_not_satisfying_test = self._split_examples(candidate_test, examples, split_criterion)

            candidate_test_score = split_criterion.calculate(examples_satisfying_test,
                                                             examples_not_satisfying_test
                                                             )
            if current_best_split_info is None or candidate_test_score > current_best_split_info.score:
                current_best_split_info = SplitInfo(test=candidate_test,
                                                    examples_left=examples_satisfying_test,
                                                    examples_right=examples_not_satisfying_test,
                                                    score=candidate_test_score,
                                                    threshold=split_criterion.get_threshold(),
                                                    split_criterion=split_criterion.get_name())

        return current_best_split_info
