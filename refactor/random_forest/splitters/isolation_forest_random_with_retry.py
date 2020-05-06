from typing import Optional, List, Iterable
from refactor.tilde_essentials.example import Example
from refactor.representation.TILDE_query import TILDEQuery 

from refactor.tilde_essentials.split_criterion import SplitCriterion, SplitCriterionBuilder
from refactor.tilde_essentials.evaluation import TestEvaluator
from refactor.tilde_essentials.test_generation import TestGeneratorBuilder
from refactor.tilde_essentials.tree_node import TreeNode
from refactor.tilde_essentials.splitter import SplitInfo, Splitter

from .generate_and_sample import GenerateAndSampleSplitter
from refactor.split_criteria import DummyAllEqual

class IsolationForestRandomRetrySplitter(GenerateAndSampleSplitter):
    def __init__(self, test_evaluator, test_generator_builder, n_retry_before_giveup=0):
        super().__init__('dummy_all_equal', test_evaluator, test_generator_builder)
        self.n_retry_before_giveup = n_retry_before_giveup
        self.test_evaluator = test_evaluator
        self.test_generator_builder = test_generator_builder
        self.split_criterion = DummyAllEqual()

    def _sample_tests(self, all_tests: List[TILDEQuery], examples: List[Example]) -> List[TILDEQuery]:
        assert(len(examples) > 1)
        split_criterion = self.split_criterion
        tests_tried = 0

        from .test_samplers import HierarchicalTestSampler, UniformRandomTestSampler
        # test_sampler = HierarchicalTestSampler(all_tests)
        test_sampler = UniformRandomTestSampler(all_tests)
        while len(all_tests)>0 and tests_tried != self.n_retry_before_giveup:
            candidate_test = test_sampler.pop_random()
            # Now i need to evaluate this to make sure it works.
            if candidate_test is None:
                break

            examples_satisfying_test, examples_not_satisfying_test = self._split_examples(candidate_test, examples, self.split_criterion)
            if len(examples_satisfying_test) > 0 and len(examples_not_satisfying_test) > 0:
                
                candidate_test_score = split_criterion.calculate(examples_satisfying_test,
                                                                examples_not_satisfying_test
                                                                )
                return [SplitInfo(test=candidate_test,
                                examples_left=examples_satisfying_test,
                                examples_right=examples_not_satisfying_test,
                                score=candidate_test_score,
                                threshold=split_criterion.get_threshold(),
                                split_criterion=split_criterion.get_name())]
            tests_tried += 1

        # The examples could not be separated
        return [None]

    def _select_test(self, candidate_tests: Iterable[TILDEQuery], examples: List[Example], split_criterion: SplitCriterion) -> SplitInfo:
        return candidate_tests[0]
