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

# Some defaults
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
    test_examples_collection = tilde_task.test_examples
    # =================================================================================================================

    # Saturate the examples with background knowledge (using prolog for now).
    model_factory = ModelFactory(config, language, config.backend_choice)

    tree_builder = model_factory.get_default_decision_tree_builder()
    rule_grounder = model_factory.get_rule_grounder(full_background_knowledge_sp, language, prediction_goal_handler)
    rule_grounder.setup()

    rule_grounder.saturate_examples(training_examples_collection.get_example_wrappers_sp())
    examples = tree_builder.splitter.test_evaluator.get_transformed_example_list(training_examples_collection.get_example_wrappers_sp())

    if test_examples_collection is not None:        
        rule_grounder.saturate_examples(test_examples_collection.get_example_wrappers_sp())
        test_examples = tree_builder.splitter.test_evaluator.get_transformed_example_list(test_examples_collection.get_example_wrappers_sp())
        all_examples = examples + test_examples
        print("Training-test split: %d:%d"%(len(examples), len(test_examples)))
    else:
        test_examples = None
        all_examples = [e for e in examples]
    
    # TODO: Move all this stuff to some controller
    for k in language.special_tests:
        special_test = language.special_tests[k]
        special_test.setup(prediction_goal_handler, language, all_examples, full_background_knowledge_sp)

    # =================================================================================================================

    average_run_time_list = []
    run_time_list = []

    for _trial_i in range(0, 5):

        if isinstance(model_options, ModelFactory.IsolationForestOptions):
            print("run kg_main_isolation instead")
            
        # from random import sample as random_sample
        # test_examples_set = random_sample(all_examples, int(0.1 * len(examples)))
        # examples = [e for e in all_examples if e not in test_examples_set]
        # test_examples = list(test_examples_set)

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
        
        # print(model)
        # for t in model.trees: print("-----------\n"+t.dump_weights())
        
        from refactor.utils import print_model_summary            
        if test_examples is not None:
            # Test phase:
            print_model_summary(model, test_examples)
        else:
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

    if query_backend_name_override is not None:
        config.override_setting(TildeConfig.SettingsKeys._backend_choice, query_backend_name_override)

    return run_task(config)


if __name__ == '__main__':
    from sys import argv as sys_argv
    main(sys_argv)
    # [main(sys_argv) for _ in range(5)]
