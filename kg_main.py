import statistics
import time


from refactor.tilde_essentials.tree import DecisionTree
from refactor.tilde_essentials.tree_builder import TreeBuilder
from refactor.query_testing_back_end.django.clause_handling import destruct_tree_tests
from refactor.representation.example import InternalExampleFormat
from refactor.tilde_config import TildeConfig

from refactor.model_factory import ModelFactory
from refactor.random_forest.random_forest import RandomForest

from refactor.tilde_tasks.tilde_task import TildeTask
from refactor.query_testing_back_end import BackendChoice

# MODEL_OPTIONS = ModelFactory.IsolationForestOptions(50, 15, 20)
# MODEL_OPTIONS = ModelFactory.RandomForestOptions(5, 0, 10)
MODEL_OPTIONS = None     # Use a simple DecisionTree

# Some defaults
DEFAULT_BACKEND_NAME = 'DJANGO'

internal_ex_format = InternalExampleFormat.CLAUSEDB

debug_printing_tree_building = False
debug_printing_tree_pruning = False
debug_printing_program_conversion = True
debug_printing_get_classifier = False
debug_printing_classification = False


def run_task(config: TildeConfig):
    debug_printing_example_parsing = False
    # These don't seem to be used, but could be useful

    tilde_task = TildeTask.from_tilde_config(config, internal_ex_format, debug_printing_example_parsing)
    model_options = ModelFactory.model_options_from_settings(tilde_task.settings.algorithm_settings.tilde_mode)
    
    language = tilde_task.settings.language  # type: TypeModeLanguage

    # TODO: unify this with models --> let models use a prediction goal predicate label()
    prediction_goal_handler = tilde_task.settings.get_prediction_goal_handler() # type: KeysPredictionGoalHandler
    prediction_goal = language.get_prediction_goal()  # type: Term

    full_background_knowledge_sp = \
        tilde_task.background_knowledge_wrapper.get_full_background_knowledge_simple_program()  # type: Optional[SimpleProgram]

    training_examples_collection = tilde_task.training_examples  # type: ExampleCollection
    # =================================================================================================================

    # Saturate the examples with background knowledge (using prolog for now).
    model_factory = ModelFactory(config, language, config.backend_choice)

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
    average_run_time_list.append((config.backend_choice, average_run_time_ms))

    print("average tree build time (ms):", average_run_time_ms)

    print("=== start destructing examples ===")
    for instance in examples:
        instance.destruct()
    print("=== end destructing examples ===")

    print ("\n=== average run times (ms) =======")
    for name, average_run_time_ms in average_run_time_list:
        print(name, ':', average_run_time_ms)

    return model


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
    query_backend_name = None
    if len(argv) > 2:
        query_backend_name = argv[2]

    return config_file_name, query_backend_name

def main(argv):
    # Read and setup according to arguments
    config_file_name, query_backend_name_override = parse_args(argv)
    config = TildeConfig.from_file(config_file_name)

    # TODO: Remove this line
    # query_backend_name_override = DEFAULT_BACKEND_NAME
    if query_backend_name_override is not None:
        config.override_setting(TildeConfig.SettingsKeys._backend_choice, query_backend_name_override)

    return run_task(config)


if __name__ == '__main__':
    from sys import argv as sys_argv
    main(sys_argv)
