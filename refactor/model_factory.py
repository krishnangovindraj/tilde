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

from refactor.query_testing_back_end import BackendChoice

class ModelFactory:

    class ModelOptions: pass
    class ClassificationOptions(ModelOptions): pass
    class RegressionTreeOptions(ModelOptions): pass

    class RandomForestOptions(ModelOptions):
        DEFAULT_RESAMPLE_SIZE = 0; DEFAULT_TESTS_TO_SAMPLE = 20
        def __init__(self, n_trees: int, resample_size: int, n_tests_to_sample: int):
            self.n_trees = n_trees
            self.resample_size = resample_size
            self.n_tests_to_sample = n_tests_to_sample

    class IsolationForestOptions(ModelOptions):
        DEFAULT_MAX_DEPTH = 15; DEFAULT_TESTS_TO_SAMPLE = 20
        def __init__(self, n_trees: int, max_branch_depth: int, n_tests_before_giveup: int):
            self.n_trees = n_trees
            self.max_branch_depth = max_branch_depth
            self.n_tests_before_giveup = n_tests_before_giveup

    # The actual class

    def __init__(self, tilde_config: TildeConfig, language: TypeModeLanguage, backend_choice: BackendChoice):
        self.tilde_config = tilde_config
        self.language = language
        if backend_choice in BackendChoice:
            self.backend_choice = backend_choice
        else:
            raise ValueError("Unknown backend choice: " + backend_choice)

    def instantiate_backend(self, backend_choice: BackendChoice) -> TestEvaluator:
        if self.backend_choice == BackendChoice.PROBLOG:
            from refactor.query_testing_back_end.problog.evaluation import SimpleProgramQueryEvaluator
            from problog.engine import DefaultEngine
            engine = DefaultEngine()
            engine.unknown = 1
            return SimpleProgramQueryEvaluator(engine=engine)
        elif self.backend_choice == BackendChoice.SUBTLE:
            from refactor.query_testing_back_end.subtle.evaluation import SubtleQueryEvaluator
            return SubtleQueryEvaluator.build(self.tilde_config.subtle_path)
        elif self.backend_choice == BackendChoice.DJANGO:
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

    def create_decision_tree(self):
        from refactor.tilde_essentials.tree import DecisionTree
        return DecisionTree()

    def get_default_random_forest_tree_builder(self, random_forest_options: RandomForestOptions):
        from refactor.random_forest.random_forest_splitter import RandomForestSplitter
        tree_builder = self.get_default_decision_tree_builder()
        tree_builder.splitter = RandomForestSplitter(tree_builder.splitter.split_criterion_str, tree_builder.splitter.test_evaluator, tree_builder.splitter.test_generator_builder, random_forest_options.n_tests_to_sample)
        return tree_builder

    def create_random_forest(self, random_forest_options: RandomForestOptions):
        from refactor.random_forest.random_forest import RandomForest
        return RandomForest(random_forest_options.n_trees, random_forest_options.resample_size)


    def get_rule_grounder(self, full_background_knowledge_sp, language, prediction_goal_handler) -> GroundedKB:
        from refactor.background_management.groundedkb import SubtleGroundedKB
        return SubtleGroundedKB(full_background_knowledge_sp, language, prediction_goal_handler)

    def get_default_isolation_forest_tree_builder(self, isolation_forest_options: IsolationForestOptions):
        from refactor.random_forest.isolation_forest_stop_criterion import IsolationForestStopCriterion
        from refactor.random_forest.isolation_forest import IsolationForest
        from refactor.random_forest.splitters.isolation_forest_random_with_retry import IsolationForestRandomRetrySplitter

        tree_builder = self.get_default_decision_tree_builder()
        tree_builder.stop_criterion = IsolationForestStopCriterion(isolation_forest_options.max_branch_depth)
        tree_builder.splitter = IsolationForestRandomRetrySplitter(tree_builder.splitter.test_evaluator, tree_builder.splitter.test_generator_builder, isolation_forest_options.n_tests_before_giveup)

        return tree_builder

    def create_isolation_forest(self, isolation_forest_options: IsolationForestOptions):
        from refactor.random_forest.isolation_forest import IsolationForest
        isolation_forest = IsolationForest(isolation_forest_options.n_trees)
        return isolation_forest

    # Some useful statics
    @staticmethod
    def model_options_from_settings(tilde_mode_term: 'problog.logic.Term'):
        if tilde_mode_term.functor == 'classification':
            return ModelFactory.ClassificationOptions()
        elif tilde_mode_term.functor == 'regression':
            return ModelFactory.RegressionTreeOptions()
        elif tilde_mode_term.functor == 'random_forest_classification':
            if tilde_mode_term.arity > 0:
                n_trees = int(tilde_mode_term.args[0])
                resample_size = int(tilde_mode_terms.args[1] if tilde_mode_term.arity > 1 else ModelFactory.RandomForestOptions.DEFAULT_RESAMPLE_SIZE)
                tests_to_sample = int(tilde_mode_terms.args[1] if tilde_mode_term.arity > 2 else ModelFactory.RandomForestOptions.DEFAULT_TESTS_TO_SAMPLE)
                return ModelFactory.RandomForestOptions(n_trees, resample_size, tests_to_sample)
            else:
                raise Exception("Tilde_mode random_forest_classification(n_trees, [resample_size, n_tests]) expects >= 1 arg")
        elif tilde_mode_term.functor == 'isolation_forest':
            if tilde_mode_term.arity > 0:
                n_trees = int(tilde_mode_term.args[0])
                max_branch_depth = int(tilde_mode_term.args[1] if tilde_mode_term.arity > 1 else ModelFactory.IsolationForestOptions.DEFAULT_MAX_DEPTH)
                tests_to_sample = int(tilde_mode_term.args[1] if tilde_mode_term.arity > 2 else ModelFactory.IsolationForestOptions.DEFAULT_TESTS_TO_SAMPLE)
                return ModelFactory.IsolationForestOptions(n_trees, max_branch_depth, tests_to_sample)
            else:
                raise Exception("Tilde_mode isolation_forest(n_trees, [max_branch_depth, n_tests_to_sample]) expects >= 1 arg")
