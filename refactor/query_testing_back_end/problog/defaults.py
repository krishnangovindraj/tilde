from problog.engine import DefaultEngine

from refactor.representation.example_collection import ExampleCollection
from refactor.default_interface import DefaultHandler
from refactor.query_testing_back_end.problog.evaluation import SimpleProgramQueryEvaluator
from refactor.tilde_essentials.test_generation import FOLTestGeneratorBuilder
from refactor.tilde_essentials.example import Example
from refactor.tilde_essentials.leaf_strategy import LeafBuilder
from refactor.tilde_essentials.splitter import Splitter
from refactor.tilde_essentials.stop_criterion import StopCriterion
from refactor.tilde_essentials.tree_builder import TreeBuilder
from refactor.tilde_config import TildeConfig


class ProblogDefaultHandler(DefaultHandler):
    @staticmethod
    def get_default_decision_tree_builder(language, prediction_goal) -> TreeBuilder:
        tilde_config = TildeConfig.get_instance()
        engine = DefaultEngine()
        engine.unknown = 1

        test_evaluator = SimpleProgramQueryEvaluator(engine=engine)

        test_generator_builder = FOLTestGeneratorBuilder(language=language,
                                                             query_head_if_keys_format=prediction_goal)
        splitter = Splitter(split_criterion_str=tilde_config.split_criterion, test_evaluator=test_evaluator,
                            test_generator_builder=test_generator_builder)
        # splitter = ProblogSplitter(language=language,split_criterion_str='entropy', test_evaluator=test_evaluator,
        #                            query_head_if_keys_format=prediction_goal)
        leaf_builder = LeafBuilder.get_leaf_builder(tilde_config.leaf_strategy)
        stop_criterion = StopCriterion()
        tree_builder = TreeBuilder(splitter=splitter, leaf_builder=leaf_builder, stop_criterion=stop_criterion)
        return tree_builder

    @staticmethod
    def get_transformed_example_list(training_examples_collection: ExampleCollection):
        examples = []
        for ex_wr_sp in training_examples_collection.get_example_wrappers_sp():
            example = Example(ex_wr_sp, ex_wr_sp.label)
            example.classification_term = ex_wr_sp.classification_term
            examples.append(example)
        return examples

