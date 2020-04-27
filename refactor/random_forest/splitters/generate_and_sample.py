from typing import Optional, List, Iterable
from refactor.tilde_essentials.example import Example
from refactor.representation.TILDE_query import TILDEQuery 

from refactor.tilde_essentials.split_criterion import SplitCriterion, SplitCriterionBuilder
from refactor.tilde_essentials.evaluation import TestEvaluator
from refactor.tilde_essentials.test_generation import TestGeneratorBuilder
from refactor.tilde_essentials.tree_node import TreeNode
from refactor.tilde_essentials.splitter import SplitInfo, Splitter

class GenerateAndSampleSplitter(Splitter):
    """ This Splitter generates all tests and randomly samples from them (blindly) before evaluating them.
    It only evaluates after the subset of attributes is sampled"""
    def __init__(self, split_criterion_str, test_evaluator: TestEvaluator,
                 test_generator_builder: TestGeneratorBuilder, verbose=False):
        self.split_criterion_str = split_criterion_str
        self.test_evaluator = test_evaluator
        self.test_generator_builder = test_generator_builder
        self.verbose=verbose

    def get_split(self, examples: List[Example], current_node: TreeNode) -> Optional[SplitInfo]:
        all_tests = []
        generator = self.test_generator_builder.generate_possible_tests(examples, current_node)
        for candidate_test in generator:
            if self.verbose:
                print(candidate_test)
            
            all_tests.append(candidate_test)

        sampled_tests =  self._sample_tests(all_tests, examples)

        split_criterion = SplitCriterionBuilder.get_split_criterion(
            self.split_criterion_str,
            examples, current_node.get_labels(examples))

        return self._select_test(sampled_tests, examples, split_criterion)


    def _sample_tests(self, all_tests: List[TILDEQuery], examples: List[Example]) -> List[TILDEQuery]:
        raise NotImplementedError('abstract method')

    def _select_test(self, candidate_tests: Iterable[TILDEQuery], examples: List[Example], split_criterion: SplitCriterion) -> SplitInfo:
        raise NotImplementedError('abstract method')
