import statistics
import time

from problog.engine import DefaultEngine

from refactor.back_end_picking import get_back_end_default, QueryBackEnd
from refactor.tilde_essentials.tree import DecisionTree
from refactor.tilde_essentials.tree_builder import TreeBuilder
from refactor.query_testing_back_end.django.clause_handling import destruct_tree_tests
from refactor.io.label_collector import LabelCollectorMapper
from refactor.io.parsing_background_knowledge import parse_background_knowledge_keys
from refactor.io.parsing_examples import KeysExampleBuilder
from refactor.io.parsing_settings.setting_parser import KeysSettingsParser
from refactor.representation.example import InternalExampleFormat
from refactor.tilde_config import TildeConfig, _default_config_file_name

# Some defaults

DEFAULT_BACKEND_NAME = 'django'

RANDOM_FOREST_OPTIONS = (5, 10)  # N_TREES, N_TESTS_TO_SAMPLE
# RANDOM_FOREST_OPTIONS = None     # To disasble random forest

default_handlers = {
    'django': QueryBackEnd.DJANGO,
    'problog-simple': QueryBackEnd.SIMPLE_PROGRAM,
    'subtle': QueryBackEnd.SUBTLE,
    'FLGG': QueryBackEnd.FLGG,
}

internal_ex_format = InternalExampleFormat.CLAUSEDB

# Some util functions to keep things neat
def usage():
    print("Usage:")
    print("\tpython3 %s [config_file] [backend_name]")
    print("Defaults:")
    print("\tconfig_file: ", TildeConfig.DEFAULT_CONFIG_FILE_NAME)
    print("\tbackend_name: ", DEFAULT_BACKEND_NAME)

def parse_args(argv):
    # argv[1]: Config file
    config_file_name = TildeConfig.DEFAULT_CONFIG_FILE_NAME
    if len(argv) > 1:
        config_file_name = argv[1]

    # argv[2]: Backend name
    query_backend_name = DEFAULT_BACKEND_NAME
    if len(argv) > 2:
        if argv[2] in default_handlers:
            query_backend_name = argv[2]
        else:
            print("Unknown argument for backend: %s, using backend %s "%(argv[2], query_backend_name))

    return config_file_name, query_backend_name


def main(argv, random_forest_options=None):

    # Read and setup according to arguments
    config_file_name, query_backend_name = parse_args(argv)

    config = TildeConfig.create_instance(config_file_name)

    backend_enum = default_handlers[query_backend_name]
    backend = get_back_end_default(backend_enum)

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
    prediction_goal_handler = parsed_settings.get_prediction_goal_handler()  # type: KeysPredictionGoalHandler
    prediction_goal = prediction_goal_handler.get_prediction_goal()  # type: Term

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



    average_run_time_list = []

    # =================================================================================================================

    # Saturate the examples with background knowledge (using prolog for now).

    from refactor.background_management.groundedkb import SubtleGroundedKB, PrologGroundedKB
    groundedkb = SubtleGroundedKB(full_background_knowledge_sp, language, prediction_goal_handler)
    groundedkb.setup()
    groundedkb.saturate_examples(training_examples_collection)

    examples = backend.get_transformed_example_list(training_examples_collection)

    # TODO: Move all this stuff to some controller
    for k in language.special_tests:
        special_test = language.special_tests[k]
        special_test.setup(prediction_goal_handler, language, examples, full_background_knowledge_sp)

    # =================================================================================================================

    run_time_list = []

    for i in range(0, 1):
        print('=== START tree building ===')

        tree_builder = backend.get_default_decision_tree_builder(language, prediction_goal)  # type: TreeBuilder

        if random_forest_options is not None:
            from refactor.random_forest.random_forest_splitter import RandomForestSplitter
            from refactor.random_forest.random_forest import RandomForest

            tree_builder.splitter = RandomForestSplitter(tree_builder.splitter.split_criterion_str, tree_builder.splitter.test_evaluator, tree_builder.splitter.test_generator_builder, random_forest_options[1])
            random_forest = RandomForest(random_forest_options[0], len(examples))
            decision_tree = random_forest   # Little hack for convenience
        else:
            decision_tree = DecisionTree()

        start_time = time.time()
        decision_tree.fit(examples=examples, tree_builder=tree_builder)
        end_time = time.time()
        run_time_sec = end_time - start_time
        run_time_ms = 1000.0 * run_time_sec
        run_time_list.append(run_time_ms)
        print("run time (ms):", run_time_ms)
        print('=== END tree building ===')

        if random_forest_options is not None:
            from refactor.utils import print_confusion_matrix, training_confusion_matrix
            for t_i, t in enumerate(random_forest.trees):
                print(t)
                legend, mat = training_confusion_matrix(t)
                correct, all = sum(mat[i][i] for i in range(len(legend))), sum(mat[i][j] for j in range(len(legend)) for i in range(len(legend)))
                print("Training acc of tree[%d]: %d/%d = %f"%(t_i,correct, all, correct/all))
                # print_confusion_matrix(legend, mat)
                print("\n-\t-\t-\t-\t-\n")
        else:
            print(decision_tree)

        predictions = [ decision_tree.predict(e) for e in examples]
        n_correct = sum(1 if predictions[i] == examples[i].label else 0 for i in range(len(examples)) )
        print("Training acc=%d/%d=%f" % (n_correct, len(examples), n_correct/len(examples)) )

        print("=== start destructing tree queries ===")
        decision_tree.destruct()
        print("=== end destructing tree queries ===\n")

    average_run_time_ms = statistics.mean(run_time_list)
    average_run_time_list.append((query_backend_name, average_run_time_ms))

    print("average tree build time (ms):", average_run_time_ms)

    if backend_enum == QueryBackEnd.DJANGO:
        print("=== start destructing examples ===")
        for instance in examples:
            instance.destruct()
        print("=== end destructing examples ===")

    print ("\n=== average run times (ms) =======")
    for name, average_run_time_ms in average_run_time_list:
        print(name, ':', average_run_time_ms)

    return decision_tree


if __name__ == '__main__':
    from sys import argv as sys_argv
    main(sys_argv, random_forest_options=RANDOM_FOREST_OPTIONS)
