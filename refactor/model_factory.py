from enum import Enum

from refactor.representation.language import TypeModeLanguage
from refactor.tilde_config import TildeConfig
from refactor.tilde_essentials.evaluation import TestEvaluator

from refactor.tilde_essentials.leaf_strategy import LeafBuilder
from refactor.tilde_essentials.splitter import Splitter
from refactor.tilde_essentials.stop_criterion import StopCriterion
from refactor.tilde_essentials.tree_builder import TreeBuilder
from refactor.tilde_essentials.test_generation import FOLTestGeneratorBuilder
from refactor.background_management.groundedkb import GroundedKB

class ModelFactory:

    class BackendChoice(Enum):
        PROBLOG = 1
        SUBTLE = 2
        DJANGO = 3

    class RandomForestOptions:
        def __init__(self, n_trees: int, resample_size: int, n_tests_to_sample: int):
            self.n_trees = n_trees
            self.resample_size = resample_size
            self.n_tests_to_sample = n_tests_to_sample

    def __init__(self, tilde_config: TildeConfig, language: TypeModeLanguage, backend_choice: BackendChoice):
        self.tilde_config = tilde_config
        self.language = language
        if backend_choice in self.BackendChoice:
            self.backend_choice = backend_choice
        else:
            raise ValueError("Unknown backend choice" + self.backend_choice)

    def instantiate_backend(self, backend_choice: BackendChoice) -> TestEvaluator:
        if self.backend_choice == self.BackendChoice.PROBLOG:
            from refactor.query_testing_back_end.problog.evaluation import SimpleProgramQueryEvaluator
            from problog.engine import DefaultEngine
            engine = DefaultEngine()
            engine.unknown = 1
            return SimpleProgramQueryEvaluator(engine=engine)
        elif self.backend_choice == self.BackendChoice.SUBTLE:
            from refactor.query_testing_back_end.subtle.evaluation import SubtleQueryEvaluator
            return SubtleQueryEvaluator.build(self.tilde_config.subtle_path)
        elif self.backend_choice == self.BackendChoice.DJANGO:
            from refactor.query_testing_back_end.django.evaluation import DjangoQueryEvaluator
            return DjangoQueryEvaluator(self.language)
        else:
            raise ValueError("Unknown backend choice: " + backend_choice)

    def get_default_decision_tree_builder(self) -> TreeBuilder:
        test_evaluator = self.instantiate_backend(self.backend_choice)
        test_generator_builder = FOLTestGeneratorBuilder(language=self.language,
                                                            query_head_if_keys_format=self.language.get_prediction_goal())

        splitter = Splitter(split_criterion_str=self.tilde_config.split_criterion, test_evaluator=test_evaluator,
                            test_generator_builder=test_generator_builder)
        leaf_builder = LeafBuilder.get_leaf_builder(self.tilde_config.leaf_strategy)
        stop_criterion = StopCriterion()
        tree_builder = TreeBuilder(splitter=splitter, leaf_builder=leaf_builder, stop_criterion=stop_criterion)
        return tree_builder

    def get_rule_grounder(self, full_background_knowledge_sp, language, prediction_goal_handler) -> GroundedKB:
        from refactor.background_management.groundedkb import SubtleGroundedKB
        return SubtleGroundedKB(full_background_knowledge_sp, language, prediction_goal_handler)