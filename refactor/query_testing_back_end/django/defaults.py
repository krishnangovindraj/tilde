from refactor.default_interface import DefaultHandler
from refactor.tilde_essentials.example import Example
from refactor.tilde_essentials.leaf_strategy import LeafBuilder
from refactor.tilde_essentials.stop_criterion import StopCriterion
from refactor.tilde_essentials.tree_builder import TreeBuilder
from refactor.query_testing_back_end.django.clause_handling import build_clause
from refactor.query_testing_back_end.django.evaluation import DjangoQueryEvaluator
from refactor.query_testing_back_end.django.splitter import DjangoSplitter
from refactor.query_testing_back_end.django.django_example import DjangoExample
from refactor.tilde_essentials.test_generation import FOLTestGeneratorBuilder
from refactor.representation.example_collection import ExampleCollection
from refactor.tilde_config import TildeConfig


class DjangoDefaultHandler(DefaultHandler):
    @staticmethod
    def get_default_decision_tree_builder(language, prediction_goal) -> TreeBuilder:
        tilde_config = TildeConfig.get_instance()
        test_evaluator = DjangoQueryEvaluator()
        test_generator_builder = FOLTestGeneratorBuilder(language=language,
                                                            query_head_if_keys_format=prediction_goal)

        splitter = DjangoSplitter(split_criterion_str=tilde_config.split_criterion, test_evaluator=test_evaluator,
                                  test_generator_builder=test_generator_builder)
        leaf_builder = LeafBuilder.get_leaf_builder(tilde_config.leaf_strategy)
        stop_criterion = StopCriterion()
        tree_builder = TreeBuilder(splitter=splitter, leaf_builder=leaf_builder, stop_criterion=stop_criterion)
        return tree_builder

    @staticmethod
    def get_transformed_example_list(training_examples_collection: ExampleCollection):
        examples = []
        for ex_wr_sp in training_examples_collection.get_example_wrappers_sp():
            # example_clause = build_clause(ex_wr_sp)
            example = DjangoExample(ex_wr_sp, ex_wr_sp.label, True)
            example.classification_term = ex_wr_sp.classification_term
            examples.append(example)
        return examples

    @staticmethod
    def get_transformed_test_example_list(simple_example_wrapper_list, training=False):
        test_examples_reformed = []
        for ex_wr_sp in simple_example_wrapper_list:
            # example_clause = build_clause(ex_wr_sp, training=False)
            classification_term = ex_wr_sp.classification_term if hasattr(ex_wr_sp, 'classification_term') else None
            example = DjangoExample(ex_wr_sp.logic_program, ex_wr_sp.label, classification_term)
            example.classification_term = ex_wr_sp.classification_term
            test_examples_reformed.append(example)
        return test_examples_reformed

