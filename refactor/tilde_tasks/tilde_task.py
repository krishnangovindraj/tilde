from enum import Enum

from refactor.representation.background_knowledge import BackgroundKnowledgeWrapper
from refactor.representation.example_collection import ExampleCollection
from refactor.io.parsing_settings.utils import FileSettings

from refactor.tilde_config import TildeConfig

from refactor.representation.example import InternalExampleFormat
class TildeTask:
    # Yet another level of abstraction in an attempt to detach things the original classification-centered design.

    # class TaskType(Enum):
    #     # Before you shoot me for the ordering, I like bits.  Mode & 8 -> forests.
    #     Classification = 1
    #     Regression = 2
    #     # Clustering = 3 # I don't have this implemented

    #     ClassificationRandomForest = 9
    #     # RegressionRandomForest = 10
    #     IsolationForest = 12

    def __init__(self, 
            settings : FileSettings, 
            training_examples : ExampleCollection,
            test_examples : ExampleCollection = None,
            bg_wrapper : BackgroundKnowledgeWrapper = None):
        self.settings = settings    # type: FileSettings

        self.training_examples = training_examples # type: ExampleCollection
        self.test_examples = test_examples  # type: ExampleCollection 

        self.background_knowledge_wrapper = bg_wrapper  # type: BackgroundKnowledgeWrapper

    @staticmethod
    def from_tilde_config(config: TildeConfig, internal_ex_format = InternalExampleFormat.CLAUSEDB, debug_printing_example_parsing=False):
        from problog.engine import DefaultEngine
        from refactor.io.label_collector import LabelCollectorMapper
        from refactor.io.parsing_background_knowledge import parse_background_knowledge_keys
        from refactor.io.parsing_examples import KeysExampleBuilder
        from refactor.io.parsing_settings.setting_parser import KeysSettingsParser


        parsed_settings = KeysSettingsParser().parse(config.s_file)

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
        # possible_labels = list(   )
        print('=== END collecting labels ===\n')

        # =================================================================================================================
        if config.fold_file is None:
            training_set = training_examples_collection
            test_set = None
        else:
            from problog.logic import Constant
            test_keys = set([ l.strip().split(':')[0] for l in open(config.fold_file,'r') if l.strip()])
            training_set = training_examples_collection.filter_examples_not_in_key_set(test_keys)
            test_set = training_examples_collection.filter_examples(test_keys)
        
        # from sys import stderr as sys_stderr
        # print("WARNING: YOU HAXED TILDE_TASK FOR RANDOM TEST_SET", file=sys_stderr)
        # from problog.logic import Constant
        # from random import sample as random_sample
        # all_keys = [e.key for e in training_examples_collection.get_example_wrappers_sp()]
        # print("ALL_KEYS_LENGTH=%d"%len(all_keys))
        # test_keys = random_sample(all_keys, int(0.1 * len(all_keys)))
        # training_set = training_examples_collection.filter_examples_not_in_key_set(test_keys)
        # test_set = training_examples_collection.filter_examples(test_keys)
    

        return TildeTask(parsed_settings, training_set, test_set, bg_wrapper=background_knowledge_wrapper)

