from refactor.default_interface import DefaultHandler
# from refactor.tilde_essentials.example import Example
from refactor.query_testing_back_end.subtle.subtle_example import SubtleExample
from refactor.tilde_essentials.leaf_strategy import LeafBuilder
from refactor.tilde_essentials.splitter import Splitter
from refactor.tilde_essentials.stop_criterion import StopCriterion
from refactor.tilde_essentials.tree_builder import TreeBuilder
from refactor.query_testing_back_end.subtle.clause_handling import build_clause
from refactor.query_testing_back_end.subtle.evaluation import SubtleQueryEvaluator
from refactor.tilde_essentials.test_generation import FOLTestGeneratorBuilder
from refactor.representation.example_collection import ExampleCollection
from refactor.tilde_config import TildeConfig


class SubtleDefaultHandler(DefaultHandler):

    @staticmethod
    def get_default_decision_tree_builder(language, prediction_goal) -> TreeBuilder:
        tilde_config = TildeConfig.get_instance()
        test_evaluator = SubtleQueryEvaluator.build(tilde_config.subtle_path)
        test_generator_builder = FOLTestGeneratorBuilder(language=language,
                                                            query_head_if_keys_format=prediction_goal)

        splitter = Splitter(split_criterion_str=tilde_config.split_criterion, test_evaluator=test_evaluator,
                            test_generator_builder=test_generator_builder)
        leaf_builder = LeafBuilder.get_leaf_builder(tilde_config.leaf_strategy)
        stop_criterion = StopCriterion()
        tree_builder = TreeBuilder(splitter=splitter, leaf_builder=leaf_builder, stop_criterion=stop_criterion)
        return tree_builder

    @staticmethod
    def get_transformed_example_list(training_examples_collection: ExampleCollection):
        examples = []
        for ex_wr_sp in training_examples_collection.get_example_wrappers_sp():
            classification_term = ex_wr_sp.classification_term if hasattr(ex_wr_sp, 'classification_term') else None
            example = SubtleExample(ex_wr_sp.logic_program, ex_wr_sp.label, classification_term)
            example.classification_term = ex_wr_sp.classification_term
            examples.append(example)
        return examples

    @staticmethod
    def get_transformed_test_example_list(simple_example_wrapper_list, training=False):
        test_examples_reformed = []
        for ex_wr_sp in simple_example_wrapper_list:
            classification_term = ex_wr_sp.classification_term if hasattr(ex_wr_sp, 'classification_term') else None
            # example_clause = build_clause(ex_wr_sp, training=False)
            example = SubtleExample(ex_wr_sp.logic_program, ex_wr_sp.label, classification_term)
            example.classification_term = ex_wr_sp.classification_term
            test_examples_reformed.append(example)
        return test_examples_reformed

    @staticmethod
    def create_example(data, label):
        pass
    