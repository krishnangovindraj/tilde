from refactor.background_management.background_manager import argument_combinations, BackgroundManager

def test_arg_combination_generator():
    signature = [ ('+', 'a'), ('+', 'b'), ('+', 'c'), ('+', 'a'), ('+', 'b'), ('-', 'd'), ('-', 'd') ]
    seen_vars = {
        'a' : {'a0', 'a1'},
        'b' : {'b0', 'b1', 'b2'},
        'c' : {'c0', 'c1', 'c2', 'c3'}
    }
    new_var = ('a', 'a_n')

    for ac in argument_combinations('f', signature, {}, seen_vars, new_var):
        print(ac)


def running_example_files():
    from os import path
    dir_path = path.join(path.dirname(path.abspath(__file__)), "even_rules")
    S_FILE = path.join(dir_path, "even.s")
    KB_FILE = path.join(dir_path, "even.kb")
    BG_FILE = path.join(dir_path, "even.bg")
    return S_FILE, KB_FILE, BG_FILE

def parse_settings_and_examples(S_FILE, KB_FILE, BG_FILE):
    
    from refactor.back_end_picking import get_back_end_default, QueryBackEnd
    from refactor.io.parsing_background_knowledge import parse_background_knowledge_keys
    from refactor.io.parsing_examples import KeysExampleBuilder
    from refactor.io.parsing_settings.setting_parser import KeysSettingsParser
    from refactor.representation.example import InternalExampleFormat

    internal_ex_format = InternalExampleFormat.CLAUSEDB
    parsed_settings = KeysSettingsParser().parse(S_FILE)
    
    prediction_goal_handler = parsed_settings.get_prediction_goal_handler()  # type: KeysPredictionGoalHandler
    prediction_goal = prediction_goal_handler.get_prediction_goal()  # type: Term

    background_knowledge_wrapper \
    = parse_background_knowledge_keys(BG_FILE,
                                      prediction_goal)  # type: BackgroundKnowledgeWrapper

    full_background_knowledge_sp \
        = background_knowledge_wrapper.get_full_background_knowledge_simple_program()  # type: Optional[SimpleProgram]

    example_builder = KeysExampleBuilder(prediction_goal, False)
    training_examples_collection = example_builder.parse(internal_ex_format, KB_FILE,
                                                     full_background_knowledge_sp)  # type: ExampleCollection

    backend = get_back_end_default(QueryBackEnd.SIMPLE_PROGRAM)
    examples = backend.get_transformed_example_list(training_examples_collection)
    

    return parsed_settings, examples, full_background_knowledge_sp

def test_language_parsing():
    from refactor.io.parsing_settings.setting_parser import KeysSettingsParser
    S_FILE, KB_FILE, BG_FILE = running_example_files()
    parsed_settings, examples, bg_sp = parse_settings_and_examples(S_FILE, KB_FILE, BG_FILE)
    pred_goal = parsed_settings.get_prediction_goal_handler().get_prediction_goal()
    
    bgm = BackgroundManager(pred_goal, parsed_settings.language, BG_FILE)
    bgm.setup()

    print(bgm.funcsig)
    print(bgm.intype2func)
    print(bgm.const_vals)


def test_lhm():
    # NOT TESTED
    S_FILE, KB_FILE, BG_FILE = running_example_files()
    parsed_settings, examples, bg_sp = parse_settings_and_examples(S_FILE, KB_FILE, BG_FILE)
    pred_goal = parsed_settings.get_prediction_goal_handler().get_prediction_goal()
    bgm = BackgroundManager(pred_goal, parsed_settings.language, BG_FILE)
    bgm.setup()

    for example in examples:
        print(bgm.derive_LHM_for_example(example))

def run_some_test():
    # test_arg_combination_generator()
    # test_language_parsing()
    test_lhm()


if __name__=='__main__':
    run_some_test()
