import statistics
import time

from problog.engine import DefaultEngine

from refactor.tilde_essentials.tree import DecisionTree
from refactor.tilde_essentials.tree_builder import TreeBuilder
from refactor.query_testing_back_end.django.clause_handling import destruct_tree_tests
from refactor.io.label_collector import LabelCollectorMapper
from refactor.io.parsing_background_knowledge import parse_background_knowledge_keys
from refactor.io.parsing_examples import KeysExampleBuilder
from refactor.io.parsing_settings.setting_parser import KeysSettingsParser
from refactor.representation.example import InternalExampleFormat
from refactor.tilde_config import TildeConfig
from refactor.model_factory import ModelFactory
from refactor.random_forest.random_forest import RandomForest


MODEL_OPTIONS = ModelFactory.IsolationForestOptions(50, 15, 20)
# MODEL_OPTIONS = ModelFactory.RandomForestOptions(5, 0, 10)
# MODEL_OPTIONS = None     # Use a simple DecisionTree

# Some defaults

DEFAULT_BACKEND_NAME = 'django' # 'problog-simple' # 'django'
backend_choice_map = {
    'django': ModelFactory.BackendChoice.DJANGO,
    'problog-simple': ModelFactory.BackendChoice.PROBLOG,
    'subtle': ModelFactory.BackendChoice.SUBTLE,
}

internal_ex_format = InternalExampleFormat.CLAUSEDB

# Some util functions to keep things neat
def usage():
    print("Usage:")
    print("\tpython3 %s [config_file] [backend_name]")
    print("Defaults:")
    print("\tconfig_file: ", TildeConfig.DEFAULT_CONFIG_FILE_PATH)
    print("\tbackend_name: ", DEFAULT_BACKEND_NAME)

def parse_args(argv):
    # argv[1]: Config file
    config_file_name = TildeConfig.DEFAULT_CONFIG_FILE_PATH
    if len(argv) > 1:
        config_file_name = argv[1]

    # argv[2]: Backend name
    query_backend_name = DEFAULT_BACKEND_NAME
    if len(argv) > 2:
        if argv[2] in backend_choice_map:
            query_backend_name = argv[2]
        else:
            print("Unknown argument for backend: %s, using backend %s "%(argv[2], query_backend_name))

    return config_file_name, query_backend_name


def main(argv, model_options=None):

    # Read and setup according to arguments
    config_file_name, query_backend_name = parse_args(argv)

    config = TildeConfig.from_file(config_file_name)

    backend_enum = backend_choice_map[query_backend_name]

    parsed_settings = KeysSettingsParser().parse(config.s_file)

    debug_printing_example_parsing = False
    # These don't seem to be used, but could be useful
    debug_printing_tree_building = False
    debug_printing_tree_pruning = False
    debug_printing_program_conversion = True
    debug_printing_get_classifier = False
    debug_printing_classification = False


    engine = DefaultEngine()
    engine.unknown = 1

    language = parsed_settings.language  # type: TypeModeLanguage

    # TODO: unify this with models --> let models use a prediction goal predicate label()
    prediction_goal_handler = parsed_settings.get_prediction_goal_handler() # type: KeysPredictionGoalHandler
    prediction_goal = language.get_prediction_goal()  # type: Term

    print('=== START parsing background ===')
    background_knowledge_wrapper \
        = parse_background_knowledge_keys(config.bg_file,
                                        prediction_goal)  # type: BackgroundKnowledgeWrapper

    full_background_knowledge_sp \
        = background_knowledge_wrapper.get_full_background_knowledge_simple_program()  # type: Optional[SimpleProgram]
    print('=== END parsing background ===\n')

    # =================================================================================================================


    print('=== START parsing examples ===')
    # EXAMPLES
    example_builder = KeysExampleBuilder(prediction_goal, debug_printing_example_parsing)
    training_examples_collection = example_builder.parse(internal_ex_format, config.kb_file,
                                                        full_background_knowledge_sp)  # type: ExampleCollection
    # =================================================================================================================


    print('=== START collecting labels ===')
    # LABELS
    index_of_label_var = prediction_goal_handler.get_predicate_goal_index_of_label_var()  # type: int
    label_collector = LabelCollectorMapper.get_label_collector(internal_ex_format, prediction_goal, index_of_label_var,
                                                            engine=engine)
    label_collector.extract_labels(training_examples_collection)

    possible_labels = label_collector.get_labels()  # type: Set[Label]
    possible_labels = list(possible_labels)
    print('=== END collecting labels ===\n')
    
    # =================================================================================================================

    # Saturate the examples with background knowledge (using prolog for now).
    model_factory = ModelFactory(config, language, backend_enum)

    tree_builder = model_factory.get_default_decision_tree_builder()
    rule_grounder = model_factory.get_rule_grounder(full_background_knowledge_sp, language, prediction_goal_handler)
    rule_grounder.setup()
    rule_grounder.saturate_examples(training_examples_collection.get_example_wrappers_sp())

    examples = tree_builder.splitter.test_evaluator.get_transformed_example_list(training_examples_collection.get_example_wrappers_sp())

    # TODO: Move all this stuff to some controller
    for k in language.special_tests:
        special_test = language.special_tests[k]
        special_test.setup(prediction_goal_handler, language, examples, full_background_knowledge_sp)

    # =================================================================================================================

    average_run_time_list = []
    run_time_list = []

    # all_examples = examples
    # pos_examples = [e for e in examples if str(e.label) != 'pos']
    # neg_examples = [e for e in examples if str(e.label) == 'pos']
    # from random import sample as random_sample
    # examples = pos_examples + random_sample(neg_examples, 3)
    # print([str(e.label) + str(e.classification_term) for e in examples])
    
    for _trial_i in range(0, 1):
        print('=== START tree building ===')

        if isinstance(model_options, ModelFactory.RandomForestOptions):
            tree_builder = model_factory.get_default_random_forest_tree_builder(model_options)
            model = model_factory.create_random_forest(model_options)
        elif isinstance(model_options, ModelFactory.IsolationForestOptions):
            tree_builder = model_factory.get_default_isolation_forest_tree_builder(model_options)        
            model = model_factory.create_isolation_forest(model_options)
        else: # elif isinstance(model_options, ModelFactory.DecisionTreeOptions):
            tree_builder = model_factory.get_default_decision_tree_builder()
            model = model_factory.create_decision_tree()
        
        start_time = time.time()
        model.fit(examples=examples, tree_builder=tree_builder)
        end_time = time.time()
        run_time_sec = end_time - start_time
        run_time_ms = 1000.0 * run_time_sec
        run_time_list.append(run_time_ms)
        print("run time (ms):", run_time_ms)
        print('=== END tree building ===')

        from refactor.utils import print_model_summary
        print_model_summary(model, examples)
        
        print("=== start destructing tree queries ===")
        model.destruct()
        print("=== end destructing tree queries ===\n")
    average_run_time_ms = statistics.mean(run_time_list)
    average_run_time_list.append((query_backend_name, average_run_time_ms))

    print("average tree build time (ms):", average_run_time_ms)

    print("=== start destructing examples ===")
    for instance in examples:
        instance.destruct()
    print("=== end destructing examples ===")

    print ("\n=== average run times (ms) =======")
    for name, average_run_time_ms in average_run_time_list:
        print(name, ':', average_run_time_ms)

    return model


if __name__ == '__main__':
    from sys import argv as sys_argv
    main(sys_argv, model_options=MODEL_OPTIONS)
